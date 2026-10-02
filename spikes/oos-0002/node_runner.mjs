#!/usr/bin/env node
// DISPOSABLE SPIKE CODE (OOS-0002). Not production. Do not import from the kernel.
//
// TypeScript/Node candidate runner (plain ESM JavaScript, so it runs without a build step;
// TypeScript would add compile-time types, not runtime behaviour). No npm dependencies.
// Drives the SAME fake provider (spikes/oos-0002/fake_provider.py) over the same JSONL protocol.
//
//   node spikes/oos-0002/node_runner.mjs [all|e1|e2|e3|e4|e6]
//   env OOS_SPIKE_PYTHON = python executable used to run the fake provider (default: "python")
//
// E5 (journal + recovery) is not duplicated: it is plain append/fsync/parse file I/O, which both
// runtimes do equivalently (fs.appendFileSync + fs.fsyncSync); it does not discriminate.
import { spawn, spawnSync } from "node:child_process";
import { createInterface } from "node:readline";
import { mkdtempSync, writeFileSync, readFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROVIDER = join(HERE, "fake_provider.py");
const PY = process.env.OOS_SPIKE_PYTHON || "python";
const IS_WINDOWS = process.platform === "win32";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function pidAlive(pid) {
  try { process.kill(pid, 0); return true; } catch (e) { return e.code === "EPERM"; }
}

function killTree(pid) {
  // No per-worker Job Object without a native addon: taskkill /T (Windows) or a process group (POSIX).
  // Asynchronous, so the event loop (and every other worker's timers) keeps running.
  if (IS_WINDOWS) return new Promise((r) => spawn("taskkill", ["/PID", String(pid), "/T", "/F"], { stdio: "ignore" }).on("exit", r));
  try { process.kill(-pid, "SIGKILL"); } catch { /* gone */ }
  return Promise.resolve(0);
}
function killTreeSync(pid) { // experiment hygiene only
  if (IS_WINDOWS) spawnSync("taskkill", ["/PID", String(pid), "/T", "/F"], { stdio: "ignore" });
  else { try { process.kill(-pid, "SIGKILL"); } catch { /* gone */ } }
}

function runWorker(spec, { timeoutMs, cancelAfterMs = null, graceMs = 500, cwd } = {}) {
  return new Promise((resolve) => {
    const t0 = performance.now();
    const child = spawn(PY, [PROVIDER], { cwd, stdio: ["pipe", "pipe", "pipe"], detached: !IS_WINDOWS });
    const events = [];
    let malformed = 0, outcome = null, exitCode = null, reaped = false, settled = false;
    createInterface({ input: child.stdout }).on("line", (line) => {
      try { events.push(JSON.parse(line)); } catch { malformed++; }
    });
    child.stdin.write(JSON.stringify(spec) + "\n");
    const timer = setTimeout(() => { outcome = "timed_out"; killTree(child.pid); }, timeoutMs);
    let cancelTimer = null;
    if (cancelAfterMs !== null) {
      cancelTimer = setTimeout(() => {
        outcome = "cancel_requested";
        child.stdin.write('{"type": "cancel"}\n');
        setTimeout(() => { if (exitCode === null) { outcome = "cancel_forced"; killTree(child.pid); } }, graceMs);
      }, cancelAfterMs);
    }
    const finish = () => {
      if (settled) return; settled = true;
      clearTimeout(timer); if (cancelTimer) clearTimeout(cancelTimer);
      const result = [...events].reverse().find((e) => e.type === "result");
      const cancelled = events.some((e) => e.type === "cancelled");
      let status, retryable;
      if (outcome === "timed_out") [status, retryable] = ["timed_out", true];
      else if (outcome === "cancel_forced") [status, retryable] = ["cancelled_forced", false];
      else if (cancelled) [status, retryable] = ["cancelled", false];
      else if (result) [status, retryable] = [result.status, false];
      else [status, retryable] = ["crashed", true];
      const gc = events.find((e) => e.type === "grandchild");
      resolve({ task_id: spec.task_id, status, retryable, exit_code: exitCode, events: events.length,
        malformed_events: malformed, descendants_reaped_after_exit: reaped,
        grandchild_alive_after: gc ? pidAlive(gc.pid) : null,
        elapsed_s: +((performance.now() - t0) / 1000).toFixed(3) });
      if (gc && pidAlive(gc.pid)) killTreeSync(gc.pid); // experiment hygiene only
    };
    child.on("exit", (code) => {
      exitCode = code;
      // 'close' (stdio EOF) never fires while an inheriting descendant lives. Try to reap the tree.
      setTimeout(async () => { if (!settled) { reaped = true; await killTree(child.pid); setTimeout(finish, 300); } }, 500);
    });
    child.on("close", () => setTimeout(finish, 0));
  });
}

async function e1() {
  const measure = (cmd, args, n = 10) => {
    const ts = [];
    for (let i = 0; i < n; i++) { const t = performance.now(); spawnSync(cmd, args); ts.push(performance.now() - t); }
    ts.sort((a, b) => a - b);
    return +ts[Math.floor(n / 2)].toFixed(1);
  };
  return { n: 10, node_spawns_python_ms_median: measure(PY, ["-c", "pass"]),
           node_cold_start_ms_median: measure(process.execPath, ["-e", "0"]) };
}

async function e2() {
  const specs = [
    [{ task_id: "A-ok-fast", behavior: "succeed", duration_s: 0.3 }, {}],
    [{ task_id: "B-ok-slow", behavior: "succeed", duration_s: 1.2 }, {}],
    [{ task_id: "C-hang", behavior: "hang" }, { timeoutMs: 1000 }],
    [{ task_id: "D-cancel", behavior: "succeed", duration_s: 5 }, { cancelAfterMs: 400 }],
    [{ task_id: "E-crash", behavior: "crash", duration_s: 0.5 }, {}],
    [{ task_id: "F-ask", behavior: "ask", duration_s: 0.3 }, {}],
    [{ task_id: "G-ignores-cancel", behavior: "ignore_cancel", duration_s: 5 }, { cancelAfterMs: 400 }],
    [{ task_id: "H-leaves-grandchild", behavior: "leave_grandchild", duration_s: 0.3 }, {}],
  ];
  const t = performance.now();
  const workers = await Promise.all(specs.map(([s, kw]) => runWorker(s, { timeoutMs: 4000, ...kw })));
  return { wall_s: +((performance.now() - t) / 1000).toFixed(3), workers };
}

function startWithGrandchild() {
  return new Promise((resolve) => {
    const child = spawn(PY, [PROVIDER], { stdio: ["pipe", "pipe", "ignore"] });
    createInterface({ input: child.stdout }).on("line", (line) => {
      const ev = JSON.parse(line);
      if (ev.type === "grandchild") resolve({ child, gc: ev.pid });
    });
    child.stdin.write(JSON.stringify({ task_id: "tree", behavior: "spawn_grandchild" }) + "\n");
  });
}

async function e3() {
  const out = {};
  let { child, gc } = await startWithGrandchild();
  child.kill(); await sleep(300);
  out.naive_kill_grandchild_survived = pidAlive(gc);
  if (pidAlive(gc)) killTreeSync(gc);
  ({ child, gc } = await startWithGrandchild());
  await killTree(child.pid); await sleep(300);
  out.tree_kill_grandchild_survived = pidAlive(gc);
  out.mechanism = IS_WINDOWS ? "taskkill /T /F (external tool, while the parent still exists)" : "process group";
  return out;
}

async function e4() {
  // The Node orchestrator dies abruptly. Do its workers survive?
  const d = mkdtempSync(join(tmpdir(), "oos-e4-"));
  const pidfile = join(d, "pids.json");
  const t = performance.now();
  spawnSync(process.execPath, [fileURLToPath(import.meta.url), "crash-child", pidfile], { stdio: "ignore" });
  const parentExit = +((performance.now() - t) / 1000).toFixed(2);
  await sleep(500);
  const pids = JSON.parse(readFileSync(pidfile, "utf8"));
  const alive = { worker: pidAlive(pids.worker), grandchild: pidAlive(pids.grandchild) };
  for (const p of Object.values(pids)) if (pidAlive(p)) killTreeSync(p);
  rmSync(d, { recursive: true, force: true });
  // Observed: the direct child dies with the Node parent, the grandchild survives. Inferred (libuv
  // source, not verified here): libuv's global kill-on-close job with silent breakaway for descendants.
  return { parent_exit_s: parentExit, after_orchestrator_crash: alive,
           direct_children_die_with_node: !alive.worker, descendants_survive: alive.grandchild };
}

async function crashChild(pidfile) {
  const { child, gc } = await startWithGrandchild();
  writeFileSync(pidfile, JSON.stringify({ worker: child.pid, grandchild: gc }));
  process.exit(1); // simulate OOS crash
}

async function e6() {
  const base = mkdtempSync(join(tmpdir(), "oos-e6-"));
  const ws = join(base, "workspace with spaces ä ö å");
  mkdirSync(ws);
  const out = {};
  for (const mode of ["utf8", "native"]) {
    if (mode === "native") process.env.OOS_FAKE_PROVIDER_NATIVE_ENCODING = "1";
    const name = `résumé ünïcode ${mode}.txt`;
    const rec = await runWorker({ task_id: "P", behavior: "write_file", file_name: name, duration_s: 0.1 },
                                { timeoutMs: 10000, cwd: ws });
    delete process.env.OOS_FAKE_PROVIDER_NATIVE_ENCODING;
    out[`${mode}_worker_status`] = rec.status;
    out[`${mode}_unicode_file_created_correctly`] = existsSync(join(ws, name));
  }
  out.note = "JSON.stringify sends raw UTF-8; a provider decoding with the locale code page mangles it";
  rmSync(base, { recursive: true, force: true });
  const dead = spawn(PY, ["-c", "pass"]); await new Promise((r) => dead.on("exit", r)); await sleep(100);
  return { ...out, liveness_probe_signal0_on_dead_pid: pidAlive(dead.pid) };
}

const EXPERIMENTS = { e1, e2, e3, e4, e6 };
const argv = process.argv.slice(2);
if (argv[0] === "crash-child") { await crashChild(argv[1]); }
else {
  const which = EXPERIMENTS[argv[0]] ? [argv[0]] : Object.keys(EXPERIMENTS);
  const results = { runtime: `node ${process.version}`, platform: process.platform };
  for (const n of which) { const t = performance.now(); results[n] = await EXPERIMENTS[n]();
    results[n + "_runtime_s"] = +((performance.now() - t) / 1000).toFixed(2); }
  console.log(JSON.stringify(results, null, 2));
  process.exit(0);
}

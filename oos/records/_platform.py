"""Platform-specific primitives, isolated here (ADR-0008). Windows and POSIX both first-class.

- FileLock: an exclusive advisory lock that the OS releases when the holder dies
  (Windows msvcrt byte-range lock, POSIX flock), so a crashed writer cannot wedge the store.
- Atomic file installation: write a temp file, fsync it, then install it in one step.
  * install_new: fails if the target already exists (create-only semantics).
  * install_replace: atomically replaces the target.
"""
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

from .errors import LockTimeout

IS_WINDOWS = os.name == "nt"
TMP_PREFIX = ".tmp-"

if IS_WINDOWS:
    import msvcrt
else:
    import fcntl


class FileLock:
    def __init__(self, path: Path, timeout_s: float = 10.0, poll_s: float = 0.01):
        self.path, self.timeout_s, self.poll_s = Path(path), timeout_s, poll_s
        self._f = None

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        f = open(self.path, "a+b")
        deadline = time.monotonic() + self.timeout_s
        while True:
            try:
                if IS_WINDOWS:
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._f = f
                return self
            except OSError:
                if time.monotonic() >= deadline:
                    f.close()
                    raise LockTimeout(f"{self.path.name}: lock not acquired within {self.timeout_s}s") from None
                time.sleep(self.poll_s)

    def __exit__(self, *exc) -> None:
        f, self._f = self._f, None
        if f is None:
            return
        try:
            if IS_WINDOWS:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()


def fsync_dir(path: Path) -> None:
    """Persist a directory entry change. Not possible on Windows (rename is metadata-journaled by NTFS)."""
    if IS_WINDOWS:
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_temp(directory: Path, data: bytes) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    tmp = directory / f"{TMP_PREFIX}{uuid.uuid4().hex}"
    with open(tmp, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return tmp


def install_new(tmp: Path, final: Path) -> None:
    """Atomically make `tmp` visible as `final`. Raise FileExistsError if `final` exists."""
    try:
        if IS_WINDOWS:
            os.rename(tmp, final)  # MoveFileEx without REPLACE_EXISTING: atomic and create-only
        else:
            os.link(tmp, final)  # create-only, atomic
            os.unlink(tmp)
    except FileExistsError:
        tmp.unlink(missing_ok=True)
        raise
    fsync_dir(final.parent)


def install_replace(tmp: Path, final: Path) -> None:
    os.replace(tmp, final)
    fsync_dir(final.parent)

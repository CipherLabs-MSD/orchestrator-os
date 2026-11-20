# Hawkes trading repository inventory — 2026-10-29

D1 documentation capture under existing OOS-0021, branch oos-0021/discovery-inbox.
Source: direct owner list continuing conversation [private conversation; reference kept in the owner's vault],
Utvärdera länkarna. Search locator: https://github.com/search?q=hawkes+trading&type=repositories.
The recovered conversation contains content-reference placeholders; the explicit
44-item owner list is the bounded inventory, not a claim to exhaust GitHub search.

44 distinct normalized GitHub identities verified present; 40 independent resources
after four identical forks are indexed under their two originals. No renamed or
transferred identities observed. Stable repository IDs distinguish same-name repos.
All 40 resources were absent: 40 new (DISC-078–117), 0 updated existing, 0 existing
matches; 77 pre-existing rows preserved byte-for-byte. Next DISC-118.
0 unavailable repositories and 0 confirmed empty repositories. Two evidence-blocked
resources are retained PARKED: DISC-083 (title-only documentation; scope unclear)
and DISC-116 (Hawkes name vs options README mismatch). This is a documentation
hold, not an unsupported BLOCKED triage enum. All 40 remain status: unprocessed,
execution UNKNOWN. Priority is independent of triage and is not experiment approval.

Read README.md, AGENTS.md, handoff/state, failed approaches, OOS-0021 scope and
INBOX.md's 11-field contract before editing. Deduplication covered the latest inbox
(including nested/grouped URLs), discovery provenance, domains, available synced
sources and fnd-002 recovery material; no matching resource found. The available
Model Foundry document mentions Hawkes as a method, not a registered candidate.
No live FinanceOS register is present in this workspace; no global absence claim.
Normalization ignores case, trailing slash, query/fragment and .git. A terminal dot
in Ishan16201's repository name is part of the verified canonical identity and kept.
Aliases include HFT-Lab-Exam (DISC-081), hawkesflow (DISC-111), and stochastic-lob
(DISC-115). Similar names and related Fusheng projects are not silently merged.

Metadata came from GitHub REST repository GET; README files were read on their
metadata-reported default branches with blob SHAs below. Descriptions and result
claims remain upstream statements; relevance/categories/priorities are preliminary
intake judgments. No source code, notebook, PDF or candidate tests were executed.
General risks for every candidate: timestamp units and ordering, look-ahead leakage,
kernel identification/stationarity, data access/rights, reproducibility, venue/regime
transfer and unmodeled fees, slippage, latency or queue position. Public access does
not imply reuse permission; missing/NOASSERTION metadata licenses are unresolved.
No architecture, safety, statistical significance or profitability is independently
validated by this intake. References are not new implementation tasks.

The first /readme endpoint attempt was unsupported by the connector (no usable
payload); it is not availability evidence. Explicit README.md file requests then
resolved documentation or returned genuine file 404s. Trading-Estimators has lowercase
readme.md. Hoanghai README.md 404 is confirmed: recursive tree is nonempty and has
no README (tree fa75ba45fea1f52556b54d96ddcc6b47378fc8f1). Its metadata links the
optimal-execution paper; no paper content was inferred from code. Four fork/source
comparisons returned identical with ahead=0/behind=0 on the checked default branches;
this does not assert all branches/history are identical.

## Priority review order

1. DISC-097 cronenberg64/HawkesLOB: four-dimensional GOOG/LOBSTER Hawkes study;
   failed opening-hour KS diagnostics and omitted cancellations/returns are material.
2. DISC-089 Fusheng0513/rl-neural-hawkes-trader: documented DQN and event-count state;
   README retracts earlier fake profits due to data bugs. Single-seed, single-day
   corrected result is an unverified source claim, not accepted profit evidence.
3. DISC-081 matthewdicks98/HFT-Hawkes: multivariate estimation/simulation on JSE TAQ;
   older project with a very short README and unresolved data/environment needs.

## Validation and completion limits

- Repository validator: 15/15 checks passed.
- Intake audit: PASS; 117 sequential unique IDs, 11 fields, all 44 supplied identities
  mapped, 40 new rows, four duplicate forks, 77 previous rows byte-identical,
  38 NEW plus two PARKED, all new execution UNKNOWN/status unprocessed, next DISC-118.
- Full suite: 33 tests in 9.586s; FAILED (errors=1, skipped=1).
  PythonRuntimeEvidence.setUpClass raised TimeoutError in unchanged runtime-spike
  concurrency setup, matching earlier handoff reports; no fresh baseline reproduction.
  Node evidence comparison skipped. The complete suite is not green.
- Diff whitespace check passed. No policy/validator change, so mutation check omitted;
  no publication, so prepublish check omitted. Documentation and exact mapping reviewed.
- No installation, candidate-code execution, trade, FinanceOS code edit, commit,
  push, merge or automatic implementation task. Owner review remains the next step.

## Exact mapping and source snapshots

### DISC-078 — hoanghai20021989/HawkesMarketImpactTrading

- Repository: https://github.com/hoanghai20021989/HawkesMarketImpactTrading; [metadata](https://api.github.com/repos/hoanghai20021989/HawkesMarketImpactTrading); stable ID 618702791; fork=false; default branch `master`; size 28924 KiB; archived=false; metadata license `unresolved`.
- README.md: file 404; [root listing](https://api.github.com/repos/hoanghai20021989/HawkesMarketImpactTrading/contents) verified nonempty. Metadata-only capture; listed files not read: `HawkesMarketImpactSubmission` (bf69c0b4cfb2f17d198c22b42aecf84abcd86d4c).
- Category: Execution / Market impact. Relevance: Compare endogenous-flow optimal execution. Risks/limits: README absent throughout verified tree; metadata and nonempty source/data tree only; data rights and reproducibility unresolved. Priority medium; NEW / UNKNOWN; status: unprocessed.
- Duplicate fork mapped to DISC-078, no new DISC: https://github.com/Hyeokreal/HawkesMarketImpactTrading; stable ID 832993851; parent `hoanghai20021989/HawkesMarketImpactTrading`; source `hoanghai20021989/HawkesMarketImpactTrading`. [Comparison](https://api.github.com/repos/hoanghai20021989/HawkesMarketImpactTrading/compare/master...Hyeokreal:master): identical, ahead=0, behind=0. Priority low; inherited category/relevance; PARKED duplicate disposition, execution UNKNOWN.
- Duplicate fork mapped to DISC-078, no new DISC: https://github.com/webclinic017/HawkesMarketImpactTrading; stable ID 852092059; parent `hoanghai20021989/HawkesMarketImpactTrading`; source `hoanghai20021989/HawkesMarketImpactTrading`. [Comparison](https://api.github.com/repos/hoanghai20021989/HawkesMarketImpactTrading/compare/master...webclinic017:master): identical, ahead=0, behind=0. Priority low; inherited category/relevance; PARKED duplicate disposition, execution UNKNOWN.

### DISC-079 — tripolskypetr/volume-anomaly

- Repository: https://github.com/tripolskypetr/volume-anomaly; [metadata](https://api.github.com/repos/tripolskypetr/volume-anomaly); stable ID 1169411086; fork=false; default branch `master`; size 1329 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/tripolskypetr/volume-anomaly/blob/master/README.md), blob `6654e52d482b11f913e87d1871cf1523e0513bb1`.
- Category: Monitoring / Volume anomalies. Relevance: Compare Hawkes, CUSUM and BOCPD alerts. Risks/limits: Anomaly scores are not calibrated return probabilities; false positives and drift. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-080 — maxwell-zweig/Trading-Estimators

- Repository: https://github.com/maxwell-zweig/Trading-Estimators; [metadata](https://api.github.com/repos/maxwell-zweig/Trading-Estimators); stable ID 708474766; fork=false; default branch `main`; size 161 KiB; archived=false; metadata license `unresolved`.
- Documentation: [readme.md](https://github.com/maxwell-zweig/Trading-Estimators/blob/main/readme.md), blob `8c01cb3928066c29da4be93e49a0fc8b7c62307f`.
- Category: Estimation / Maximum likelihood. Relevance: Compare multivariate Hawkes and jump-process estimators. Risks/limits: Lowercase readme.md resolved; numerical constraints and estimator correctness unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-081 — matthewdicks98/HFT-Hawkes

- Repository: https://github.com/matthewdicks98/HFT-Hawkes; [metadata](https://api.github.com/repos/matthewdicks98/HFT-Hawkes); stable ID 410198662; fork=false; default branch `main`; size 3872 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/matthewdicks98/HFT-Hawkes/blob/main/README.md), blob `452324fb75c9ef653aa908987a4c032bd97ed246`.
- Category: Estimation / Multivariate Hawkes. Relevance: TAQ event construction, estimation and simulation baseline for Hawkes Lab. Risks/limits: Alias HFT-Lab-Exam; terse README, older JSE data/toolchain and access assumptions. Priority high; NEW / UNKNOWN; status: unprocessed.

### DISC-082 — rspence821505/HFT-Equity-Prediction-Pipeline

- Repository: https://github.com/rspence821505/HFT-Equity-Prediction-Pipeline; [metadata](https://api.github.com/repos/rspence821505/HFT-Equity-Prediction-Pipeline); stable ID 1073123481; fork=false; default branch `main`; size 67563 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/rspence821505/HFT-Equity-Prediction-Pipeline/blob/main/README.md), blob `0bca9848f87b4ec53e2710166eb923a452987260`.
- Category: Forecast / Microstructure features. Relevance: Compare Hawkes features, HMM regimes and tree forecasts. Risks/limits: README describes only five trading days; temporal leakage, overfitting and Polygon data access. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-083 — fatphil99/Hawkes_Trading_System

- Repository: https://github.com/fatphil99/Hawkes_Trading_System; [metadata](https://api.github.com/repos/fatphil99/Hawkes_Trading_System); stable ID 1021122892; fork=false; default branch `main`; size 35 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/fatphil99/Hawkes_Trading_System/blob/main/README.md), blob `336b3141d158bc27bee211b6309b136f6615dbd8`.
- Category: Unclassified / Hawkes candidate. Relevance: Identity captured; resolve actual scope before method selection. Risks/limits: Title-only README; nonempty nested directory, not a verified empty repository; insufficient scope evidence. Priority low; PARKED / UNKNOWN; status: unprocessed.

### DISC-084 — Fusheng0513/neural-hawkes-process

- Repository: https://github.com/Fusheng0513/neural-hawkes-process; [metadata](https://api.github.com/repos/Fusheng0513/neural-hawkes-process); stable ID 1293138114; fork=false; default branch `main`; size 90 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Fusheng0513/neural-hawkes-process/blob/main/README.md), blob `bfcb2e9980aa7b374b69d4c03f408d5c6364dc94`.
- Category: Forecast / Neural point processes. Relevance: Compare LSTM-generated Hawkes parameters with classical likelihood baselines. Risks/limits: Snapshot event definitions, timestamp precision, data alignment and model stability require review. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-085 — shrihanavilala/hawkes-kalshi

- Repository: https://github.com/shrihanavilala/hawkes-kalshi; [metadata](https://api.github.com/repos/shrihanavilala/hawkes-kalshi); stable ID 1316583424; fork=false; default branch `main`; size 6274 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/shrihanavilala/hawkes-kalshi/blob/main/README.md), blob `a21bc9ea565fa5a156295cbe2ceee404439a93e6`.
- Category: Research / Prediction-market event flow. Relevance: Compare exogenous sports-event excitation against endogenous trade clustering. Risks/limits: Small event sample, timestamp deduplication and significance assumptions; no causal or profit conclusion verified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-086 — AkhilG-exe/HawkesPulse

- Repository: https://github.com/AkhilG-exe/HawkesPulse; [metadata](https://api.github.com/repos/AkhilG-exe/HawkesPulse); stable ID 1320916072; fork=false; default branch `main`; size 26 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/AkhilG-exe/HawkesPulse/blob/main/README.md), blob `df8e5f0da9f8cf987855549f7626f7b67232eaf2`.
- Category: Monitoring / Intensity and toxicity. Relevance: Compare C++ online intensity estimation for flow monitoring. Risks/limits: Intensity-to-toxicity mapping and latency claims unvalidated; README clone URL has stray punctuation. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-087 — aban369/crypto-trading-system-17-papers

- Repository: https://github.com/aban369/crypto-trading-system-17-papers; [metadata](https://api.github.com/repos/aban369/crypto-trading-system-17-papers); stable ID 1142649977; fork=false; default branch `main`; size 28 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/aban369/crypto-trading-system-17-papers/blob/main/README.md), blob `260837a738928c15ad04b6dbd2ebdb06f3a02b4a`.
- Category: Strategy / Multi-model crypto system. Relevance: Architecture reference for Hawkes, DeepLOB and RL combination. Risks/limits: MT5 auto-execution claims, credentials, model mixing and unverified paper coverage; no execution authorized. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-088 — Leo-Y-Zhang/HawkesDiffusion

- Repository: https://github.com/Leo-Y-Zhang/HawkesDiffusion; [metadata](https://api.github.com/repos/Leo-Y-Zhang/HawkesDiffusion); stable ID 1351053680; fork=false; default branch `main`; size 149 KiB; archived=false; metadata license `NOASSERTION`.
- Documentation: [README.md](https://github.com/Leo-Y-Zhang/HawkesDiffusion/blob/main/README.md), blob `be1df1bff75a4b906fbdf04b1d79986addd11384`.
- Category: Estimation / Kernel identification. Relevance: Compare self/cross-excitation and kernel-identification limits. Risks/limits: README marks proprietary source-available licensing; branching estimates depend on kernel assumptions. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-089 — Fusheng0513/rl-neural-hawkes-trader

- Repository: https://github.com/Fusheng0513/rl-neural-hawkes-trader; [metadata](https://api.github.com/repos/Fusheng0513/rl-neural-hawkes-trader); stable ID 1315734542; fork=false; default branch `master`; size 586 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Fusheng0513/rl-neural-hawkes-trader/blob/master/README.md), blob `e254927f905a3a6f7e06a38522dc600d95a2394b`.
- Category: Strategy / Reinforcement learning. Relevance: Compare DQN state construction and event/price alignment in ModelFoundry. Risks/limits: README retracts large fake profits caused by wrong columns, time alignment and mixed contracts; corrected single-seed single-day result remains unverified; event-count DQN state does not prove neural-Hawkes integration. Priority high; NEW / UNKNOWN; status: unprocessed.

### DISC-090 — arnavsharma0727/trade-arrival-hawkes

- Repository: https://github.com/arnavsharma0727/trade-arrival-hawkes; [metadata](https://api.github.com/repos/arnavsharma0727/trade-arrival-hawkes); stable ID 1410837815; fork=false; default branch `main`; size 4 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/arnavsharma0727/trade-arrival-hawkes/blob/main/README.md), blob `5ca473da4001a0045cee6fd2393e21ff6354775a`.
- Category: Estimation / Trade-arrival calibration. Relevance: Poisson-vs-Hawkes baseline with explicit timestamp resolution. Risks/limits: Aggregated trades are not individual orders; timestamp collapse and event cap change the estimand. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-091 — adilzhanbrmg4/Multivariate-Hawkes-Process-Implementation-into-Work-MHPIW-

- Repository: https://github.com/adilzhanbrmg4/Multivariate-Hawkes-Process-Implementation-into-Work-MHPIW-; [metadata](https://api.github.com/repos/adilzhanbrmg4/Multivariate-Hawkes-Process-Implementation-into-Work-MHPIW-); stable ID 1382385054; fork=false; default branch `main`; size 9 KiB; archived=false; metadata license `Apache-2.0`.
- Documentation: [README.md](https://github.com/adilzhanbrmg4/Multivariate-Hawkes-Process-Implementation-into-Work-MHPIW-/blob/main/README.md), blob `688be9c7a2c1d74833bc3015a21053c6ad710bc8`.
- Category: Research / Multivariate Hawkes. Relevance: Potential algorithmic-trading method reference. Risks/limits: Two-line README; paper/code completeness and empirical support unresolved. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-092 — HiggRn/hawkes-with-propagator

- Repository: https://github.com/HiggRn/hawkes-with-propagator; [metadata](https://api.github.com/repos/HiggRn/hawkes-with-propagator); stable ID 1074476111; fork=false; default branch `master`; size 1019 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/HiggRn/hawkes-with-propagator/blob/master/README.md), blob `1997fea7bf4d70d14fadb81ead6026cdbf983c01`.
- Category: Execution / Propagator impact. Relevance: Compare trade-flow excitation with propagator price dynamics. Risks/limits: Exploratory individual project; calibration and executable impact not established. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-093 — NealLovesProgramming/Hawkes-Processes-in-High-Frequency-Trading

- Repository: https://github.com/NealLovesProgramming/Hawkes-Processes-in-High-Frequency-Trading; [metadata](https://api.github.com/repos/NealLovesProgramming/Hawkes-Processes-in-High-Frequency-Trading); stable ID 950775362; fork=false; default branch `main`; size 1729 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/NealLovesProgramming/Hawkes-Processes-in-High-Frequency-Trading/blob/main/README.md), blob `501eaa67ed4a98bb8faa0f6d82f24d59438c41a0`.
- Category: Estimation / Kernel comparison. Relevance: Compare power-law and exponential kernels on real/simulated HFT data. Risks/limits: PDF not reviewed; kernel fit and proposed strategy results unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-094 — RayyanWaseem1/MRJD-and-Hawkes-for-Pairs-Trading

- Repository: https://github.com/RayyanWaseem1/MRJD-and-Hawkes-for-Pairs-Trading; [metadata](https://api.github.com/repos/RayyanWaseem1/MRJD-and-Hawkes-for-Pairs-Trading); stable ID 1156592353; fork=false; default branch `main`; size 38952 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/RayyanWaseem1/MRJD-and-Hawkes-for-Pairs-Trading/blob/main/README.md), blob `3fcb348b59ccfa857a96564906d3a3c958f52416`.
- Category: Strategy / Pairs and jump diffusion. Relevance: Compare self-exciting spread jumps with Poisson and MRJD controls. Risks/limits: Jump detection, pair selection, multiple testing, temporal splits and trading costs need independent review. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-095 — hemv-857/hawkes-lob

- Repository: https://github.com/hemv-857/hawkes-lob; [metadata](https://api.github.com/repos/hemv-857/hawkes-lob); stable ID 1344460002; fork=false; default branch `master`; size 321 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/hemv-857/hawkes-lob/blob/master/README.md), blob `05d405420aae16edd08f7993d05cb8aa13230bec`.
- Category: Estimation / Crypto arrivals. Relevance: Compare univariate MLE, Ogata simulation and time-rescaling diagnostics. Risks/limits: Trade arrivals do not reconstruct a full LOB; venue sampling and resolution limits. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-096 — RishiDarkDevil/Hawkes-Process-Price-Model

- Repository: https://github.com/RishiDarkDevil/Hawkes-Process-Price-Model; [metadata](https://api.github.com/repos/RishiDarkDevil/Hawkes-Process-Price-Model); stable ID 881375240; fork=false; default branch `main`; size 1180 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/RishiDarkDevil/Hawkes-Process-Price-Model/blob/main/README.md), blob `3b758ae614c673687d18021c881adf38425ac568`.
- Category: Research / High-frequency price model. Relevance: Educational price-process baseline. Risks/limits: Course assignment, minimal README; empirical validity and executable prices not established. Priority medium; NEW / UNKNOWN; status: unprocessed.
- Duplicate fork mapped to DISC-096, no new DISC: https://github.com/muhoushaonian/Hawkes-Process-Price-Model; stable ID 1250982713; parent `Newtype07/Hawkes-Process-Price-Model`; source `RishiDarkDevil/Hawkes-Process-Price-Model`. [Comparison](https://api.github.com/repos/RishiDarkDevil/Hawkes-Process-Price-Model/compare/main...muhoushaonian:main): identical, ahead=0, behind=0. Priority low; inherited category/relevance; PARKED duplicate disposition, execution UNKNOWN.
- Duplicate fork mapped to DISC-096, no new DISC: https://github.com/Newtype07/Hawkes-Process-Price-Model; stable ID 943749493; parent `RishiDarkDevil/Hawkes-Process-Price-Model`; source `RishiDarkDevil/Hawkes-Process-Price-Model`. [Comparison](https://api.github.com/repos/RishiDarkDevil/Hawkes-Process-Price-Model/compare/main...Newtype07:main): identical, ahead=0, behind=0. Priority low; inherited category/relevance; PARKED duplicate disposition, execution UNKNOWN.

### DISC-097 — cronenberg64/HawkesLOB

- Repository: https://github.com/cronenberg64/HawkesLOB; [metadata](https://api.github.com/repos/cronenberg64/HawkesLOB); stable ID 1235800892; fork=false; default branch `main`; size 7618 KiB; archived=false; metadata license `Apache-2.0`.
- Documentation: [README.md](https://github.com/cronenberg64/HawkesLOB/blob/main/README.md), blob `6ef88ab9b750eeace419ea5dd2cffda94cc2c420`.
- Category: Estimation / Multivariate LOB diagnostics. Relevance: Priority reference for four-event Hawkes calibration and rejection diagnostics. Risks/limits: README reports failed KS tests for all four opening-hour dimensions, missing cancellations/returns and tick ABI patch requirement; no validated model or profit inferred. Priority high; NEW / UNKNOWN; status: unprocessed.

### DISC-098 — federicobaio/Hawkes_in_finance

- Repository: https://github.com/federicobaio/Hawkes_in_finance; [metadata](https://api.github.com/repos/federicobaio/Hawkes_in_finance); stable ID 1199657233; fork=false; default branch `main`; size 803 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/federicobaio/Hawkes_in_finance/blob/main/README.md), blob `98d7ed276496ec3fb7c74232f7b52f69d6c841e1`.
- Category: Research / BTC return shocks. Relevance: Compare threshold-defined return events and volatility clustering. Risks/limits: Hourly return threshold events are not order-level flow; threshold and sampling sensitivity. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-099 — Walkera-y14/Parameter-estimation-for-Hawkes-process-in-Finance

- Repository: https://github.com/Walkera-y14/Parameter-estimation-for-Hawkes-process-in-Finance; [metadata](https://api.github.com/repos/Walkera-y14/Parameter-estimation-for-Hawkes-process-in-Finance); stable ID 998656318; fork=false; default branch `main`; size 234 KiB; archived=false; metadata license `unresolved`.
- README.md: file 404; [root listing](https://api.github.com/repos/Walkera-y14/Parameter-estimation-for-Hawkes-process-in-Finance/contents) verified nonempty. Metadata-only capture; listed files not read: `Good data on amazon.R` (f1899dd2cbe342ea374f44121a2ced1cd066f5d3); `Multivariate hawkes plots.ipynb` (880e0fda3140bf1eb5567ee10cf3e7f0b8453f15); `Non-parametric estimation.ipynb` (d5cf629ac2e321e61fd10c07f19f5df7daacb6a0); `Price impact.ipynb` (1febd2e8af2cd8d35647d686c4a83d8f32d377b8); `gmm.R` (7ee1b5c3195edcbb798c8d72c7d99a41465ac300).
- Category: Estimation / Parametric and nonparametric. Relevance: Compare estimation and price-impact notebook approaches. Risks/limits: No README; root filenames plus repository description only; notebooks not inspected. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-100 — ajcutuli/DRPHawkes

- Repository: https://github.com/ajcutuli/DRPHawkes; [metadata](https://api.github.com/repos/ajcutuli/DRPHawkes); stable ID 444530332; fork=false; default branch `main`; size 654 KiB; archived=false; metadata license `unresolved`.
- README.md: file 404; [root listing](https://api.github.com/repos/ajcutuli/DRPHawkes/contents) verified nonempty. Metadata-only capture; listed files not read: `DRP Hawkes.pdf` (2c9f296211d06ab89b886cffba2bef62f4c8b929); `Hawkes_article.pdf` (0c7735c195eeac4b28bf69b89162b7286def6e51).
- Category: Reference / Hawkes teaching. Relevance: Introductory finance point-process reading reference. Risks/limits: No README; two PDF files listed but not read; no executable implementation inferred. Priority low; NEW / UNKNOWN; status: unprocessed.

### DISC-101 — jeremymck/High-Frequency-Data---Limit-Order-Books

- Repository: https://github.com/jeremymck/High-Frequency-Data---Limit-Order-Books; [metadata](https://api.github.com/repos/jeremymck/High-Frequency-Data---Limit-Order-Books); stable ID 254332557; fork=false; default branch `master`; size 1918 KiB; archived=false; metadata license `unresolved`.
- README.md: file 404; [root listing](https://api.github.com/repos/jeremymck/High-Frequency-Data---Limit-Order-Books/contents) verified nonempty. Metadata-only capture; listed files not read: `HF Data.ipynb` (a0ab533f44d4208e9c62fea1daa5c2b0a50dafeb); `Hawkes Processes.ipynb` (b64744c8d18843c3ebac4c897e24ac0491301b60); `Limit Order Books Simulator.ipynb` (82cf555bc185fbf19034161ea80787dc8aab6541).
- Category: Simulation / Hawkes and LOB notebooks. Relevance: Potential educational generator/estimator/LOB comparison. Risks/limits: No README; three notebooks listed but not inspected; old environment and data assumptions. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-102 — BGasperov/drlformm

- Repository: https://github.com/BGasperov/drlformm; [metadata](https://api.github.com/repos/BGasperov/drlformm); stable ID 466452486; fork=false; default branch `main`; size 604 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/BGasperov/drlformm/blob/main/README.md), blob `8510d07dc2a2e4f032acff5628f38a8c76d30874`.
- Category: Strategy / RL market making. Relevance: Paper-linked Hawkes LOB market-making research reference. Risks/limits: Very short README; paper claims and synthetic-to-real transfer unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-103 — odenpetersen/order-book-hawkes

- Repository: https://github.com/odenpetersen/order-book-hawkes; [metadata](https://api.github.com/repos/odenpetersen/order-book-hawkes); stable ID 766742695; fork=false; default branch `main`; size 15596 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/odenpetersen/order-book-hawkes/blob/main/README.md), blob `db8596f62567f93a12add86cd040f77371ee3bfe`.
- Category: Simulation / Point-process LOB. Relevance: Compare point-process book modeling as a distinct candidate. Risks/limits: Minimal README; data, calibration and matching fidelity unresolved. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-104 — marouaneb48/Hawkes-process-based-LOB-modeling

- Repository: https://github.com/marouaneb48/Hawkes-process-based-LOB-modeling; [metadata](https://api.github.com/repos/marouaneb48/Hawkes-process-based-LOB-modeling); stable ID 996786089; fork=false; default branch `main`; size 2180 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/marouaneb48/Hawkes-process-based-LOB-modeling/blob/main/README.md), blob `d0b261efff2b5dbfe30cb5e6007c6ca790c45bbc`.
- Category: Simulation / LOB event modeling. Relevance: Compare event-interval diagnostics, calibration and forecasting workflows. Risks/limits: Interpolation can alter arrival structure; notebook results and validation unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-105 — marcocambi/energy-lob-hawkes

- Repository: https://github.com/marcocambi/energy-lob-hawkes; [metadata](https://api.github.com/repos/marcocambi/energy-lob-hawkes); stable ID 1347230159; fork=false; default branch `main`; size 4353 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/marcocambi/energy-lob-hawkes/blob/main/README.md), blob `928b2315c65e5e5046d4444155a95c8b5cf8b448`.
- Category: Estimation / Energy event flow. Relevance: Compare univariate clustering across equities and energy venues. Risks/limits: README excludes multivariate cross-excitation and full L2/L3 reconstruction; venue/data rights differ. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-106 — Suprzm/hawkes-lob

- Repository: https://github.com/Suprzm/hawkes-lob; [metadata](https://api.github.com/repos/Suprzm/hawkes-lob); stable ID 1259419027; fork=false; default branch `main`; size 2175 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Suprzm/hawkes-lob/blob/main/README.md), blob `e649d5db62cc7d85c5165065acfa58b264cbe46e`.
- Category: Simulation / Crypto LOB. Relevance: Compare Hawkes simulator and documented BTC/ETH calibration workflow. Risks/limits: Real-data validation claims not reproduced; sampling, queue fidelity and costs need review; distinct from hemv-857/hawkes-lob. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-107 — Luciferk07/MarketXray

- Repository: https://github.com/Luciferk07/MarketXray; [metadata](https://api.github.com/repos/Luciferk07/MarketXray); stable ID 1282075852; fork=false; default branch `main`; size 245 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Luciferk07/MarketXray/blob/main/README.md), blob `be541fe63ac87b39784310dae30a99b3571af934`.
- Category: Monitoring / HFT analytics. Relevance: Compare dashboard and C++/Rust flow-analytics boundaries. Risks/limits: Live/replay/browser fallback distinctions and latency/toxicity claims unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-108 — Maitreyi1506/Hawkes-Simulator-OrderBook

- Repository: https://github.com/Maitreyi1506/Hawkes-Simulator-OrderBook; [metadata](https://api.github.com/repos/Maitreyi1506/Hawkes-Simulator-OrderBook); stable ID 1060735898; fork=false; default branch `main`; size 10 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Maitreyi1506/Hawkes-Simulator-OrderBook/blob/main/README.md), blob `f4afc89e6895b370b6dd864ac63b491b7d2205c6`.
- Category: Simulation / Synthetic market making. Relevance: Compare Poisson vs Hawkes arrivals and basic matching/strategies. Risks/limits: Synthetic strategy P&L does not establish empirical realism or profitability. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-109 — Sacss-dev/hawkes_processes

- Repository: https://github.com/Sacss-dev/hawkes_processes; [metadata](https://api.github.com/repos/Sacss-dev/hawkes_processes); stable ID 1328817682; fork=false; default branch `main`; size 690 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Sacss-dev/hawkes_processes/blob/main/README.md), blob `a393fe4bf3362f6a1e9089519d29ed6eda74ff28`.
- Category: Forecast / Hawkes features and boosting. Relevance: Compare incremental Hawkes features against full-book boosting baseline. Risks/limits: Reported out-of-sample gains remain source claims; leakage, horizon, multiple comparisons and costs. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-110 — Manya-Chawla/neural-hawkes-limit-order-book

- Repository: https://github.com/Manya-Chawla/neural-hawkes-limit-order-book; [metadata](https://api.github.com/repos/Manya-Chawla/neural-hawkes-limit-order-book); stable ID 1336512677; fork=false; default branch `main`; size 290 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/Manya-Chawla/neural-hawkes-limit-order-book/blob/main/README.md), blob `6984e1cf3dc849adc59010117c77678ba9cc7771`.
- Category: Forecast / Neural LOB events. Relevance: Candidate neural-event modeling comparison. Risks/limits: Minimal README; architecture, data and evaluation evidence insufficient. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-111 — MaherHarp/hawkes-order-flow

- Repository: https://github.com/MaherHarp/hawkes-order-flow; [metadata](https://api.github.com/repos/MaherHarp/hawkes-order-flow); stable ID 1351160639; fork=false; default branch `main`; size 250 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/MaherHarp/hawkes-order-flow/blob/main/README.md), blob `1ed330664e5a71a5dd45d778bcb0c07dfdfff495`.
- Category: Estimation / Multivariate flow diagnostics. Relevance: Compare convex MLE, Ogata simulation and rejection-capable residual checks. Risks/limits: Alias hawkesflow; optimization assumptions, fixed kernel choices and empirical validity unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-112 — kbacha92/mhp_lob

- Repository: https://github.com/kbacha92/mhp_lob; [metadata](https://api.github.com/repos/kbacha92/mhp_lob); stable ID 1437260238; fork=false; default branch `main`; size 202 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/kbacha92/mhp_lob/blob/main/README.md), blob `61d8f57bd3083740e54ab125a51d32b9013c6701`.
- Category: Simulation / Mamba Hawkes. Relevance: Compare state-space neural event generation against classical Hawkes. Risks/limits: LOBSTER data access, hardware/device assumptions and simulation fidelity unverified. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-113 — Ishan16201/Hawkes-driven-limit-order-book-simulator.

- Repository: https://github.com/Ishan16201/Hawkes-driven-limit-order-book-simulator.; [metadata](https://api.github.com/repos/Ishan16201/Hawkes-driven-limit-order-book-simulator.); stable ID 1437317883; fork=false; default branch `main`; size 160 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/Ishan16201/Hawkes-driven-limit-order-book-simulator./blob/main/README.md), blob `fc5d373d500bbfc71c2615aa27a42151187436a5`.
- Category: Simulation / Hawkes LOB and execution. Relevance: Compare event-to-order adapter, deterministic matching and causal evaluation. Risks/limits: README explicitly states no empirical calibration/market validation; illustrative marks and coarse decay grid; synthetic tests not market evidence. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-114 — RuhaanB6/Market_Book_Simulator-Hawkes

- Repository: https://github.com/RuhaanB6/Market_Book_Simulator-Hawkes; [metadata](https://api.github.com/repos/RuhaanB6/Market_Book_Simulator-Hawkes); stable ID 1106324744; fork=false; default branch `main`; size 4 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/RuhaanB6/Market_Book_Simulator-Hawkes/blob/main/README.md), blob `f80956a5161575e4e5c915dd1a3fc5f1afff6708`.
- Category: Simulation / Matching engine. Relevance: Potential price-time-priority matching comparison. Risks/limits: Brief README; Hawkes generator and microsecond realism not established by title. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-115 — syaohui/stochastic_limit_order_book

- Repository: https://github.com/syaohui/stochastic_limit_order_book; [metadata](https://api.github.com/repos/syaohui/stochastic_limit_order_book); stable ID 1430559003; fork=false; default branch `main`; size 8763 KiB; archived=false; metadata license `MIT`.
- Documentation: [README.md](https://github.com/syaohui/stochastic_limit_order_book/blob/main/README.md), blob `c674c89c48f8d513dc535904c0fd7b0277316b22`.
- Category: Reference / Stochastic LOB models. Relevance: Compare teaching models for queues, Hawkes, impact and quoting. Risks/limits: README says all figures synthetic and no market data; teaching checks do not validate trading use. Priority medium; NEW / UNKNOWN; status: unprocessed.

### DISC-116 — 0tabris/Hawkes-Process-Limit-Order-Book-Simulator-Market-Making

- Repository: https://github.com/0tabris/Hawkes-Process-Limit-Order-Book-Simulator-Market-Making; [metadata](https://api.github.com/repos/0tabris/Hawkes-Process-Limit-Order-Book-Simulator-Market-Making); stable ID 1097950073; fork=false; default branch `main`; size 125 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/0tabris/Hawkes-Process-Limit-Order-Book-Simulator-Market-Making/blob/main/README.md), blob `b025c97ce1a6828be5e0820932a58e757daf0ae4`.
- Category: Research / Identity-content mismatch. Relevance: Potential ModelFoundry options-method reference only pending scope clarification. Risks/limits: Hawkes/LOB repository name conflicts with MLMC path-dependent-options README; Hawkes relevance blocked. Priority low; PARKED / UNKNOWN; status: unprocessed.

### DISC-117 — DEMONICRAMIRO/A-Deterministic-Limit-Order-Book-Simulator-with-Hawkes-driven-order-flow

- Repository: https://github.com/DEMONICRAMIRO/A-Deterministic-Limit-Order-Book-Simulator-with-Hawkes-driven-order-flow; [metadata](https://api.github.com/repos/DEMONICRAMIRO/A-Deterministic-Limit-Order-Book-Simulator-with-Hawkes-driven-order-flow); stable ID 1214940492; fork=false; default branch `main`; size 2023 KiB; archived=false; metadata license `unresolved`.
- Documentation: [README.md](https://github.com/DEMONICRAMIRO/A-Deterministic-Limit-Order-Book-Simulator-with-Hawkes-driven-order-flow/blob/main/README.md), blob `2d9a2351c5b74bf33facc829f59610f232ce979a`.
- Category: Simulation / Layered Hawkes LOB. Relevance: Compare generator, translator, matching, calibration and diagnostics separation. Risks/limits: Paper attribution and reported diagnostics unverified; calibration, marks, fills and empirical fidelity require separate review. Priority medium; NEW / UNKNOWN; status: unprocessed.


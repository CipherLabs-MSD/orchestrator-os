# Algotrading search intake — 2026-10-29

OOS-0021; D1 documentation capture under direct owner continuation. Existing branch `oos-0021/discovery-inbox`; no commit, publication or merge. Read README.md, AGENTS.md, inbox contract, handoff/state, failed approaches, OOS-0021 and decision/security rules before editing.

Source: explicit owner list continuing conversation [private conversation; reference kept in the owner's vault], Utvärdera länkarna. Search phrases: algotrading; algorithmic trading backtesting; algotrading execution risk. The supplied lists bound intake; search rankings were not rerun.

## Reconciliation

64 supplied hits (30 + 30 + 4), 62 unique normalized owner/repository URLs. Two within-batch overlaps: algotrading-lab/ai-algotrading-agent and nkaz001/algotrading-example (searches 1 and 2). Two existing inbox resources updated: DISC-003 Kha-Ching and DISC-073 PyBroker. 60 new records DISC-208–267, 2 existing/updated, 0 rejected, 0 repository-blocked/unavailable, 1 verified GitHub fork, 3 archived repositories. Next DISC-268. Existing and updated counts overlap: the two existing entries were both updated, not four separate resources. Fork is retained with a separate repository ID and explicit parent, not counted as an independent architecture.

Compared normalized URLs (case-insensitive, trailing slash, .git, query/fragment removed), names and aliases against current inbox, all four earlier batch ledgers (repository, AI-trading, Hawkes and Quant searches), domain material, synced sources and available fnd-002 recovery documents. Accessible local project mirror has no current FinanceOS domain registry or raw-universe file; those were not re-audited, and historical batch claims of broader coverage are not claimed as a fresh check. No held results read. No similarly named repositories merged without identity evidence. Prior inbox rows are authoritative for IDs/statuses.

Kha-Ching identity is supported by explicit owner URL and [recovered spec section 12](../../fnd-002/recovery/FinanceOS_Model_Foundry_v0.1.md) / [gap-map item 12](../../fnd-002/FND-002-recovery-and-gap-map.md). DISC-003 capture date and PARKED/UNKNOWN retained; README now identifies SignalX, not evidence of prior evaluation. DISC-073 preserves its prior priority, description and Commons Clause warning, adding current search provenance only. Other 205 existing rows preserved verbatim. Named priorities occupy DISC-208–216 in the exact owner order, ranks 1–9; all new entries NEW/UNKNOWN/unprocessed. Runtime evidence remains unknown even after source inspection.

## Verification scope and exceptions

Primary evidence: connected GitHub GET repository metadata, root listing only when README.md returned 404, and README content lines 1–100 (fallback READMEs 1–140), inspected 2026-10-29. SHA below is a README blob SHA, not a pinned repository commit or code-audit proof. Repository metadata confirms public identity, fork/parent and archive flags. Source summaries are documentation assertions; no code/runtime/safety/performance or license-compliance validation. External setup/trade instructions treated as data and never followed. No stars or profit claims used as acceptance evidence.

README.md 404 recovered for mementum/bta-lib (README.rst), Arech/t18 (readme.md), wegamekinglc/AlgoTrading (README.rst), sagarrathi/AlgoTrading (readme.md), ricequant/rqalpha (README.rst), dinesh/RTA (README). These are path/case issues, not blocked repositories. RQAlpha README.rst documents mods for accounts, simulation, transaction costs, analysis and pre-trade risk, and says non-commercial use only. Linked hosted docs were not independently audited. Arech English README is minimal and points to Russian documentation; deeper feature assessment remains blocked by limited inspected evidence, not repo access.

algotrading-lab/ai-algotrading-agent is a TypeScript crypto backtest/tick-replay/simulation framework; no documented multi-agent architecture. whchien/ai-trader is distinct from HKUDS/AI-Trader DISC-069. MCP/AI naming does not prove agents. StockSharp core and its examples, VeighNa core and execution module, AlgoBulls API and strategy pool, and Investing Algorithm Framework and CABBAGE are distinct resources with relationships, not duplicates.

Lin-Thet-Zaw QuantBridge: fork=true, parent WiltonMarques QuantBridge; identical README SHA, different repo IDs. day0market README describes translated/modified fork lineage although GitHub says fork=false; precise parent/commit unresolved. CABBAGE says upstream package included although fork=false; no lineage audit. nkaz001 README migration to hftbacktest and Artimatic successor notice are cross-references only, not identity merges or recursive intake. Archived: brookmiles/freqtrade-stuff, Arech/t18, devalpha-io/devalpha-node. Artimatic README says deprecated even though archived=false. Paperbroker UI/margins/commissions listed as future work; no completed UI inferred. FTX material is a historical API guide; no service availability inferred.

Classification uses FinanceOS/ModelFoundry relevance plus backtesting, risk, execution, dashboard, model research, indicators, education or discovery. Agents is recorded only as an interface/claim where documented; no multi-agent classification inferred from names. Priorities mean review order, not adoption. Costs, fill assumptions, point-in-time data, overfitting, credentials, dynamic code and paper/live boundaries need separate evaluation; no profitability established.

Concurrent updates were detected before mutation: Hawkes added DISC-078–117 and Quant added DISC-118–207. Re-read those ledgers and current inbox; 207 existing rows at write time. No matches to the 62 owner inputs beyond DISC-003 and DISC-073. The original 77-entry observation was superseded; allocated from actual next DISC-208 with a pre-write content guard.

## Source and action ledger

Each Source links to inspected README; repository metadata endpoint is `https://api.github.com/repos/{owner}/{repo}`. Search column preserves all three input lists and overlap provenance.

| DISC ID | Repository | Search | Action | Repository ID | Fork / parent | Archived | README blob SHA | Source |
|---|---|---|---|---|---|---|---|---|
| DISC-208 | BoringQuantSystems/nanobook | 3 | created | 1150666464 | false | false | dbe4f6e3452eeaabe96d34191c8235fc20dddb8f | [README](https://github.com/BoringQuantSystems/nanobook/blob/main/README.md) |
| DISC-209 | vnpy/vnpy | 1 | created | 31522041 | false | false | 64eefd38fcb83a24b74ce6b1429b6ed6f58acc25 | [README](https://github.com/vnpy/vnpy/blob/master/README.md) |
| DISC-210 | StockSharp/StockSharp | 2 | created | 27703983 | false | false | 80829d518aa89c07a6c0d1b0cdcf3a13b47028b2 | [README](https://github.com/StockSharp/StockSharp/blob/master/README.md) |
| DISC-211 | ricequant/rqalpha | 2 | created | 63773246 | false | false | 5f9c85faf1e9c6b046f91b619607ab11e4f1d013 | [README](https://github.com/ricequant/rqalpha/blob/master/README.rst) |
| DISC-212 | Superalgos/Superalgos | 2 | created | 201978761 | false | false | 4518cfe3967d188474b9034b33dea32edaf4f939 | [README](https://github.com/Superalgos/Superalgos/blob/master/README.md) |
| DISC-213 | josephchenhk/qtrader | 2 | created | 295894890 | false | false | fc8caf2b17218a03c7ff907b138768e3e888e4aa | [README](https://github.com/josephchenhk/qtrader/blob/master/README.md) |
| DISC-214 | goldspanlabs/optopsy | 2 | created | 103795689 | false | false | 5595e5b13a28356bd8fd9841c36c6373b3a65a65 | [README](https://github.com/goldspanlabs/optopsy/blob/main/README.md) |
| DISC-215 | neurallayer/roboquant | 2 | created | 406929056 | false | false | f9748a513683ccbc04b4d6c144cead9838c70229 | [README](https://github.com/neurallayer/roboquant/blob/main/README.md) |
| DISC-216 | mementum/bta-lib | 1 | created | 237531189 | false | false | d8d183c9a868f0f72218b55fda3dcc82935e5842 | [README](https://github.com/mementum/bta-lib/blob/master/README.rst) |
| DISC-217 | ivopetiz/algotrading | 1 | created | 140492255 | false | false | a60b7c843402bc908aa4ccca1c4833c77dc7fcfe | [README](https://github.com/ivopetiz/algotrading/blob/master/README.md) |
| DISC-218 | jonromero/forex_algotrading | 1 | created | 46603596 | false | false | d3a91ad4283f9830b407ac8b0cb0525b87f7f72e | [README](https://github.com/jonromero/forex_algotrading/blob/master/README.md) |
| DISC-003 | aakashlpin/kha-ching | 1 | updated existing | 341176659 | false | false | 17ce241c5545762d0927a17597056a85204878a9 | [README](https://github.com/aakashlpin/kha-ching/blob/master/README.md) |
| DISC-219 | algotrading-lab/ai-algotrading-agent | 1,2 | created | 1265987986 | false | false | 2c4015393b2a5acc73bdb094c313bf99611e749a | [README](https://github.com/algotrading-lab/ai-algotrading-agent/blob/master/README.md) |
| DISC-220 | ultra1971/algotrading_stack | 1 | created | 364037215 | false | false | 2f66c48cb4a0b805e31829d002859165b239792f | [README](https://github.com/ultra1971/algotrading_stack/blob/main/README.md) |
| DISC-221 | debanshur/algotrading | 1 | created | 260526202 | false | false | a7a18061b38594b12ad33739be7783a95912e21d | [README](https://github.com/debanshur/algotrading/blob/master/README.md) |
| DISC-222 | nkaz001/algotrading-example | 1,2 | created | 348786079 | false | false | 8cee051af3f18c6a47de542a070a4f49e9c77492 | [README](https://github.com/nkaz001/algotrading-example/blob/master/README.md) |
| DISC-223 | day0market/pyalgotrader | 1 | created | 210655904 | false | false | ba6095fb51d4b6588e910f95ec0eed35d65bfbe3 | [README](https://github.com/day0market/pyalgotrader/blob/master/README.md) |
| DISC-224 | LiamConnell/deep-algotrading | 1 | created | 63157824 | false | false | 389def9709fe8db3776ca263fab60e21885e1e12 | [README](https://github.com/LiamConnell/deep-algotrading/blob/master/README.md) |
| DISC-225 | vrishank97/AlgoTrading | 1 | created | 152781574 | false | false | b0266e2751c8cffe604e7557788b7da947868d48 | [README](https://github.com/vrishank97/AlgoTrading/blob/master/README.md) |
| DISC-226 | StockSharp/AlgoTrading | 1 | created | 787045953 | false | false | 37b53e9621229fa63c3931e8b80e600e8d303782 | [README](https://github.com/StockSharp/AlgoTrading/blob/main/README.md) |
| DISC-227 | AlexShakaev/backtesting_and_algotrading_options_with_Interactive_Brokers_API | 1 | created | 701504555 | false | false | 484e45569e4d2a09a8774f596b394306ed66763d | [README](https://github.com/AlexShakaev/backtesting_and_algotrading_options_with_Interactive_Brokers_API/blob/main/README.md) |
| DISC-228 | thekuldeepsingh/100-Days-Of-Hell-With-Python-Algotrading | 1 | created | 798449223 | false | false | 46baaa251caaaaf4d8863386fc7b9b17794d940a | [README](https://github.com/thekuldeepsingh/100-Days-Of-Hell-With-Python-Algotrading/blob/main/README.md) |
| DISC-229 | vnpy/vnpy_algotrading | 1 | created | 411481233 | false | false | 6fbec6f37e36bf25c80a3fe269271247fe08dd4a | [README](https://github.com/vnpy/vnpy_algotrading/blob/main/README.md) |
| DISC-230 | Samvid95/AlgoTradingRepoList | 1 | created | 371378552 | false | false | ca32d9fc6974e9312c652d3ef04bffd0398c74f8 | [README](https://github.com/Samvid95/AlgoTradingRepoList/blob/main/README.md) |
| DISC-231 | brookmiles/freqtrade-stuff | 1 | created | 349384024 | false | true | a63505ecef37af86e8888ac660c59990ce3e6f47 | [README](https://github.com/brookmiles/freqtrade-stuff/blob/main/README.md) |
| DISC-232 | awoo424/algotrading | 1 | created | 274876131 | false | false | 773c1246e8af776664d19acd708ab0ab26f7c587 | [README](https://github.com/awoo424/algotrading/blob/master/README.md) |
| DISC-233 | Arech/t18 | 1 | created | 214448296 | false | true | a6fc6add553b85afd0c45705371f5ed728c29dda | [README](https://github.com/Arech/t18/blob/master/readme.md) |
| DISC-234 | wegamekinglc/AlgoTrading | 1 | created | 42573887 | false | false | 0b95bc75931f93367b7594530881824608735d82 | [README](https://github.com/wegamekinglc/AlgoTrading/blob/master/README.rst) |
| DISC-235 | tradologics/AlgoTradingSummit | 1 | created | 388851544 | false | false | 7a85ac263ff6fa478ee43f175e0bf31db3105fb1 | [README](https://github.com/tradologics/AlgoTradingSummit/blob/main/README.md) |
| DISC-236 | sagarrathi/AlgoTrading | 1 | created | 359590991 | false | false | 0831f78c974f05d6cca0c72f8da4b8d78650403b | [README](https://github.com/sagarrathi/AlgoTrading/blob/main/readme.md) |
| DISC-237 | ethanbond64/Algotrading_Medium | 1 | created | 196858416 | false | false | 8cc6e78e0740cf69dc5b4c8b13fb6658c66803e3 | [README](https://github.com/ethanbond64/Algotrading_Medium/blob/master/README.md) |
| DISC-238 | atj-khactu/atj-algotrading-edu | 1 | created | 836327399 | false | false | 23abd73d6f6163d02f70b3716bff73906c465c7a | [README](https://github.com/atj-khactu/atj-algotrading-edu/blob/main/README.md) |
| DISC-239 | ashbz/CryptoSharp | 1 | created | 277259943 | false | false | f7022317cb38556626e92ada368d8d44eb600745 | [README](https://github.com/ashbz/CryptoSharp/blob/master/README.md) |
| DISC-240 | dieko95/AlgoTrading | 1 | created | 191256372 | false | false | a825d2fcb2e0ca84be512c14ecc7e10f3fadf67c | [README](https://github.com/dieko95/AlgoTrading/blob/master/README.md) |
| DISC-241 | nburgessx/AlgoTrading | 1 | created | 678329631 | false | false | 46497a42a39b50cfb057ee3bcc61e3bed9786618 | [README](https://github.com/nburgessx/AlgoTrading/blob/main/README.md) |
| DISC-242 | IgorWounds/FTX-API-Algotrading101 | 1 | created | 346723230 | false | false | 1540c98c74328966c3e313dceea02ae154c2e4b6 | [README](https://github.com/IgorWounds/FTX-API-Algotrading101/blob/main/README.md) |
| DISC-243 | IgorWounds/Crypto-Arbitrage-Mispricing-Algotrading101 | 1 | created | 346719861 | false | false | 06612bfc17b600e3ccda4aa7090a7902ad63d748 | [README](https://github.com/IgorWounds/Crypto-Arbitrage-Mispricing-Algotrading101/blob/main/README.md) |
| DISC-244 | coding-kitties/investing-algorithm-framework | 2 | created | 228824550 | false | false | efa2f3de6b89a38c6e63ea85c5ed99fa8635d2f4 | [README](https://github.com/coding-kitties/investing-algorithm-framework/blob/main/README.md) |
| DISC-073 | edtechre/pybroker | 2 | updated existing | 589385734 | false | false | b0fdfb53c52aab75186ad8750e7d649b3792a399 | [README](https://github.com/edtechre/pybroker/blob/master/README.md) |
| DISC-245 | philipodonnell/paperbroker | 2 | created | 96378149 | false | false | 90515e2ea5ab75bf22209676b368786153061da8 | [README](https://github.com/philipodonnell/paperbroker/blob/master/README.md) |
| DISC-246 | whchien/ai-trader | 2 | created | 816848129 | false | false | ff994cefcd1033f84f49c36967de000a37186f99 | [README](https://github.com/whchien/ai-trader/blob/main/README.md) |
| DISC-247 | evankirkiles/backtest-environment | 2 | created | 134926618 | false | false | ebcd8989ed2527a4847813447a9ce34e6aeb989f | [README](https://github.com/evankirkiles/backtest-environment/blob/master/README.md) |
| DISC-248 | devalpha-io/devalpha-node | 2 | created | 101687938 | false | true | d70c7eeec15f80db09a1e4e6b6906d1bdea8656b | [README](https://github.com/devalpha-io/devalpha-node/blob/master/README.md) |
| DISC-249 | timolson/cointrader | 2 | created | 20368549 | false | false | 9878dfed9a54d09010c32139a5e2de40936f032c | [README](https://github.com/timolson/cointrader/blob/master/README.md) |
| DISC-250 | algobulls/pyalgotrading | 2 | created | 260428823 | false | false | 232d854181f9138396426a024f305225fa0effbc | [README](https://github.com/algobulls/pyalgotrading/blob/master/README.md) |
| DISC-251 | gbeced/basana | 2 | created | 609367611 | false | false | bc2b4934229c977278d4155a611d859e482b69af | [README](https://github.com/gbeced/basana/blob/develop/README.md) |
| DISC-252 | ryantcullen/stock-bot | 2 | created | 320710006 | false | false | 68aa2efe5a048a40f9304e1f0652ecc7b4aaa124 | [README](https://github.com/ryantcullen/stock-bot/blob/master/README.md) |
| DISC-253 | Al0010/grid-spot-algorithm-trading | 2 | created | 483986297 | false | false | 73b8b84c039b34e9a1a13fb0402f36087dbcaed6 | [README](https://github.com/Al0010/grid-spot-algorithm-trading/blob/main/README.md) |
| DISC-254 | philippe-ostiguy/PyBacktesting | 2 | created | 287831173 | false | false | 49d35ee4d5f818d9c4b9ae314dd4ff23d436cc20 | [README](https://github.com/philippe-ostiguy/PyBacktesting/blob/master/README.md) |
| DISC-255 | renatovotto/Nostradamus | 2 | created | 390453570 | false | false | 8c2785287b3d8009320d592821b68c491a0cda9b | [README](https://github.com/renatovotto/Nostradamus/blob/master/README.md) |
| DISC-256 | algobulls/pyalgostrategypool | 2 | created | 260225658 | false | false | b6fc9333dd41be2994a21b92051124fd664a5454 | [README](https://github.com/algobulls/pyalgostrategypool/blob/master/README.md) |
| DISC-257 | dinesh/RTA | 2 | created | 3901135 | false | false | 38617f7188ad34148c16bfdb901a0ce4909c09ca | [README](https://github.com/dinesh/RTA/blob/master/README) |
| DISC-258 | davidkellis/securitiesdb | 2 | created | 49042869 | false | false | df688b44870e913ae8ea25064a5a7a518838168d | [README](https://github.com/davidkellis/securitiesdb/blob/master/README.md) |
| DISC-259 | dsinyakov/quant | 2 | created | 96394522 | false | false | 20f6f40c0d85dd4ef6c68f83c6f60c363207a9a0 | [README](https://github.com/dsinyakov/quant/blob/dev/README.md) |
| DISC-260 | Artimatic/td-algorithmic-trading-in-angular | 2 | created | 105725425 | false | false | d1f00918f710370d23a9fe9689068e094e4eb198 | [README](https://github.com/Artimatic/td-algorithmic-trading-in-angular/blob/master/README.md) |
| DISC-261 | umeshpalai/Algorithmic-Trading---Backtesting---Banknifty-Straddle-using-Python | 2 | created | 455925338 | false | false | c7f88ef7453b5cb9e9f833dc1c47add5a656b871 | [README](https://github.com/umeshpalai/Algorithmic-Trading---Backtesting---Banknifty-Straddle-using-Python/blob/main/README.md) |
| DISC-262 | sopersone/cabbage-trading-machine | 2 | created | 1385657279 | false | false | e6bbba8516baab2cee34b9953bb5270b3bf0ade1 | [README](https://github.com/sopersone/cabbage-trading-machine/blob/main/README.md) |
| DISC-263 | squidKid-deluxe/QTradeX-Algo-Trading-SDK | 2 | created | 956171842 | false | false | 7c038699e878bbf731894ba9498dbafa2d9c0460 | [README](https://github.com/squidKid-deluxe/QTradeX-Algo-Trading-SDK/blob/master/README.md) |
| DISC-264 | karthikramx/Algorithmic-Trading-Backtesting-in-python | 2 | created | 443823569 | false | false | b33f1e493cb45880ad08ebac62152db5081fee36 | [README](https://github.com/karthikramx/Algorithmic-Trading-Backtesting-in-python/blob/main/README.md) |
| DISC-265 | KVignesh122/MT5-SMC-trading-bot | 3 | created | 1061576246 | false | false | 4398490f5cd89f9fb0aa2309bd8f2b9c13c8ea45 | [README](https://github.com/KVignesh122/MT5-SMC-trading-bot/blob/main/README.md) |
| DISC-266 | WiltonMarques/QuantBridge-MT5-Python-AlgoTrading | 3 | created | 1204017286 | false | false | 42d4e44cc2039afc5117ca74e65b5c348735c267 | [README](https://github.com/WiltonMarques/QuantBridge-MT5-Python-AlgoTrading/blob/main/README.md) |
| DISC-267 | Lin-Thet-Zaw/QuantBridge-MT5-Python-AlgoTrading | 3 | created | 1207606392 | true / WiltonMarques/QuantBridge-MT5-Python-AlgoTrading | false | 42d4e44cc2039afc5117ca74e65b5c348735c267 | [README](https://github.com/Lin-Thet-Zaw/QuantBridge-MT5-Python-AlgoTrading/blob/main/README.md) |

## Validation

Repository document validator: 15/15 PASS. Intake audit: PASS — 64 hits, 62 distinct stable repository IDs, 60 new, 2 existing/updated, 0 rejected; 267 sequential unique DISC IDs, 11 fields per row, all 62 inputs mapped once, 205 unaffected previous rows byte-identical, source blob SHAs and next DISC-268 checked. Whitespace check clean. Full unit/runtime suite deliberately skipped under owner no-code-execution boundary; no claim of a green test suite. Only local document validation/data processing ran. Mutation/prepublish not applicable: no policy/validator edits or push. No candidate installation or execution, API/account coupling or trading.

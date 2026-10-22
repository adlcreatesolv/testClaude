# Pine Script catalog

Full run-by-run record: [`experiments/LOG.md`](../experiments/LOG.md).

Every script carries a header block with `TAG`, `STATUS`, `DESCRIPTION`,
lineage (`DERIVED FROM` / `SUCCESSOR`) and test results.

| Tag | Folder | Meaning |
|---|---|---|
| `ORIGINAL` | `pine/original/` | Shared by the user, code kept verbatim (only the header is added). Never edited. |
| `DEV` | `pine/dev/` | Versions developed from an original. Status: `UNDER TEST`, `NOT YET TESTED`, `REJECTED`, `CANDIDATE`. |

File naming: `<Name>.original.pine`, `<Name>[.<variant>].dev.pine`.

## Scripts

| File | Tag | Status | Description | Best test result |
|---|---|---|---|---|
| `original/OBV_Cross_Auto.original.pine` | ORIGINAL | Superseded | OBV stack above 34/55 SMAs + price > 13 SMA; CE on flag on, PE on flag off; intraday square-off 15:15 | 5m, 13 mo: +889 pts, PF 1.05, no costs (incl. overnight-carry bug) |
| `dev/OBV_Cross_Auto.dev.pine` | DEV | **REJECTED** | Square-off fix, entry cutoff, confirmation bars, HTF filter, exit modes, daily entry cap | 5m, 13 mo, 1 pt cost: −178 pts, PF 0.98 |
| `original/avi_regV2_Strategy.original.pine` | ORIGINAL | Superseded | Normalised regression-slope acceleration of two sources; both accelerating = long, both decelerating = short | 30m, 2020–2026: +21,834 pts/unit, PF 1.32, no costs |
| `dev/avi_regV2_Strategy.interday.dev.pine` | DEV | **UNDER TEST (best version)** | Original logic, fixed 1 unit, 1 pt cost, built-in OBV option, Side filter | 30m, 2020–2026, 1 pt cost: +20,469 pts, PF 1.29, maxDD −3,397 |
| `dev/avi_regV2_Strategy.intraday.dev.pine` | DEV | TESTED (MIXED) | Interday dev + Intraday mode (default; 15:15 square-off, 15:00 cutoff) | 30m, 2020–2026, 1 pt cost: +5,627 pts, PF 1.20, maxDD −2,199 |
| `dev/avi_regV2_Strategy.regime.dev.pine` | DEV | **REJECTED** (E15) | Interday dev + daily ADX(14) > 20 regime filter for entries + optional drawdown kill switch | 30m, 2020–2026, 1 pt cost: +11,808 pts, PF 1.27, maxDD −3,416 |
| `dev/Confluence4_Intraday.dev.pine` | DEV | SUPERSEDED | From user spec (no original script): Supertrend(10,3), daily pivot R1/S1, BB(20,2), RSI(14) 70/30; enter when all 4 agree; 5 exit types (any flip, or Supertrend / pivot / Bollinger / RSI flip) + Supertrend trail option; intraday NIFTY | — |
| `dev/QuadConfluenceBreakout.dev.pine` | DEV | UNDER TEST (3/10 runs) | **Quad Confluence Breakout (QCB).** One strategy, all choices as inputs: tick any of Supertrend / Pivot R1-S1 / Bollinger / RSI for entry (all ticked must agree), 6 exit types, Intraday/Interday, side. Setup tag written into every entry comment and a chart table | E19 5m 2009–2026: +9,448 pts, PF 1.35, maxDD −1,080 |

## OBV_Cross_Auto development history

| Commit | Change | Result (net pts) |
|---|---|---|
| `d1ab41f` | Same-bar square-off fix, entry cutoff, stale-carry close | 1m, 60 days: +1,087, no costs |
| `e64a9bc` | 2-bar entry confirmation | 1m, 60 days: +491, no costs (worse) |
| `940f7c8` | Non-repainting higher-TF filter | 1m, 60 days, N=2: +462, maxDD −317 |
| `3b3f6a4` | Defaults N=0, 1 pt round-trip commission | 1m, 60 days: −185 after cost; 5m, 13 mo: −178 |
| `3f5b2dc` | Exit modes + daily entry cap | 5m, 13 mo, HTF-flip exit: −976 |

Analyze any TradingView "List of trades" export with `python tools/analyze_trades.py <file.csv> --cost 0`
(use `--cost 0` when commission is already set in the strategy).

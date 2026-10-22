# Repository conventions

## Pine Scripts
- Every Pine Script the user shares, or that we develop, is saved under `pine/`.
- User-shared scripts: `pine/original/<Name>.original.pine`, code kept **verbatim**
  (only a header comment block is added), header `TAG: ORIGINAL`. Never edit them.
- Our versions: `pine/dev/<Name>[.<variant>].dev.pine`, header `TAG: DEV` with
  `STATUS`, `DERIVED FROM`, `DESCRIPTION` and `TESTED` results.
- Header block goes above `//@version=5` and lists: TAG, STATUS (dev only), NAME,
  FILE, AUTHOR / DERIVED FROM, DESCRIPTION, KNOWN ISSUES, TESTED, SUCCESSOR(S).
- Keep `pine/README.md` (catalog + history) up to date whenever a script is added,
  changed or tested.
- Dev scripts: one statement per line, no wrapped/continuation lines (user pastes them into TradingView).
- Don't put model identifiers in files or commits.

## Backtest analysis
- `tools/analyze_trades.py` analyses TradingView "List of trades" CSV exports (points).
- `tools/analyze_pct.py` compares several exports side by side in % per trade with a % cost (use for long histories, e.g. QCB 2009–2026, default 0.02%).

## Experiment log
- Log every backtest run, analysis/finding and planned idea in `experiments/LOG.md`
  (IDs: `E##` runs, `A##` analyses), with date, script + commit, chart/period,
  settings, key metrics, status tag and data file.
- Save each TradingView trade-list export as `experiments/data/E##_<script>_<variant>_<tf>.csv`.
- Update the script's header `TESTED` line and `pine/README.md` when a run changes its status.

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
- Don't put model identifiers in files or commits.

## Backtest analysis
- `tools/analyze_trades.py` analyses TradingView "List of trades" CSV exports.

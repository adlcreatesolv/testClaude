# Experiment log

Every backtest run, analysis and idea we try is recorded here, newest strategy
section last. Instrument: **NSE:NIFTY** (index) on TradingView unless noted.
P&L is in **NIFTY index points per 1 unit** (avi_regV2 original converted from
%-of-equity sizing). "Cost" = round-trip cost per trade in points.

Trade-list exports are in `experiments/data/` (named by experiment ID).
Analyse with `python tools/analyze_trades.py experiments/data/<file>.csv --cost 0`.

**Status tags:** `PASS` · `FAIL` · `MIXED` · `INFO` (analysis only) · `PENDING`

**Pass criteria (set before the 13-month tests):** after costs, PF > 1.3,
more than half the months profitable, both sides profitable.

---

## Strategy 1: OBV_Cross_Auto (`pine/original/OBV_Cross_Auto.original.pine`)

**Overall status: REJECTED.** No setup showed an edge after costs over 13 months.

### Backtest runs

| ID | Date | Script / commit | Chart, period | Settings | Trades | Net | PF | Max DD | Status | Data |
|---|---|---|---|---|---|---|---|---|---|---|
| E01 | 2026-10-13 | original | 5m, 2025-09-08 → 2026-10-13 | Intraday, Both, no SL, no cost | 1,443 | +889 | 1.05 | −1,285 | FAIL | `E01_OBV_original_5m.csv` |
| E02 | 2026-10-13 | dev `d1ab41f` (square-off fix) | 1m, 2026-07-20 → 2026-10-13 | cutoff 15:00, no cost | 1,518 | +1,087 (−431 @1pt) | 1.16 | −750 | FAIL | `E02_OBV_dev-fix_1m.csv` |
| E03 | 2026-10-13 | dev `e64a9bc` | 1m, same 60 days | confirmation N=2, no cost | 954 | +491 (−463 @1pt) | 1.08 | −1,063 | FAIL | `E03_OBV_dev-confirm2_1m.csv` |
| E04 | 2026-10-13 | dev `940f7c8` | 1m, same 60 days | N=2 + HTF 15m OBV filter, no cost | 451 | +462 (+11 @1pt) | 1.16 | −317 | MIXED | `E04_OBV_dev-confirm2-htf15_1m.csv` |
| E05 | 2026-10-13 | dev `3b3f6a4` | 1m, same 60 days | N=0 + HTF 15m, cost 1 pt | 727 | −185 | 0.95 | −575 | FAIL | `E05_OBV_dev-htf15-cost1_1m.csv` |
| E06 | 2026-10-13 | dev `3b3f6a4` | 5m, 2025-09-08 → 2026-10-13 | N=0 + HTF (60m assumed), Both, cost 1 pt | 639 | −178 | 0.98 | −1,126 | FAIL | `E06_OBV_dev-htf-cost1_5m-13mo.csv` |
| E07 | 2026-10-13 | dev `3f5b2dc` | 5m, same 13 months | Exit on HTF flip, max 2 entries/day, cost 1 pt | 245 | −976 | 0.90 | −2,534 | FAIL | `E07_OBV_dev-htfflip-exit_5m-13mo.csv` |

### Analyses / findings

| ID | Source | Finding | Status |
|---|---|---|---|
| A01 | E01 | **Bug:** intraday square-off filled at next bar open → 45 trades carried overnight; they made +825 of the +889. Fixed in `d1ab41f` (`close_all(immediately=true)`, stale-carry close). Fix verified in E02–E07 (0 overnight; 1 Muhurat-day trade closed by the safety net in E07). | INFO |
| A02 | E01, E02, E06 | Trades lasting ≤2 bars are the main loss source (e.g. E02: 563 trades, −2,233). | INFO |
| A03 | E02–E05 | Post-hoc filter "PE only + entries before 13:00" looked strong on the 60-day 1m window (PF 1.6–1.9, +829 to +1,267 after 1 pt) … | INFO |
| A04 | E06 | … but on 13 months it was flat (PF 1.00, +14). **Overfit to a 60-day downtrend** (NIFTY 24,200 → 22,500). PE edge only appeared in falling months. | FAIL |
| A05 | E03 vs E02 | 2-bar confirmation: lag cost more than whipsaws saved (net +1,087 → +491, DD worse). | FAIL |
| A06 | E04 vs E03 | HTF 15m filter halved trades and cut DD to a third (−1,063 → −317) at similar net. Helped risk, not edge. | MIXED |
| A07 | E04 | Max DD anatomy (E03): slow bleed 22 Jul → 15 Sep, 657 trades, worst day only −199; choppy market + ~16 trades/day. | INFO |
| A08 | E06 → E07 | "Square-off exits make +5,131" was **survivorship bias**: holding every trade to 15:15 made it worse (−976). Lesson: exit-signal subsets are not tradable filters. | FAIL |

### Ideas not run
- Square-off-only exit with / without signal-extreme stop; max 1 entry/day (expected to fail same as E07, dropped).

---

## Strategy 2: avi_regV2 (`pine/original/avi_regV2_Strategy.original.pine`)

**Overall status: UNDER TEST (promising).**

### Backtest runs

| ID | Date | Script / commit | Chart, period | Settings | Trades | Net | PF | Max DD | Status | Data |
|---|---|---|---|---|---|---|---|---|---|---|
| E08 | 2026-10-13 | original | 30m, 2020-01-01 → 2026-10-13 | as-is (both sources = close), 100% equity, no cost | 1,365 | +21,834 | 1.32 | −3,284 | PASS (pre-cost) | `E08_avi_regV2_original_30m.csv` |
| E09 | 2026-10-13 | dev interday `fcb6740` | 30m, same period | defaults (price/price), 1 unit, cost 1 pt | 1,365 | +20,469 | 1.29 | −3,397 | MIXED (PF just < 1.3) | `E09_avi_regV2_interday-dev_30m.csv` |
| E12 | 2026-10-13 | dev intraday (Mode = Intraday) | 30m, same period | price/price, 15:15 square-off, 15:00 cutoff, cost 1 pt | 1,175 | +5,627 | 1.20 | −2,199 | MIXED | `E12_avi_regV2_intraday-dev_30m.csv` |

### Analyses / findings

| ID | Source | Finding | Status |
|---|---|---|---|
| A09 | E08 | Both sources defaulted to `close` → OBV never used; strategy is an **always-in** long/short reversal on price regression-slope acceleration (every exit = next entry). | INFO |
| A10 | E08 | Every year positive (2022 weakest, +391); longs +16,083, shorts +5,751; avg +16 pts/trade, so robust to costs (+15,009 at 5 pts). Buy & hold ≈ +10,300 pts. | INFO |
| A11 | E08 | Overnight-held trades +39,649 vs same-day −17,815 (partly survivorship, see A08), so an intraday-only version is unlikely to keep the edge. | INFO |
| A12 | E09 vs E08 | Dev version reproduces the original exactly minus 1 pt × 1,365 trades. | INFO |
| A13 | E12 vs E09 | Intraday-only keeps an edge but only ~27% of the interday profit (+5,627 vs +20,469); avg 4.8 vs 15 pts/trade, so far more cost-sensitive (+927 at 4 pts extra slippage). Both sides positive (L +1,856 / S +3,771), 52/82 months green, but 2022–23 flat and 2025 −1,431. Max DD −2,199 (May-2025 → Jan-2026), recovered only Oct-2026. Fails PF > 1.3. Trades only on 635 of ~1,680 days (needs a fresh signal after square-off). | MIXED |
| A14 | E12, E09 | **Equity-curve filter** (trade only while strategy equity ≥ its N-trade MA, N=10/20/50), simulated from trade lists. Intraday: maxDD −2,199 → −1,557 at best but net −34% (+3,726). Interday: worse for N=10/20 (maxDD ≈ −4,050, net −75…−90%); N=50 ≈ same DD, net −29%. Does not prevent drawdowns. | FAIL |
| A15 | E12 | **Year-by-year (intraday):** 2020 +1,611 · 2021 +1,106 · 2022 +86 · 2023 +82 · 2024 +2,525 · 2025 −1,431 · 2026 +1,648. Extra slippage: +1 pt → +4,452, +2 → +3,277, +4 → +927. Exit split (square-off +19,748 vs Trend Break −14,113) is survivorship by construction, not a filter (see A08). | INFO |
| A16 | E12 | **Max DD anatomy (intraday):** peak 2025-05-20 (+5,625) → trough 2026-01-27 (+3,426) = −2,199 over 116 trades; recovered only 2026-10-13 (~17 months under water). Monthly: May −162, Jun −334, Jul +25, Aug −165, Sep −117, Oct −40, Nov −325, Dec −528, Jan −553 (8/9 red). Both sides lost (L −1,395 / S −804), win% 36, longest losing streak 8, worst days 14-Nov-25 −346, 27-Jan-26 −298, 23-Jan-26 −230. Second DD −1,741 from May-2022 to Apr-2024 (~2 years). On 1 futures lot (75) −2,199 pts ≈ ₹1.65 lakh. Both DDs = choppy, trendless regimes. | INFO |

### Risk-management guidelines (decided 2026-10-13)
| ID | Guideline | Basis |
|---|---|---|
| R1 | Drawdowns cannot be eliminated, only made smaller or survivable; every reduction costs profit or risks overfitting. | A14 |
| R2 | **Position sizing:** capital ≥ 2× worst historical drawdown. Interday: 2 × ~3,400 pts × 75 ≈ ₹5 lakh per NIFTY futures lot. | E09 |
| R3 | **Kill switch, set in advance:** stop and re-evaluate if live drawdown reaches ~1.5× the historical worst (interday ≈ −5,100 pts). | E09 |
| R4 | Prefer **interday** over intraday: ~3.6× the profit for ~1.5× the drawdown, and less cost-sensitive (15 vs 4.8 pts/trade). | A13 |
| R5 | Any new filter must be designed on 2020–2023 only and judged on 2024–2026 (out-of-sample), to avoid the A03/A04 overfitting trap. | A04 |

### Queue
| ID | Plan | Status |
|---|---|---|
| E10 | Interday dev, Primary source = OBV (built-in), 30m 2020–2026 | PENDING (next) |
| E11 | Interday dev, slippage 2–3 ticks | PENDING |
| E12 | Intraday dev, Mode = Intraday | DONE (see runs) |
| E13 | Long only vs Short only | PENDING |
| E14 | Out-of-sample check on another index (e.g. BANKNIFTY) with unchanged settings | PENDING |
| E15 | Regime filter to skip choppy markets (candidates: daily ADX, regression R² 'trendiness'); rule fixed on 2020–2023, judged only on 2024–2026 (R5). Motivated by A16. | PENDING (after E10) |

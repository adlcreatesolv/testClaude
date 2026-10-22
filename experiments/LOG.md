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

**Overall status: UNDER TEST — promising on NIFTY, not confirmed on BANKNIFTY (A22).**

### Backtest runs

| ID | Date | Script / commit | Chart, period | Settings | Trades | Net | PF | Max DD | Status | Data |
|---|---|---|---|---|---|---|---|---|---|---|
| E08 | 2026-10-13 | original | 30m, 2020-01-01 → 2026-10-13 | as-is (both sources = close), 100% equity, no cost | 1,365 | +21,834 | 1.32 | −3,284 | PASS (pre-cost) | `E08_avi_regV2_original_30m.csv` |
| E09 | 2026-10-13 | dev interday `fcb6740` | 30m, same period | defaults (price/price), 1 unit, cost 1 pt | 1,365 | +20,469 | 1.29 | −3,397 | MIXED (PF just < 1.3) | `E09_avi_regV2_interday-dev_30m.csv` |
| E10 | 2026-10-13 | dev interday `pine/dev/avi_regV2_Strategy.interday.dev.pine` | 30m, 2020-01-01 → 2026-10-13 | **Primary source = OBV (built-in)**, secondary = close, 1 unit, cost 1 pt | 1,380 | +12,705 | 1.23 | −2,755 | FAIL (worse than E09) | `E10_avi_regV2_interday-obv_30m.csv` |
| E11 | 2026-10-14 | dev interday `pine/dev/avi_regV2_Strategy.interday.dev.pine` | 30m, 2020-01-01 → 2026-10-13 | price/price, cost 1 pt + **slippage 20 ticks** (= 2 pts/round trip; total 3 pts) | 1,365 | +17,739 | 1.25 | −3,623 | PASS (robust to costs) | `E11_avi_regV2_interday-slip20_30m.csv` |
| E14 | 2026-10-14 | dev interday `pine/dev/avi_regV2_Strategy.interday.dev.pine` | **NSE:BANKNIFTY** 30m, 2020-01-01 → 2026-10-13 | all defaults (price/price, cost 1 pt, no slippage) | 1,553 | +30,912 | 1.14 | −13,235 | MIXED (weak) | `E14_avi_regV2_interday_BANKNIFTY_30m.csv` |
| E12 | 2026-10-13 | dev intraday (Mode = Intraday) | 30m, same period | price/price, 15:15 square-off, 15:00 cutoff, cost 1 pt | 1,175 | +5,627 | 1.20 | −2,199 | MIXED | `E12_avi_regV2_intraday-dev_30m.csv` |
| E15 | 2026-10-13 | dev regime `pine/dev/avi_regV2_Strategy.regime.dev.pine` | 30m, 2020-01-01 → 2026-10-13 | interday, price/price, daily ADX(14) > 20 for entries, kill switch off, cost 1 pt | 867 | +11,808 | 1.27 | −3,416 | FAIL | `E15_avi_regV2_regime-adx_30m.csv` |

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
| A17 | E15 vs E09 | **Daily ADX(14) > 20 regime filter does not reduce drawdown.** Full period: trades 1,365 → 867, net +20,469 → +11,808 (−42%), PF 1.29 → 1.27, maxDD −3,397 → −3,416 (unchanged; now 2022-03 → 2022-11, recovered 2024-09). 2022 got worse (+190 → −1,049): ADX called 2022 'trending' while the signal whipsawed. Out-of-sample 2024–26 (R5): net +11,221 → +7,306, PF 1.36 → 1.44, maxDD −3,397 → −2,056; return/DD 3.3 → 3.6, a marginal gain that does not justify 35–42% less profit. Decision: keep E09 interday as baseline; do not tune ADX values (would be overfitting). | FAIL |
| A18 | E09 | Correction/detail: the interday (E09) max DD is −3,397 from 2025-11-14 to 2026-04-07 (113 trades), recovered 2026-10-01. In-sample 2020–23: +9,248, PF 1.24; out-of-sample 2024–26: +11,221, PF 1.36 (edge held up in the later period). | INFO |
| A19 | E10 vs E09 | **OBV as primary source is worse than price-only.** Net +12,705 vs +20,469 (−38%), PF 1.23 vs 1.29, avg 9.2 vs 15.0 pts/trade, green months 45/82 vs 56/82, 2021 negative (−192). MaxDD smaller (−2,755 vs −3,397, Nov-2025 → Feb-2026, not yet recovered) but profit/DD 4.6 vs 6.0. No longer always-in: OBV and price disagree often, so only 11% of exits are immediate reversals (flat in between). In-sample 2020–23 PF 1.14, out-of-sample 2024–26 PF 1.32 (E09: 1.24 / 1.36). Both sides still positive (L +8,934, S +3,772). Decision: keep **price/price** (E09) as baseline. | FAIL |
| A20 | E11 vs E09 | **Survives realistic slippage.** Identical 1,365 trades, each exactly 2 pts worse (verified). Net +17,739 (−13%), PF 1.25, avg 13 pts/trade, maxDD −3,623 (Nov-2025 → Apr-2026, not yet recovered), 54/82 green months. By year: 2020 +4,397 · 2021 +761 · 2022 **−212** · 2023 +2,645 · 2024 +5,687 · 2025 +2,859 · 2026 +1,601. In-sample 2020–23 PF 1.19, out-of-sample 2024–26 PF 1.32. Shorts thin (+3,702) vs longs +14,037. At 3 pts total cost per trade the strategy still clears ~2× buy & hold (~+10,300). | PASS |
| A21 | E14 | **Edge does not transfer cleanly to BANKNIFTY.** Positive overall (+30,912 pts vs buy & hold ≈ +22,959 from 32,248 → 55,207) but PF only 1.14, 45/82 green months, maxDD −13,235 (Jun-2021 → Dec-2022, recovered only Mar-2024, ~2.75 years under water); profit/DD 2.3 vs 6.0 on NIFTY. By year: 2020 +16,493 · 2021 +9,409 · 2022 −4,474 · 2023 +6,355 · 2024 +3,805 · 2025 +4,602 · 2026 −5,278. In-sample 2020–23 PF 1.23 vs **out-of-sample 2024–26 PF 1.03 (≈ flat)**. Longs +26,936 (PF 1.26) carry it; shorts +3,976 (PF 1.04) ≈ nothing, so much of the profit is the bull trend. Cost is generous here (1 pt on a ~2× higher price); +6 pts/trade leaves +21,593. | MIXED |
| A22 | E09–E15 | **Overall verdict avi_regV2 (2026-10-14):** best = interday price/price (E09). Robust to 3 pts cost on NIFTY (E11), edge stronger in 2024–26 than 2020–23 on NIFTY, but weak and fading on BANKNIFTY (E14) → NIFTY result is at least partly instrument-specific. Not a confirmed edge; next step is forward/paper testing on NIFTY with small size, not more filters. | INFO |
| A23 | E09, E14 | **Do losses cluster?** Wald–Wolfowitz runs test on win/loss sequence: NIFTY z = −0.37, BANKNIFTY z = −0.74 → **no significant clustering**; streaks are what a 37% win rate produces by chance (expected longest losing streak in 1,365 trades ≈ 15). Win% after 1/2/3 losses ≈ unchanged (36.8/34.0/37.1% NIFTY). Explains why equity-curve filters (A14) fail. Trade density in prior 7 days: non-monotonic, noise. | INFO |
| A24 | E09, E14 | **Candidate: skip the entry right after a whipsaw** (previous trade lasted ≤ 2 bars). Next-trade avg 6.9 vs 19.5 pts (NIFTY), 5.2 vs 29.8 (BANKNIFTY). Simulated exactly from trade lists (always-in, so skipping = flat until next signal): NIFTY 2020–23 PF 1.24 → 1.32, DD −2,984 → −2,154, net −16%; 2024–26 PF 1.36 → 1.44, DD −3,397 → −2,296, net −16%. BANKNIFTY 2020–23 PF 1.23 → 1.44, DD −13,235 → −4,849; but 2024–26 PF 1.03 → 0.95, DD worse (−14,493). **Caveat: rule found by looking at the full data, so not a clean out-of-sample result** → must be confirmed on unseen data (E17). | MIXED |

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
| E10 | Interday dev, Primary source = OBV (built-in), 30m 2020–2026 | DONE — FAIL (A19) |
| E11 | Interday dev, Properties → Slippage = 20 ticks (NIFTY tick 0.05 → 1 pt per fill, 2 pts per round trip, on top of 1 pt commission). Corrects the earlier '2–3 ticks', which would be only ~0.1 pt. | DONE — PASS (A20) |
| E12 | Intraday dev, Mode = Intraday | DONE (see runs) |
| E13 | Long only vs Short only | PENDING |
| E14 | Out-of-sample check on NSE:BANKNIFTY, 30m, 2020–2026, interday dev with all defaults unchanged | DONE — MIXED (A21) |
| E17 | Skip-after-whipsaw rule (A24) as a Pine option, fixed at ≤ 2 bars, tested only on data not yet seen (e.g. NSE:FINNIFTY or BSE:SENSEX 30m, and NIFTY 15m) | PROPOSED |
| E16 | Forward/paper test: NIFTY interday (E09 settings) from 2026-10-14, log every live signal and fill vs backtest | PROPOSED |
| E15 | Regime filter to skip choppy markets (candidates: daily ADX, regression R² 'trendiness'); rule fixed on 2020–2023, judged only on 2024–2026 (R5). Motivated by A16. Script: `pine/dev/avi_regV2_Strategy.regime.dev.pine` (daily ADX(14) > 20, fixed in advance; kill switch off by default). | DONE — FAIL (A17) |

---

## Strategy 3: Confluence4 Intraday (`pine/dev/Confluence4_Intraday.dev.pine`)

**Overall status: NOT YET TESTED.** Built from the user's spec (2026-10-22): Supertrend (10,3) long, pivot R1 crossed, Bollinger 2 SD crossed up/down, RSI > 70; any 3 true → entry; any one flip → exit; intraday NIFTY.

2026-10-22: default exit changed to a Supertrend trailing stop at the user's request; in that mode entries require Supertrend to agree.

2026-10-22 user clarification: **all 4 must agree for entry, with 3 already aligned and the 4th just flipping** (score 3 → 4); further clarified: several flipping on the same bar (e.g. 2 → 4) also counts, so entry = score becomes 4. Exits: five types decided 2026-10-22 (any flip + each indicator's flip, E18–E22); square-off at 15:25 IST (bar close), entries still stop at 15:00.

Interpretation choices: crosses treated as states (close beyond R1/S1 or the band); shorts mirror longs (Supertrend down, close < S1, close < lower band, RSI < 30).

### Queue (fixed 2026-10-22; existing script options only, nothing new to be added; chart timeframe not fixed, each run records the one used and each timeframe tried counts as a separate variant)
| ID | Symbol | Entry condition (Long / Short) | Exit condition | Exit on setting | Status |
|---|---|---|---|---|---|
| E18 | NSE:NIFTY | All 4 true on this bar, fewer than 4 on the previous bar; before 15:00 | **Any** of the 4 turns false; or 15:25 square-off | 1 Any condition flips | PENDING |
| E19 | NSE:NIFTY | Same | **Supertrend** flips; or 15:25 | 2 Supertrend flips | PENDING |
| E20 | NSE:NIFTY | Same | **Pivot**: close back below R1 / above S1; or 15:25 | 3 Pivot flips | PENDING |
| E21 | NSE:NIFTY | Same | **Bollinger**: close back inside the band; or 15:25 | 4 Bollinger flips | PENDING |
| E22 | NSE:NIFTY | Same | **RSI**: back below 70 / above 30; or 15:25 | 5 RSI flips | PENDING |
| E23 | NSE:BANKNIFTY | Same | Best of E18–E22, unchanged | (best) | PENDING |
| — | — | Supertrend trailing stop kept as an extra option (intrabar version of E19); not in the plan | — | Supertrend trail | NOT PLANNED |
| E18i–E22i | NSE:NIFTY | Same as E18–E22 with **Mode = Interday** (held overnight, no square-off / entry cutoff) | Same exit types, no 15:25 | 1–5 | OPTIONAL |

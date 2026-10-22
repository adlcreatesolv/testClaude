"""Percent-based comparison of TradingView trade-list exports.

Use for long histories where price levels change a lot (e.g. NIFTY 2009-2026),
so fixed point costs are unrealistic. Each trade's gross return is
(net PnL + commission) / entry price; a cost in % per round trip is then
subtracted.

Usage:
    python analyze_pct.py run1.csv [run2.csv ...] [--cost 0.02]
"""
import argparse

import pandas as pd

pd.set_option("display.width", 220)


def load(path):
    d = pd.read_csv(path, encoding="utf-8-sig")
    en = d[d["Type"].str.startswith("Entry")].set_index("Trade number")
    ex = d[d["Type"].str.startswith("Exit")].set_index("Trade number")
    t = pd.DataFrame({
        "entry": pd.to_datetime(en["Date and time"]),
        "exit": pd.to_datetime(ex["Date and time"], errors="coerce"),
        "exit_sig": ex["Signal"],
        "tag": en["Signal"].str.split(" ", n=1).str[1],
        "pnl": en["Net PnL NONE"],
        "comm": en["Commission NONE"],
        "px": en["Price"],
        "bars": en["Duration (bars)"],
    })
    t["gross"] = 100 * (t.pnl + t.comm) / t.px
    return t.dropna(subset=["exit"]).sort_values("exit")


def pf(r):
    loss = -r[r < 0].sum()
    return r[r > 0].sum() / loss if loss else float("inf")


def summary(t, cost):
    r = t.gross - cost
    eq = (1 + r / 100).cumprod()
    yrs = t.entry.dt.year
    by_year = r.groupby(yrs).sum()
    out = {
        "tag": t.tag.mode().iat[0] if t.tag.notna().any() else "",
        "period": f"{t.entry.min():%Y-%m} -> {t.exit.max():%Y-%m}",
        "trades": len(t),
        "overnight": int((t.entry.dt.date != t.exit.dt.date).sum()),
        "win%": round(100 * (r > 0).mean(), 1),
        "avg_win%": round(r[r > 0].mean(), 3),
        "avg_loss%": round(r[r <= 0].mean(), 3),
        "avg%": round(r.mean(), 4),
        "PF": round(pf(r), 2),
        "compounded%": round(100 * (eq.iat[-1] - 1), 1),
        "maxDD%": round(100 * (eq / eq.cummax() - 1).min(), 1),
        "green_years": f"{(by_year > 0).sum()}/{len(by_year)}",
        "PF_2009-17": round(pf(r[yrs <= 2017]), 2),
        "PF_2018-22": round(pf(r[(yrs >= 2018) & (yrs <= 2022)]), 2),
        "PF_2023+": round(pf(r[yrs >= 2023]), 2),
        "median_bars": t.bars.median(),
    }
    return out, by_year.round(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--cost", type=float, default=0.02, help="round-trip cost in %% per trade")
    a = ap.parse_args()
    rows, years = {}, {}
    for f in a.files:
        s, y = summary(load(f), a.cost)
        name = f.rsplit("/", 1)[-1].replace(".csv", "")
        rows[name], years[name] = s, y
    print(f"Cost: {a.cost}% per round trip\n")
    print(pd.DataFrame(rows).to_string())
    print("\nNet % by entry year")
    print(pd.DataFrame(years).T.to_string())


if __name__ == "__main__":
    main()

"""Analyze TradingView "List of trades" CSV exports.

Usage:
    pip install pandas
    python analyze_trades.py run1.csv [run2.csv ...] [--cost 1.0]

--cost is the round-trip cost per trade in points used for the
"after cost" figures (default 1.0). Results are also shown at 0.5x and 2x.
"""
import argparse

import pandas as pd

pd.set_option("display.width", 200)


def load(path):
    d = pd.read_csv(path, encoding="utf-8-sig")
    en = d[d["Type"].str.startswith("Entry")].set_index("Trade number")
    ex = d[d["Type"].str.startswith("Exit")].set_index("Trade number")
    return pd.DataFrame({
        "side": en["Type"].str.split().str[1],
        "entry": pd.to_datetime(en["Date and time"]),
        "exit": pd.to_datetime(ex["Date and time"], errors="coerce"),  # "Open" -> NaT
        "exit_sig": ex["Signal"],
        "pnl": en["Net PnL NONE"],
        "bars": en["Duration (bars)"],
        "entry_sig": en["Signal"],
    })


def stats(g):
    w, l = g.pnl[g.pnl > 0], g.pnl[g.pnl <= 0]
    eq = g.pnl.cumsum()
    return pd.Series({
        "trades": len(g),
        "net": g.pnl.sum(),
        "win%": 100 * len(w) / len(g) if len(g) else 0,
        "avg_win": w.mean(),
        "avg_loss": l.mean(),
        "PF": w.sum() / -l.sum() if l.sum() else float("inf"),
        "avg": g.pnl.mean(),
        "maxDD": (eq - eq.cummax()).min(),
    })


def drawdown_period(c):
    eq = c.pnl.cumsum().reset_index(drop=True)
    dd = eq - eq.cummax()
    tr = dd.idxmin()
    pk = eq[: tr + 1].idxmax()
    after = eq[tr:]
    rec = after[after >= eq[pk]]
    ex = c["exit"].reset_index(drop=True)
    return {
        "peak": ex[pk], "trough": ex[tr], "depth": round(dd[tr], 1),
        "trades_in_dd": tr - pk,
        "recovered": ex[rec.index[0]] if len(rec) else "not yet",
    }


def report(path, cost):
    t = load(path)
    c = t.dropna(subset=["exit"]).sort_values("exit")
    days = c.entry.dt.date.nunique()
    overnight = c[c.entry.dt.date != c.exit.dt.date]

    print("=" * 80)
    print(path)
    tags = t.entry_sig.str.split(" ", n=1).str[1].dropna().unique()
    if len(tags) and "|" in str(tags[0]):
        print("Setup tag:", ", ".join(map(str, tags)))
    print(f"Period {c.entry.min()} -> {c.exit.max()} | {days} days | "
          f"{len(c) / days:.1f} trades/day | open: {t.exit.isna().sum()} | "
          f"overnight: {len(overnight)}")
    if len(overnight):
        print(overnight.to_string())

    print("\nOverall")
    print(stats(c).round(2).to_string())
    for title, key in [("By side", c.side),
                       ("By exit signal", c.exit_sig),
                       ("By duration (<=2 bars)", c.bars <= 2),
                       ("By entry hour", c.entry.dt.hour),
                       ("By month", c.entry.dt.to_period("M"))]:
        print(f"\n{title}")
        print(c.groupby(key).apply(stats).round(2).to_string())

    print("\nMax drawdown period:", drawdown_period(c))

    print(f"\nCost sensitivity (points per round trip)")
    for k in (0.5 * cost, cost, 2 * cost):
        print(f"  {k:4.2f} -> net {c.pnl.sum() - k * len(c):9.1f}")

    # Entry-only filters: each subset is exact because removing an entry
    # does not change any other trade.
    print(f"\nFilter subsets (net after {cost} pt cost)")
    subsets = {
        "All": c,
        "CE only": c[c.side == "long"],
        "PE only": c[c.side == "short"],
        "Entries < 13:00": c[c.entry.dt.hour < 13],
        "PE & < 13:00": c[(c.side == "short") & (c.entry.dt.hour < 13)],
    }
    rows = []
    for name, g in subsets.items():
        if len(g):
            r = stats(g)
            r["net_after_cost"] = r.net - cost * len(g)
            rows.append(r.rename(name))
    print(pd.DataFrame(rows)[["trades", "net", "PF", "avg", "maxDD", "net_after_cost"]].round(2).to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--cost", type=float, default=1.0)
    a = ap.parse_args()
    for f in a.files:
        report(f, a.cost)


if __name__ == "__main__":
    main()

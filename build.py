"""Render site/index.html from findings.json + monthly.csv + cohort.csv. All numbers computed."""
import csv, datetime as dt, json

F = json.load(open("findings.json"))
monthly = list(csv.DictReader(open("monthly.csv")))
cohort = list(csv.DictReader(open("cohort.csv")))

def money(x: float) -> str:
    return f"£{x/1e6:.2f}M" if x >= 1e6 else f"£{x:,.0f}"

def svg_line() -> str:
    vals = [float(m["revenue"]) for m in monthly]
    w, h, pad = 720, 200, 24
    mx = max(vals)
    pts = [(pad + i * (w - 2*pad) / max(len(vals)-1, 1), h - pad - (v / mx) * (h - 2*pad)) for i, v in enumerate(vals)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    labels = "".join(f'<text x="{pad + i*(w-2*pad)/max(len(vals)-1,1):.0f}" y="{h-6}" font-size="8" text-anchor="middle">{m["month"][2:]}</text>'
                     for i, m in enumerate(monthly) if i % 3 == 0)
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Monthly net revenue">'
            f'<path d="{path}" fill="none" stroke="#00D4AA" stroke-width="2"/>{labels}</svg>')

def heat() -> str:
    cohorts = sorted({r["cohort"] for r in cohort})[:12]
    grid = {(r["cohort"], int(r["off"])): float(r["pct"]) for r in cohort}
    head = "<tr><th>Cohort</th>" + "".join(f"<th>M{o}</th>" for o in range(12)) + "</tr>"
    rows = ""
    for c in cohorts:
        cells = ""
        for o in range(12):
            v = grid.get((c, o))
            if v is None:
                cells += "<td></td>"
            else:
                a = min(v / 100, 1.0)
                cells += f'<td style="background:rgba(0,212,170,{a:.2f})">{v:.0f}%</td>'
        rows += f"<tr><th>{c}</th>{cells}</tr>"
    return f"<table>{head}{rows}</table>"

KPIS = [
    (money(F["net_revenue"]), "net revenue (known customers)"),
    (f'{F["orders"]:,}', "orders"),
    (money(F["aov"]), "avg order value"),
    (f'{F["customers"]:,}', "customers"),
    (f'{F["repeat_revenue_pct"]}%', "revenue from repeat buyers"),
    (f'{F["top10_customer_revenue_pct"]}%', "revenue from top-decile customers"),
]
tiles = "".join(f'<div class="kpi"><b>{v}</b><span>{l}</span></div>' for v, l in KPIS)

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Retail KPI dashboard — freddyxai</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:780px;margin:2rem auto;padding:0 1rem;color:#111}}
h1{{font-size:1.4rem}} .kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem;margin:1rem 0}}
.kpi{{border:1px solid #ddd;border-radius:10px;padding:.8rem}} .kpi b{{display:block;font-size:1.25rem}}
.kpi span{{font-size:.75rem;color:#555}} table{{border-collapse:collapse;font-size:.7rem;width:100%}}
th,td{{border:1px solid #eee;padding:2px 4px;text-align:center}} footer{{margin-top:1.5rem;font-size:.75rem;color:#555}}
</style></head><body>
<h1>Retail KPI dashboard <small>· one view, real data</small></h1>
<p>UCI Online Retail II — a real UK online retailer, Dec 2009–Dec 2011 (historical dataset; {F["rows"]:,} rows analyzed, {F["cancel_rate_pct"]}% of invoices were cancellations).</p>
<div class="kpis">{tiles}</div>
<h2>Monthly net revenue</h2>{svg_line()}
<h2>Cohort retention (first 12 cohorts × 12 months)</h2>{heat()}
<footer>Median next-month retention: {F["median_m1_retention_pct"]}%. Every number computed from
<a href="https://github.com/freddylearnsai/retail-kpi-dashboard">the pipeline in this repo</a> — nothing hand-typed.
Built by <a href="https://freddyxai.com/work-with-me">freddyxai</a>; this is the shape of a $500 single-view starter.
Generated {dt.date.today().isoformat()}.</footer>
</body></html>"""
open("site/index.html", "w").write(html)
print(json.dumps({"kpis": len(KPIS), "bytes": len(html)}))

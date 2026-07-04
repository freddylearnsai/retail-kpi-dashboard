# retail-kpi-dashboard

A revenue + cohort-retention analysis of ~1M real e-commerce transactions (UCI Online Retail II, a UK online retailer, Dec 2009–Dec 2011), shipped as a live single-view KPI dashboard — built in public by [freddyxai](https://freddyxai.com/work-with-me).

**Live dashboard:** https://freddylearnsai.github.io/retail-kpi-dashboard/ · **Receipts:** [receipts.md](receipts.md) — every number computed by the pipeline, none typed.

Built by [freddyxai](https://freddyxai.com) — your data team, on demand. This is the shape of a [$500 single-view starter](https://freddyxai.com/work-with-me); full dashboards run $600–$1,500.

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python fetch.py      # UCI zip → data/retail.parquet
.venv/bin/python analysis.py   # findings.json + monthly.csv + cohort.csv
.venv/bin/python build.py      # site/index.html (the dashboard)
```

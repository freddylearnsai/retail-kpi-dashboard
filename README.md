# retail-kpi-dashboard

A revenue + cohort-retention analysis of ~1M real e-commerce transactions (UCI Online Retail II, a UK online retailer, Dec 2009–Dec 2011), shipped as a live single-view KPI dashboard — built in public by [freddyxai](https://freddyxai.com/work-with-me).

Status: build in progress. Receipts land in `receipts.md` when the run completes.

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python fetch.py      # UCI zip → data/retail.parquet
.venv/bin/python analysis.py   # findings.json + monthly.csv + cohort.csv
.venv/bin/python build.py      # site/index.html (the dashboard)
```

"""Findings from data/retail.parquet → findings.json + monthly.csv + cohort.csv (committed)."""
import json, time
import duckdb

Q_BASE = """
create view sales as
select invoice, quantity, invoiced_at, price, customer_id,
       quantity * price as amount,
       date_trunc('month', invoiced_at) as month
from read_parquet('data/retail.parquet')
where not starts_with(invoice, 'C') and quantity > 0 and price > 0
"""

def main() -> None:
    t0 = time.time()
    con = duckdb.connect()
    con.execute(Q_BASE)
    total = con.execute("select count(*) from read_parquet('data/retail.parquet')").fetchone()[0]
    cancels = con.execute(
        "select count(distinct invoice) from read_parquet('data/retail.parquet') where starts_with(invoice, 'C')").fetchone()[0]
    invoices_all = con.execute(
        "select count(distinct invoice) from read_parquet('data/retail.parquet')").fetchone()[0]
    kpi = con.execute("""select round(sum(amount), 2), count(distinct invoice),
                         round(sum(amount) / count(distinct invoice), 2),
                         count(distinct customer_id) from sales where customer_id is not null""").fetchone()
    known = con.execute("select round(sum(amount),2) from sales where customer_id is not null").fetchone()[0]
    top10 = con.execute("""
      with per_cust as (select customer_id, sum(amount) rev from sales where customer_id is not null group by 1),
      ranked as (select rev, ntile(10) over (order by rev desc) as decile from per_cust)
      select round(100 * sum(rev) filter (where decile = 1) / sum(rev), 1) from ranked""").fetchone()[0]
    repeat_share = con.execute("""
      with per_cust as (select customer_id, count(distinct invoice) inv, sum(amount) rev
                        from sales where customer_id is not null group by 1)
      select round(100 * sum(rev) filter (where inv > 1) / sum(rev), 1) from per_cust""").fetchone()[0]
    m1 = con.execute("""
      with firsts as (select customer_id, min(month) cohort from sales where customer_id is not null group by 1),
      act as (select distinct s.customer_id, f.cohort,
                     datediff('month', f.cohort, s.month) as off
              from sales s join firsts f using (customer_id)),
      sizes as (select cohort, count(distinct customer_id) n from act where off = 0 group by 1),
      rets as (select cohort, count(distinct customer_id) r from act where off = 1 group by 1)
      select round(100 * median(coalesce(r, 0)::double / n), 1)
      from sizes left join rets using (cohort)
      where cohort < (select max(month) from sales)""").fetchone()[0]
    con.execute("""copy (select strftime(month, '%Y-%m') as month, round(sum(amount), 2) revenue,
                   count(distinct invoice) orders from sales where customer_id is not null
                   group by 1 order by 1) to 'monthly.csv' (header, delimiter ',')""")
    con.execute("""copy (
      with firsts as (select customer_id, min(month) cohort from sales where customer_id is not null group by 1),
      act as (select distinct s.customer_id, f.cohort, datediff('month', f.cohort, s.month) as off
              from sales s join firsts f using (customer_id)),
      sizes as (select cohort, count(distinct customer_id) n from act where off = 0 group by 1)
      select strftime(a.cohort, '%Y-%m') cohort, a.off, round(100.0 * count(distinct a.customer_id) / s.n, 1) pct
      from act a join sizes s using (cohort) where a.off between 0 and 11
      group by a.cohort, a.off, s.n order by 1, 2) to 'cohort.csv' (header, delimiter ',')""")
    findings = {
        "rows": total, "invoices": invoices_all, "cancelled_invoices": cancels,
        "cancel_rate_pct": round(100 * cancels / invoices_all, 1),
        "net_revenue": kpi[0], "orders": kpi[1], "aov": kpi[2], "customers": kpi[3],
        "known_revenue": known, "top10_customer_revenue_pct": top10,
        "repeat_revenue_pct": repeat_share, "median_m1_retention_pct": m1,
        "seconds": round(time.time() - t0, 1),
    }
    json.dump(findings, open("findings.json", "w"), indent=1)
    print(json.dumps(findings))

if __name__ == "__main__":
    main()

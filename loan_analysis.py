"""
Loan Disbursement Analysis — Python Script
Data Source: /mnt/user-data/uploads/All_Disb___Not_Disb20260420__1_.xlsx
Tools: pandas, sqlite3, matplotlib
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ─── 1. LOAD DATA ───────────────────────────────────────────────────────────
df = pd.read_excel("/mnt/user-data/uploads/All_Disb___Not_Disb20260420__1_.xlsx")
df['CB_check_date'] = pd.to_datetime(df['CB_check_date'], errors='coerce')
df['CB_Create_date'] = pd.to_datetime(df['CB_Create_date'], errors='coerce')

print(f"✅ Loaded {len(df):,} records | Columns: {len(df.columns)}")

# ─── 2. CONNECT TO SQLite DB ────────────────────────────────────────────────
conn = sqlite3.connect("/home/claude/loan_disbursement.db")
df.to_sql("loan_applications", conn, if_exists="replace", index=False)

# ─── 3. KEY METRICS ─────────────────────────────────────────────────────────
total       = len(df)
disbursed   = (df['Isdisbursed'] == 'Disbursed').sum()
not_disb    = (df['Isdisbursed'] == 'Not Disbursed').sum()
rate        = disbursed / total * 100
cb_pass     = (df['Member_Pass'] == 'Pass').sum()
grt_done    = (df['CGTRemark'] == 'Grt Complete').sum()

print(f"\n{'='*55}")
print(f"  {'KPI SUMMARY':^51}  ")
print(f"{'='*55}")
print(f"  Total Applications    : {total:,}")
print(f"  ✅ Disbursed          : {disbursed:,}")
print(f"  ❌ Not Disbursed      : {not_disb:,}")
print(f"  📈 Disbursement Rate  : {rate:.1f}%")
print(f"  ✔  CB Pass Members    : {cb_pass:,}")
print(f"  🎓 GRT Complete       : {grt_done:,}")
print(f"{'='*55}\n")

# ─── 4. SQL ANALYSIS ────────────────────────────────────────────────────────
queries = {
    "Branch Summary": """
        SELECT BRANCHNAME,
          COUNT(*) AS total,
          SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END) AS disbursed,
          ROUND(100.0*SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END)/COUNT(*),2) AS rate_pct,
          SUM(CASE WHEN Member_Pass='Pass' THEN 1 ELSE 0 END) AS cb_pass
        FROM loan_applications GROUP BY BRANCHNAME ORDER BY rate_pct DESC
    """,
    "Top 10 FE by Conversion": """
        SELECT FeName, BRANCHNAME,
          COUNT(*) AS total,
          SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END) AS disbursed,
          ROUND(100.0*SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END)/COUNT(*),2) AS conversion_pct
        FROM loan_applications
        GROUP BY FeName HAVING total > 10
        ORDER BY conversion_pct DESC LIMIT 10
    """,
    "CGT Funnel": """
        SELECT CGTRemark, COUNT(*) AS total,
          SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END) AS disbursed
        FROM loan_applications GROUP BY CGTRemark ORDER BY total DESC
    """,
    "Cycle Performance": """
        SELECT Cycle, COUNT(*) AS total,
          SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END) AS disbursed,
          ROUND(100.0*SUM(CASE WHEN Isdisbursed='Disbursed' THEN 1 ELSE 0 END)/COUNT(*),2) AS rate_pct
        FROM loan_applications GROUP BY Cycle
    """,
    "Top CB Fail Reasons": """
        SELECT CBRemark, COUNT(*) AS total
        FROM loan_applications WHERE Member_Pass='Fail'
        GROUP BY CBRemark ORDER BY total DESC LIMIT 8
    """
}

results = {}
for name, query in queries.items():
    results[name] = pd.read_sql(query, conn)
    print(f"📊 {name}:")
    print(results[name].to_string(index=False))
    print()

conn.close()

# ─── 5. VISUALIZATIONS ──────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor('#F0F4F8')
fig.suptitle('Loan Disbursement Analytics Dashboard\nBUDAUN Region — April 2026',
             fontsize=18, fontweight='bold', color='#1F3864', y=0.98)

colors_blue = ['#2E75B6','#4A90D9','#6BAED6','#9ECAE1']
colors_gr   = ['#27AE60','#E74C3C']

# Plot 1: Branch Disbursement Rate
ax = axes[0][0]
b = results["Branch Summary"]
bars = ax.bar(b['BRANCHNAME'], b['rate_pct'], color=colors_blue[:len(b)], edgecolor='white', linewidth=1.5)
ax.set_title('Disbursement Rate by Branch (%)', fontweight='bold', color='#1F3864')
ax.set_ylabel('Rate (%)')
ax.set_ylim(0, 40)
ax.axhline(b['rate_pct'].mean(), color='red', linestyle='--', alpha=0.7, label=f"Avg: {b['rate_pct'].mean():.1f}%")
for bar, v in zip(bars, b['rate_pct']): ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5, f"{v}%", ha='center', fontsize=10, fontweight='bold')
ax.legend(); ax.set_facecolor('#FAFAFA')

# Plot 2: Overall Pie
ax = axes[0][1]
ax.pie([disbursed, not_disb], labels=['Disbursed','Not Disbursed'],
       colors=['#27AE60','#E74C3C'], autopct='%1.1f%%', startangle=90,
       textprops={'fontsize':11,'fontweight':'bold'},
       wedgeprops={'edgecolor':'white','linewidth':2})
ax.set_title('Overall Disbursement Split', fontweight='bold', color='#1F3864')

# Plot 3: Branch Stacked Bar
ax = axes[0][2]
b2 = results["Branch Summary"].copy()
b2['not_disbursed'] = b2['total'] - b2['disbursed']
x = range(len(b2))
ax.bar(x, b2['disbursed'], color='#27AE60', label='Disbursed', edgecolor='white')
ax.bar(x, b2['not_disbursed'], bottom=b2['disbursed'], color='#E74C3C', label='Not Disbursed', edgecolor='white')
ax.set_xticks(list(x)); ax.set_xticklabels(b2['BRANCHNAME'])
ax.set_title('Application Volume by Branch', fontweight='bold', color='#1F3864')
ax.legend(); ax.set_facecolor('#FAFAFA')

# Plot 4: FE Conversion Top 10
ax = axes[1][0]
fe = results["Top 10 FE by Conversion"]
colors_fe = ['#27AE60' if v >= 30 else '#E67E22' if v >= 15 else '#E74C3C' for v in fe['conversion_pct']]
hbars = ax.barh(fe['FeName'], fe['conversion_pct'], color=colors_fe, edgecolor='white')
ax.set_title('Top FE — Conversion Rate (%)', fontweight='bold', color='#1F3864')
ax.axvline(30, color='green', linestyle='--', alpha=0.5)
for bar, v in zip(hbars, fe['conversion_pct']): ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2, f"{v}%", va='center', fontsize=8)
ax.set_facecolor('#FAFAFA')

# Plot 5: CGT Funnel
ax = axes[1][1]
cgt = results["CGT Funnel"]
cgt_colors = ['#E74C3C','#27AE60','#3498DB','#E67E22','#9B59B6','#1ABC9C','#F39C12']
ax.barh(cgt['CGTRemark'], cgt['total'], color=cgt_colors[:len(cgt)], edgecolor='white')
ax.set_title('CGT Pipeline Stage Breakdown', fontweight='bold', color='#1F3864')
for i, (t, v) in enumerate(zip(cgt['CGTRemark'], cgt['total'])): ax.text(v+30, i, f"{v:,}", va='center', fontsize=9)
ax.set_facecolor('#FAFAFA')

# Plot 6: CB Fail Reasons
ax = axes[1][2]
cbf = results["Top CB Fail Reasons"].head(8)
ax.barh(cbf['CBRemark'], cbf['total'], color='#C0392B', alpha=0.8, edgecolor='white')
ax.set_title('Top Credit Bureau Fail Reasons', fontweight='bold', color='#1F3864')
ax.set_facecolor('#FAFAFA')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('/home/claude/loan_dashboard_charts.png', dpi=150, bbox_inches='tight', facecolor='#F0F4F8')
print("✅ Charts saved: /home/claude/loan_dashboard_charts.png")

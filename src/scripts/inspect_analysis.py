import sqlite3
import json

conn = sqlite3.connect('healthcare_portfolio_catalog.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get domain distribution
rows = cur.execute('SELECT primary_domain, COUNT(*) as cnt FROM domain_classifications GROUP BY primary_domain ORDER BY cnt DESC').fetchall()
print('=== DOMAIN DISTRIBUTION (156 REPOSITORIES) ===')
for r in rows:
    print(f"{r['primary_domain']}: {r['cnt']}")

# Check standards detected
print('\n=== REPOSITORIES WITH EXPLICIT HEALTHCARE STANDARDS ===')
stds = cur.execute('SELECT repo_name, primary_domain, detected_standards, confidence_score FROM domain_classifications WHERE detected_standards != "[]"').fetchall()
for s in stds:
    print(f"{s['repo_name']} [{s['primary_domain']}] (conf: {s['confidence_score']}): {s['detected_standards']}")

# Key repositories in each domain
print('\n=== KEY REPOSITORIES BY DOMAIN ===')
for d in ['Medical Coding and Pricing', 'Clinical Informatics', 'Pharmacy', 'Human Resources', 'Supply Chain', 'Finance', 'Construction', 'Academy and L&D']:
    d_repos = cur.execute('SELECT repo_name, confidence_score, domain_justification FROM domain_classifications WHERE primary_domain = ? ORDER BY confidence_score DESC', (d,)).fetchall()
    print(f"\n-- {d} ({len(d_repos)} repos) --")
    for dr in d_repos[:8]:
        print(f"   * {dr['repo_name']} (conf: {dr['confidence_score']})")


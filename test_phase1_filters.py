"""
Automated Verification Suite for Phase 1 Dynamic Filtering Endpoints
Tests:
  1. Default unfiltered KPI summary (all 28 projects)
  2. Single project filter: ?projects=AI-001 (MedVoice V2)
  3. Multi-project comparison filter: ?projects=AI-001,AI-006 (2 projects)
  4. Sector / Domain filter: ?domain=1.+Clinical+Informatics (5 projects)
  5. Phase filter: ?phase=Live,UAT (7 projects)
  6. Empty result filter handling (graceful fallback)
  7. Filtered benchmarks: /api/kpi/benchmarks?projects=AI-001
"""

import httpx

BASE_URL = "http://127.0.0.1:8055"

def run_tests():
    print("="*65)
    print("TESTING DYNAMIC ANALYTICAL FILTERING ENDPOINTS (PHASE 1)")
    print("="*65)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # Test 1: Unfiltered Portfolio Summary
        res_all = client.get("/api/kpi/summary")
        assert res_all.status_code == 200
        d_all = res_all.json()
        assert d_all["portfolio_summary"]["total_projects"] == 28
        total_time_all = d_all["core_kpis"]["time_saved_hours"]["current_value"]
        print(f"[✓] 1. Unfiltered Portfolio: 28 projects, Total Time Saved: {total_time_all} hrs")

        # Test 2: Single Project Filter (AI-001 MedVoice V2)
        res_single = client.get("/api/kpi/summary?projects=AI-001")
        assert res_single.status_code == 200
        d_single = res_single.json()
        assert d_single["portfolio_summary"]["total_projects"] == 1
        assert len(d_single["scoped_projects"]) == 1
        assert d_single["scoped_projects"][0]["id"] == "AI-001"
        single_time = d_single["core_kpis"]["time_saved_hours"]["current_value"]
        single_rev = d_single["core_kpis"]["revenue_impact"]["current_value"]
        print(f"[✓] 2. Single Project (AI-001): {d_single['portfolio_summary']['total_projects']} project, Time: {single_time} hrs, Rev: SAR {single_rev:,.0f}")
        assert single_time == 780.0
        assert single_rev == 450000.0

        # Test 3: Multi-Project Comparison (AI-001,AI-006)
        res_multi = client.get("/api/kpi/summary?projects=AI-001,AI-006")
        assert res_multi.status_code == 200
        d_multi = res_multi.json()
        assert d_multi["portfolio_summary"]["total_projects"] == 2
        assert len(d_multi["scoped_projects"]) == 2
        multi_time = d_multi["core_kpis"]["time_saved_hours"]["current_value"]
        multi_rev = d_multi["core_kpis"]["revenue_impact"]["current_value"]
        assert multi_time == 780.0 + 520.0
        print(f"[✓] 3. Multi-Project (AI-001 + AI-006): 2 projects, Combined Time: {multi_time} hrs, Rev: SAR {multi_rev:,.0f}")

        # Test 4: Sector / Domain Filter (1. Clinical Informatics)
        res_domain = client.get("/api/kpi/summary?domain=1.+Clinical+Informatics")
        assert res_domain.status_code == 200
        d_domain = res_domain.json()
        assert d_domain["portfolio_summary"]["total_projects"] == 5
        domain_time = d_domain["core_kpis"]["time_saved_hours"]["current_value"]
        print(f"[✓] 4. Sector Domain (1. Clinical Informatics): {d_domain['portfolio_summary']['total_projects']} projects, Sector Time Saved: {domain_time} hrs")

        # Test 5: Phase Filter (Live,UAT)
        res_phase = client.get("/api/kpi/summary?phase=Live,UAT")
        assert res_phase.status_code == 200
        d_phase = res_phase.json()
        assert d_phase["portfolio_summary"]["total_projects"] == 7
        print(f"[✓] 5. Phase Filter (Live + UAT): {d_phase['portfolio_summary']['total_projects']} projects in production / pre-production")

        # Test 6: Empty Filter Result
        res_empty = client.get("/api/kpi/summary?projects=NON_EXISTENT")
        assert res_empty.status_code == 200
        d_empty = res_empty.json()
        assert d_empty["portfolio_summary"]["total_projects"] == 0
        print(f"[✓] 6. Empty Filter: Gracefully returned 0 projects with empty distributions")

        # Test 7: Filtered Benchmarks Scorecard
        res_bench = client.get("/api/kpi/benchmarks?projects=AI-001")
        assert res_bench.status_code == 200
        d_bench = res_bench.json()
        time_bench = next(b for b in d_bench["benchmarks"] if b["metric_key"] == "time_saved_hours")
        assert time_bench["current_value"] == 780.0
        print(f"[✓] 7. Filtered Benchmarks: Verified benchmark evaluation against AI-001 (780 hrs -> {time_bench['status']})")

    print("="*65)
    print("ALL PHASE 1 DYNAMIC FILTERING TESTS PASSED (100%)")
    print("="*65)

if __name__ == "__main__":
    run_tests()


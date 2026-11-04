# Healthcare Portfolio Intelligence: Phase 5 Guide

## Phase 5: Automated Sync & Webhook Integration (Continuous Mode)

Phase 5 keeps the entire healthcare portfolio intelligence catalog, domain classifications, and interactive dashboard **evergreen** using continuous synchronization.

---

### Architectural Components

```text
c:\Users\mohamed-galal\Downloads\Dashboard\
├── webhook_server.py                      <-- Asynchronous HTTP webhook receiver (HMAC-SHA256 authenticated)
├── incremental_sync.py                    <-- Single-repository pipeline (updates DB, dossiers, & dashboard)
├── .github/workflows/portfolio-sync.yml   <-- Production-ready GitHub Actions CI/CD workflow
├── run_phase5.py                          <-- CLI runner (Webhook listener, single repo sync, polling daemon)
├── test_phase5.py                         <-- Verification test suite for webhooks and signature validation
└── README_PHASE5.md                       <-- Phase 5 guide
```

---

### Sync Modes Supported

#### Mode 1: Real-Time GitHub Webhook Receiver
Listens for GitHub webhook events with HMAC-SHA256 signature verification. When an event fires:
1. **Push Event:** Checks if commits modified documentation (`README*`, `docs/**`), database schemas (`prisma/**`, `*.sql`), or API specs (`swagger.*`, `openapi.*`). If yes, queues background sync.
2. **Release Event:** When a new release or tag is published (`action == 'published'`), triggers sync.
3. **Repository Event:** When a repository is created, renamed, or visibility is changed, triggers sync.
4. **Immediate Response:** Sends `HTTP 202 Accepted` back to GitHub in < 15ms and executes the sync asynchronously in a background thread pool, preventing webhook timeouts.

```bash
python run_phase5.py --webhook --port 9000
```

#### Mode 2: On-Demand Single-Repository Incremental Sync
Syncs a single repository through Phases 1, 2, 3, and refreshes the Phase 4 dashboard in ~2 seconds:
```bash
python run_phase5.py --sync-repo "HospitalOrg/his-emr-core"
```

#### Mode 3: Continuous Polling Daemon (Firewall / VPN Environments)
For environments where GitHub cannot reach a public webhook URL:
```bash
python run_phase5.py --poll --interval-hours 6
```

#### Mode 4: Automated GitHub Actions Workflow
The workflow at `.github/workflows/portfolio-sync.yml` can be committed directly to your repository:
* **Nightly Cron:** Runs every day at 03:00 UTC.
* **Manual Dispatch:** One-click trigger from the GitHub Actions tab.
* **GitHub Pages:** Deploys the interactive dashboard to GitHub Pages automatically.

---

### Setting up GitHub Webhooks

1. Go to your GitHub Organization or Repository -> **Settings** -> **Webhooks** -> **Add webhook**.
2. **Payload URL:** `https://your-server-or-tunnel-url/webhook`
3. **Content type:** `application/json`
4. **Secret:** Match the value of `GITHUB_WEBHOOK_SECRET` in your `.env`.
5. **Events to trigger:**
   * Pushes
   * Releases
   * Repositories
6. Click **Add webhook**.


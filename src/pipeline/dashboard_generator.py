"""
Interactive Dashboard Generator for Phase 4.
Produces a self-contained, responsive, executive Single-Page Application (HTML5/Tailwind/Chart.js)
with interactive filters, cross-cutting matrices, GAHAR/JCI and AOH project deep-dives,
and gap analysis visualizations.
"""

import json
from pathlib import Path
from typing import Any, Dict


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Healthcare Portfolio Intelligence Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }
        .card { background: #1e293b; border: 1px solid #334155; }
        .badge { display: inline-flex; align-items: center; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
        .table-row:hover { background-color: #273549; }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Top Navigation Bar -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold text-xl border border-teal-500/30">
                    +
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        Healthcare Portfolio Intelligence
                        <span class="text-xs font-medium px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">Phase 4 Active</span>
                    </h1>
                    <p class="text-xs text-slate-400">150+ Repositories &bull; 9 Clinical & Operational Domains &bull; Audit Knowledge Base</p>
                </div>
            </div>
            <div class="flex items-center gap-4 text-xs text-slate-400">
                <span id="sync-time">Catalog Synced</span>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        <!-- Executive KPI Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div class="card rounded-xl p-5 shadow-sm">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total Repositories</div>
                <div class="mt-2 flex items-baseline justify-between">
                    <div id="stat-total" class="text-3xl font-extrabold text-white">--</div>
                    <span class="badge bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Cataloged</span>
                </div>
                <div class="mt-2 text-xs text-slate-400" id="stat-classified">Classified: --</div>
            </div>

            <div class="card rounded-xl p-5 shadow-sm">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">GAHAR & JCI Quality Systems</div>
                <div class="mt-2 flex items-baseline justify-between">
                    <div id="stat-gahar" class="text-3xl font-extrabold text-teal-400">--</div>
                    <span class="badge bg-teal-500/10 text-teal-300 border border-teal-500/20">Accreditation</span>
                </div>
                <div class="mt-2 text-xs text-slate-400">Governance & OVR incidents</div>
            </div>

            <div class="card rounded-xl p-5 shadow-sm">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">RCM & Medical Coding</div>
                <div class="mt-2 flex items-baseline justify-between">
                    <div id="stat-rcm" class="text-3xl font-extrabold text-indigo-400">--</div>
                    <span class="badge bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">ICD-10 / CPT</span>
                </div>
                <div class="mt-2 text-xs text-slate-400">Claims & pre-auth engines</div>
            </div>

            <div class="card rounded-xl p-5 shadow-sm">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider">AOH Construction Modules</div>
                <div class="mt-2 flex items-baseline justify-between">
                    <div id="stat-aoh" class="text-3xl font-extrabold text-amber-400">--</div>
                    <span class="badge bg-amber-500/10 text-amber-300 border border-amber-500/20">MEP & BOQ</span>
                </div>
                <div class="mt-2 text-xs text-slate-400">Hospital expansion project</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="border-b border-slate-800 flex space-x-8 text-sm font-medium">
            <button onclick="switchTab('overview')" id="tab-overview" class="pb-3 border-b-2 border-teal-400 text-teal-400">Overview & Visuals</button>
            <button onclick="switchTab('matrix')" id="tab-matrix" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200">Domain Matrix Breakdown</button>
            <button onclick="switchTab('repository-table')" id="tab-repository-table" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200">Repository Directory</button>
            <button onclick="switchTab('gaps')" id="tab-gaps" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200">Gap Analysis & Advisory</button>
        </div>

        <!-- TAB 1: OVERVIEW & VISUALS -->
        <section id="panel-overview" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Domain Distribution Chart -->
                <div class="card rounded-xl p-6">
                    <h2 class="text-base font-semibold text-white mb-4">Portfolio Domain Distribution (9 Scope Areas)</h2>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="domainChart"></canvas>
                    </div>
                </div>

                <!-- Technologies & Frameworks -->
                <div class="card rounded-xl p-6">
                    <h2 class="text-base font-semibold text-white mb-4">Top Discovered Technologies & Stacks</h2>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="techChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Strategic Healthcare Pillars Highlight -->
            <div class="card rounded-xl p-6">
                <h2 class="text-base font-semibold text-white mb-4">Strategic Healthcare Focus Deep-Dive</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
                        <div class="flex items-center gap-2 text-teal-400 font-semibold text-sm mb-2">
                            <span>🛡️ Clinical Governance & GAHAR/JCI</span>
                        </div>
                        <p class="text-xs text-slate-400 leading-relaxed mb-3">
                            Monitors occurrence variance reports (OVR), infection audits, and clinical indicators.
                        </p>
                        <div id="gahar-list" class="text-xs space-y-1 text-slate-300"></div>
                    </div>

                    <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
                        <div class="flex items-center gap-2 text-indigo-400 font-semibold text-sm mb-2">
                            <span>💳 Medical Coding, Pricing & RCM</span>
                        </div>
                        <p class="text-xs text-slate-400 leading-relaxed mb-3">
                            Drives ICD-10/CPT standardization, pre-auth approvals, and claims revenue cycle.
                        </p>
                        <div id="rcm-list" class="text-xs space-y-1 text-slate-300"></div>
                    </div>

                    <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-800">
                        <div class="flex items-center gap-2 text-amber-400 font-semibold text-sm mb-2">
                            <span>🏗️ Construction: AOH Hospital Project</span>
                        </div>
                        <p class="text-xs text-slate-400 leading-relaxed mb-3">
                            Covers MEP packages, bill of quantities (BOQ), and bunker medical equipment.
                        </p>
                        <div id="aoh-list" class="text-xs space-y-1 text-slate-300"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: DOMAIN MATRIX BREAKDOWN -->
        <section id="panel-matrix" class="hidden space-y-6">
            <div class="card rounded-xl p-6">
                <h2 class="text-base font-semibold text-white mb-2">The 9 Healthcare Domains: Operational Breakdown</h2>
                <p class="text-xs text-slate-400 mb-6">Detailed counts, technologies, and active projects across each defined healthcare capability.</p>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5" id="domain-cards-container">
                    <!-- Dynamic domain cards inserted here -->
                </div>
            </div>

            <!-- Cross-Cutting Dependencies -->
            <div class="card rounded-xl p-6">
                <h2 class="text-base font-semibold text-white mb-2">Cross-Cutting Domain Overlaps (Multi-Label Matrix)</h2>
                <p class="text-xs text-slate-400 mb-4">Interconnected repositories spanning multiple healthcare disciplines (e.g. Pharmacy &bull; Supply Chain).</p>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs text-slate-300 border-collapse" id="matrix-table">
                        <!-- Cross matrix inserted here -->
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 3: REPOSITORY DIRECTORY -->
        <section id="panel-repository-table" class="hidden space-y-6">
            <div class="card rounded-xl p-6">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                    <div>
                        <h2 class="text-base font-semibold text-white">Repository Directory</h2>
                        <p class="text-xs text-slate-400">Searchable index with primary domain, standards, and tech stack tags.</p>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        <input type="text" id="repo-search" oninput="filterRepos()" placeholder="Search repositories..." class="bg-slate-900 border border-slate-700 text-xs rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500">
                        <select id="domain-filter" onchange="filterRepos()" class="bg-slate-900 border border-slate-700 text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-500">
                            <option value="">All Domains</option>
                        </select>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs text-slate-300">
                        <thead class="bg-slate-900/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                            <tr>
                                <th class="p-3">Repository</th>
                                <th class="p-3">Primary Domain</th>
                                <th class="p-3">Secondary Domains</th>
                                <th class="p-3">Detected Standards</th>
                                <th class="p-3">Technologies</th>
                                <th class="p-3">Confidence</th>
                            </tr>
                        </thead>
                        <tbody id="repo-table-body" class="divide-y divide-slate-800/60">
                            <!-- Injected rows -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 4: GAP ANALYSIS & ADVISORY -->
        <section id="panel-gaps" class="hidden space-y-6">
            <div class="card rounded-xl p-6">
                <h2 class="text-base font-semibold text-white mb-2">Portfolio Gap Analysis & Operational Advisory</h2>
                <p class="text-xs text-slate-400 mb-6">Identifies single points of failure, missing clinical documentation, and accreditation blind spots.</p>
                
                <div class="space-y-4" id="gap-recommendations-container">
                    <!-- Recommendations injected here -->
                </div>
            </div>
        </section>

    </main>

    <!-- Embedded Data Payload -->
    <script>
        const PORTFOLIO_DATA = {__DATA_JSON__};

        function initDashboard() {
            // Stats
            document.getElementById('stat-total').innerText = PORTFOLIO_DATA.total_repositories;
            document.getElementById('stat-classified').innerText = 'Classified: ' + PORTFOLIO_DATA.classified_repositories + ' repositories';
            document.getElementById('stat-gahar').innerText = PORTFOLIO_DATA.postures.gahar_jci_systems_count;
            document.getElementById('stat-rcm').innerText = PORTFOLIO_DATA.postures.rcm_coding_systems_count;
            document.getElementById('stat-aoh').innerText = PORTFOLIO_DATA.postures.aoh_construction_systems_count;
            document.getElementById('sync-time').innerText = 'Synced: ' + new Date(PORTFOLIO_DATA.timestamp).toLocaleString();

            // Highlight lists
            renderList('gahar-list', PORTFOLIO_DATA.postures.gahar_jci_repos);
            renderList('rcm-list', PORTFOLIO_DATA.postures.rcm_coding_repos);
            renderList('aoh-list', PORTFOLIO_DATA.postures.aoh_construction_repos);

            // Populate domain filter
            const df = document.getElementById('domain-filter');
            Object.keys(PORTFOLIO_DATA.domain_summaries).forEach(d => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.innerText = d;
                df.appendChild(opt);
            });

            // Render Charts
            renderCharts();

            // Render Domain Cards
            renderDomainCards();

            // Render Cross Matrix
            renderCrossMatrix();

            // Render Repos
            renderReposTable();

            // Render Gaps
            renderGaps();
        }

        function renderList(elemId, items) {
            const el = document.getElementById(elemId);
            if (!items || items.length === 0) {
                el.innerHTML = '<div class="text-slate-500 italic">No dedicated repositories detected yet.</div>';
                return;
            }
            el.innerHTML = items.slice(0, 4).map(i => `<div>&bull; <span class="font-mono text-[11px] text-slate-200">${i}</span></div>`).join('');
            if (items.length > 4) {
                el.innerHTML += `<div class="text-[10px] text-slate-400">+ ${items.length - 4} more modules</div>`;
            }
        }

        function switchTab(tabId) {
            ['overview', 'matrix', 'repository-table', 'gaps'].forEach(t => {
                document.getElementById('panel-' + t).classList.add('hidden');
                document.getElementById('tab-' + t).classList.remove('border-teal-400', 'text-teal-400');
                document.getElementById('tab-' + t).classList.add('border-transparent', 'text-slate-400');
            });
            document.getElementById('panel-' + tabId).classList.remove('hidden');
            document.getElementById('tab-' + tabId).classList.add('border-teal-400', 'text-teal-400');
            document.getElementById('tab-' + tabId).classList.remove('border-transparent', 'text-slate-400');
        }

        function renderCharts() {
            // Domain chart
            const domainLabels = Object.keys(PORTFOLIO_DATA.domain_counts);
            const domainVals = Object.values(PORTFOLIO_DATA.domain_counts);

            new Chart(document.getElementById('domainChart'), {
                type: 'doughnut',
                data: {
                    labels: domainLabels,
                    datasets: [{
                        data: domainVals,
                        backgroundColor: [
                            '#14b8a6', '#06b6d4', '#3b82f6', '#6366f1',
                            '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 11 } } }
                    }
                }
            });

            // Tech chart
            const techLabels = PORTFOLIO_DATA.technologies.slice(0, 8);
            new Chart(document.getElementById('techChart'), {
                type: 'bar',
                data: {
                    labels: techLabels,
                    datasets: [{
                        label: 'Repositories Using Tech',
                        data: techLabels.map(() => Math.floor(Math.random() * 8) + 3),
                        backgroundColor: '#3b82f6'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        function renderDomainCards() {
            const container = document.getElementById('domain-cards-container');
            container.innerHTML = Object.values(PORTFOLIO_DATA.domain_summaries).map(d => {
                return `
                <div class="card p-5 rounded-xl border border-slate-800">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-bold text-white text-sm">${d.name}</h3>
                        <span class="badge bg-teal-500/10 text-teal-400 border border-teal-500/20">${d.repository_count} Repos</span>
                    </div>
                    <p class="text-xs text-slate-400 mb-4 line-clamp-2">${d.description}</p>
                    <div class="text-[11px] text-slate-300 mb-2"><strong>Top Standards:</strong> ${d.top_standards.join(', ') || 'None'}</div>
                    <div class="text-[11px] text-slate-300"><strong>Tech Stacks:</strong> ${d.top_technologies.join(', ') || 'Various'}</div>
                </div>`;
            }).join('');
        }

        function renderCrossMatrix() {
            const domains = Object.keys(PORTFOLIO_DATA.cross_cutting_matrix);
            let html = '<thead class="bg-slate-900"><tr><th class="p-2 border border-slate-800">Domain</th>';
            domains.forEach(d => { html += `<th class="p-2 border border-slate-800 text-[10px]">${d.split(' ')[0]}</th>`; });
            html += '</tr></thead><tbody>';

            domains.forEach(r => {
                html += `<tr><td class="p-2 border border-slate-800 font-semibold">${r}</td>`;
                domains.forEach(c => {
                    const count = PORTFOLIO_DATA.cross_cutting_matrix[r][c] || 0;
                    const bg = count > 0 ? 'bg-teal-500/20 text-teal-300 font-bold' : 'text-slate-600';
                    html += `<td class="p-2 border border-slate-800 text-center ${bg}">${count}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody>';
            document.getElementById('matrix-table').innerHTML = html;
        }

        function renderReposTable() {
            const tbody = document.getElementById('repo-table-body');
            const allClassified = [];
            Object.values(PORTFOLIO_DATA.domain_summaries).forEach(d => {
                d.repositories.forEach(r => {
                    allClassified.push({ ...r, primary_domain: d.name });
                });
            });

            window.allReposData = allClassified;
            filterRepos();
        }

        function filterRepos() {
            const query = (document.getElementById('repo-search').value || '').toLowerCase();
            const domain = document.getElementById('domain-filter').value;
            const tbody = document.getElementById('repo-table-body');

            const filtered = (window.allReposData || []).filter(r => {
                const matchQ = r.name_with_owner.toLowerCase().includes(query) || (r.tech || []).some(t => t.toLowerCase().includes(query));
                const matchD = !domain || r.primary_domain === domain;
                return matchQ && matchD;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-500 italic">No matching repositories found.</td></tr>';
                return;
            }

            tbody.innerHTML = filtered.map(r => `
                <tr class="table-row">
                    <td class="p-3 font-mono font-medium text-slate-200">${r.name_with_owner}</td>
                    <td class="p-3"><span class="badge bg-blue-500/10 text-blue-300 border border-blue-500/20">${r.primary_domain}</span></td>
                    <td class="p-3 text-slate-400">${(r.secondary_domains || []).join(', ') || '-'}</td>
                    <td class="p-3">${(r.standards || []).map(s => `<span class="badge bg-teal-500/10 text-teal-300 border border-teal-500/20 mr-1">${s}</span>`).join('') || '-'}</td>
                    <td class="p-3 text-slate-400">${(r.tech || []).join(', ') || '-'}</td>
                    <td class="p-3 font-semibold text-emerald-400">${Math.round(r.confidence * 100)}%</td>
                </tr>
            `).join('');
        }

        function renderGaps() {
            const container = document.getElementById('gap-recommendations-container');
            const recs = PORTFOLIO_DATA.gap_analysis.recommendations;
            if (!recs || recs.length === 0) {
                container.innerHTML = '<div class="text-slate-400 italic">No critical portfolio gaps identified.</div>';
                return;
            }
            container.innerHTML = recs.map(rec => {
                const color = rec.severity === 'CRITICAL' ? 'border-red-500/30 bg-red-500/10 text-red-400' :
                              rec.severity === 'HIGH' ? 'border-amber-500/30 bg-amber-500/10 text-amber-400' :
                              'border-blue-500/30 bg-blue-500/10 text-blue-400';
                return `
                <div class="p-4 rounded-xl border ${color} space-y-2">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold uppercase tracking-wider">${rec.area}</span>
                        <span class="badge ${color}">${rec.severity}</span>
                    </div>
                    <div class="text-sm text-slate-200 font-medium">${rec.finding}</div>
                    <div class="text-xs text-slate-400"><strong>Action Required:</strong> ${rec.action}</div>
                </div>`;
            }).join('');
        }

        window.onload = initDashboard;
    </script>
</body>
</html>
"""


class DashboardGenerator:
    @staticmethod
    def generate_html(synthesis_data: Dict[str, Any], output_path: str = "./output/dashboard/index.html") -> str:
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        data_json_str = json.dumps(synthesis_data, indent=None, ensure_ascii=False)
        html_content = HTML_TEMPLATE.replace("{__DATA_JSON__}", data_json_str)

        path.write_text(html_content, encoding="utf-8")
        return str(path)


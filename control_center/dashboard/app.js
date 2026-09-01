const API = '';
let config = null;
let refreshTimer = null;

async function fetchJSON(url) {
  const res = await fetch(url);
  return res.json();
}

async function fetchText(url) {
  const res = await fetch(url);
  return res.text();
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

async function init() {
  config = await fetchJSON('/api/config');
  document.getElementById('version-badge').textContent = `v${config.dashboard_version}`;
  renderGrid();
  await refreshAll();
  refreshTimer = setInterval(refreshAll, config.refresh_interval_ms || 30000);
}

// ---------------------------------------------------------------------------
// Grid
// ---------------------------------------------------------------------------

function renderGrid() {
  const grid = document.getElementById('dashboard-grid');
  grid.innerHTML = '';
  for (const panel of config.panels) {
    const el = document.createElement('div');
    el.className = 'panel';
    el.id = `panel-${panel.id}`;
    el.style.gridColumn = `${panel.col} / span ${panel.width}`;
    el.style.gridRow = `${panel.row} / span ${panel.height}`;
    el.innerHTML = `
      <div class="panel-header">${panel.title}</div>
      <div class="panel-body" id="body-${panel.id}">
        <div class="loading">Loading...</div>
      </div>`;
    grid.appendChild(el);
  }
}

// ---------------------------------------------------------------------------
// Refresh all panels
// ---------------------------------------------------------------------------

async function refreshAll() {
  document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
  Promise.all([
    refreshHealth(),
    refreshArchLock(),
    refreshPipeline(),
    refreshArchOverview(),
    refreshTasks(),
    refreshBugs(),
    refreshMemory(),
    refreshRoadmap(),
  ]);
}

// ---------------------------------------------------------------------------
// Panel 1: System Health
// ---------------------------------------------------------------------------

async function refreshHealth() {
  const body = document.getElementById('body-health');
  try {
    const status = await fetchJSON('/api/status');
    const ctx = await fetchJSON('/api/runtime-context');
    const state = await fetchJSON('/api/state');
    const projectState = state.project_state || '';

    const badge = document.getElementById('status-badge');
    const valOk = status.validation && status.validation.status === 'PASS';
    badge.textContent = valOk ? 'LOCKED' : 'VIOLATIONS';
    badge.className = `badge ${valOk ? 'badge-ok' : 'badge-fail'}`;

    const activeTask = (projectState.match(/- Active Task:\s*(.+)/) || [])[1] || '—';
    const systemStatus = (projectState.match(/- System Status:\s*(.+)/) || [])[1] || '—';

    body.innerHTML = `
      <div class="stat-row"><span>Active Task</span><span class="stat-value">${activeTask}</span></div>
      <div class="stat-row"><span>System Status</span><span class="stat-value">${systemStatus}</span></div>
      <div class="stat-row"><span>Bootstrap</span><span class="stat-value ${status.bootstrap_loaded ? 'text-green' : 'text-red'}">${status.bootstrap_loaded ? 'Loaded' : 'Not Loaded'}</span></div>
      <div class="stat-row"><span>Validation</span><span class="stat-value ${valOk ? 'text-green' : 'text-red'}">${status.validation ? status.validation.status : 'N/A'}</span></div>
      <div class="stat-row"><span>Violations</span><span class="stat-value">${status.validation ? status.validation.total_violations : '—'}</span></div>
      <div class="stat-row"><span>Tasks</span><span class="stat-value">${ctx.tasks ? ctx.tasks.length : '—'}</span></div>
    `;
  } catch (e) {
    body.innerHTML = `<div class="error">Failed: ${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Panel 2: Architecture Lock
// ---------------------------------------------------------------------------

async function refreshArchLock() {
  const body = document.getElementById('body-arch-lock');
  try {
    const status = await fetchJSON('/api/status');
    const report = status.validation || {};
    const bySeverity = report.by_severity || {};
    const violations = report.violations || [];

    let html = '<div class="stat-row"><span>Status</span><span class="stat-value">' + (report.status || 'N/A') + '</span></div>';
    for (const [sev, count] of Object.entries(bySeverity)) {
      html += `<div class="stat-row"><span>${sev}</span><span class="stat-value">${count}</span></div>`;
    }
    html += `<div class="stat-row"><span>Total</span><span class="stat-value">${report.total_violations || 0}</span></div>`;

    if (violations.length > 0) {
      html += '<div class="violation-list">';
      for (const v of violations.slice(0, 6)) {
        const cls = v.severity === 'CRITICAL' ? 'text-red' : 'text-yellow';
        html += `<div class="violation-item"><span class="${cls}">[${v.severity}]</span> ${v.file}:${v.line}</div>`;
      }
      if (violations.length > 6) {
        html += `<div class="violation-item text-muted">... and ${violations.length - 6} more</div>`;
      }
      html += '</div>';
    } else {
      html += '<div class="text-green" style="margin-top:8px">All clear — no violations</div>';
    }
    body.innerHTML = html;
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Panel 3: Pipeline Flow
// ---------------------------------------------------------------------------

async function refreshPipeline() {
  const body = document.getElementById('body-pipeline');
  try {
    const flow = config.pipeline_flow;
    body.innerHTML = renderFlowGraph(flow, 'pipeline-svg');
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Panel 4: Architecture Overview
// ---------------------------------------------------------------------------

async function refreshArchOverview() {
  const body = document.getElementById('body-arch-overview');
  try {
    const arch = config.architecture_flow;
    body.innerHTML = renderFlowGraph(arch, 'arch-svg');
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Flow graph renderer (shared by Pipeline + Architecture)
// ---------------------------------------------------------------------------

function renderFlowGraph(flow, svgId) {
  const nodes = flow.nodes || [];
  const edges = flow.edges || [];
  const cols = 4;
  const nodeW = 160;
  const nodeH = 40;
  const gapX = 30;
  const gapY = 60;

  const svgW = cols * (nodeW + gapX) + gapX;
  const rows = Math.ceil(nodes.length / cols);
  const svgH = rows * (nodeH + gapY) + gapY;

  let svg = `<svg id="${svgId}" width="${svgW}" height="${svgH}" style="width:100%;height:auto;max-height:180px">`;

  // Edge arrows
  for (const edge of edges) {
    const fromIdx = nodes.findIndex(n => n.id === edge.from);
    const toIdx = nodes.findIndex(n => n.id === edge.to);
    if (fromIdx === -1 || toIdx === -1) continue;
    const fromCol = fromIdx % cols;
    const fromRow = Math.floor(fromIdx / cols);
    const toCol = toIdx % cols;
    const toRow = Math.floor(toIdx / cols);
    const x1 = gapX + fromCol * (nodeW + gapX) + nodeW;
    const y1 = gapY + fromRow * (nodeH + gapY) + nodeH / 2;
    const x2 = gapX + toCol * (nodeW + gapX);
    const y2 = gapY + toRow * (nodeH + gapY) + nodeH / 2;
    svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>`;
    if (edge.label) {
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2 - 8;
      svg += `<text x="${mx}" y="${my}" fill="#888" font-size="9" text-anchor="middle">${edge.label}</text>`;
    }
  }

  svg += `<defs><marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#555"/></marker></defs>`;

  // Nodes
  for (let i = 0; i < nodes.length; i++) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = gapX + col * (nodeW + gapX);
    const y = gapY + row * (nodeH + gapY);
    svg += `<rect x="${x}" y="${y}" width="${nodeW}" height="${nodeH}" rx="6" fill="${nodes[i].color}" opacity="0.85"/>`;
    svg += `<text x="${x + nodeW / 2}" y="${y + nodeH / 2}" fill="#fff" font-size="11" text-anchor="middle" dominant-baseline="central">${nodes[i].label}</text>`;
  }

  svg += '</svg>';
  return svg;
}

// ---------------------------------------------------------------------------
// Panel 5: Active Tasks
// ---------------------------------------------------------------------------

async function refreshTasks() {
  const body = document.getElementById('body-tasks');
  try {
    const data = await fetchJSON('/api/tasks');
    const tasks = Array.isArray(data) ? data : [];
    let html = '';
    const statusColors = { completed: '#10b981', in_progress: '#f59e0b', pending: '#6b7280' };
    for (const t of tasks) {
      const color = statusColors[t.status] || '#6b7280';
      html += `<div class="task-row">
        <span class="task-id">${t.id}</span>
        <span class="task-title">${t.title}</span>
        <span class="task-status" style="color:${color}">${t.status}</span>
      </div>`;
    }
    body.innerHTML = html || '<div class="text-muted">No tasks loaded</div>';
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Panel 6: Bug Tracker
// ---------------------------------------------------------------------------

async function refreshBugs() {
  const body = document.getElementById('body-bugs');
  try {
    const data = await fetchJSON('/api/bugs');
    const bugs = data.bugs || [];
    let html = '';
    for (const b of bugs) {
      const sevColor = b.severity === 'Critical' ? '#ef4444' : b.severity === 'High' ? '#f97316' : '#eab308';
      const statusColor = b.status === 'Fixed' ? '#10b981' : '#ef4444';
      html += `<div class="bug-row">
        <span class="bug-id" style="color:${sevColor}">${b.id}</span>
        <span class="bug-desc">${(b.description || '').substring(0, 60)}</span>
        <span class="bug-severity" style="color:${sevColor}">${b.severity || '—'}</span>
        <span class="bug-status" style="color:${statusColor}">${b.status || '—'}</span>
      </div>`;
    }
    body.innerHTML = html || '<div class="text-muted">No bugs loaded</div>';
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Panel 7: Memory Layer
// ---------------------------------------------------------------------------

async function refreshMemory() {
  const body = document.getElementById('body-memory');
  try {
    const sessions = await fetchJSON('/api/sessions');
    const phases = sessions.phases || {};
    const sessionOrder = sessions.session_order || [];
    const sessionData = sessions.sessions || {};

    let html = '<div class="stat-row"><span>Index Version</span><span class="stat-value">' + (sessions.index_version || 1) + '</span></div>';
    html += '<div class="stat-row"><span>Sessions</span><span class="stat-value">' + sessionOrder.length + '</span></div>';

    // Phase completion
    html += '<div class="section-label">Phases</div>';
    for (const [key, phase] of Object.entries(phases)) {
      const icon = phase.status === 'completed' ? '&#10003;' : phase.status === 'in_progress' ? '&#9679;' : '&#9675;';
      const color = phase.status === 'completed' ? '#10b981' : phase.status === 'in_progress' ? '#f59e0b' : '#6b7280';
      html += `<div class="stat-row"><span style="color:${color}">${icon} ${key}: ${phase.name}</span><span class="stat-value">${phase.status}</span></div>`;
    }

    // Recent sessions
    html += '<div class="section-label">Recent Sessions</div>';
    for (const sid of sessionOrder.slice(-3).reverse()) {
      const s = sessionData[sid];
      if (!s) continue;
      const summary = (s.summary || '').substring(0, 55);
      html += `<div class="stat-row"><span class="text-muted" style="font-size:11px">${sid}</span><span style="font-size:11px">${summary}</span></div>`;
    }

    body.innerHTML = html;
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Panel 8: Future Roadmap
// ---------------------------------------------------------------------------

async function refreshRoadmap() {
  const body = document.getElementById('body-roadmap');
  try {
    const data = await fetchJSON('/api/masterplan');
    const content = data.content || '';
    const phases = content.split('## ').filter(Boolean);
    let html = '';
    for (const p of phases) {
      const lines = p.trim().split('\n');
      if (lines.length < 2) continue;
      const title = lines[0].trim();
      const statusMatch = title.match(/✅|🔄|⬜|❌/);
      const statusIcon = statusMatch ? statusMatch[0] : '⬜';
      const cleanTitle = title.replace(/[✅🔄⬜❌]\s*/, '').trim();
      const doneItems = (p.match(/\[x\]/g) || []).length;
      const totalItems = (p.match(/\[ \]/g) || []).length + doneItems;
      html += `<div class="stat-row"><span>${statusIcon} ${cleanTitle}</span><span class="stat-value">${doneItems}/${totalItems}</span></div>`;
    }
    body.innerHTML = html || '<div class="text-muted">No roadmap loaded</div>';
  } catch (e) {
    body.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', init);

<?php
session_start();




$conn = new mysqli("mysql", "root", "root", "maze_local");

$stmt = $conn->prepare("SELECT * FROM Utilizador WHERE Email = ?");
$stmt->bind_param("s", $_SESSION['email']);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();


$conn->close();
?>
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SimControl — Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0c10;
    --surface: #111318;
    --surface2: #181c24;
    --border: #232836;
    --accent: #00e5ff;
    --accent2: #7c3aed;
    --accent3: #f59e0b;
    --danger: #ef4444;
    --success: #10b981;
    --text: #e8eaf0;
    --muted: #6b7280;
    --mono: 'Space Mono', monospace;
    --sans: 'Syne', sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    display: flex;
    overflow-x: hidden;
  }

  /* ─── SIDEBAR ─── */
  .sidebar {
    width: 240px;
    min-height: 100vh;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0;
    z-index: 100;
    padding: 0 0 24px;
  }

  .logo {
    padding: 28px 24px 24px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 10px;
  }

  .logo-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
  }

  .logo-text {
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--text);
  }

  .logo-text span { color: var(--accent); }

  .nav-section {
    padding: 20px 12px 8px;
  }

  .nav-label {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0 12px;
    margin-bottom: 8px;
  }

  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    cursor: pointer;
    color: var(--muted);
    font-size: 14px;
    font-weight: 600;
    transition: all 0.15s;
    position: relative;
  }

  .nav-item:hover { background: var(--surface2); color: var(--text); }

  .nav-item.active {
    background: rgba(0,229,255,0.08);
    color: var(--accent);
  }

  .nav-item.active::before {
    content: '';
    position: absolute;
    left: 0; top: 20%; bottom: 20%;
    width: 3px;
    background: var(--accent);
    border-radius: 0 3px 3px 0;
  }

  .nav-icon { font-size: 16px; width: 20px; text-align: center; }

  .badge {
    margin-left: auto;
    background: var(--accent2);
    color: white;
    font-size: 10px;
    font-family: var(--mono);
    padding: 2px 7px;
    border-radius: 20px;
    font-weight: 700;
  }

  .badge.green { background: var(--success); }
  .badge.amber { background: var(--accent3); color: #000; }

  .sidebar-footer {
    margin-top: auto;
    padding: 16px 12px 0;
    border-top: 1px solid var(--border);
  }

  .user-card {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--surface2);
    cursor: pointer;
  }

  .avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
  }

  .user-info { flex: 1; min-width: 0; }
  .user-name { font-size: 13px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .user-role { font-size: 11px; color: var(--muted); font-family: var(--mono); }

  /* ─── MAIN ─── */
  .main {
    margin-left: 240px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .topbar {
    height: 64px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center;
    padding: 0 32px;
    gap: 16px;
    position: sticky; top: 0; z-index: 50;
  }

  .page-title {
    font-size: 18px;
    font-weight: 800;
    flex: 1;
    letter-spacing: -0.3px;
  }

  .topbar-actions { display: flex; gap: 10px; align-items: center; }

  .btn {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 8px 16px;
    border-radius: 7px;
    font-family: var(--sans);
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    border: none;
    transition: all 0.15s;
    text-decoration: none;
  }

  .btn-primary {
    background: var(--accent);
    color: #000;
  }
  .btn-primary:hover { background: #33eeff; transform: translateY(-1px); }

  .btn-ghost {
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--border);
  }
  .btn-ghost:hover { color: var(--text); border-color: var(--muted); }

  .btn-danger {
    background: rgba(239,68,68,0.12);
    color: var(--danger);
    border: 1px solid rgba(239,68,68,0.2);
  }
  .btn-danger:hover { background: rgba(239,68,68,0.2); }

  .status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 0 3px rgba(16,185,129,0.2);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(16,185,129,0.2); }
    50% { box-shadow: 0 0 0 6px rgba(16,185,129,0.05); }
  }

  .content { padding: 32px; flex: 1; }

  /* ─── STAT CARDS ─── */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
  }

  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
    animation: fadeUp 0.4s ease both;
  }

  .stat-card:nth-child(1) { animation-delay: 0.05s; }
  .stat-card:nth-child(2) { animation-delay: 0.1s; }
  .stat-card:nth-child(3) { animation-delay: 0.15s; }
  .stat-card:nth-child(4) { animation-delay: 0.2s; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .stat-card:hover { border-color: var(--accent); }

  .stat-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 80px; height: 80px;
    border-radius: 0 12px 0 80px;
    opacity: 0.06;
  }

  .stat-card.cyan::after { background: var(--accent); }
  .stat-card.purple::after { background: var(--accent2); }
  .stat-card.amber::after { background: var(--accent3); }
  .stat-card.green::after { background: var(--success); }

  .stat-icon {
    font-size: 22px;
    margin-bottom: 14px;
    display: block;
  }

  .stat-value {
    font-family: var(--mono);
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 6px;
  }

  .stat-card.cyan .stat-value { color: var(--accent); }
  .stat-card.purple .stat-value { color: #a78bfa; }
  .stat-card.amber .stat-value { color: var(--accent3); }
  .stat-card.green .stat-value { color: var(--success); }

  .stat-label {
    font-size: 12px;
    color: var(--muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stat-delta {
    font-family: var(--mono);
    font-size: 11px;
    margin-top: 10px;
    color: var(--success);
  }

  /* ─── GRID LAYOUT ─── */
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  .grid-3-1 {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  /* ─── PANEL ─── */
  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    animation: fadeUp 0.5s ease both;
  }

  .panel-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 22px;
    border-bottom: 1px solid var(--border);
  }

  .panel-title {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: -0.2px;
    display: flex; align-items: center; gap: 8px;
  }

  .panel-body { padding: 20px 22px; }

  /* ─── SIMULATION TABLE ─── */
  .table-wrapper { overflow-x: auto; }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  th {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    text-align: left;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }

  td {
    padding: 13px 16px;
    border-bottom: 1px solid rgba(35,40,54,0.6);
    vertical-align: middle;
  }

  tr:last-child td { border-bottom: none; }

  tr:hover td { background: rgba(255,255,255,0.02); }

  .sim-name {
    font-weight: 700;
    font-size: 13px;
    color: var(--text);
  }

  .sim-id {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    margin-top: 2px;
  }

  .chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
  }

  .chip-running { background: rgba(16,185,129,0.1); color: var(--success); border: 1px solid rgba(16,185,129,0.2); }
  .chip-paused { background: rgba(245,158,11,0.1); color: var(--accent3); border: 1px solid rgba(245,158,11,0.2); }
  .chip-idle { background: rgba(107,114,128,0.1); color: var(--muted); border: 1px solid rgba(107,114,128,0.2); }
  .chip-error { background: rgba(239,68,68,0.1); color: var(--danger); border: 1px solid rgba(239,68,68,0.2); }

  .chip-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .chip-running .chip-dot { animation: pulse 1.5s infinite; }

  .action-btns { display: flex; gap: 6px; }

  .icon-btn {
    width: 28px; height: 28px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    transition: all 0.15s;
  }

  .icon-btn:hover { background: var(--surface2); color: var(--text); }
  .icon-btn.edit:hover { color: var(--accent); border-color: var(--accent); }
  .icon-btn.del:hover { color: var(--danger); border-color: var(--danger); }

  .progress-bar {
    height: 4px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    width: 80px;
  }

  .progress-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
    transition: width 0.5s ease;
  }

  /* ─── SENSOR FEED ─── */
  .sensor-list { display: flex; flex-direction: column; gap: 12px; }

  .sensor-row {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px;
    background: var(--surface2);
    border-radius: 8px;
    border: 1px solid var(--border);
    transition: border-color 0.15s;
  }

  .sensor-row:hover { border-color: var(--accent); }

  .sensor-indicator {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }

  .si-cyan { background: rgba(0,229,255,0.1); }
  .si-purple { background: rgba(124,58,237,0.1); }
  .si-amber { background: rgba(245,158,11,0.1); }
  .si-green { background: rgba(16,185,129,0.1); }

  .sensor-info { flex: 1; }
  .sensor-name { font-size: 12px; font-weight: 700; }
  .sensor-val { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 2px; }

  .sensor-live {
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 700;
    color: var(--accent);
  }

  /* ─── USERS TABLE ─── */
  .user-row-avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
  }

  .ua-cyan { background: linear-gradient(135deg, var(--accent2), var(--accent)); }
  .ua-purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); }
  .ua-amber { background: linear-gradient(135deg, #d97706, var(--accent3)); }

  .user-cell { display: flex; align-items: center; gap: 10px; }

  /* ─── MIGRATION STATUS ─── */
  .migration-card {
    background: var(--surface2);
    border-radius: 10px;
    padding: 16px 18px;
    border: 1px solid var(--border);
    display: flex; align-items: center; gap: 14px;
  }

  .mig-icon {
    width: 44px; height: 44px;
    border-radius: 10px;
    background: rgba(0,229,255,0.08);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }

  .mig-info { flex: 1; }
  .mig-title { font-size: 13px; font-weight: 700; margin-bottom: 4px; }
  .mig-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); }

  .mig-status-ok { color: var(--success); font-weight: 700; font-size: 12px; font-family: var(--mono); }
  .mig-status-err { color: var(--danger); font-weight: 700; font-size: 12px; font-family: var(--mono); }

  /* ─── MINI CHART ─── */
  .chart-area {
    height: 120px;
    display: flex;
    align-items: flex-end;
    gap: 4px;
    padding: 0 0 4px;
  }

  .bar-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    height: 100%;
    justify-content: flex-end;
  }

  .bar {
    width: 100%;
    border-radius: 4px 4px 0 0;
    background: linear-gradient(180deg, var(--accent2), var(--accent));
    opacity: 0.7;
    transition: opacity 0.15s;
    min-height: 4px;
  }

  .bar-col:hover .bar { opacity: 1; }

  .bar-label {
    font-family: var(--mono);
    font-size: 9px;
    color: var(--muted);
  }

  /* ─── EMPTY STATE ─── */
  .empty {
    display: flex; flex-direction: column; align-items: center;
    padding: 40px;
    color: var(--muted);
    gap: 8px;
    font-size: 13px;
  }

  .empty-icon { font-size: 32px; opacity: 0.4; }

  /* ─── SCROLLBAR ─── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ─── TOAST ─── */
  .toast {
    position: fixed;
    bottom: 24px; right: 24px;
    background: var(--surface);
    border: 1px solid var(--success);
    color: var(--text);
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    display: flex; align-items: center; gap: 8px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    z-index: 999;
    transform: translateY(80px);
    opacity: 0;
    transition: all 0.3s cubic-bezier(.34,1.56,.64,1);
  }

  .toast.show { transform: translateY(0); opacity: 1; }

  /* ─── MODAL ─── */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    z-index: 200;
    opacity: 0; pointer-events: none;
    transition: opacity 0.2s;
  }

  .modal-overlay.open { opacity: 1; pointer-events: all; }

  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px;
    width: 440px;
    max-width: 90vw;
    transform: scale(0.95);
    transition: transform 0.2s;
  }

  .modal-overlay.open .modal { transform: scale(1); }

  .modal-title {
    font-size: 17px; font-weight: 800;
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
  }

  .form-group { margin-bottom: 16px; }

  label {
    display: block;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
  }

  input, select, textarea {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 10px 13px;
    color: var(--text);
    font-family: var(--sans);
    font-size: 13px;
    outline: none;
    transition: border-color 0.15s;
  }

  input:focus, select:focus, textarea:focus {
    border-color: var(--accent);
  }

  select option { background: var(--surface2); }

  .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
</style>

</head>
<body>

<!-- SIDEBAR -->
<aside class="sidebar">
  <div class="logo">
    <div class="logo-icon">⚡</div>
    <span class="logo-text">Sim<span>Control</span></span>
  </div>

  <div class="nav-section">
    <div class="nav-label">Principal</div>
    <div class="nav-item active" onclick="showPage('dashboard')">
      <span class="nav-icon">⊞</span> Dashboard
    </div>
    <div class="nav-item" onclick="showPage('simulacoes')">
      <span class="nav-icon">▶</span> Simulações
      <span class="badge green">3</span>
    </div>
    <div class="nav-item" onclick="showPage('sensores')">
      <span class="nav-icon">📡</span> Sensores
      <span class="badge amber">Live</span>
    </div>
  </div>

  <div class="nav-section">
    <div class="nav-label">Administração</div>
    <div class="nav-item" onclick="showPage('utilizadores')">
      <span class="nav-icon">👥</span> Utilizadores
    </div>
    <div class="nav-item" onclick="showPage('equipes')">
      <span class="nav-icon">🏷️</span> Equipes
    </div>
    <div class="nav-item" onclick="showPage('migracao')">
      <span class="nav-icon">🔄</span> Migração DB
      <span class="badge">!</span>
    </div>
  </div>

  <div class="nav-section">
    <div class="nav-label">Conta</div>
    <div class="nav-item" onclick="showPage('perfil')">
      <span class="nav-icon">⚙</span> Meu Perfil
    </div>
  </div>

  <div class="sidebar-footer">
    <div class="user-card">
      <div class="avatar">AD</div>
      <div class="user-info">
        <div class="user-name"><?php echo $user['Nome']?></div>
        <div class="user-role"><?php echo $user['Tipo']?></div>
      </div>
    </div>
  </div>
</aside>

<!-- MAIN -->
<main class="main">
  <div class="topbar">
    <span class="page-title" id="topbar-title">Dashboard</span>
    <div class="topbar-actions">
      <div class="status-dot"></div>
      <span style="font-size:12px; color: var(--muted); font-family: var(--mono);">MongoDB → MySQL</span>
      <button class="btn btn-primary" onclick="openModal('nova-sim')">+ Nova Simulação</button>
    </div>
  </div>

  <div class="content">

    <!-- ═══ DASHBOARD PAGE ═══ -->
    <div id="page-dashboard">
      <div class="stats-grid">
        <div class="stat-card cyan">
          <span class="stat-icon">▶</span>
          <div class="stat-value">3</div>
          <div class="stat-label">Simulações Ativas</div>
          <div class="stat-delta">↑ +1 esta semana</div>
        </div>
        <div class="stat-card purple">
          <span class="stat-icon">👥</span>
          <div class="stat-value">12</div>
          <div class="stat-label">Utilizadores</div>
          <div class="stat-delta">↑ +2 este mês</div>
        </div>
        <div class="stat-card amber">
          <span class="stat-icon">📡</span>
          <div class="stat-value">48</div>
          <div class="stat-label">Sensores Online</div>
          <div class="stat-delta">↔ estável</div>
        </div>
        <div class="stat-card green">
          <span class="stat-icon">🔄</span>
          <div class="stat-value">99.8%</div>
          <div class="stat-label">Uptime Migração</div>
          <div class="stat-delta">↑ últimas 24h</div>
        </div>
      </div>

      <div class="grid-3-1">
        <!-- Simulações recentes -->
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">▶ Simulações Recentes</span>
            <button class="btn btn-ghost" style="font-size:12px; padding:6px 12px;" onclick="showPage('simulacoes')">Ver todas →</button>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Simulação</th>
                  <th>Equipe</th>
                  <th>Estado</th>
                  <th>Progresso</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <div class="sim-name">Sim Alpha 01</div>
                    <div class="sim-id">#SIM-001 · criado por: joao.silva</div>
                  </td>
                  <td style="color: var(--muted); font-size: 12px;">Equipe A</td>
                  <td><span class="chip chip-running"><span class="chip-dot"></span>Running</span></td>
                  <td>
                    <div class="progress-bar"><div class="progress-fill" style="width:72%"></div></div>
                    <span style="font-family: var(--mono); font-size: 10px; color: var(--muted);">72%</span>
                  </td>
                  <td>
                    <div class="action-btns">
                      <button class="icon-btn edit" title="Editar parâmetros">✎</button>
                      <button class="icon-btn" title="Pausar">⏸</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>
                    <div class="sim-name">Beta Test ENV</div>
                    <div class="sim-id">#SIM-002 · criado por: maria.costa</div>
                  </td>
                  <td style="color: var(--muted); font-size: 12px;">Equipe B</td>
                  <td><span class="chip chip-paused"><span class="chip-dot"></span>Paused</span></td>
                  <td>
                    <div class="progress-bar"><div class="progress-fill" style="width:35%"></div></div>
                    <span style="font-family: var(--mono); font-size: 10px; color: var(--muted);">35%</span>
                  </td>
                  <td>
                    <div class="action-btns">
                      <button class="icon-btn edit" title="Editar">✎</button>
                      <button class="icon-btn" title="Retomar">▶</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>
                    <div class="sim-name">Stress Test v3</div>
                    <div class="sim-id">#SIM-003 · criado por: rui.pedro</div>
                  </td>
                  <td style="color: var(--muted); font-size: 12px;">Equipe A</td>
                  <td><span class="chip chip-running"><span class="chip-dot"></span>Running</span></td>
                  <td>
                    <div class="progress-bar"><div class="progress-fill" style="width:91%"></div></div>
                    <span style="font-family: var(--mono); font-size: 10px; color: var(--muted);">91%</span>
                  </td>
                  <td>
                    <div class="action-btns">
                      <button class="icon-btn" title="Apenas criador pode editar" style="opacity:.3; cursor:not-allowed;">✎</button>
                      <button class="icon-btn" title="Parar">⏹</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Sensor feed -->
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">📡 Leituras Live</span>
            <span class="chip chip-running" style="font-size:10px;"><span class="chip-dot"></span>ao vivo</span>
          </div>
          <div class="panel-body">
            <div class="sensor-list">
              <div class="sensor-row">
                <div class="sensor-indicator si-cyan">🌡️</div>
                <div class="sensor-info">
                  <div class="sensor-name">Temperatura</div>
                  <div class="sensor-val">Sensor T-01 · Zona A</div>
                </div>
                <div class="sensor-live" id="temp">23.4°C</div>
              </div>
              <div class="sensor-row">
                <div class="sensor-indicator si-purple">💧</div>
                <div class="sensor-info">
                  <div class="sensor-name">Humidade</div>
                  <div class="sensor-val">Sensor H-02 · Zona B</div>
                </div>
                <div class="sensor-live" id="hum">61.2%</div>
              </div>
              <div class="sensor-row">
                <div class="sensor-indicator si-amber">⚡</div>
                <div class="sensor-info">
                  <div class="sensor-name">Tensão</div>
                  <div class="sensor-val">Sensor V-03 · Painel</div>
                </div>
                <div class="sensor-live" id="volt">220.8V</div>
              </div>
              <div class="sensor-row">
                <div class="sensor-indicator si-green">🌊</div>
                <div class="sensor-info">
                  <div class="sensor-name">Pressão</div>
                  <div class="sensor-val">Sensor P-04 · Reserv.</div>
                </div>
                <div class="sensor-live" id="pres">1.013 bar</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Gráfico + Migração -->
      <div class="grid-2">
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">📊 Leituras por Hora (últimas 8h)</span>
          </div>
          <div class="panel-body">
            <div class="chart-area" id="chart">
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:6px;">
              <span style="font-family: var(--mono); font-size: 10px; color: var(--muted);">0 leituras</span>
              <span style="font-family: var(--mono); font-size: 10px; color: var(--muted);">máximo: 1200</span>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">🔄 Estado da Migração</span>
          </div>
          <div class="panel-body" style="display: flex; flex-direction: column; gap: 12px;">
            <div class="migration-card">
              <div class="mig-icon">🍃</div>
              <div class="mig-info">
                <div class="mig-title">MongoDB → MySQL</div>
                <div class="mig-sub">Última sync: há 4 segundos</div>
              </div>
              <div class="mig-status-ok">● ONLINE</div>
            </div>
            <div class="migration-card" style="border-color: rgba(239,68,68,0.2);">
              <div class="mig-icon" style="background: rgba(239,68,68,0.08);">⚠️</div>
              <div class="mig-info">
                <div class="mig-title">Worker de Backup</div>
                <div class="mig-sub">Última tentativa: 12 min atrás</div>
              </div>
              <div class="mig-status-err">● FALHA</div>
            </div>
            <button class="btn btn-danger" onclick="reiniciarMigracao()" style="width:100%; justify-content: center;">
              🔄 Reinicializar Processo de Migração
            </button>
            <p style="font-size: 11px; color: var(--muted); text-align:center; font-family: var(--mono);">Executa procedimento SQL sp_restart_migration</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ SIMULAÇÕES PAGE ═══ -->
    <div id="page-simulacoes" style="display:none;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 24px;">
        <div>
          <h2 style="font-size:22px; font-weight:800;">Simulações</h2>
          <p style="color: var(--muted); font-size:13px; margin-top:4px;">Gerir e monitorizar todas as simulações da plataforma</p>
        </div>
        <button class="btn btn-primary" onclick="openModal('nova-sim')">+ Nova Simulação</button>
      </div>
      <div class="panel">
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Nome</th><th>Equipe</th><th>Criador</th><th>Estado</th><th>Parâmetros</th><th>Iniciada</th><th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span style="font-family: var(--mono); font-size:11px; color:var(--muted);">#001</span></td>
                <td><div class="sim-name">Sim Alpha 01</div></td>
                <td style="color:var(--muted); font-size:12px;">Equipe A</td>
                <td style="font-family: var(--mono); font-size:11px;">joao.silva</td>
                <td><span class="chip chip-running"><span class="chip-dot"></span>Running</span></td>
                <td style="font-family: var(--mono); font-size:11px; color:var(--accent);">8 params</td>
                <td style="font-size:12px; color:var(--muted);">09/03/2026 08:14</td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn edit" onclick="openModal('edit-sim')" title="Editar">✎</button>
                    <button class="icon-btn" title="Parar">⏹</button>
                    <button class="icon-btn del" title="Apagar">✕</button>
                  </div>
                </td>
              </tr>
              <tr>
                <td><span style="font-family: var(--mono); font-size:11px; color:var(--muted);">#002</span></td>
                <td><div class="sim-name">Beta Test ENV</div></td>
                <td style="color:var(--muted); font-size:12px;">Equipe B</td>
                <td style="font-family: var(--mono); font-size:11px;">maria.costa</td>
                <td><span class="chip chip-paused"><span class="chip-dot"></span>Paused</span></td>
                <td style="font-family: var(--mono); font-size:11px; color:var(--accent);">5 params</td>
                <td style="font-size:12px; color:var(--muted);">08/03/2026 15:30</td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn" style="opacity:.3; cursor:not-allowed;" title="Só o criador pode editar">✎</button>
                    <button class="icon-btn" title="Retomar">▶</button>
                    <button class="icon-btn del" title="Apagar">✕</button>
                  </div>
                </td>
              </tr>
              <tr>
                <td><span style="font-family: var(--mono); font-size:11px; color:var(--muted);">#003</span></td>
                <td><div class="sim-name">Stress Test v3</div></td>
                <td style="color:var(--muted); font-size:12px;">Equipe A</td>
                <td style="font-family: var(--mono); font-size:11px;">rui.pedro</td>
                <td><span class="chip chip-running"><span class="chip-dot"></span>Running</span></td>
                <td style="font-family: var(--mono); font-size:11px; color:var(--accent);">12 params</td>
                <td style="font-size:12px; color:var(--muted);">09/03/2026 10:02</td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn" style="opacity:.3; cursor:not-allowed;" title="Só o criador pode editar">✎</button>
                    <button class="icon-btn" title="Parar">⏹</button>
                    <button class="icon-btn del" title="Apagar">✕</button>
                  </div>
                </td>
              </tr>
              <tr>
                <td><span style="font-family: var(--mono); font-size:11px; color:var(--muted);">#004</span></td>
                <td><div class="sim-name">Cold Boot Seq</div></td>
                <td style="color:var(--muted); font-size:12px;">Equipe C</td>
                <td style="font-family: var(--mono); font-size:11px;">ana.ferreira</td>
                <td><span class="chip chip-idle"><span class="chip-dot"></span>Idle</span></td>
                <td style="font-family: var(--mono); font-size:11px; color:var(--accent);">3 params</td>
                <td style="font-size:12px; color:var(--muted);">07/03/2026 09:00</td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn edit" title="Editar">✎</button>
                    <button class="icon-btn" title="Iniciar">▶</button>
                    <button class="icon-btn del" title="Apagar">✕</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ UTILIZADORES PAGE ═══ -->
    <div id="page-utilizadores" style="display:none;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 24px;">
        <div>
          <h2 style="font-size:22px; font-weight:800;">Utilizadores</h2>
          <p style="color: var(--muted); font-size:13px; margin-top:4px;">Criar, gerir e remover utilizadores da plataforma</p>
        </div>
        <button class="btn btn-primary" onclick="openModal('novo-user')">+ Criar Utilizador</button>
      </div>
      <div class="panel">
        <div class="table-wrapper">
          <table>
            <thead>
              <tr><th>Utilizador</th><th>Email</th><th>Equipe</th><th>Papel</th><th>Estado</th><th>Ações</th></tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div class="user-cell">
                    <div class="user-row-avatar ua-cyan">JS</div>
                    <div>
                      <div style="font-weight:700; font-size:13px;">João Silva</div>
                      <div style="font-family:var(--mono); font-size:10px; color:var(--muted);">joao.silva</div>
                    </div>
                  </div>
                </td>
                <td style="font-size:12px; color:var(--muted);">joao@empresa.pt</td>
                <td style="font-size:12px;">Equipe A</td>
                <td><span class="chip" style="background:rgba(0,229,255,.1); color:var(--accent); border:1px solid rgba(0,229,255,.2);">Membro</span></td>
                <td><span class="chip chip-running"><span class="chip-dot"></span>Ativo</span></td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn edit" title="Editar">✎</button>
                    <button class="icon-btn del" title="Remover" onclick="showToast('Utilizador removido','error')">✕</button>
                  </div>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="user-cell">
                    <div class="user-row-avatar ua-purple">MC</div>
                    <div>
                      <div style="font-weight:700; font-size:13px;">Maria Costa</div>
                      <div style="font-family:var(--mono); font-size:10px; color:var(--muted);">maria.costa</div>
                    </div>
                  </div>
                </td>
                <td style="font-size:12px; color:var(--muted);">maria@empresa.pt</td>
                <td style="font-size:12px;">Equipe B</td>
                <td><span class="chip" style="background:rgba(0,229,255,.1); color:var(--accent); border:1px solid rgba(0,229,255,.2);">Membro</span></td>
                <td><span class="chip chip-running"><span class="chip-dot"></span>Ativo</span></td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn edit" title="Editar">✎</button>
                    <button class="icon-btn del" title="Remover">✕</button>
                  </div>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="user-cell">
                    <div class="user-row-avatar ua-amber">AF</div>
                    <div>
                      <div style="font-weight:700; font-size:13px;">Ana Ferreira</div>
                      <div style="font-family:var(--mono); font-size:10px; color:var(--muted);">ana.ferreira</div>
                    </div>
                  </div>
                </td>
                <td style="font-size:12px; color:var(--muted);">ana@empresa.pt</td>
                <td style="font-size:12px;">Equipe C</td>
                <td><span class="chip" style="background:rgba(124,58,237,.1); color:#a78bfa; border:1px solid rgba(124,58,237,.2);">Lead</span></td>
                <td><span class="chip chip-paused"><span class="chip-dot"></span>Ausente</span></td>
                <td>
                  <div class="action-btns">
                    <button class="icon-btn edit" title="Editar">✎</button>
                    <button class="icon-btn del" title="Remover">✕</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ EQUIPES PAGE ═══ -->
    <div id="page-equipes" style="display:none;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 24px;">
        <div>
          <h2 style="font-size:22px; font-weight:800;">Equipes</h2>
          <p style="color: var(--muted); font-size:13px; margin-top:4px;">Gerir grupos de utilizadores e as suas simulações</p>
        </div>
        <button class="btn btn-primary" onclick="openModal('nova-equipe')">+ Criar Equipe</button>
      </div>
      <div class="stats-grid">
        <div class="stat-card cyan" style="cursor:pointer;">
          <span class="stat-icon">🏷️</span>
          <div class="stat-value">Equipe A</div>
          <div class="stat-label">4 membros · 2 sims ativas</div>
        </div>
        <div class="stat-card purple" style="cursor:pointer;">
          <span class="stat-icon">🏷️</span>
          <div class="stat-value">Equipe B</div>
          <div class="stat-label">3 membros · 1 sim ativa</div>
        </div>
        <div class="stat-card amber" style="cursor:pointer;">
          <span class="stat-icon">🏷️</span>
          <div class="stat-value">Equipe C</div>
          <div class="stat-label">5 membros · 0 sims ativas</div>
        </div>
        <div class="stat-card green" style="cursor:pointer; border-style: dashed;" onclick="openModal('nova-equipe')">
          <span class="stat-icon">+</span>
          <div class="stat-value" style="font-size:18px; color: var(--muted);">Nova Equipe</div>
          <div class="stat-label">Adicionar grupo</div>
        </div>
      </div>
    </div>

    <!-- ═══ MIGRAÇÃO PAGE ═══ -->
    <div id="page-migracao" style="display:none;">
      <div style="margin-bottom: 24px;">
        <h2 style="font-size:22px; font-weight:800;">Migração de Dados</h2>
        <p style="color: var(--muted); font-size:13px; margin-top:4px;">Monitorização e controlo da migração MongoDB → MySQL</p>
      </div>
      <div class="grid-2">
        <div class="panel">
          <div class="panel-header"><span class="panel-title">🔄 Status do Processo</span></div>
          <div class="panel-body" style="display:flex; flex-direction:column; gap:14px;">
            <div class="migration-card">
              <div class="mig-icon">🍃</div>
              <div class="mig-info">
                <div class="mig-title">Worker Principal (Java)</div>
                <div class="mig-sub">PID: 4821 · Thread: migration-main · Porto: 8080</div>
              </div>
              <div class="mig-status-ok">● RUNNING</div>
            </div>
            <div class="migration-card" style="border-color:rgba(239,68,68,.2);">
              <div class="mig-icon" style="background:rgba(239,68,68,.08);">⚠️</div>
              <div class="mig-info">
                <div class="mig-title">Worker de Backup</div>
                <div class="mig-sub">Erro: Connection timeout · Última: 12 min atrás</div>
              </div>
              <div class="mig-status-err">● ERROR</div>
            </div>
            <div class="migration-card">
              <div class="mig-icon">🗄️</div>
              <div class="mig-info">
                <div class="mig-title">MySQL Target DB</div>
                <div class="mig-sub">maze_local · 127.0.0.1:3306</div>
              </div>
              <div class="mig-status-ok">● ONLINE</div>
            </div>
            <div class="migration-card">
              <div class="mig-icon">🌿</div>
              <div class="mig-info">
                <div class="mig-title">MongoDB Source</div>
                <div class="mig-sub">sensors_db · mongo:27017</div>
              </div>
              <div class="mig-status-ok">● ONLINE</div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header"><span class="panel-title">⚙ Ações de Administrador</span></div>
          <div class="panel-body" style="display:flex; flex-direction:column; gap:12px;">
            <p style="font-size:13px; color:var(--muted); line-height:1.6;">
              Em caso de falha no processo de migração, o administrador pode reinicializar chamando o procedimento SQL ou o programa externo.
            </p>
            <button class="btn btn-danger" onclick="reiniciarMigracao()" style="width:100%; justify-content:center; padding:12px;">
              🔄 Reinicializar via Procedimento SQL
            </button>
            <button class="btn btn-ghost" style="width:100%; justify-content:center;" onclick="showToast('A chamar worker Python...','info')">
              🐍 Reinicializar via Python Worker
            </button>
            <button class="btn btn-ghost" style="width:100%; justify-content:center;" onclick="showToast('A chamar worker PHP...','info')">
              🐘 Reinicializar via PHP Script
            </button>
            <div style="background: var(--surface2); border-radius:8px; padding: 14px; font-family: var(--mono); font-size: 11px; color: var(--muted); line-height: 1.7; border: 1px solid var(--border);">
              <span style="color:var(--accent);">mysql&gt;</span> CALL sp_restart_migration();<br>
              <span style="color:var(--success);">Query OK, 0 rows affected</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ SENSORES PAGE ═══ -->
    <div id="page-sensores" style="display:none;">
      <div style="margin-bottom: 24px;">
        <h2 style="font-size:22px; font-weight:800;">Sensores</h2>
        <p style="color: var(--muted); font-size:13px; margin-top:4px;">Leituras em tempo real dos sensores via MongoDB</p>
      </div>
      <div class="stats-grid">
        <div class="stat-card cyan"><span class="stat-icon">🌡️</span><div class="stat-value" id="s-temp">23.4°C</div><div class="stat-label">Temperatura</div></div>
        <div class="stat-card purple"><span class="stat-icon">💧</span><div class="stat-value" id="s-hum">61.2%</div><div class="stat-label">Humidade</div></div>
        <div class="stat-card amber"><span class="stat-icon">⚡</span><div class="stat-value" id="s-volt">220.8V</div><div class="stat-label">Tensão</div></div>
        <div class="stat-card green"><span class="stat-icon">🌊</span><div class="stat-value" id="s-pres">1.013</div><div class="stat-label">Pressão (bar)</div></div>
      </div>
    </div>

    <!-- ═══ PERFIL PAGE ═══ -->
    <div id="page-perfil" style="display:none;">
      <div style="margin-bottom: 24px;">
        <h2 style="font-size:22px; font-weight:800;">Meu Perfil</h2>
        <p style="color: var(--muted); font-size:13px; margin-top:4px;">Apenas pode editar os seus próprios dados pessoais</p>
      </div>
      <div class="panel" style="max-width: 500px;">
        <div class="panel-header"><span class="panel-title">👤 Dados Pessoais</span></div>
        <div class="panel-body">
          <div class="form-group">
            <label>Nome Completo</label>
            <input type="text" value="Administrador Sistema">
          </div>
          <div class="form-group">
            <label>Username</label>
            <input type="text" value="admin" disabled style="opacity:.5;">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" value="admin@empresa.pt">
          </div>
          <div class="form-group">
            <label>Nova Password</label>
            <input type="password" placeholder="••••••••">
          </div>
          <button class="btn btn-primary" onclick="showToast('Perfil atualizado com sucesso!')" style="margin-top:8px;">Guardar Alterações</button>
        </div>
      </div>
    </div>

  </div>
</main>

<!-- TOAST -->
<div class="toast" id="toast">
  <span id="toast-icon">✓</span>
  <span id="toast-msg">Ação executada com sucesso!</span>
</div>

<!-- MODAL: Nova Simulação -->
<div class="modal-overlay" id="modal-nova-sim">
  <div class="modal">
    <div class="modal-title">▶ Nova Simulação</div>
    <div class="form-group">
      <label>Nome da Simulação</label>
      <input type="text" placeholder="ex: Sim Delta 04">
    </div>
    <div class="form-group">
      <label>Equipe</label>
      <select><option>Equipe A</option><option>Equipe B</option><option>Equipe C</option></select>
    </div>
    <div class="form-group">
      <label>Parâmetro: Duração (min)</label>
      <input type="number" value="60">
    </div>
    <div class="form-group">
      <label>Parâmetro: Frequência Sensor (Hz)</label>
      <input type="number" value="10">
    </div>
    <div class="form-group">
      <label>Notas</label>
      <textarea rows="2" placeholder="Descrição opcional..."></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('nova-sim')">Cancelar</button>
      <button class="btn btn-primary" onclick="closeModal('nova-sim'); showToast('Simulação criada e iniciada!')">Criar & Iniciar</button>
    </div>
  </div>
</div>

<!-- MODAL: Editar Simulação -->
<div class="modal-overlay" id="modal-edit-sim">
  <div class="modal">
    <div class="modal-title">✎ Editar Parâmetros — Sim Alpha 01</div>
    <div class="form-group">
      <label>Duração (min)</label>
      <input type="number" value="120">
    </div>
    <div class="form-group">
      <label>Frequência Sensor (Hz)</label>
      <input type="number" value="10">
    </div>
    <div class="form-group">
      <label>Threshold Temperatura (°C)</label>
      <input type="number" value="85">
    </div>
    <div class="form-group">
      <label>Modo</label>
      <select><option>Normal</option><option>Stress</option><option>Silent</option></select>
    </div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('edit-sim')">Cancelar</button>
      <button class="btn btn-primary" onclick="closeModal('edit-sim'); showToast('Parâmetros atualizados!')">Guardar</button>
    </div>
  </div>
</div>

<!-- MODAL: Novo Utilizador -->
<div class="modal-overlay" id="modal-novo-user">
  <div class="modal">
    <div class="modal-title">👤 Criar Utilizador</div>
    <div class="form-group">
      <label>Nome Completo</label>
      <input type="text" placeholder="Nome do utilizador">
    </div>
    <div class="form-group">
      <label>Username</label>
      <input type="text" placeholder="nome.apelido">
    </div>
    <div class="form-group">
      <label>Email</label>
      <input type="email" placeholder="email@empresa.pt">
    </div>
    <div class="form-group">
      <label>Password Inicial</label>
      <input type="password" placeholder="••••••••">
    </div>
    <div class="form-group">
      <label>Equipe</label>
      <select><option>Equipe A</option><option>Equipe B</option><option>Equipe C</option></select>
    </div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('novo-user')">Cancelar</button>
      <button class="btn btn-primary" onclick="closeModal('novo-user'); showToast('Utilizador criado com sucesso!')">Criar</button>
    </div>
  </div>
</div>

<!-- MODAL: Nova Equipe -->
<div class="modal-overlay" id="modal-nova-equipe">
  <div class="modal">
    <div class="modal-title">🏷️ Criar Equipe</div>
    <div class="form-group">
      <label>Nome da Equipe</label>
      <input type="text" placeholder="ex: Equipe Delta">
    </div>
    <div class="form-group">
      <label>Descrição</label>
      <textarea rows="2" placeholder="Descrição opcional..."></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('nova-equipe')">Cancelar</button>
      <button class="btn btn-primary" onclick="closeModal('nova-equipe'); showToast('Equipe criada!')">Criar</button>
    </div>
  </div>
</div>

<script>
  // ─── Navigation ───
  const pages = ['dashboard','simulacoes','utilizadores','equipes','migracao','sensores','perfil'];
  const titles = {
    dashboard: 'Dashboard',
    simulacoes: 'Simulações',
    utilizadores: 'Utilizadores',
    equipes: 'Equipes',
    migracao: 'Migração de Dados',
    sensores: 'Sensores Live',
    perfil: 'Meu Perfil'
  };

  function showPage(name) {
    pages.forEach(p => {
      document.getElementById('page-' + p).style.display = p === name ? 'block' : 'none';
    });
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    event && event.currentTarget && event.currentTarget.classList.add('active');
    document.getElementById('topbar-title').textContent = titles[name] || name;
  }

  // ─── Modals ───
  function openModal(id) {
    document.getElementById('modal-' + id).classList.add('open');
  }

  function closeModal(id) {
    document.getElementById('modal-' + id).classList.remove('open');
  }

  document.querySelectorAll('.modal-overlay').forEach(el => {
    el.addEventListener('click', function(e) {
      if (e.target === this) this.classList.remove('open');
    });
  });

  // ─── Toast ───
  function showToast(msg, type = 'success') {
    const t = document.getElementById('toast');
    const icon = document.getElementById('toast-icon');
    document.getElementById('toast-msg').textContent = msg;
    icon.textContent = type === 'error' ? '✕' : type === 'info' ? 'ℹ' : '✓';
    t.style.borderColor = type === 'error' ? 'var(--danger)' : type === 'info' ? 'var(--accent)' : 'var(--success)';
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
  }

  // ─── Migration restart ───
  function reiniciarMigracao() {
    showToast('A executar sp_restart_migration...', 'info');
    setTimeout(() => showToast('Migração reiniciada com sucesso!'), 2000);
  }

  // ─── Live sensor simulation ───
  function updateSensors() {
    const t = (23 + Math.random() * 2 - 1).toFixed(1) + '°C';
    const h = (61 + Math.random() * 4 - 2).toFixed(1) + '%';
    const v = (220 + Math.random() * 3 - 1.5).toFixed(1) + 'V';
    const p = (1.013 + (Math.random() * 0.01 - 0.005)).toFixed(3) + ' bar';

    ['temp','hum','volt','pres'].forEach((id, i) => {
      const el = document.getElementById(id);
      if (el) { el.textContent = [t,h,v,p][i]; }
    });
    ['s-temp','s-hum','s-volt','s-pres'].forEach((id, i) => {
      const el = document.getElementById(id);
      if (el) { el.textContent = [t,h,v,p][i].replace(' bar',''); }
    });
  }
  setInterval(updateSensors, 2000);

  // ─── Bar chart ───
  const bars = [420, 680, 890, 1100, 950, 760, 1050, 1180];
  const chart = document.getElementById('chart');
  const hours = ['02h','04h','06h','08h','10h','12h','14h','16h'];
  bars.forEach((v, i) => {
    const col = document.createElement('div');
    col.className = 'bar-col';
    const pct = (v / 1200 * 100).toFixed(0);
    col.innerHTML = `<div class="bar" style="height:${pct}%"></div><div class="bar-label">${hours[i]}</div>`;
    chart.appendChild(col);
  });
</script>
</body>
</html>

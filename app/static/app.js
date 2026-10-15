'use strict';
const $ = id => document.getElementById(id);
const state = { user: 'demo', data: null, preview: null, account: null, page: 0, busy: false, plan: null, selected: new Set(), b50Mode: 'compare' };
function notice(message, error = false) {
  $('notice').textContent = message; $('notice').classList.remove('hidden'); $('notice').classList.toggle('error', error);
}
async function api(path, body) {
  const options = { credentials: 'same-origin' };
  if (body !== undefined) Object.assign(options, { method: 'POST', headers: {'Content-Type': 'application/json', 'X-AquaSync-Action': '1'}, body: JSON.stringify(body) });
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) {
    const detail = data.detail;
    throw new Error(typeof detail === 'string' ? detail : detail?.message || (response.status === 404 ? '没有已存成绩，请先选择 AquaDX JSON 文件。' : `请求失败（${response.status}）`));
  }
  return data;
}
function userPath(tail) { return '/api/user/' + encodeURIComponent(state.user) + tail; }
function syncControls() {
  const connected = !!state.account;
  $('connection-status').textContent = connected ? '已连接' : '未连接';
  $('disconnect').classList.toggle('hidden', !connected);
  $('account-name').textContent = connected ? `${state.account.name} · 好友码 ${state.account.friend_code}` : '连接后会显示目标玩家';
  const p = state.preview;
  const rejected = !!p?.rejected.length;
  const lower = !!state.plan?.rows.some(r => state.selected.has(r.key) && r.hasLower);
  $('partial-label').classList.toggle('hidden', !rejected);
  $('lower-label').classList.toggle('hidden', !lower);
  $('review-upload').disabled = state.busy || !p || !connected || !state.plan || state.plan.used || !state.selected.size || (rejected && !$('allow-partial').checked) || (lower && !$('allow-lower').checked);
  $('sync-info').textContent = !p ? '请先导入或加载成绩。' : !connected ? '请先连接落雪账号。' : !state.plan ? '请在“上传差异”中读取落雪成绩并备份，再选择成绩。' : state.plan.used ? '本次预览已提交；再次操作前请重新读取落雪成绩并备份。' : `将提交所选 ${state.selected.size} 张到 ${state.account.name}；其余成绩不提交。`;
  for (const id of ['load', 'connect', 'disconnect', 'refresh-catalog', 'confirm-upload']) $(id).disabled = state.busy;
  for (const id of ['select-all','select-recommended','clear-selection']) $(id).disabled = state.busy || !state.plan || state.plan.used;
  $('prepare-diff').disabled = state.busy || !connected || !state.data;
  $('file').disabled = state.busy;
  $('confirm-upload').textContent = state.busy ? '正在提交…' : '确认上传';
}
async function run(task) {
  if (state.busy) return;
  state.busy = true; syncControls();
  try { await task(); } catch (error) { notice(error.message, true); }
  finally { state.busy = false; renderDiff(); syncControls(); }
}
function cell(row, value, className) { const td = document.createElement('td'); td.textContent = value; if (className) td.className = className; row.appendChild(td); return td; }
function tableRow(tbody) { const tr = document.createElement('tr'); tbody.appendChild(tr); return tr; }
function titleCell(row, title, id) { const td = cell(row, ''); const name = document.createElement('div'); name.className = 'song-title'; name.textContent = title || '未匹配曲目'; const sub = document.createElement('div'); sub.className = 'song-id'; sub.textContent = 'musicId ' + id; td.append(name, sub); }
function difficultyCell(row, value) { const td = cell(row, ''); const badge = document.createElement('span'); badge.className = 'difficulty'; badge.textContent = value; td.appendChild(badge); }
function invalidatePlan() { state.plan = null; state.selected.clear(); $('allow-lower').checked = false; $('download-backup').classList.add('hidden'); $('verification').classList.add('hidden'); renderDiff(); renderB50(); }
function showTab(name) { for (const other of ['preview','b50','diff','private','plates']) { $('tab-' + other).classList.toggle('active', other === name); $('tab-' + other).setAttribute('aria-selected', other === name ? 'true' : 'false'); $(other + '-view').classList.toggle('hidden', other !== name); } }
function renderB50() {
  const d = state.data; if (!d) return;
  $('b50-comparison').classList.toggle('hidden', state.b50Mode !== 'compare'); $('b50-single').classList.toggle('hidden', state.b50Mode === 'compare');
  renderComparison();
  if (state.b50Mode === 'compare') return;
  const view = state.b50Mode === 'local' ? d.b50 : state.b50Mode === 'remote' ? state.plan?.remoteB50 : d.b50Views?.[state.b50Mode];
  const label = {source:'私服原始',target:'落雪导入估算',remote:'落雪账号估算',local:'原本地分析'}[state.b50Mode];
  $('b50-records').replaceChildren();
  if (!view || view.available === false) { $('b50-info').textContent = state.b50Mode === 'remote' ? '先在“上传差异”中读取落雪已有成绩。' : (view?.warnings?.join('；') || '此视图不可用，请重新导入原始 AquaDX 文件。'); return; }
  $('b50-info').textContent = `${label}：旧曲 ${view.old.length} 张 / ${view.oldRating ?? '未知'} + 新曲 ${view.new.length} 张 / ${view.newRating ?? '未知'} = ${view.rating ?? '未知'}。` + (state.b50Mode === 'source' ? '分组、顺序和总分来自私服导出；单曲 Rating 未导出，留空。' : (view.basis || '按本地分析曲库计算。'));
  for (const group of ['old','new']) for (const r of view[group]) { const row = tableRow($('b50-records')); cell(row, group === 'old' ? '旧曲' : '新曲'); titleCell(row, r.title, r.musicId); cell(row, r.difficulty); cell(row, r.achievements.toFixed(4) + '%','score-achievement'); cell(row, r.ra ?? '—'); }
  const changes = d.b50Views?.differences || []; $('b50-differences-label').textContent = `私服名单与落雪导入估算的差异（${changes.length} 张）`;
  $('b50-differences').replaceChildren();
  for (const r of changes) { const item = document.createElement('p'); item.textContent = `${r.title || 'ID ' + r.musicId} · 难度 ${r.level}：私服${r.sourceGroup === 'old' ? '旧曲' : '新曲'} → ${r.targetGroup ? '落雪' + (r.targetGroup === 'old' ? '旧曲' : '新曲') : '未进入落雪估算 B50'}`; $('b50-differences').appendChild(item); }
}
const diffLabels = {new:'新增',higher:'提高',lower:'降低',mixed:'有升有降',same:'相同'};
function renderComparison() {
  if (!state.data) return;
  const hasRemote = !!state.plan?.remoteComparison;
  $('compare-target').options[1].disabled = !hasRemote;
  if (!hasRemote && $('compare-target').value === 'remote') $('compare-target').value = 'target';
  const remote = $('compare-target').value === 'remote';
  const source = state.data.b50Views?.source, target = remote ? state.plan?.remoteB50 : state.data.b50Views?.target;
  const comparison = remote ? state.plan?.remoteComparison : state.data.b50Views?.comparison;
  $('compare-source-total').textContent = source?.rating ?? '未知'; $('compare-target-total').textContent = target?.rating ?? '未知';
  $('compare-target-title').textContent = remote ? '落雪账号 B50（估算）' : '本次导入 B50（落雪估算）';
  const detail = v => v ? `旧曲 ${v.old.length} 张 / ${v.oldRating ?? '—'} · 新曲 ${v.new.length} 张 / ${v.newRating ?? '—'}` : '未读取';
  $('compare-source-detail').textContent = detail(source); $('compare-target-detail').textContent = detail(target);
  const delta = comparison?.ratingDelta; $('compare-total-delta').textContent = delta == null ? '—' : `${delta > 0 ? '+' : ''}${delta}`;
  $('compare-info').textContent = comparison?.available ? '按同一 musicId + 难度对齐。私服单曲 Rating 未导出，留空；右侧是估算。颜色标出分组、名次、达成率和名单变化。' : (source?.warnings?.join('；') || '请重新导入包含私服 B50 名单的完整 JSON。');
  const labels = {same:'一致',source_only:'仅私服 B50',target_only:'仅落雪 B50',group_changed:'分组变化',score_changed:'达成率变化',rank_changed:'名次变化'};
  $('compare-counts').replaceChildren();
  for (const [kind,count] of Object.entries(comparison?.counts || {})) { const badge = document.createElement('span'); badge.className = 'compare-badge ' + kind; badge.textContent = `${labels[kind]} ${count}`; $('compare-counts').appendChild(badge); }
  $('comparison-records').replaceChildren();
  const differences = new Map((state.plan?.rows || []).map(r => [`${r.musicId}:${r.after.level_index}`,r]));
  for (const r of comparison?.rows || []) {
    if ($('compare-only-changed').checked && r.changes.length === 1 && r.changes[0] === 'same') continue;
    const tr = tableRow($('comparison-records')); tr.className = r.changes[0] === 'same' ? '' : 'compare-changed';
    titleCell(tr, `${r.title || '未匹配曲目'} · ${(r.source || r.target).difficulty || r.level}`,r.musicId);
    const group = v => v ? `${v.group === 'old' ? '旧曲' : '新曲'} #${v.position}` : '未入选';
    cell(tr,group(r.source),r.changes.includes('group_changed') ? 'group-change' : '');
    cell(tr,r.source ? r.source.achievements.toFixed(4) + '%' : '—'); cell(tr,r.source?.ra ?? '—');
    cell(tr,group(r.target),r.changes.includes('group_changed') ? 'group-change' : '');
    cell(tr,r.target ? r.target.achievements.toFixed(4) + '%' : '—',r.changes.includes('score_changed') ? 'score-change' : ''); cell(tr,r.target?.ra ?? '—');
    const change = cell(tr,'');
    for (const kind of r.changes) { const badge = document.createElement('span'); badge.className = 'compare-badge ' + kind; badge.textContent = labels[kind]; change.appendChild(badge); }
    const diff = differences.get(`${r.musicId}:${r.level}`);
    if (diff) { const text = document.createElement('small'); text.textContent = `成绩：${diffLabels[diff.category]}${diff.fcChanged ? ' / FC变动' : ''}${diff.fsChanged ? ' / FS变动' : ''}`; change.appendChild(text); }
  }
}
async function prepareDiff() {
  invalidatePlan();
  const plan = await api(userPath('/lxns/prepare'), {});
  state.plan = plan; state.selected = new Set(plan.rows.filter(r => r.recommended).map(r => r.key));
  $('compare-target').value = 'remote'; $('verification').classList.add('hidden');
  renderDiff(); renderB50(); await renderBackups();
}
function renderDiff() {
  $('diff-records').replaceChildren(); const plan = state.plan;
  if (!plan) { $('diff-summary').textContent = '连接落雪后自动对比。原来的官服与私服成绩在落雪同一账号中会合并。'; return; }
  const labels = {new:'新增',higher:'提高',lower:'降低',mixed:'有升有降',same:'完全相同'};
  $('diff-summary').textContent = `已备份落雪 ${plan.remoteCount} 张成绩。` + Object.entries(plan.counts).map(([k,v]) => `${labels[k]} ${v}`).join(' · ') + `。已选择 ${state.selected.size} 张。`;
  const filter = $('diff-filter').value;
  for (const r of plan.rows.filter(r => filter === 'all' || (filter === 'changed' ? r.category !== 'same' : r.category === filter))) {
    const row = tableRow($('diff-records')); const td = cell(row,''); const input = document.createElement('input'); input.type = 'checkbox'; input.checked = state.selected.has(r.key); input.disabled = r.category === 'same' || state.busy || plan.used; input.setAttribute('aria-label', `选择 ${r.title} ${r.difficulty} ${r.key}`);
    input.addEventListener('change', () => { if (input.checked) state.selected.add(r.key); else state.selected.delete(r.key); $('allow-lower').checked = false; renderDiff(); syncControls(); }); td.appendChild(input);
    titleCell(row, `${r.title} · ${r.difficulty}`, r.musicId);
    cell(row, r.before ? r.before.achievements.toFixed(4) + '%' : '无'); cell(row,r.after.achievements.toFixed(4) + '%','score-achievement'); cell(row, `${r.before?.dx_score ?? '无'} → ${r.after.dx_score}`);
    const marks = s => s ? `${(s.fc || '—').toUpperCase()} / ${(s.fs || '—').toUpperCase()}` : '无'; cell(row, `${marks(r.before)} → ${marks(r.after)}`);
    cell(row, labels[r.category] + (r.fcChanged ? ' · FC变化' : '') + (r.fsChanged ? ' · FS变化' : ''), r.hasLower ? 'risk-change' : '');
  }
  $('download-backup').classList.remove('hidden'); $('download-backup').href = userPath('/lxns/backups/' + plan.backup.id);
}
async function renderBackups() { const data = await api(userPath('/lxns/backups')); $('backup-history').replaceChildren(); for (const b of data.backups) { const a = document.createElement('a'); a.href = userPath('/lxns/backups/' + b.id); a.download = ''; a.textContent = `${new Date(b.created_at).toLocaleString()} · ${b.phase} · 账号 ${b.friend_code}`; $('backup-history').appendChild(a); } }
function renderRecords() {
  const query = $('search').value.toLocaleLowerCase().trim();
  const all = (state.preview?.scores || []).filter(r => (r.title + ' ' + r.musicId).toLocaleLowerCase().includes(query));
  const pages = Math.max(1, Math.ceil(all.length / 15)); state.page = Math.min(state.page, pages - 1);
  $('records').replaceChildren();
  for (const r of all.slice(state.page * 15, state.page * 15 + 15)) {
    const row = tableRow($('records')); titleCell(row, r.title, r.musicId); cell(row, r.type === 'dx' ? 'DX' : '标准'); difficultyCell(row, r.difficulty); cell(row, r.achievements.toFixed(4) + '%', 'score-achievement'); cell(row, r.dx_score); cell(row, (r.fc || '—').toUpperCase() + ' / ' + (r.fs || '—').toUpperCase());
  }
  if (!all.length) cell(tableRow($('records')), '没有符合条件的成绩').colSpan = 6;
  $('page-label').textContent = `${all.length} 张谱面 · 第 ${state.page + 1} / ${pages} 页`;
  $('prev').disabled = state.page === 0; $('next').disabled = state.page >= pages - 1;
}
function render() {
  const d = state.data, p = state.preview;
  if (!d) return;
  $('summary').classList.remove('hidden'); $('empty').classList.add('hidden');
  $('player-name').textContent = d.player.name || state.user;
  $('source-version').textContent = `AquaDX 版本 ${d.player.romVersion || '未知'} · 数据 ${d.player.dataVersion || '未知'}`;
  $('total').textContent = d.best.length; $('matched').textContent = p ? p.exportable : '—'; $('rejected-count').textContent = p ? p.rejected.length : '—';
  $('marks').textContent = `${d.statistics.fcOrBetter} / ${d.statistics.apOrBetter}`;
  $('rating-label').textContent = `本地计算 Rating ${d.rating.toLocaleString()} · 私服自报 ${d.player.rating ?? '未知'}`;
  $('rating-message').textContent = d.calculation.ratingComplete ? '计算依照本地曲库的新旧版本划分。' : '本地分析曲库不完整，计算值可能与私服不同。';
  $('missing-label').textContent = p ? `（${p.rejected.length} 张）` : '（等待曲库）';
  $('missing-list').replaceChildren();
  const privateNames = new Map((d.privateCatalog?.rows || []).map(r => [r.musicId + ':' + r.level, r.title]));
  for (const r of p?.rejected || []) { const item = document.createElement('div'); item.className = 'missing-item'; item.textContent = `${privateNames.get(r.musicId + ':' + r.level) || '未知曲目'} · ID ${r.musicId} · ${r.difficulty} · ${r.reason}`; $('missing-list').appendChild(item); }
  $('missing').classList.toggle('hidden', !!p && !p.rejected.length);
  $('download').href = userPath('/lxns/download');
  renderB50(); renderDiff(); renderPrivate();
  $('plate-records').replaceChildren();
  for (const [version, marks] of Object.entries(d.plates)) { const row = tableRow($('plate-records')); cell(row, version); for (const mark of ['将', '极', '神', '舞舞']) { const m = marks[mark]; cell(row, m.supported ? `${m.completed} / ${m.total}${m.achieved ? ' ✓' : ''}` : '不支持'); } }
  renderRecords(); syncControls();
}
async function load() {
  state.user = $('user-id').value.trim();
  if (!state.user) throw new Error('请填写本地玩家 ID。');
  state.data = null; state.preview = null; $('summary').classList.add('hidden'); $('empty').classList.remove('hidden');
  invalidatePlan();
  state.data = await api(userPath('/dashboard'));
  try { state.preview = await api(userPath('/lxns/preview')); } catch (error) { notice(error.message, true); }
  state.page = 0; $('allow-partial').checked = false; render();
  await renderBackups();
  if (state.account) await prepareDiff();
}
$('load').addEventListener('click', () => run(async () => { await load(); if (state.preview) notice(`已加载 ${state.preview.total} 张最佳谱面，请核对上传预览。`); }));
$('file').addEventListener('change', () => run(async () => {
  const file = $('file').files[0]; if (!file) return;
  if (file.size > 20 * 1024 * 1024) throw new Error('文件超过 20 MB，请确认选择了 AquaDX 导出的 JSON。');
  state.user = $('user-id').value.trim(); if (!state.user) throw new Error('请填写本地玩家 ID。');
  let data; try { data = JSON.parse((await file.text()).replace(/^\uFEFF/, '')); } catch { throw new Error('文件不是有效的 JSON。'); }
  await api('/user/' + encodeURIComponent(state.user) + '/import', data); $('file-label').textContent = file.name; await load();
  if (state.preview) notice(`导入完成：${state.preview.total} 张最佳谱面，落雪可匹配 ${state.preview.exportable} 张。`);
}));
$('connect').addEventListener('click', () => run(async () => {
  const token = $('token').value.trim(); if (!token) throw new Error('请填写落雪个人 API 密钥。');
  try { const result = await api('/api/lxns/connect', {token}); state.account = result.account; } finally { $('token').value = ''; }
  invalidatePlan();
  if (state.data) { state.preview = await api(userPath('/lxns/preview')); render(); }
  if (state.data) await prepareDiff();
  notice(state.data ? `已连接 ${state.account.name}，已自动备份并对比 B50 和成绩差异；尚未上传。` : `已连接 ${state.account.name}，请先导入成绩。`);
}));
$('disconnect').addEventListener('click', () => run(async () => { await api('/api/lxns/disconnect', {}); state.account = null; invalidatePlan(); if (state.data) { state.preview = await api(userPath('/lxns/preview')); render(); } notice('已断开落雪连接并清除本次密钥。'); }));
$('refresh-catalog').addEventListener('click', () => run(async () => { const data = await api('/api/lxns/catalog/refresh', {}); if (state.data) { state.preview = await api(userPath('/lxns/preview')); state.data = await api(userPath('/dashboard')); invalidatePlan(); $('allow-partial').checked = false; render(); if (state.account) await prepareDiff(); } notice(`落雪曲库已更新：${data.songs} 首曲目、${data.charts} 张普通谱面。`); }));
$('allow-partial').addEventListener('change', syncControls);
$('allow-lower').addEventListener('change', syncControls);
$('prepare-diff').addEventListener('click', () => run(async () => { await prepareDiff(); notice('落雪原成绩已备份；B50 和成绩差异已自动更新，尚未上传。'); }));
$('select-all').addEventListener('click', () => { state.selected = new Set((state.plan?.rows || []).filter(r => r.category !== 'same').map(r => r.key)); $('allow-lower').checked = false; renderDiff(); syncControls(); });
$('diff-filter').addEventListener('change', renderDiff);
$('select-recommended').addEventListener('click', () => { state.selected = new Set((state.plan?.rows || []).filter(r => r.recommended).map(r => r.key)); $('allow-lower').checked = false; renderDiff(); syncControls(); });
$('clear-selection').addEventListener('click', () => { state.selected.clear(); $('allow-lower').checked = false; renderDiff(); syncControls(); });
for (const mode of ['compare','source','target','remote','local']) $('b50-' + mode).addEventListener('click', () => { state.b50Mode = mode; renderB50(); });
$('compare-target').addEventListener('change',renderComparison);
$('compare-only-changed').addEventListener('change',renderComparison);
$('search').addEventListener('input', () => { state.page = 0; renderRecords(); });
$('prev').addEventListener('click', () => { state.page--; renderRecords(); });
$('next').addEventListener('click', () => { state.page++; renderRecords(); });
for (const name of ['preview', 'b50', 'diff', 'private', 'plates']) $('tab-' + name).addEventListener('click', () => showTab(name));
$('review-upload').addEventListener('click', () => {
  const p = state.preview; if (!p || $('review-upload').disabled) return;
  $('confirm-account').textContent = `目标玩家：${p.account.name} · 好友码 ${p.account.friend_code}`;
  const lower = state.plan.rows.filter(r => state.selected.has(r.key) && r.hasLower).length;
  $('confirm-count').textContent = `只提交所选 ${state.selected.size} 张（其中 ${lower} 张含降低字段），不提交其他 ${p.exportable - state.selected.size} 张匹配成绩；跳过 ${p.rejected.length} 张未匹配谱面。上传前备份已保存，提交前会再次核对落雪原成绩。`;
  $('confirm-dialog').showModal();
});
$('cancel-upload').addEventListener('click', () => $('confirm-dialog').close());
$('confirm-upload').addEventListener('click', () => run(async () => {
  const p = state.preview;
  const result = await api(userPath('/lxns/upload'), { fingerprint: state.plan.fingerprint, plan_id: state.plan.plan_id, selected_keys: [...state.selected], allow_lower: $('allow-lower').checked, allow_partial: $('allow-partial').checked, confirmed: true });
  $('confirm-dialog').close(); $('allow-partial').checked = false;
  state.selected.clear(); $('allow-lower').checked = false;
  state.plan.used = true; state.plan.backup = result.backup;
  const v = result.verification; const text = v.available ? `回读核对：完全一致 ${v.counts.exact}，落雪保留更高值 ${v.counts.stronger}，字段不一致 ${v.counts.different}，未找到 ${v.counts.missing}。` : v.message;
  $('verification').textContent = text; $('verification').classList.remove('hidden'); $('verification').classList.toggle('error', !v.available || !!v.counts?.different || !!v.counts?.missing); $('download-backup').href = userPath('/lxns/backups/' + result.backup.id);
  showTab('diff'); await renderBackups(); notice(`请求已被落雪确认，提交 ${result.submitted} 张，未选 ${result.notSelected} 张。${text}`);
}));
run(async () => {
  const session = await api('/api/lxns/session'); state.account = session.account;
  try { await load(); } catch (error) { if (!error.message.includes('没有已存成绩')) notice(error.message, true); }
});

function renderPrivate() {
  const view = state.data?.privateCatalog; if (!view) return;
  $('private-info').textContent = `全部 ${view.rows.length} 张 · 已知曲名 ${view.known} · 待补充 ${view.unknown} · 日服参考库 ${view.referenceCharts} 张谱面`;
  $('private-download').href = userPath('/private/download');
  const query = $('private-search').value.trim().toLowerCase();
  $('private-records').replaceChildren();
  for (const r of view.rows.filter(r => !query || (r.title || '').toLowerCase().includes(query) || String(r.musicId).includes(query))) {
    const row = tableRow($('private-records'));
    titleCell(row, `${r.title || '未知曲目'} · ${r.difficulty}`, r.musicId);
    cell(row, r.ds == null ? '未知' : `${r.ds}${r.referenceOnly ? '（日服）' : '（本地）'}`);
    cell(row, r.version || '未知');
    cell(row, `${r.achievements.toFixed(4)}% / ${r.dxScore}`, 'score-achievement');
    cell(row, `${r.fc || '—'} / ${r.fs || '—'}`);
    cell(row, r.lxnsSupported ? '已收录' : '仅本地展示');
    row.title = r.metadataSource || '尚无可核实曲库信息';
  }
}
$('private-search').addEventListener('input', renderPrivate);

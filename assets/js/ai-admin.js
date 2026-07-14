const scenarios = {
  automation: {
    company: 'Demo Logistics Ukraine',
    contact: 'operations@example.com',
    request: 'Ми отримуємо близько 80 заявок на день через пошту і сайт. Потрібно автоматично класифікувати їх, готувати чернетки відповідей, створювати завдання для менеджерів і формувати щоденний звіт директору.',
    score: 91,
    risk: 'Low',
    price: '24 000 грн запуск + 7 500 грн/міс.',
    scope: 'Пошта + форма сайту → класифікація → чернетка відповіді → задача менеджеру → щоденний звіт.'
  },
  analytics: {
    company: 'Demo Manufacturing Group',
    contact: 'director@example.com',
    request: 'Щопонеділка директор вручну збирає дані з Excel, пошти та CRM. Потрібен короткий звіт із KPI, проблемами, простроченими задачами та рекомендаціями.',
    score: 86,
    risk: 'Medium',
    price: '29 000 грн запуск + 9 500 грн/міс.',
    scope: 'Excel + CRM + пошта → перевірка якості → KPI dashboard → executive summary → evidence log.'
  },
  support: {
    company: 'Demo Service Company',
    contact: 'support@example.com',
    request: 'Потрібен AI-помічник, який відповідатиме на стандартні питання клієнтів з бази знань, але передаватиме складні та ризикові випадки людині.',
    score: 83,
    risk: 'Medium',
    price: '22 000 грн запуск + 8 000 грн/міс.',
    scope: 'Запит → пошук у затвердженій базі знань → чернетка відповіді → risk routing → журнал джерел.'
  }
};

const els = {
  scenario: document.getElementById('scenario'),
  company: document.getElementById('company'),
  contact: document.getElementById('contact'),
  request: document.getElementById('request'),
  run: document.getElementById('runDemo'),
  sample: document.getElementById('loadSample'),
  reset: document.getElementById('resetDemo'),
  output: document.getElementById('output'),
  log: document.getElementById('evidenceLog'),
  lead: document.getElementById('leadScore'),
  risk: document.getElementById('riskScore'),
  evidenceId: document.getElementById('evidenceId'),
  approval: document.getElementById('approvalState'),
  approvalActions: document.getElementById('approvalActions'),
  approve: document.getElementById('approve'),
  reject: document.getElementById('reject')
};

function loadScenario(key) {
  const data = scenarios[key];
  els.company.value = data.company;
  els.contact.value = data.contact;
  els.request.value = data.request;
  resetState(false);
}

function setStep(step, state, text) {
  const node = document.querySelector(`[data-step="${step}"]`);
  node.dataset.state = state;
  node.querySelector('.status').textContent = text;
}

function makeEvidenceId() {
  const now = new Date();
  const stamp = now.toISOString().slice(0, 10).replaceAll('-', '');
  return `BADS-${stamp}-${String(Math.floor(Math.random() * 900) + 100)}`;
}

function simpleHash(value) {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) hash = ((hash << 5) - hash) + value.charCodeAt(i) | 0;
  return `demo-${Math.abs(hash).toString(16).padStart(8, '0')}`;
}

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function renderEvidence(evidenceId, inputHash, data) {
  const time = new Date().toLocaleString('uk-UA');
  const rows = [
    ['Input captured', `${time} · Source: pilot web form · Hash: ${inputHash}`],
    ['Policy applied', 'BADS-AI-ADMIN-PILOT v0.1 · No autonomous external actions'],
    ['Qualification decision', `Lead score ${data.score}/100 · Risk ${data.risk} · Human review required`],
    ['Proposal generated', `Scope and pricing produced from approved pilot template · ${data.price}`],
    ['Evidence package sealed', `${evidenceId} · Synthetic demo only · Awaiting owner approval`]
  ];
  els.log.innerHTML = rows.map(([title, detail]) => `<div class="evidence-row"><b>${title}</b><small>${detail}</small></div>`).join('');
}

async function runDemo() {
  const key = els.scenario.value;
  const data = scenarios[key];
  const company = els.company.value.trim() || data.company;
  const request = els.request.value.trim();
  const evidenceId = makeEvidenceId();
  const inputHash = simpleHash(`${company}|${els.contact.value}|${request}`);

  els.run.disabled = true;
  els.approvalActions.classList.add('hidden');
  els.output.textContent = 'Агенти обробляють заявку…';
  els.lead.textContent = '…';
  els.risk.textContent = '…';
  els.evidenceId.textContent = '…';
  els.approval.textContent = 'Required';

  for (let step = 1; step <= 5; step += 1) {
    setStep(step, 'running', 'Працює');
    await wait(420);
    setStep(step, 'done', 'Готово');
  }
  setStep(6, 'waiting', 'Потрібне рішення');

  els.lead.textContent = `${data.score}/100`;
  els.risk.textContent = data.risk;
  els.evidenceId.textContent = evidenceId;
  els.output.textContent = `ПІЛОТНА ПРОПОЗИЦІЯ ДЛЯ ${company.toUpperCase()}\n\nПроблема\n${request}\n\nЗапропонований workflow\n${data.scope}\n\nПілотний пакет\n• 1 discovery-сесія\n• карта процесу та ризиків\n• робоче демо на синтетичних або погоджених даних\n• human-in-the-loop approval\n• Evidence ID, журнал джерел і дій\n• підсумковий звіт та roadmap\n\nОрієнтовна комерційна модель\n${data.price}\n\nНаступний крок\n30-хвилинне уточнення процесу та погодження одного KPI пілоту. Чернетка не буде надіслана без ручного погодження.`;
  renderEvidence(evidenceId, inputHash, data);
  els.approvalActions.classList.remove('hidden');
  els.run.disabled = false;
}

function resetState(clearFields = false) {
  for (let step = 1; step <= 6; step += 1) setStep(step, 'idle', 'Очікує');
  els.output.textContent = 'Запустіть демо, щоб агенти підготували результат.';
  els.log.innerHTML = '<div class="evidence-row">Evidence Agent ще не запускався.<small>Журнал буде створено після обробки заявки.</small></div>';
  els.lead.textContent = '—';
  els.risk.textContent = '—';
  els.evidenceId.textContent = '—';
  els.approval.textContent = 'Required';
  els.approvalActions.classList.add('hidden');
  if (clearFields) loadScenario('automation');
}

els.run.addEventListener('click', runDemo);
els.scenario.addEventListener('change', event => loadScenario(event.target.value));
els.sample.addEventListener('click', () => {
  const keys = Object.keys(scenarios);
  const current = keys.indexOf(els.scenario.value);
  const next = keys[(current + 1) % keys.length];
  els.scenario.value = next;
  loadScenario(next);
});
els.reset.addEventListener('click', () => resetState(true));
els.approve.addEventListener('click', () => {
  setStep(6, 'done', 'Погоджено');
  els.approval.textContent = 'Approved';
  els.approvalActions.classList.add('hidden');
  els.log.insertAdjacentHTML('beforeend', `<div class="evidence-row"><b>Human approval recorded</b><small>${new Date().toLocaleString('uk-UA')} · Demo owner approved the draft. No external message was actually sent.</small></div>`);
});
els.reject.addEventListener('click', () => {
  setStep(6, 'waiting', 'На доопрацюванні');
  els.approval.textContent = 'Revision';
  els.log.insertAdjacentHTML('beforeend', `<div class="evidence-row"><b>Revision requested</b><small>${new Date().toLocaleString('uk-UA')} · Draft returned to Proposal Agent. No external action occurred.</small></div>`);
});

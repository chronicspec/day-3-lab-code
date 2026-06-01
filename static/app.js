const $ = (sel) => document.querySelector(sel);

const messagesEl = $('#messages');
const inputEl = $('#input');
const btnSend = $('#btn-send');
const btnClear = $('#btn-clear');
const btnExport = $('#btn-export');
const statusPill = $('#status-pill');

const traceEl = $('#trace');
const traceEmpty = $('#trace-empty');

const latencyVal = $('#telemetry .metric:nth-child(1) .metric-value');
const costVal = $('#telemetry .metric:nth-child(2) .metric-value');
const tokensVal = $('#telemetry .metric:nth-child(3) .metric-value');
const providerVal = $('#telemetry .metric:nth-child(4) .metric-value');

let lastTrace = null;

function nowTime(){
  const d=new Date();
  return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
}

function escapeHtml(str){
  return String(str)
    .replaceAll('&','&amp;')
    .replaceAll('<','<')
    .replaceAll('>','>');
}

function addMessage(role, text){
  const msg = document.createElement('div');
  msg.className = 'message';

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? '👤' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = `bubble ${role === 'user' ? 'user' : 'assistant'}`;

  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = role === 'user' ? `Bạn • ${nowTime()}` : `Assistant • ${nowTime()}`;

  const content = document.createElement('div');
  content.className = 'text';
  content.innerHTML = escapeHtml(text);

  bubble.appendChild(meta);
  bubble.appendChild(content);
  msg.appendChild(avatar);
  msg.appendChild(bubble);

  messagesEl.appendChild(msg);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatusReady(){
  statusPill.textContent = 'Sẵn sàng';
}
function setStatusLoading(){
  statusPill.innerHTML = '<span class="loading" style="display:inline-block;margin-right:8px;"></span>Đang xử lý...';
}

function renderTrace(trace){
  traceEl.innerHTML = '';
  if(!trace || trace.length === 0){
    traceEmpty.style.display = 'block';
    return;
  }
  traceEmpty.style.display = 'none';

  for(const step of trace){
    const card = document.createElement('div');
    card.className = 'trace-step';

    const k = document.createElement('div');
    k.className = 'k';
    k.textContent = `Trace step`;

    const v = document.createElement('div');
    v.className = 'v';
    v.textContent = (step.llm_output ?? '');

    card.appendChild(k);
    card.appendChild(v);
    traceEl.appendChild(card);
  }
}

function renderTelemetry(telemetry){
  // UI giữ cấu trúc, nhưng server hiện gửi {} nếu chưa expose metrics.
  latencyVal.textContent = telemetry?.latency_ms != null ? telemetry.latency_ms + ' ms' : '—';
  costVal.textContent = telemetry?.cost_estimate != null ? String(telemetry.cost_estimate) : '—';
  tokensVal.textContent = telemetry?.total_tokens != null ? String(telemetry.total_tokens) : '—';
  providerVal.textContent = telemetry?.provider ?? '—';
}

async function send(){
  const userText = inputEl.value.trim();
  if(!userText) return;

  inputEl.value = '';
  addMessage('user', userText);

  setStatusLoading();
  btnSend.disabled = true;

  // assistant placeholder
  addMessage('assistant', 'Đang tạo itinerary...');
  const lastAssistant = messagesEl.lastElementChild;
  const lastBubbleText = lastAssistant.querySelector('.text');

  try{
    const res = await fetch('/api/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ user_input: userText })
    });

    const data = await res.json();
    if(data.error){
      lastBubbleText.textContent = data.error;
      throw new Error(data.error);
    }

    lastBubbleText.textContent = data.final_answer || '';
    lastTrace = data;

    renderTrace(data.trace);
    renderTelemetry(data.telemetry);
    setStatusReady();
  }catch(err){
    console.error(err);
    setStatusReady();
  }finally{
    btnSend.disabled = false;
  }
}

btnSend.addEventListener('click', send);
btnClear.addEventListener('click', () => {
  messagesEl.innerHTML = '';
  traceEl.innerHTML = '';
  traceEmpty.style.display = 'block';
  lastTrace = null;
  renderTelemetry({});
  setStatusReady();
});

btnExport.addEventListener('click', async () => {
  if(!lastTrace){
    alert('Chưa có trace để export.');
    return;
  }
  const txt = JSON.stringify(lastTrace, null, 2);
  try{
    await navigator.clipboard.writeText(txt);
    alert('Đã copy trace JSON vào clipboard.');
  }catch{
    const blob = new Blob([txt], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trace-${lastTrace.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
});

inputEl.addEventListener('keydown', (e) => {
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    send();
  }
});


/* ——— Translation App JavaScript ——— */

// Translations for JavaScript messages
const translations = {
  'en': {
    'suggestions': 'Suggestions...',
    'no_suggestions': 'No suggestions',
    'error_getting_suggestions': 'Error getting suggestions',
    'correcting_sentence': 'Correcting sentence…',
    'change_reverted_inconsistent': 'Change reverted — inconsistent with source',
    'failed_to_correct_reverted': 'Failed to correct — reverted',
    'translating': 'Translating…',
    'detected': 'Detected'
  },
  'pl': {
    'suggestions': 'Propozycje...',
    'no_suggestions': 'Brak propozycji',
    'error_getting_suggestions': 'Błąd pobierania propozycji',
    'correcting_sentence': 'Koryguję zdanie…',
    'change_reverted_inconsistent': 'Zmiana cofnięta — niespójna ze źródłem',
    'failed_to_correct_reverted': 'Nie udało się skorygować — cofnięto',
    'translating': 'W trakcie tłumaczenia…',
    'detected': 'Wykryto'
  },
  'de': {
    'suggestions': 'Vorschläge...',
    'no_suggestions': 'Keine Vorschläge',
    'error_getting_suggestions': 'Fehler beim Abrufen der Vorschläge',
    'correcting_sentence': 'Korrigiere Satz…',
    'change_reverted_inconsistent': 'Änderung rückgängig — inkonsistent mit Quelle',
    'failed_to_correct_reverted': 'Korrektur fehlgeschlagen — rückgängig gemacht',
    'translating': 'Übersetze…',
    'detected': 'Erkannt'
  },
  'fr': {
    'suggestions': 'Suggestions...',
    'no_suggestions': 'Aucune suggestion',
    'error_getting_suggestions': 'Erreur lors de la récupération des suggestions',
    'correcting_sentence': 'Correction de la phrase…',
    'change_reverted_inconsistent': 'Changement annulé — incohérent avec la source',
    'failed_to_correct_reverted': 'Échec de la correction — annulé',
    'translating': 'Traduction…',
    'detected': 'Détecté'
  },
  'es': {
    'suggestions': 'Sugerencias...',
    'no_suggestions': 'Sin sugerencias',
    'error_getting_suggestions': 'Error al obtener sugerencias',
    'correcting_sentence': 'Corrigiendo oración…',
    'change_reverted_inconsistent': 'Cambio revertido — inconsistente con el origen',
    'failed_to_correct_reverted': 'Falló la corrección — revertido',
    'translating': 'Traduciendo…',
    'detected': 'Detectado'
  },
  'cs': {
    'suggestions': 'Návrhy...',
    'no_suggestions': 'Žádné návrhy',
    'error_getting_suggestions': 'Chyba při získávání návrhů',
    'correcting_sentence': 'Opravuji větu…',
    'change_reverted_inconsistent': 'Změna vrácena — nekonzistentní se zdrojem',
    'failed_to_correct_reverted': 'Oprava selhala — vráceno',
    'translating': 'Překládám…',
    'detected': 'Detekováno'
  },
  'zh': {
    'suggestions': '建议...',
    'no_suggestions': '无建议',
    'error_getting_suggestions': '获取建议时出错',
    'correcting_sentence': '正在纠正句子…',
    'change_reverted_inconsistent': '更改已撤销 — 与源不一致',
    'failed_to_correct_reverted': '纠正失败 — 已撤销',
    'translating': '翻译中…',
    'detected': '已检测'
  },
  'hi': {
    'suggestions': 'सुझाव...',
    'no_suggestions': 'कोई सुझाव नहीं',
    'error_getting_suggestions': 'सुझाव प्राप्त करने में त्रुटि',
    'correcting_sentence': 'वाक्य सुधार रहे हैं…',
    'change_reverted_inconsistent': 'परिवर्तन वापस किया गया — स्रोत के साथ असंगत',
    'failed_to_correct_reverted': 'सुधार असफल — वापस किया गया',
    'translating': 'अनुवाद हो रहा है…',
    'detected': 'पहचाना गया'
  },
  'ar': {
    'suggestions': 'اقتراحات...',
    'no_suggestions': 'لا توجد اقتراحات',
    'error_getting_suggestions': 'خطأ في الحصول على الاقتراحات',
    'correcting_sentence': 'تصحيح الجملة…',
    'change_reverted_inconsistent': 'تم التراجع عن التغيير — غير متسق مع المصدر',
    'failed_to_correct_reverted': 'فشل التصحيح — تم التراجع',
    'translating': 'جارٍ الترجمة…',
    'detected': 'تم الكشف'
  },
  'ru': {
    'suggestions': 'Предложения...',
    'no_suggestions': 'Нет предложений',
    'error_getting_suggestions': 'Ошибка получения предложений',
    'correcting_sentence': 'Исправляю предложение…',
    'change_reverted_inconsistent': 'Изменение отменено — несовместимо с источником',
    'failed_to_correct_reverted': 'Исправление не удалось — отменено',
    'translating': 'Переводим…',
    'detected': 'Обнаружено'
  },
  'ja': {
    'suggestions': '提案...',
    'no_suggestions': '提案なし',
    'error_getting_suggestions': '提案の取得エラー',
    'correcting_sentence': '文を修正中…',
    'change_reverted_inconsistent': '変更が取り消されました — ソースと一致しません',
    'failed_to_correct_reverted': '修正に失敗しました — 取り消されました',
    'translating': '翻訳中…',
    'detected': '検出済み'
  }
};

// Get current language from HTML lang attribute
const currentLang = document.documentElement.lang || 'en';
const t = translations[currentLang] || translations['en'];

function _(key) {
  return t[key] || key;
}

function setStatus(text, timeoutMs){
  const box = document.getElementById('status');
  const statusText = document.getElementById('status_text');
  if(text){ statusText.textContent = text; box.style.display = 'inline-flex'; }
  else { box.style.display = 'none'; }
  if(text && timeoutMs){ setTimeout(()=>{ box.style.display='none'; }, timeoutMs); }
}

function autoGrow(el){
  if(!el) return;
  el.style.height = 'auto';
  el.style.height = (el.scrollHeight) + 'px';
  syncResultMinHeight();
}

function syncResultMinHeight(){
  const src = document.getElementById('source_text');
  const res = document.getElementById('result');
  if(src && res){
    const h = (parseFloat(getComputedStyle(src).height) || src.scrollHeight) + 'px';
    res.style.minHeight = h;
  }
}

let lastDetectedLang = null;

function setSelectValue(sel, val){
  if(!sel) return;
  const opt = Array.from(sel.options).find(o => o.value === val);
  if(opt) sel.value = val;
}

function getPlainResult(){ return document.getElementById('result').innerText; }
function setResultPlain(text){ renderResultInteractive(text); }

function swap(){
  const srcTa = document.getElementById('source_text');
  const resTxt = getPlainResult();
  const prevSourceSel = document.getElementById('source_lang');
  const prevTargetSel = document.getElementById('target_lang');

  const prevSourceLang = prevSourceSel.value;
  const prevTargetLang = prevTargetSel.value;

  const oldSrc = srcTa.value;
  srcTa.value = resTxt;
  autoGrow(srcTa);
  setResultPlain(oldSrc);

  setSelectValue(prevSourceSel, prevTargetLang);
  if(prevSourceLang !== 'auto'){
    setSelectValue(prevTargetSel, prevSourceLang);
  } else {
    const fallback = lastDetectedLang && lastDetectedLang !== 'auto' ? lastDetectedLang : 'de';
    setSelectValue(prevTargetSel, fallback);
  }

  savePrefs();
  triggerAutoTranslate();
}

// History management using localStorage
function getHistoryItems(){
  try {
    const stored = localStorage.getItem('lt_history');
    return stored ? JSON.parse(stored) : [];
  } catch(e) {
    return [];
  }
}

function saveHistoryItems(items){
  try {
    localStorage.setItem('lt_history', JSON.stringify(items.slice(0,5)));
  } catch(e) {}
}

let historyItems = getHistoryItems();

function renderHistoryChips(){
  const wrap = document.getElementById('history');
  if(!wrap) return;
  wrap.innerHTML = '';
  const items = historyItems.slice(0,5);
  if(items.length === 0){
    const span = document.createElement('span');
    span.className = 'small';
    span.style.color = '#94a3b8';
    // Get "none" text from template - for multi-language support
    const noneTexts = {
      'en': 'none',
      'es': 'ninguna', 
      'fr': 'aucune',
      'de': 'keine',
      'pl': 'brak',
      'it': 'nessuna',
      'pt': 'nenhuma',
      'ru': 'нет',
      'zh': '无',
      'hi': 'कोई नहीं',
      'ar': 'لا توجد',
      'ja': 'なし',
      'ko': '없음'
    };
    span.textContent = noneTexts[currentLang] || 'none';
    wrap.appendChild(span);
    return;
  }
  items.forEach((item, idx) => {
    const chip = document.createElement('div');
    chip.className = 'chip';
    const short = (item.source || '').replace(/\n/g,' ').slice(0,40) + ((item.source||'').length>40?'...':'');
    chip.textContent = short;
    chip.dataset.historyIndex = idx;
    chip.addEventListener('click', ()=>loadHistory(idx));
    wrap.appendChild(chip);
  });
}

let userChosenPhrases = [];
let altMenuEl = null;
let lastClickedToken = null;

function clearAltMenu(){ if(altMenuEl && altMenuEl.parentNode){ altMenuEl.parentNode.removeChild(altMenuEl); } altMenuEl = null; }

function tokenizeForUI(text){
  const parts = text.split(/(\s+|[.,!?;:()«»„"""—–-])/g).filter(p => p !== undefined && p !== null && p !== '');
  return parts;
}

function renderResultInteractive(text){
  const box = document.getElementById('result');
  box.innerHTML = '';
  const frag = document.createDocumentFragment();
  const parts = tokenizeForUI(text);
  parts.forEach((p) => {
    if (/^\s+$/.test(p) || /^[.,!?;:()«»„"""—–-]$/.test(p)) {
      frag.appendChild(document.createTextNode(p));
    } else {
      const span = document.createElement('span');
      span.className = 'token';
      span.textContent = p;
      span.dataset.token = p;
      span.addEventListener('click', (e)=>onTokenClick(e, p, span));
      frag.appendChild(span);
    }
  });
  box.appendChild(frag);
}

async function onTokenClick(ev, token, el){
  clearAltMenu();
  lastClickedToken = token;
  const src = document.getElementById('source_text').value.trim();
  const tgt = getPlainResult().trim();
  if(!src || !tgt) return;

  const menu = document.createElement('div');
  menu.className = 'alt-menu';
  menu.innerHTML = `<div class="small" style="padding:6px 10px;color:#64748b">${_('suggestions')}</div>`;
  document.body.appendChild(menu);
  altMenuEl = menu;

  const rect = el.getBoundingClientRect();
  menu.style.left = (window.scrollX + rect.left) + 'px';
  menu.style.top = (window.scrollY + rect.bottom + 6) + 'px';

  const payload = {
    source_text: src,
    current_translation: tgt,
    clicked_word: token,
    target_lang: document.getElementById('target_lang').value,
    tone: document.getElementById('tone').value
  };

  try{
    const r = await fetch('/api/alternatives', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    const j = await r.json();
    const list = (j && Array.isArray(j.alternatives)) ? j.alternatives : [];
    if(list.length === 0){
      menu.innerHTML = `<div class="small" style="padding:8px 12px;color:#64748b">${_('no_suggestions')}</div>`;
      return;
    }
    menu.innerHTML = '';
    list.forEach(alt => {
      const item = document.createElement('div');
      item.className = 'alt-item';
      item.textContent = alt;
      item.addEventListener('click', async ()=> {
        clearAltMenu();
        await applyReplacement(alt);
      });
      menu.appendChild(item);
    });
  }catch(e){
    menu.innerHTML = `<div class="small" style="padding:8px 12px;color:#b91c1c">${_('error_getting_suggestions')}</div>`;
  }
}

function escapeRegExp(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
function replaceTokenOnce(text, from, to){
  if(!from) return text;
  const re = new RegExp('(^|\\b)' + escapeRegExp(from) + '(\\b|$)');
  return text.replace(re, (m, p1, p2)=> p1 + to + p2);
}

async function applyReplacement(selectedPhrase){
  if(!userChosenPhrases.includes(selectedPhrase)) userChosenPhrases.push(selectedPhrase);

  const src = document.getElementById('source_text').value.trim();
  const before = getPlainResult();
  const draft = replaceTokenOnce(before, lastClickedToken, selectedPhrase);
  setResultPlain(draft);

  const payload = {
    source_text: src,
    current_translation: draft,
    target_lang: document.getElementById('target_lang').value,
    tone: document.getElementById('tone').value,
    enforced_phrases: userChosenPhrases,
    replacements: lastClickedToken ? [{from: lastClickedToken, to: selectedPhrase}] : []
  };
  try{
    setStatus(_('correcting_sentence'));
    const r = await fetch('/api/refine', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    const j = await r.json();
    const finalTxt = (j && typeof j.translated === 'string') ? j.translated : '';
    const faithful = (j && typeof j.faithful === 'boolean') ? j.faithful : true;
    if(finalTxt && faithful){
      setResultPlain(finalTxt);
      setStatus('');
    } else {
      setResultPlain(before);
      setStatus(_('change_reverted_inconsistent'), 1600);
      userChosenPhrases = userChosenPhrases.filter(p => p !== selectedPhrase);
    }
  }catch(e){
    setResultPlain(before);
    setStatus(_('failed_to_correct_reverted'), 1600);
    userChosenPhrases = userChosenPhrases.filter(p => p !== selectedPhrase);
  } finally {
    syncResultMinHeight();
  }
}

let debounceId = null;
let reqSeqCounter = 0;
let latestSeq = 0;
let currentAbort = null;
let idleCommitTimer = null;
let latestInputSnapshot = '';
let latestTranslatedSnapshot = '';
let latestTargetSnapshot = '';

function planIdleCommit(){
  if(idleCommitTimer) clearTimeout(idleCommitTimer);
  idleCommitTimer = setTimeout(commitHistoryIfStable, 900);
}

async function commitHistoryIfStable(){
  const currText = document.getElementById('source_text').value.trim();
  const currResult = getPlainResult().trim();
  const currTarget = document.getElementById('target_lang').value;
  if(!currText || !currResult) return;
  if(currText !== latestInputSnapshot || currResult !== latestTranslatedSnapshot || currTarget !== latestTargetSnapshot){
    return;
  }
  
  // Save to localStorage instead of server
  const item = { 
    source: currText, 
    target: currTarget,
    translated: currResult,
    timestamp: Date.now()
  };
  
  // Remove duplicates
  historyItems = historyItems.filter(h => !(h.source === item.source && h.target === item.target));
  // Add to beginning
  historyItems.unshift(item);
  // Keep only 5 items
  if(historyItems.length > 5) historyItems.length = 5;
  
  // Save to localStorage
  saveHistoryItems(historyItems);
  renderHistoryChips();
}

function triggerAutoTranslate(){
  if(debounceId) clearTimeout(debounceId);
  debounceId = setTimeout(()=> autoTranslate(), 350);
}

async function autoTranslate(){
  const source_text = document.getElementById('source_text').value.trim();
  const source_lang = document.getElementById('source_lang').value;
  const target_lang = document.getElementById('target_lang').value;
  const tone = document.getElementById('tone').value;

  userChosenPhrases = [];

  if(!source_text){
    setResultPlain('');
    document.getElementById('detected_badge').style.display='none';
    setStatus('');
    syncResultMinHeight();
    return;
  }

  if(currentAbort) currentAbort.abort();
  const ab = new AbortController();
  currentAbort = ab;
  const mySeq = ++reqSeqCounter;
  latestSeq = mySeq;

  try{
    setStatus(_('translating'));
    const r = await fetch('/api/translate?no_history=1', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ source_text, source_lang, target_lang, tone, seq: mySeq }),
      signal: ab.signal
    });
    const j = await r.json();
    if(j.error){
      setResultPlain('');
      document.getElementById('detected_badge').style.display='none';
      return;
    }
    if(mySeq !== latestSeq){ return; }

    setResultPlain(j.translated || '');
    latestInputSnapshot = source_text;
    latestTranslatedSnapshot = j.translated || '';
    latestTargetSnapshot = target_lang;

    const badge = document.getElementById('detected_badge');
    if(j.detected && j.detected !== 'auto'){
      badge.textContent = _('detected') + ': ' + j.detected;
      badge.style.display = 'inline-block';
      lastDetectedLang = j.detected;
    } else {
      badge.style.display = 'none';
      lastDetectedLang = null;
    }

    planIdleCommit();
  }catch(e){
    if(e.name !== 'AbortError'){ }
  } finally {
    setStatus('');
    syncResultMinHeight();
  }
}

function loadHistory(idx){
  const item = historyItems[idx];
  if(!item) return;
  const ta = document.getElementById('source_text');
  ta.value = item.source;
  autoGrow(ta);
  document.getElementById('target_lang').value = item.target;
  
  // If we have the translated result, show it immediately
  if(item.translated) {
    setResultPlain(item.translated);
  }
  
  savePrefs();
  
  // Only retranslate if we don't have cached result
  if(!item.translated) {
    triggerAutoTranslate();
  }
}

function savePrefs(){
  try {
    localStorage.setItem('lt_source_lang', document.getElementById('source_lang').value);
    localStorage.setItem('lt_target_lang', document.getElementById('target_lang').value);
    localStorage.setItem('lt_tone', document.getElementById('tone').value);
  } catch(e) {}
}

function loadPrefs(){
  try {
    const s = localStorage.getItem('lt_source_lang');
    const t = localStorage.getItem('lt_target_lang');
    const o = localStorage.getItem('lt_tone');
    if(s){ setSelectValue(document.getElementById('source_lang'), s); }
    if(t){ setSelectValue(document.getElementById('target_lang'), t); }
    if(o){ setSelectValue(document.getElementById('tone'), o); }
  } catch(e) {}
}

// Event listeners and initialization
document.addEventListener('DOMContentLoaded', function() {
  // Load history from localStorage - ignore server-side history
  historyItems = getHistoryItems();
  const srcEl = document.getElementById('source_text');
  srcEl.addEventListener('input', ()=> { autoGrow(srcEl); triggerAutoTranslate(); });
  
  ['source_lang','target_lang','tone'].forEach(id => {
    document.getElementById(id).addEventListener('change', ()=> { savePrefs(); triggerAutoTranslate(); });
  });
  
  document.getElementById('swap_top').addEventListener('click', swap);

  document.addEventListener('click', (e)=> {
    if(altMenuEl && !altMenuEl.contains(e.target) && !(e.target.classList && e.target.classList.contains('token'))) clearAltMenu();
  });
  
  document.addEventListener('keydown', (e)=> { if(e.key === 'Escape') clearAltMenu(); });

  // Initialize
  loadPrefs();
  autoGrow(srcEl);
  
  const initial = window.initialTranslated || '';
  if(initial){ renderResultInteractive(initial); }
  
  renderHistoryChips();
  syncResultMinHeight();

  if(srcEl.value.trim().length > 0){
    triggerAutoTranslate();
  }
});
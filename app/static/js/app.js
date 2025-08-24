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
  console.log('DEBUG: setStatus called with:', JSON.stringify(text), 'timeout:', timeoutMs);
  console.log('DEBUG: Status elements found:', !!box, !!statusText);
  if(text){ 
    statusText.textContent = text; 
    box.style.display = 'inline-flex'; 
    console.log('DEBUG: Status set to visible with text:', text);
  } else { 
    box.style.display = 'none'; 
    console.log('DEBUG: Status hidden');
  }
  if(text && timeoutMs){ setTimeout(()=>{ box.style.display='none'; }, timeoutMs); }
}

function setTranslationHint(text){
  const hintEl = document.getElementById('translation_hint');
  const badge = document.getElementById('detected_badge');
  if(hintEl && text){
    // Preserve the badge element
    const badgeHtml = badge ? badge.outerHTML : '<span id="detected_badge" class="badge" style="display:none;"></span>';
    hintEl.innerHTML = text + badgeHtml;
  }
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

// Store the complete translation text to prevent DOM corruption issues
let storedCompleteText = '';

function getPlainResult(){ 
  const resultEl = document.getElementById('result');
  if (!resultEl) {
    console.error('DEBUG: Result element not found');
    return '';
  }
  
  // Use textContent to get all text regardless of CSS styling
  const currentText = resultEl.textContent || '';
  
  // Debug logging
  console.log('DEBUG: DOM textContent length:', currentText.length);
  console.log('DEBUG: Stored complete text length:', storedCompleteText.length);
  console.log('DEBUG: Current DOM text:', JSON.stringify(currentText.substring(0, 100) + '...'));
  console.log('DEBUG: Stored text:', JSON.stringify(storedCompleteText.substring(0, 100) + '...'));
  
  // If current DOM text is shorter than stored text and stored text starts with current text,
  // it means DOM was truncated - return the complete stored text
  if (storedCompleteText.length > currentText.length && 
      storedCompleteText.startsWith(currentText.replace(/…$/, ''))) {
    console.log('DEBUG: DOM appears truncated, returning stored complete text');
    return storedCompleteText;
  }
  
  // Otherwise return current DOM text
  console.log('DEBUG: Returning current DOM text');
  return currentText;
}
function setResultPlain(text){ 
  // Store the complete text before rendering
  storedCompleteText = text || '';
  console.log('DEBUG: Stored complete text (length:', storedCompleteText.length, '):', JSON.stringify(storedCompleteText.substring(0, 100) + '...'));
  renderResultInteractive(text); 
}

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
    localStorage.setItem('lt_history', JSON.stringify(items.slice(0,3)));
  } catch(e) {}
}

let historyItems = getHistoryItems();

function renderHistoryChips(){
  const wrap = document.getElementById('history');
  if(!wrap) return;
  wrap.innerHTML = '';
  const items = historyItems.slice(0,3);
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
    const short = (item.source || '').replace(/\n/g,' ').replace(/\s+/g, ' ').slice(0,40) + ((item.source||'').length>40?'...':'');
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
      // Preserve newlines and other whitespace properly
      if (p.includes('\n')) {
        // Split by newlines and handle each part
        const lines = p.split('\n');
        lines.forEach((line, index) => {
          if (index > 0) {
            frag.appendChild(document.createElement('br'));
          }
          if (line.trim() === '' && line.length > 0) {
            frag.appendChild(document.createTextNode(line));
          } else if (line.length > 0) {
            frag.appendChild(document.createTextNode(line));
          }
        });
      } else {
        frag.appendChild(document.createTextNode(p));
      }
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
  
  // Show TTS button if there's translated text, but keep it disabled initially (only if TTS is enabled)
  const ttsBtn = document.getElementById('tts-btn');
  if (ttsBtn) {
    if (text && text.trim()) {
      ttsBtn.style.display = 'flex';
      ttsBtn.classList.add('disabled');
      ttsBtn.setAttribute('disabled', 'true');
      // Enable after a short delay to ensure text is fully rendered
      setTimeout(() => {
        ttsBtn.classList.remove('disabled');
        ttsBtn.removeAttribute('disabled');
      }, 200);
    } else {
      ttsBtn.style.display = 'none';
    }
  }
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
  idleCommitTimer = setTimeout(commitHistoryIfStable, 5000);
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
  // Keep only 3 items
  if(historyItems.length > 3) historyItems.length = 3;
  
  // Save to localStorage
  saveHistoryItems(historyItems);
  renderHistoryChips();
}

function triggerAutoTranslate(){
  if(debounceId) clearTimeout(debounceId);
  console.log('DEBUG: triggerAutoTranslate called');
  // Shorter debounce for better responsiveness, and ensure minimum text length
  debounceId = setTimeout(()=> {
    const srcText = document.getElementById('source_text').value.trim();
    console.log('DEBUG: After debounce - text length:', srcText.length, 'text:', JSON.stringify(srcText.substring(0, 50) + '...'));
    // Only translate if we have at least 2 characters (to avoid single letter translations)
    if(srcText.length >= 2) {
      console.log('DEBUG: Calling autoTranslate');
      autoTranslate();
    } else {
      console.log('DEBUG: Text too short, not translating');
    }
  }, 250);
}

async function autoTranslate(){
  const source_text = document.getElementById('source_text').value.trim();
  const source_lang = document.getElementById('source_lang').value;
  const target_lang = document.getElementById('target_lang').value;
  const tone = document.getElementById('tone').value;

  console.log('DEBUG: autoTranslate called with text:', JSON.stringify(source_text.substring(0, 50) + '...'));
  console.log('DEBUG: Translation settings:', source_lang, '→', target_lang, 'tone:', tone);

  userChosenPhrases = [];

  if(!source_text){
    console.log('DEBUG: No source text, clearing results');
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
    console.log('DEBUG: Setting status to translating...');
    setStatus(_('translating'));
    // Hide translation hint during translation
    const hintEl = document.getElementById('translation_hint');
    if(hintEl) hintEl.style.display = 'none';
    const r = await fetch('/api/translate?no_history=1', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ source_text, source_lang, target_lang, tone, seq: mySeq }),
      signal: ab.signal
    });
    const j = await r.json();
    console.log('DEBUG: Translation response received:', j);
    if(j.error){
      console.log('DEBUG: Translation error:', j.error);
      setResultPlain('');
      document.getElementById('detected_badge').style.display='none';
      return;
    }
    if(mySeq !== latestSeq){ 
      console.log('DEBUG: Sequence mismatch, ignoring result. mySeq:', mySeq, 'latestSeq:', latestSeq);
      return; 
    }

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
    console.log('DEBUG: Translation error caught:', e);
    if(e.name !== 'AbortError'){ 
      console.log('DEBUG: Non-abort error during translation');
      // Only clear status on real errors, not aborts
      setStatus('');
      const hintEl = document.getElementById('translation_hint');
      if(hintEl) hintEl.style.display = '';
    } else {
      console.log('DEBUG: Translation aborted - keeping status for next request');
      // Don't clear status on abort - let next request handle it
    }
  } finally {
    // Only clear status if this is the latest request
    if(mySeq === latestSeq) {
      console.log('DEBUG: Translation finally block - clearing status (latest request)');
      setStatus('');
      const hintEl = document.getElementById('translation_hint');
      if(hintEl) hintEl.style.display = '';
    } else {
      console.log('DEBUG: Translation finally block - not latest request, keeping status');
    }
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
  
  // Progressive Streaming TTS Implementation
  class StreamingTTSPlayer {
    constructor() {
      this.audioElement = null;
      this.objectUrl = null;
      this.isPlaying = false;
    }

    async playStreaming(text, language) {
      console.log('TTS: Starting streaming with backend pauses for:', text, 'language:', language);
      
      try {
        // Use streaming backend with sentence pauses
        const response = await fetch('/api/tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: text,
            language: language,
            streaming: true  // Use Wyoming streaming with backend pauses
          })
        });

        if (!response.ok) {
          throw new Error(`Streaming failed with status: ${response.status}`);
        }

        // Process as blob for reliable audio playback
        const audioBlob = await response.blob();
        console.log('TTS: Received streaming blob with pauses:', audioBlob.size, 'bytes, type:', audioBlob.type);
        
        this.objectUrl = URL.createObjectURL(audioBlob);
        this.audioElement = new Audio(this.objectUrl);
        
        // Add event listeners for better debugging
        this.audioElement.addEventListener('canplay', () => {
          console.log('TTS: Audio can play, duration:', this.audioElement.duration);
        });
        
        this.audioElement.addEventListener('loadedmetadata', () => {
          console.log('TTS: Metadata loaded, duration:', this.audioElement.duration, 'seconds');
        });
        
        this.audioElement.addEventListener('error', (e) => {
          console.error('TTS: Audio element error:', e.target.error);
        });
        
        console.log('TTS: Wyoming streaming with pauses successful, starting playback');
        await this.audioElement.play();
        console.log('TTS: Playback started successfully');
        return this.audioElement;
        
      } catch (streamError) {
        console.warn('TTS: Wyoming streaming failed, using fast mode:', streamError.message);
        return await this.playFast(text, language);
      }
    }

    async playFast(text, language) {
      console.log('TTS: Using fast mode');
      
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          language: language,
          streaming: false  // Use fast mode for reliability
        })
      });

      if (!response.ok) {
        throw new Error('TTS request failed');
      }

      const audioBlob = await response.blob();
      this.objectUrl = URL.createObjectURL(audioBlob);
      
      this.audioElement = new Audio(this.objectUrl);
      await this.audioElement.play();
      
      return this.audioElement;
    }

    stop() {
      if (this.audioElement) {
        this.audioElement.pause();
        this.audioElement.currentTime = 0;
      }
      
      if (this.objectUrl) {
        URL.revokeObjectURL(this.objectUrl);
        this.objectUrl = null;
      }
      
      this.isPlaying = false;
    }

    addEventListener(event, callback) {
      if (this.audioElement) {
        this.audioElement.addEventListener(event, callback);
      }
    }
  }

  // TTS functionality (only if TTS button exists)
  const ttsBtn = document.getElementById('tts-btn');
  
  if (ttsBtn) {
    // Initialize streaming TTS player
    const streamingPlayer = new StreamingTTSPlayer();
    
    ttsBtn.addEventListener('click', async () => {
    const resultText = getPlainResult().trim();
    console.log('DEBUG: TTS button clicked, extracted text:', JSON.stringify(resultText));
    console.log('DEBUG: Text length:', resultText.length);
    if (!resultText) {
      console.log('DEBUG: No text found, aborting TTS');
      return;
    }
    
    // Stop current audio if playing
    if (streamingPlayer.isPlaying) {
      streamingPlayer.stop();
      ttsBtn.classList.remove('playing');
      return;
    }
    
    try {
      ttsBtn.classList.add('loading');
      
      // Get target language for TTS
      const targetLang = document.getElementById('target_lang').value;
      
      // Map language codes to TTS languages
      const langMap = {
        'de': 'de',
        'en': 'en', 
        'fr': 'fr',
        'es': 'es',
        'it': 'it',
        'ru': 'ru',
        'cs': 'cs',
        'pl': 'pl'
      };
      
      const ttsLang = langMap[targetLang] || 'pl';
      
      console.log('TTS: Using streaming player for:', resultText, 'in language:', ttsLang);
      
      // Switch from loading to playing  
      ttsBtn.classList.remove('loading');
      ttsBtn.classList.add('playing');
      
      // Use streaming player with fallback to fast mode
      const audioElement = await streamingPlayer.playStreaming(resultText, ttsLang);
      streamingPlayer.isPlaying = true;
      
      // Set up completion handlers
      if (audioElement) {
        audioElement.addEventListener('ended', () => {
          console.log('TTS: Streaming audio ended');
          ttsBtn.classList.remove('playing');
          streamingPlayer.stop();
        });
        
        audioElement.addEventListener('error', (error) => {
          console.error('TTS: Streaming audio error:', error);
          ttsBtn.classList.remove('playing');
          ttsBtn.classList.remove('loading');
          streamingPlayer.stop();
        });
      }
      
      console.log('TTS: Streaming audio started');
      
    } catch (error) {
      console.error('TTS error:', error);
      ttsBtn.classList.remove('playing');
      ttsBtn.classList.remove('loading');
    }
    });
  }
});
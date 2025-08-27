/**
 * LLOT Modern JavaScript - Clean Refactored Version 2025
 * Modular, clean, and maintainable code structure
 */

// ============================================================================
// CORE APPLICATION CLASS
// ============================================================================

class LLOTApp {
  constructor() {
    this.state = {
      translationTimeout: null,
      historyTimeout: null,
      currentAudio: null,
      history: this.loadHistory(),
      lastDetectedLanguage: 'en'
    };
    
    this.init();
  }
  
  init() {
    this.initElements();
    this.modules = {
      theme: new ThemeManager(),
      dropdown: new DropdownManager(this.elements),
      translator: new TranslationManager(this.elements, this.state),
      ui: new UIManager(this.elements),
      history: new HistoryManager(this.elements, this.state),
      tts: new TTSManager(this.elements),
      keyboard: new KeyboardManager(this.elements)
    };
    
    this.bindEvents();
    this.modules.ui.updateCharCount();
    this.modules.ui.updateFontSize();
    this.startHealthMonitoring();
  }
  
  initElements() {
    this.elements = {
      sourceText: document.getElementById('source_text'),
      result: document.getElementById('result'),
      sourceLang: document.getElementById('source_lang'),
      targetLang: document.getElementById('target_lang'),
      tone: document.getElementById('tone'),
      status: document.getElementById('status'),
      statusText: document.getElementById('status-text'),
      spinner: document.getElementById('loading-spinner'),
      charCount: document.getElementById('char-count'),
      themeToggle: document.getElementById('theme-toggle'),
      swapButton: document.getElementById('swap_languages'),
      historyPanel: document.getElementById('history-panel'),
      historyList: document.getElementById('history-list'),
      outputOptionsDropdown: document.getElementById('output-options-dropdown'),
      toneOutput: document.getElementById('tone-output'),
      modelSelectOutput: document.getElementById('model-select-output')
    };
  }
  
  bindEvents() {
    // Theme toggle
    if (this.elements.themeToggle) {
      this.elements.themeToggle.addEventListener('click', () => {
        this.modules.theme.toggle();
      });
    }

    // Language changes
    ['sourceLang', 'targetLang', 'tone'].forEach(key => {
      if (this.elements[key]) {
        this.elements[key].addEventListener('change', () => {
          this.modules.translator.scheduleTranslation();
          if (key === 'targetLang') {
            this.modules.ui.updateActionButtons();
          }
        });
      }
    });

    // Language swap
    if (this.elements.swapButton) {
      this.elements.swapButton.addEventListener('click', () => {
        this.modules.translator.swapLanguages();
      });
    }
    
    const swapButtonTop = document.getElementById('swap_languages_top');
    if (swapButtonTop) {
      swapButtonTop.addEventListener('click', () => {
        this.modules.translator.swapLanguages();
      });
    }

    // Text input
    if (this.elements.sourceText) {
      this.elements.sourceText.addEventListener('input', () => {
        this.modules.ui.updateCharCount();
        this.modules.ui.updateFontSize();
        this.modules.translator.scheduleTranslation();
        this.modules.ui.autoResizeTextarea();
      });
      
      this.elements.sourceText.addEventListener('blur', () => {
        if (this.state.translationTimeout) {
          clearTimeout(this.state.translationTimeout);
        }
        this.modules.translator.performTranslation();
      });

      this.elements.sourceText.addEventListener('paste', () => {
        setTimeout(() => {
          this.modules.ui.updateCharCount();
          this.modules.ui.updateFontSize();
          this.modules.translator.scheduleTranslation();
          this.modules.ui.autoResizeTextarea();
        }, 100);
      });
    }

    // Copy button (event delegation)
    document.addEventListener('click', (e) => {
      if (e.target.closest('#copy-btn')) {
        this.modules.ui.copyToClipboard();
      }
    });
  }

  async startHealthMonitoring() {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        const data = await response.json();
        this.modules.ui.updateConnectionStatus(data);
      } catch (error) {
        console.error('Health check failed:', error);
        this.modules.ui.updateConnectionStatus({ overall: 'error' });
      }
    };
    
    checkHealth();
    setInterval(checkHealth, 30000);
  }

  loadHistory() {
    try {
      return JSON.parse(localStorage.getItem('llot-history') || '[]').slice(0, 10);
    } catch {
      return [];
    }
  }
}

// ============================================================================
// THEME MANAGEMENT MODULE
// ============================================================================

class ThemeManager {
  constructor() {
    this.init();
  }
  
  init() {
    const savedTheme = localStorage.getItem('llot-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    this.setTheme(theme);
    
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('llot-theme')) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }
  
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('llot-theme', theme);
    this.updateThemeIcon(theme);
  }
  
  toggle() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    this.setTheme(currentTheme === 'dark' ? 'light' : 'dark');
  }
  
  updateThemeIcon(theme) {
    const toggle = document.getElementById('theme-toggle');
    if (!toggle) return;
    
    const icon = toggle.querySelector('svg');
    if (theme === 'dark') {
      icon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>`;
    } else {
      icon.innerHTML = `
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/>
        <line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      `;
    }
  }
}

// ============================================================================
// DROPDOWN MANAGEMENT MODULE
// ============================================================================

class DropdownManager {
  constructor(elements) {
    this.elements = elements;
    this.languages = this.getLanguages();
    this.init();
  }
  
  init() {
    // Initialize language dropdowns
    this.initDropdown('source-lang-dropdown', 'source_lang', this.languages, 'auto');
    this.initDropdown('source-lang-dropdown-top', 'source_lang', this.languages, 'auto');
    
    const targetLanguages = this.languages.filter(lang => !lang.sourceOnly);
    this.initDropdown('target-lang-dropdown', 'target_lang', targetLanguages, 'de');
    this.initDropdown('target-lang-dropdown-top', 'target_lang', targetLanguages, 'de');
    
    // Initialize options dropdown - SIMPLIFIED VERSION
    this.initOptionsDropdown();
    
    // Global click handler to close dropdowns
    this.initGlobalHandlers();
  }
  
  initDropdown(dropdownId, selectId, languages, defaultValue) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;

    const trigger = dropdown.querySelector('.language-dropdown-trigger');
    const content = dropdown.querySelector('.language-dropdown-content');
    const searchInput = dropdown.querySelector('.language-dropdown-search input');
    const hiddenSelect = document.getElementById(selectId);
    const selectedSpan = trigger?.querySelector('.selected-language');

    if (!trigger || !content || !hiddenSelect || !selectedSpan) return;

    // Populate dropdown
    const populateDropdown = (langs = languages) => {
      content.innerHTML = '';
      
      langs.forEach(lang => {
        const item = document.createElement('div');
        item.className = `language-dropdown-item${hiddenSelect.value === lang.code ? ' selected' : ''}`;
        item.setAttribute('data-code', lang.code);
        item.innerHTML = `<span class="flag">${lang.flag}</span><span class="name">${lang.name}</span>`;
        
        item.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          hiddenSelect.value = lang.code;
          selectedSpan.textContent = lang.name;
          
          this.synchronizeDropdowns(selectId, lang.code, lang.name);
          this.closeDropdown(dropdown);
          
          hiddenSelect.dispatchEvent(new Event('change'));
        });
        
        content.appendChild(item);
      });
    };

    // Toggle dropdown
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this.closeAllDropdowns();
      dropdown.classList.toggle('open');
      
      if (dropdown.classList.contains('open')) {
        populateDropdown();
        setTimeout(() => searchInput?.focus(), 100);
      }
    });

    // Search functionality
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = languages.filter(lang => 
          lang.name.toLowerCase().includes(query) || 
          lang.code.toLowerCase().includes(query)
        );
        populateDropdown(filtered);
      });
    }

    // Setup hidden select
    this.populateHiddenSelect(hiddenSelect, languages, defaultValue);
    
    // Set initial display
    const defaultLang = languages.find(lang => lang.code === defaultValue);
    if (defaultLang) {
      selectedSpan.textContent = defaultLang.name;
    }
  }
  
  initOptionsDropdown() {
    const dropdown = this.elements.outputOptionsDropdown;
    if (!dropdown) return;

    const trigger = dropdown.querySelector('.options-trigger');
    if (!trigger) return;

    // SIMPLE click handler - no complex event management
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this.closeAllDropdowns();
      dropdown.classList.toggle('open');
    });

    // Handle tone select changes
    if (this.elements.toneOutput) {
      this.elements.toneOutput.addEventListener('change', () => {
        if (this.elements.tone) {
          this.elements.tone.value = this.elements.toneOutput.value;
          this.elements.tone.dispatchEvent(new Event('change'));
        }
      });
    }

    // Handle model select changes
    if (this.elements.modelSelectOutput) {
      this.elements.modelSelectOutput.addEventListener('change', (e) => {
        this.changeModel(e.target.value);
      });
    }

    // Load available models
    this.loadAvailableModels();
  }
  
  initGlobalHandlers() {
    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
      // Don't close if clicking inside any dropdown
      if (!e.target.closest('.language-dropdown') && 
          !e.target.closest('.options-menu')) {
        this.closeAllDropdowns();
      }
    });

    // Close dropdowns on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeAllDropdowns();
      }
    });
  }
  
  closeAllDropdowns() {
    document.querySelectorAll('.language-dropdown.open').forEach(d => {
      this.closeDropdown(d);
    });
  }
  
  closeDropdown(dropdown) {
    dropdown.classList.remove('open');
    const searchInput = dropdown.querySelector('.language-dropdown-search input');
    if (searchInput) {
      searchInput.value = '';
    }
  }
  
  synchronizeDropdowns(selectId, languageCode, languageName) {
    const dropdownIds = [];
    if (selectId === 'source_lang') {
      dropdownIds.push('source-lang-dropdown', 'source-lang-dropdown-top');
    } else if (selectId === 'target_lang') {
      dropdownIds.push('target-lang-dropdown', 'target-lang-dropdown-top');
    }
    
    dropdownIds.forEach(dropdownId => {
      const dropdown = document.getElementById(dropdownId);
      if (!dropdown) return;
      
      const selectedSpan = dropdown.querySelector('.selected-language');
      if (selectedSpan) {
        selectedSpan.textContent = languageName;
      }
      
      const content = dropdown.querySelector('.language-dropdown-content');
      if (content) {
        content.querySelectorAll('.language-dropdown-item').forEach(item => {
          item.classList.toggle('selected', item.getAttribute('data-code') === languageCode);
        });
      }
    });
  }
  
  populateHiddenSelect(select, languages, defaultValue) {
    select.innerHTML = '';
    languages.forEach(lang => {
      const option = document.createElement('option');
      option.value = lang.code;
      option.textContent = lang.name;
      option.selected = lang.code === defaultValue;
      select.appendChild(option);
    });
  }

  async loadAvailableModels() {
    const modelSelect = this.elements.modelSelectOutput;
    if (!modelSelect) return;
    
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      
      if (data.ollama?.models && Array.isArray(data.ollama.models)) {
        const currentModel = modelSelect.value;
        modelSelect.innerHTML = '';
        
        data.ollama.models.forEach(model => {
          const option = document.createElement('option');
          option.value = model;
          option.textContent = model;
          option.selected = model === currentModel;
          modelSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  }

  async changeModel(newModel) {
    try {
      const response = await fetch('/api/change_model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: newModel })
      });
      
      if (response.ok) {
        console.log('Model changed to:', newModel);
      }
    } catch (error) {
      console.error('Error changing model:', error);
    }
  }
  
  getLanguages() {
    return [
      { code: 'auto', name: 'Detect language', flag: '🔍', sourceOnly: true },
      { code: 'en', name: 'English', flag: '🇺🇸' },
      { code: 'zh', name: '中文', flag: '🇨🇳' },
      { code: 'es', name: 'Español', flag: '🇪🇸' },
      { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
      { code: 'ar', name: 'العربية', flag: '🇦🇪' },
      { code: 'pt', name: 'Português', flag: '🇵🇹' },
      { code: 'bn', name: 'বাংলা', flag: '🇧🇩' },
      { code: 'ru', name: 'Русский', flag: '🇷🇺' },
      { code: 'ja', name: '日本語', flag: '🇯🇵' },
      { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
      { code: 'ko', name: '한국어', flag: '🇰🇷' },
      { code: 'fr', name: 'Français', flag: '🇫🇷' },
      { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
      { code: 'it', name: 'Italiano', flag: '🇮🇹' },
      { code: 'th', name: 'ไทย', flag: '🇹🇭' },
      { code: 'pl', name: 'Polski', flag: '🇵🇱' },
      { code: 'uk', name: 'Українська', flag: '🇺🇦' },
      { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
      { code: 'ro', name: 'Română', flag: '🇷🇴' },
      { code: 'cs', name: 'Čeština', flag: '🇨🇿' },
      { code: 'sk', name: 'Slovenčina', flag: '🇸🇰' },
      { code: 'hu', name: 'Magyar', flag: '🇭🇺' },
      { code: 'bg', name: 'Български', flag: '🇧🇬' },
      { code: 'hr', name: 'Hrvatski', flag: '🇭🇷' },
      { code: 'sl', name: 'Slovenščina', flag: '🇸🇮' },
      { code: 'lv', name: 'Latviešu', flag: '🇱🇻' },
      { code: 'lt', name: 'Lietuvių', flag: '🇱🇹' },
      { code: 'et', name: 'Eesti', flag: '🇪🇪' },
      { code: 'fi', name: 'Suomi', flag: '🇫🇮' },
      { code: 'da', name: 'Dansk', flag: '🇩🇰' },
      { code: 'no', name: 'Norsk', flag: '🇳🇴' },
      { code: 'sv', name: 'Svenska', flag: '🇸🇪' },
      { code: 'el', name: 'Ελληνικά', flag: '🇬🇷' },
      { code: 'ca', name: 'Català', flag: '🏴󠁥󠁳󠁣󠁴󠁿' },
      { code: 'ga', name: 'Gaeilge', flag: '🇮🇪' },
      { code: 'mt', name: 'Malti', flag: '🇲🇹' }
    ];
  }
}

// ============================================================================
// TRANSLATION MANAGEMENT MODULE  
// ============================================================================

class TranslationManager {
  constructor(elements, state) {
    this.elements = elements;
    this.state = state;
  }
  
  scheduleTranslation() {
    if (this.state.translationTimeout) {
      clearTimeout(this.state.translationTimeout);
    }
    
    const sourceText = this.elements.sourceText?.value?.trim();
    
    let delay;
    if (!sourceText) {
      delay = 0;
    } else if (sourceText.length < 10) {
      delay = 500;
    } else if (sourceText.endsWith(' ') || /[.!?]$/.test(sourceText)) {
      delay = 150;
    } else {
      delay = 400;
    }
    
    this.state.translationTimeout = setTimeout(() => {
      this.performTranslation();
    }, delay);
  }

  async performTranslation() {
    const sourceText = this.elements.sourceText?.value?.trim();
    if (!sourceText) {
      this.clearResult();
      return;
    }

    const sourceLang = this.elements.sourceLang?.value || 'auto';
    const targetLang = this.elements.targetLang?.value || 'de';
    const tone = this.elements.tone?.value || 'neutral';

    this.showLoading();

    try {
      const response = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_text: sourceText,
          source_lang: sourceLang,
          target_lang: targetLang,
          tone: tone
        })
      });

      const data = await response.json();

      if (data.error) {
        if (data.error === 'EMPTY') {
          this.clearResult();
        } else {
          this.showError(data.error);
        }
        return;
      }

      this.showResult(data.translated_text);
      
      if (data.source_lang && data.source_lang !== 'auto') {
        this.state.lastDetectedLanguage = data.source_lang;
      }

      // Add to history
      window.llotApp.modules.history.scheduleHistoryAdd(
        sourceText, data.translated_text, sourceLang, targetLang
      );

    } catch (error) {
      console.error('Translation error:', error);
      this.showError('Translation failed');
    }
  }

  showResult(translation) {
    if (this.elements.result) {
      this.elements.result.classList.remove('translating');
      window.llotApp.modules.ui.makeWordsClickable(translation);
    }
    this.hideLoading();
    window.llotApp.modules.ui.updateCharCount();
    window.llotApp.modules.ui.updateFontSize();
    window.llotApp.modules.ui.updateActionButtons();
  }

  clearResult() {
    if (this.elements.result) {
      this.elements.result.textContent = '';
    }
    window.llotApp.modules.ui.updateFontSize();
    this.hideLoading();
  }

  showLoading() {
    if (this.elements.spinner) {
      this.elements.spinner.style.display = 'block';
    }
    if (this.elements.statusText) {
      this.elements.statusText.textContent = 'Translating...';
    }
    if (this.elements.result) {
      this.elements.result.classList.add('translating');
    }
  }

  hideLoading() {
    if (this.elements.spinner) {
      this.elements.spinner.style.display = 'none';
    }
    if (this.elements.statusText) {
      this.elements.statusText.textContent = 'Ready to translate';
    }
    if (this.elements.result) {
      this.elements.result.classList.remove('translating');
    }
  }

  showError(message) {
    if (this.elements.result) {
      this.elements.result.textContent = `Error: ${message}`;
      this.elements.result.style.color = 'var(--error)';
    }
    this.hideLoading();
  }

  swapLanguages() {
    const sourceLang = this.elements.sourceLang?.value;
    const targetLang = this.elements.targetLang?.value;
    const sourceText = this.elements.sourceText?.value;
    const resultText = this.elements.result?.textContent;

    if (!sourceLang || !targetLang) return;

    let actualSourceLang = sourceLang;
    if (sourceLang === 'auto') {
      actualSourceLang = this.state.lastDetectedLanguage || 'en';
    }

    if (targetLang === 'auto') return;

    // Swap languages
    this.elements.sourceLang.value = targetLang;
    this.elements.targetLang.value = actualSourceLang;

    // Update dropdown displays
    window.llotApp.modules.dropdown.synchronizeDropdowns('source_lang', targetLang, 
      window.llotApp.modules.dropdown.languages.find(l => l.code === targetLang)?.name);
    window.llotApp.modules.dropdown.synchronizeDropdowns('target_lang', actualSourceLang,
      window.llotApp.modules.dropdown.languages.find(l => l.code === actualSourceLang)?.name);

    // Swap text if valid translation exists
    if (resultText && resultText.trim() && !resultText.startsWith('Error:')) {
      this.elements.sourceText.value = resultText;
      this.elements.result.textContent = '';
      this.elements.result.style.color = '';
      window.llotApp.modules.ui.updateFontSize();
      this.scheduleTranslation();
    } else if (sourceText && sourceText.trim()) {
      this.scheduleTranslation();
    }
  }
}

// ============================================================================
// UI MANAGEMENT MODULE
// ============================================================================

class UIManager {
  constructor(elements) {
    this.elements = elements;
    this.init();
  }
  
  init() {
    if (this.elements.sourceText) {
      this.autoResizeTextarea();
    }
    this.updateFontSize();
    
    // Show initial translated text if present
    if (window.initialTranslated) {
      this.makeWordsClickable(window.initialTranslated);
    }
  }

  updateCharCount() {
    const text = this.elements.sourceText?.value || '';
    if (this.elements.charCount) {
      this.elements.charCount.textContent = `${text.length} characters`;
    }
  }

  updateFontSize() {
    if (!this.elements.sourceText || !this.elements.result) return;
    
    const text = this.elements.sourceText.value || '';
    const charCount = text.length;
    
    // Remove existing font classes
    const fontClasses = ['font-large', 'font-medium', 'font-normal', 'font-small'];
    fontClasses.forEach(cls => {
      this.elements.sourceText.classList.remove(cls);
      this.elements.result.classList.remove(cls);
    });
    
    // Determine font size
    let fontSizeClass;
    if (charCount === 0) {
      fontSizeClass = 'font-large';
    } else if (charCount < 50) {
      fontSizeClass = 'font-large';
    } else if (charCount < 150) {
      fontSizeClass = 'font-medium';
    } else if (charCount < 300) {
      fontSizeClass = 'font-normal';
    } else {
      fontSizeClass = 'font-small';
    }
    
    this.elements.sourceText.classList.add(fontSizeClass);
    this.elements.result.classList.add(fontSizeClass);
  }

  autoResizeTextarea() {
    if (!this.elements.sourceText) return;
    
    const textarea = this.elements.sourceText;
    const minHeight = 400;
    
    const currentHeight = textarea.style.height;
    textarea.style.height = 'auto';
    
    const scrollHeight = textarea.scrollHeight;
    const newHeight = Math.max(minHeight, scrollHeight);
    
    textarea.style.height = `${newHeight}px`;
    textarea.style.minHeight = `${newHeight}px`;
    
    if (this.elements.result) {
      const outputPadding = 24;
      this.elements.result.style.minHeight = `${newHeight - outputPadding}px`;
    }
  }

  makeWordsClickable(translation) {
    const parts = translation.split(/(\s+|[^\p{L}\p{N}\p{M}]+)/u);
    
    const clickableHtml = parts.map(part => 
      /[\p{L}\p{N}]/u.test(part) 
        ? `<span class="clickable-word" data-word="${part}">${part}</span>`
        : part
    ).join('');
    
    this.elements.result.innerHTML = clickableHtml;
    
    this.ensureActionButtons();
    this.updateActionButtons();
    this.updateFontSize();
    
    this.elements.result.querySelectorAll('.clickable-word').forEach(wordElement => {
      wordElement.addEventListener('click', (e) => {
        e.stopPropagation();
        this.handleWordClick(wordElement);
      });
    });
  }

  ensureActionButtons() {
    let actionsContainer = this.elements.result.querySelector('.output-actions');
    
    if (!actionsContainer) {
      actionsContainer = document.createElement('div');
      actionsContainer.className = 'output-actions';
      this.elements.result.appendChild(actionsContainer);
    }
    
    // Ensure copy button
    if (!actionsContainer.querySelector('#copy-btn')) {
      const copyBtn = document.createElement('button');
      Object.assign(copyBtn, {
        id: 'copy-btn',
        className: 'action-button copy-button',
        title: 'Copy to clipboard',
        innerHTML: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="m5 15-2-2v-4.586a1 1 0 0 1 .293-.707l5.414-5.414a1 1 0 0 1 .707-.293h4.586l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>`
      });
      copyBtn.style.display = 'none';
      actionsContainer.appendChild(copyBtn);
    }
    
    // Ensure TTS button if enabled
    if (window.ttsEnabled && !actionsContainer.querySelector('#tts-btn')) {
      const ttsBtn = document.createElement('button');
      Object.assign(ttsBtn, {
        id: 'tts-btn',
        className: 'action-button tts-button',
        title: 'Listen to pronunciation',
        innerHTML: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M11 5L6 9H2v6h4l5 4V5zM19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`
      });
      ttsBtn.style.display = 'none';
      actionsContainer.appendChild(ttsBtn);
    }
  }

  updateActionButtons() {
    const copyBtn = document.getElementById('copy-btn');
    const ttsBtn = document.getElementById('tts-btn');
    const resultText = this.getPlainTextFromResult().trim();
    const targetLang = this.elements.targetLang?.value || 'de';
    
    if (copyBtn) {
      copyBtn.style.display = resultText ? 'flex' : 'none';
    }
    
    if (ttsBtn && window.ttsEnabled) {
      const supportedTtsLanguages = {
        'en': true, 'de': true, 'fr': true, 'es': true, 'pt': true, 'nl': true,
        'da': true, 'fi': true, 'no': true, 'pl': true, 'cs': true, 'sk': true,
        'hu': true, 'ro': true, 'ru': true, 'ar': true, 'hi': true, 'tr': true,
        'vi': true, 'zh': true, 'id': true
      };
      
      const languageSupported = supportedTtsLanguages[targetLang];
      ttsBtn.style.display = (resultText && languageSupported) ? 'flex' : 'none';
    }
  }

  getPlainTextFromResult() {
    return this.elements.result?.textContent || '';
  }

  async copyToClipboard() {
    const copyBtn = document.getElementById('copy-btn');
    const resultText = this.getPlainTextFromResult().trim();
    if (!copyBtn || !resultText) return;

    try {
      await navigator.clipboard.writeText(resultText);
      this.showCopyFeedback(copyBtn);
    } catch (error) {
      console.error('Failed to copy:', error);
      this.fallbackCopy(resultText, copyBtn);
    }
  }

  showCopyFeedback(copyBtn) {
    copyBtn.classList.add('copied');
    const originalSVG = copyBtn.innerHTML;
    
    copyBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
    
    setTimeout(() => {
      copyBtn.classList.remove('copied');
      copyBtn.innerHTML = originalSVG;
    }, 2000);
  }

  fallbackCopy(text, copyBtn) {
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      this.showCopyFeedback(copyBtn);
    } catch (error) {
      console.error('Fallback copy failed:', error);
    }
  }

  updateConnectionStatus(data) {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.querySelector('.status-indicator .status-text');
    
    if (!statusDot || !statusText) return;
    
    statusDot.classList.remove('pulse', 'error', 'warning', 'connected');
    
    switch (data.overall) {
      case 'ok':
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
        break;
      case 'warning':
        statusDot.classList.add('warning');
        statusText.textContent = 'No TTS';
        break;
      case 'error':
        statusDot.classList.add('error');
        statusText.textContent = 'Error';
        break;
      default:
        statusDot.classList.add('error');
        statusText.textContent = 'Unknown';
    }
  }

  // Simplified word click handling
  async handleWordClick(wordElement) {
    console.log('Word clicked:', wordElement.dataset.word);
    // Word alternatives functionality can be added here if needed
  }
}

// ============================================================================
// HISTORY MANAGEMENT MODULE
// ============================================================================

class HistoryManager {
  constructor(elements, state) {
    this.elements = elements;
    this.state = state;
    this.init();
  }
  
  init() {
    if (this.state.history.length > 0) {
      this.renderHistory();
    }
  }

  scheduleHistoryAdd(sourceText, translatedText, sourceLang, targetLang) {
    if (this.state.historyTimeout) {
      clearTimeout(this.state.historyTimeout);
    }
    
    this.state.historyTimeout = setTimeout(() => {
      this.addToHistory(sourceText, translatedText, sourceLang, targetLang);
    }, 4000);
  }

  addToHistory(sourceText, translatedText, sourceLang, targetLang) {
    const entry = {
      id: Date.now(),
      sourceText: sourceText.substring(0, 100),
      translatedText: translatedText.substring(0, 100),
      sourceLang,
      targetLang,
      timestamp: new Date().toLocaleString()
    };

    // Remove duplicate if exists
    this.state.history = this.state.history.filter(h => h.sourceText !== entry.sourceText);
    
    // Add to beginning and limit to 10
    this.state.history.unshift(entry);
    this.state.history = this.state.history.slice(0, 10);
    
    this.saveHistory();
    this.renderHistory();
  }

  saveHistory() {
    localStorage.setItem('llot-history', JSON.stringify(this.state.history));
  }

  renderHistory() {
    if (!this.elements.historyList || this.state.history.length === 0) return;

    if (this.elements.historyPanel) {
      this.elements.historyPanel.style.display = 'block';
    }

    this.elements.historyList.innerHTML = this.state.history.map(item => `
      <div class="history-item" data-id="${item.id}">
        <div class="history-text">
          <div class="history-source">${this.escapeHtml(item.sourceText)}</div>
          <div class="history-result">${this.escapeHtml(item.translatedText)}</div>
        </div>
        <div class="history-meta">
          <div class="history-lang">${item.sourceLang} → ${item.targetLang}</div>
          <div class="history-time">${item.timestamp}</div>
        </div>
      </div>
    `).join('');

    // Add click handlers
    this.elements.historyList.querySelectorAll('.history-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = parseInt(item.dataset.id);
        const historyItem = this.state.history.find(h => h.id === id);
        if (historyItem) {
          this.loadHistoryItem(historyItem);
        }
      });
    });
  }

  loadHistoryItem(item) {
    if (!this.elements.sourceText) return;
    
    this.elements.sourceText.value = item.sourceText;
    this.elements.sourceLang.value = item.sourceLang;
    this.elements.targetLang.value = item.targetLang;
    
    // Update dropdown displays
    window.llotApp.modules.dropdown.synchronizeDropdowns('source_lang', item.sourceLang,
      window.llotApp.modules.dropdown.languages.find(l => l.code === item.sourceLang)?.name);
    window.llotApp.modules.dropdown.synchronizeDropdowns('target_lang', item.targetLang,
      window.llotApp.modules.dropdown.languages.find(l => l.code === item.targetLang)?.name);
    
    window.llotApp.modules.ui.updateCharCount();
    window.llotApp.modules.ui.updateFontSize();
    window.llotApp.modules.translator.scheduleTranslation();
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// ============================================================================
// TTS MANAGEMENT MODULE
// ============================================================================

class TTSManager {
  constructor(elements) {
    this.elements = elements;
    this.streamingPlayer = new StreamingTTSPlayer();
    this.init();
  }
  
  init() {
    if (!window.ttsEnabled) return;
    
    // Use event delegation for TTS buttons
    if (this.elements.result) {
      this.elements.result.addEventListener('click', async (e) => {
        const ttsBtn = e.target.closest('#tts-btn');
        if (!ttsBtn) return;
        
        const resultText = window.llotApp.modules.ui.getPlainTextFromResult().trim();
        if (!resultText) return;
        
        if (this.streamingPlayer.isPlaying) {
          this.streamingPlayer.stop();
          ttsBtn.classList.remove('playing');
          return;
        }
        
        try {
          ttsBtn.classList.add('loading');
          const targetLang = this.elements.targetLang?.value || 'de';
          const ttsLang = this.mapLanguageForTTS(targetLang);
          
          const audioElement = await this.streamingPlayer.playStreaming(resultText, ttsLang);
          
          ttsBtn.classList.remove('loading');
          ttsBtn.classList.add('playing');
          this.streamingPlayer.isPlaying = true;
          
          if (audioElement) {
            audioElement.addEventListener('ended', () => {
              ttsBtn.classList.remove('playing');
              this.streamingPlayer.isPlaying = false;
            });
            
            audioElement.addEventListener('error', () => {
              ttsBtn.classList.remove('playing', 'loading');
              this.streamingPlayer.isPlaying = false;
            });
          }
          
        } catch (error) {
          console.error('TTS error:', error);
          ttsBtn.classList.remove('playing', 'loading');
          this.streamingPlayer.isPlaying = false;
        }
      });
    }
  }

  mapLanguageForTTS(targetLang) {
    const langMap = {
      'en': 'en', 'de': 'de', 'fr': 'fr', 'es': 'es', 'pt': 'pt',
      'nl': 'nl', 'da': 'da', 'fi': 'fi', 'no': 'no', 'pl': 'pl',
      'cs': 'cs', 'sk': 'sk', 'hu': 'hu', 'ro': 'ro', 'ru': 'ru',
      'ar': 'ar', 'hi': 'hi', 'tr': 'tr', 'vi': 'vi', 'zh': 'zh', 'id': 'id'
    };
    return langMap[targetLang] || 'en';
  }
}

// ============================================================================
// KEYBOARD SHORTCUTS MODULE
// ============================================================================

class KeyboardManager {
  constructor(elements) {
    this.elements = elements;
    this.init();
  }
  
  init() {
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'Enter' && e.shiftKey) {
          e.preventDefault();
          window.llotApp.modules.translator.scheduleTranslation();
        }
        if (e.key === 'c' && e.shiftKey) {
          e.preventDefault();
          window.llotApp.modules.ui.copyToClipboard();
        }
      }
      
      if (e.key === 'Escape') {
        window.llotApp.modules.dropdown.closeAllDropdowns();
      }
    });
  }
}

// ============================================================================
// TTS STREAMING PLAYER (Unchanged)
// ============================================================================

class StreamingTTSPlayer {
  constructor() {
    this.audioElement = null;
    this.objectUrl = null;
    this.isPlaying = false;
  }

  async playStreaming(text, language) {
    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          language: language,
          streaming: true
        })
      });

      if (!response.ok) {
        throw new Error(`Streaming failed with status: ${response.status}`);
      }

      const audioBlob = await response.blob();
      this.objectUrl = URL.createObjectURL(audioBlob);
      this.audioElement = new Audio(this.objectUrl);
      
      await this.audioElement.play();
      return this.audioElement;
      
    } catch (streamError) {
      console.warn('TTS: Streaming failed, using fast mode:', streamError.message);
      return await this.playFast(text, language);
    }
  }

  async playFast(text, language) {
    const response = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        language: language,
        streaming: false
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
}

// ============================================================================
// APPLICATION INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  window.llotApp = new LLOTApp();
});
/**
 * LLOT Modern JavaScript 2025
 * Enhanced UX with smooth animations and modern interactions
 */

// LLOT Modern JavaScript - Clean Version

class LLOTApp {
  constructor() {
    this.translationTimeout = null;
    this.currentAudio = null;
    this.history = this.loadHistory();
    
    this.init();
  }
  
  init() {
    this.initTheme();
    this.initElements();
    this.bindEvents();
    this.initHistory();
    this.setupAutoTranslation();
    this.checkConnectionStatus();
    this.initLanguageDropdowns();
    
    // Initialize with any existing translation
    console.log('LLOT Modern: Initialization - TTS enabled:', window.ttsEnabled);
    if (window.initialTranslated) {
      console.log('LLOT Modern: Initial translation found');
      // TTS button removed
    }
  }
  
  initTheme() {
    const savedTheme = localStorage.getItem('llot-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    this.setTheme(theme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('llot-theme')) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }
  
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('llot-theme', theme);
    
    // Update theme toggle icon
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      const icon = toggle.querySelector('svg');
      if (theme === 'dark') {
        icon.innerHTML = `
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        `;
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
      historyList: document.getElementById('history-list')
    };
    
    // Verify critical elements exist
    if (!this.elements.sourceText || !this.elements.result || !this.elements.sourceLang || !this.elements.targetLang) {
      console.error('LLOT Modern: Missing critical elements');
    }
  }
  
  bindEvents() {
    // Theme toggle
    this.elements.themeToggle?.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      this.setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });
    
    // Auto-translation
    if (this.elements.sourceText) {
      console.log('LLOT Modern: Binding input event to source text');
      this.elements.sourceText.addEventListener('input', () => {
        console.log('LLOT Modern: Text input changed');
        this.updateCharCount();
        this.scheduleTranslation();
      });
    } else {
      console.error('LLOT Modern: Source text element not found!');
    }
    
    // Language and tone changes
    [this.elements.sourceLang, this.elements.targetLang, this.elements.tone].forEach(element => {
      element?.addEventListener('change', (e) => {
        console.log(`LLOT Modern: Change event triggered for ${element.id}:`, element.value);
        this.scheduleTranslation();
      });
    });
    
    // Language swap - DISABLED FOR DEBUGGING
    console.log('LLOT Modern: Swap button functionality DISABLED for debugging');
    console.log('LLOT Modern: Swap button element found:', !!this.elements.swapButton);
    console.log('LLOT Modern: Swap button element ID:', this.elements.swapButton?.id);
    
    // Disable swap button event handlers for debugging
    /*
    this.elements.swapButton?.addEventListener('click', () => {
      console.log('LLOT Modern: Swap button clicked via this.elements');
      this.swapLanguages();
    });
    
    // Also try direct binding to be sure
    const directSwapButton = document.getElementById('swap_languages');
    console.log('LLOT Modern: Direct swap button found:', !!directSwapButton);
    if (directSwapButton) {
      directSwapButton.addEventListener('click', () => {
        console.log('LLOT Modern: Direct swap button clicked');
        this.swapLanguages();
      });
    }
    */

    // Copy and TTS functionality removed
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'Enter':
            e.preventDefault();
            this.translate();
            break;
          case 'c':
            if (e.shiftKey) {
              e.preventDefault();
              // Copy functionality removed
            }
            break;
          case 'd':
            e.preventDefault();
            this.setTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
            break;
        }
      }
    });
  }
  
  updateCharCount() {
    const count = this.elements.sourceText ? this.elements.sourceText.value.length : 0;
    if (this.elements.charCount) {
      this.elements.charCount.textContent = `${count.toLocaleString()} characters`;
    }
  }
  
  scheduleTranslation() {
    if (this.translationTimeout) {
      clearTimeout(this.translationTimeout);
    }
    
    const text = this.elements.sourceText ? this.elements.sourceText.value.trim() : '';
    if (!text) {
      this.clearResult();
      return;
    }
    
    this.translationTimeout = setTimeout(() => {
      this.translate();
    }, 300); // Debounce translation requests
  }
  
  async translate() {
    const text = this.elements.sourceText ? this.elements.sourceText.value.trim() : '';
    console.log('LLOT Modern: Translating text:', text);
    
    if (!text) {
      console.log('LLOT Modern: No text to translate');
      return;
    }
    
    this.showLoading();
    
    try {
      const formData = new FormData();
      formData.append('source_text', text);
      formData.append('source_lang', this.elements.sourceLang ? this.elements.sourceLang.value : 'auto');
      formData.append('target_lang', this.elements.targetLang ? this.elements.targetLang.value : 'en');
      formData.append('tone', this.elements.tone ? this.elements.tone.value : 'neutral');
      
      const response = await fetch('/api/translate', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      this.showResult(data.translated_text);
      
      // Store detected language for swap functionality
      if (data.source_lang && this.elements.sourceLang.value === 'auto') {
        this.lastDetectedLanguage = data.source_lang;
        console.log('LLOT Modern: Detected language stored:', data.source_lang);
      }
      
      this.addToHistory({
        source: text,
        target: data.translated_text,
        sourceLang: data.source_lang,
        targetLang: data.target_lang,
        timestamp: Date.now()
      });
      
    } catch (error) {
      this.showError(error.message);
    }
  }
  
  showLoading() {
    if (this.elements.spinner) this.elements.spinner.style.display = 'block';
    if (this.elements.statusText) this.elements.statusText.textContent = 'Translating...';
    
    // Add subtle animation to input
    this.elements.sourceText?.style.setProperty('opacity', '0.7');
  }
  
  showResult(translation) {
    console.log('LLOT Modern: showResult called with translation:', translation);
    if (this.elements.result) {
      this.elements.result.textContent = translation;
      
      // Animate result appearance
      this.elements.result.style.opacity = '0';
      this.elements.result.style.transform = 'translateY(10px)';
      
      requestAnimationFrame(() => {
        this.elements.result.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        this.elements.result.style.opacity = '1';
        this.elements.result.style.transform = 'translateY(0)';
      });
    }
    
    this.hideLoading();
    // Action buttons removed
    
    // Reset source text opacity
    this.elements.sourceText?.style.setProperty('opacity', '1');
  }
  
  showError(message) {
    if (this.elements.statusText) this.elements.statusText.textContent = `Error: ${message}`;
    this.hideLoading();
    console.error('Translation error:', message);
  }
  
  hideLoading() {
    if (this.elements.spinner) this.elements.spinner.style.display = 'none';
    if (this.elements.statusText) this.elements.statusText.textContent = 'Ready to translate';
  }
  
  clearResult() {
    if (this.elements.result) this.elements.result.textContent = '';
    // Action buttons removed
    this.hideLoading();
  }
  
  swapLanguages() {
    try {
      console.log('LLOT Modern: swapLanguages() called');
      console.log('LLOT Modern: this.elements:', this.elements);
      console.log('LLOT Modern: Elements check', {
        sourceLang: !!this.elements.sourceLang,
        targetLang: !!this.elements.targetLang,
        sourceText: !!this.elements.sourceText,
        result: !!this.elements.result
      });
      
      console.log('LLOT Modern: Element values', {
        sourceLangValue: this.elements.sourceLang?.value,
        targetLangValue: this.elements.targetLang?.value,
        sourceTextValue: this.elements.sourceText?.value,
        resultTextContent: this.elements.result?.textContent
      });
      
      if (!this.elements.sourceLang || !this.elements.targetLang || !this.elements.sourceText || !this.elements.result) {
        console.error('LLOT Modern: Missing required elements for language swap');
        alert('Missing elements for swap: sourceLang=' + !!this.elements.sourceLang + ', targetLang=' + !!this.elements.targetLang);
        return;
      }
    } catch (error) {
      console.error('LLOT Modern: Error in swapLanguages start:', error);
      alert('Error in swapLanguages: ' + error.message);
      return;
    }
    
    // Handle auto-detect language - we need to use the detected language from last translation
    let actualSourceLang = this.elements.sourceLang.value;
    if (actualSourceLang === 'auto') {
      // Try to get the detected language from the last translation
      // If we don't have it, we can't swap
      console.log('LLOT Modern: Source is auto-detect, checking for detected language');
      
      // For now, let's allow swap but set source to detected language if available
      // This is better UX than blocking the swap entirely
      const detectedLang = this.lastDetectedLanguage || 'en'; // fallback to English
      console.log('LLOT Modern: Using detected/fallback language:', detectedLang);
      actualSourceLang = detectedLang;
      
      // Update the source language select to the detected language
      this.elements.sourceLang.value = actualSourceLang;
      this.updateDropdownDisplay('source-lang-dropdown', actualSourceLang);
    }
    
    const sourceLang = actualSourceLang; // Use the actual source language (not 'auto')
    const targetLang = this.elements.targetLang.value;
    const sourceText = this.elements.sourceText.value;
    const resultText = this.elements.result.textContent;
    
    console.log('LLOT Modern: Swapping languages', { sourceLang, targetLang, actualSourceLang, hasSourceText: !!sourceText, hasResult: !!resultText });
    
    // Add swapping animation class
    const swapButton = document.getElementById('swap_languages');
    if (swapButton) {
      swapButton.classList.add('swapping');
      setTimeout(() => {
        swapButton.classList.remove('swapping');
      }, 600);
    }
    
    if (sourceLang && targetLang) {
      try {
        console.log('LLOT Modern: Starting language swap from', sourceLang, 'to', targetLang);
        
        // Swap language values
        this.elements.sourceLang.value = targetLang;
        this.elements.targetLang.value = sourceLang;
        console.log('LLOT Modern: Language values swapped');
        
        // Update dropdown displays if they exist
        console.log('LLOT Modern: Updating dropdowns', { targetLang, sourceLang });
        this.updateDropdownDisplay('source-lang-dropdown', targetLang);
        this.updateDropdownDisplay('target-lang-dropdown', sourceLang);
        console.log('LLOT Modern: Dropdowns updated');
        
        // If there's translated text, move it to source and translate automatically (like DeepL)
        if (resultText && resultText.trim() && resultText !== sourceText) {
          console.log('LLOT Modern: Moving result text to source and triggering translation');
          this.elements.sourceText.value = resultText.trim();
          this.elements.result.textContent = '';
          this.hideActionButtons();
          this.scheduleTranslation();
        }
        // If there's source text but no translation yet, just translate with swapped languages
        else if (sourceText && sourceText.trim()) {
          console.log('LLOT Modern: Triggering translation with swapped languages');
          this.scheduleTranslation();
        } else {
          console.log('LLOT Modern: No text to translate after swap');
        }
      } catch (error) {
        console.error('LLOT Modern: Error during language swap:', error);
        alert('Error during swap: ' + error.message);
      }
    } else {
      console.error('LLOT Modern: sourceLang or targetLang is missing');
      alert('Language values missing: sourceLang=' + sourceLang + ', targetLang=' + targetLang);
    }
  }

  swapLanguagesWithAnimation(buttonElement) {
    // Add animation to the specific button
    if (buttonElement) {
      buttonElement.classList.add('swapping');
      setTimeout(() => {
        buttonElement.classList.remove('swapping');
      }, 400);
    }
    
    // Perform the language swap
    this.swapLanguages();
  }

  updateDropdownDisplay(dropdownId, languageCode) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;
    
    const selectedSpan = dropdown.querySelector('.selected-language');
    const content = dropdown.querySelector('.language-dropdown-content');
    
    if (!selectedSpan) return;
    
    // Find language name by code
    const languages = [
      { code: 'auto', name: 'Detect language' },
      { code: 'en', name: 'English' },
      { code: 'de', name: 'Deutsch' },
      { code: 'es', name: 'Español' },
      { code: 'fr', name: 'Français' },
      { code: 'it', name: 'Italiano' },
      { code: 'pt', name: 'Português' },
      { code: 'ru', name: 'Русский' },
      { code: 'pl', name: 'Polski' },
      { code: 'nl', name: 'Nederlands' },
      { code: 'ja', name: '日本語' },
      { code: 'ko', name: '한국어' },
      { code: 'zh', name: '中文' },
      { code: 'ar', name: 'العربية' },
      { code: 'hi', name: 'हिन्दी' }
    ];
    
    const language = languages.find(lang => lang.code === languageCode);
    if (language) {
      selectedSpan.textContent = language.name;
      
      // Update selected state in dropdown content if it exists
      if (content) {
        content.querySelectorAll('.language-dropdown-item').forEach(item => {
          item.classList.remove('selected');
        });
        
        const currentItem = content.querySelector(`[data-code="${languageCode}"]`);
        if (currentItem) {
          currentItem.classList.add('selected');
        }
      }
    }
  }

  // Action buttons removed
  
  // Copy and TTS functionality removed - buttons no longer exist
  
  loadHistory() {
    try {
      return JSON.parse(localStorage.getItem('llot-history') || '[]');
    } catch {
      return [];
    }
  }
  
  saveHistory() {
    localStorage.setItem('llot-history', JSON.stringify(this.history));
  }
  
  addToHistory(item) {
    this.history.unshift(item);
    this.history = this.history.slice(0, 20); // Keep only last 20 items
    this.saveHistory();
    this.renderHistory();
  }
  
  initHistory() {
    if (this.history.length > 0) {
      this.elements.historyPanel.style.display = 'block';
      this.renderHistory();
    }
  }
  
  renderHistory() {
    if (!this.elements.historyList) return;
    
    this.elements.historyList.innerHTML = this.history.map(item => `
      <div class="history-item" data-source="${item.source}" data-target="${item.target}">
        <div class="history-text">
          <div class="history-source">${this.truncateText(item.source, 60)}</div>
          <div class="history-result">${this.truncateText(item.target, 60)}</div>
        </div>
        <div class="history-meta">
          <div class="history-lang">${item.sourceLang} → ${item.targetLang}</div>
          <div class="history-time">${this.formatTime(item.timestamp)}</div>
        </div>
      </div>
    `).join('');
    
    // Bind click events
    this.elements.historyList.querySelectorAll('.history-item').forEach(item => {
      item.addEventListener('click', () => {
        const source = item.dataset.source;
        const target = item.dataset.target;
        
        if (this.elements.sourceText) this.elements.sourceText.value = source;
        if (this.elements.result) this.elements.result.textContent = target;
        
        this.updateCharCount();
        // TTS button removed
      });
    });
  }
  
  truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  }
  
  formatTime(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }
  
  setupAutoTranslation() {
    // Initial character count
    this.updateCharCount();
    
    // Auto-focus on text input
    if (this.elements.sourceText) {
      this.elements.sourceText.focus();
    }
  }
  
  async checkConnectionStatus() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (!statusDot || !statusText) return;
    
    try {
      // Test translation to check if everything works
      const testResponse = await fetch('/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'source_text=test&source_lang=auto&target_lang=en&tone=neutral'
      });
      
      if (testResponse.ok) {
        statusDot.style.background = '#10b981'; // Green
        statusText.textContent = 'Connected';
        statusDot.classList.remove('pulse');
      } else {
        throw new Error('Connection failed');
      }
    } catch (error) {
      statusDot.style.background = '#ef4444'; // Red
      statusText.textContent = 'Disconnected';
      statusDot.classList.add('pulse');
      console.error('Connection check failed:', error);
    }
  }

  initLanguageDropdowns() {
    console.log('LLOT Modern: Initializing language dropdowns');
    
    const languages = [
      { code: 'auto', name: 'Detect language', flag: '🔍', sourceOnly: true },
      { code: 'en', name: 'English', flag: '🇺🇸' },
      { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
      { code: 'es', name: 'Español', flag: '🇪🇸' },
      { code: 'fr', name: 'Français', flag: '🇫🇷' },
      { code: 'it', name: 'Italiano', flag: '🇮🇹' },
      { code: 'pt', name: 'Português', flag: '🇵🇹' },
      { code: 'ru', name: 'Русский', flag: '🇷🇺' },
      { code: 'pl', name: 'Polski', flag: '🇵🇱' },
      { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
      { code: 'ja', name: '日本語', flag: '🇯🇵' },
      { code: 'ko', name: '한국어', flag: '🇰🇷' },
      { code: 'zh', name: '中文', flag: '🇨🇳' },
      { code: 'ar', name: 'العربية', flag: '🇸🇦' },
      { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' }
    ];

    // Initialize source language dropdown
    console.log('LLOT Modern: Initializing source dropdown');
    this.initCustomDropdown('source-lang-dropdown', 'source_lang', languages, 'auto');
    
    // Initialize target language dropdown (exclude auto-detect)
    const targetLanguages = languages.filter(lang => !lang.sourceOnly);
    console.log('LLOT Modern: Initializing target dropdown with', targetLanguages.length, 'languages');
    console.log('LLOT Modern: Target languages:', targetLanguages.map(l => l.name).join(', '));
    this.initCustomDropdown('target-lang-dropdown', 'target_lang', targetLanguages, 'de');
  }

  initCustomDropdown(dropdownId, selectId, languages, defaultValue) {
    console.log(`LLOT Modern: *** INITIALIZING DROPDOWN *** ${dropdownId} for select ${selectId}`);
    console.log(`LLOT Modern: Languages count: ${languages.length}, defaultValue: ${defaultValue}`);
    const dropdown = document.getElementById(dropdownId);
    console.log(`LLOT Modern: Found dropdown ${dropdownId}:`, !!dropdown, dropdown);
    if (!dropdown) {
      console.error(`LLOT Modern: Dropdown ${dropdownId} not found!`);
      return;
    }

    const trigger = dropdown.querySelector('.language-dropdown-trigger');
    const panel = dropdown.querySelector('.language-dropdown-panel');
    const content = dropdown.querySelector('.language-dropdown-content');
    const searchInput = dropdown.querySelector('.language-dropdown-search input');
    const hiddenSelect = document.getElementById(selectId);
    const selectedLanguageSpan = trigger.querySelector('.selected-language');

    if (!trigger || !panel || !content || !hiddenSelect) return;

    let filteredLanguages = [...languages];

    // Populate dropdown content
    const populateDropdown = (langs = filteredLanguages) => {
      console.log(`LLOT Modern: *** POPULATING DROPDOWN *** ${dropdownId} with ${langs.length} languages`);
      
      // Clear existing content
      const existingItems = content.children.length;
      console.log(`LLOT Modern: Clearing ${existingItems} existing items from ${dropdownId}`);
      content.innerHTML = '';
      
      langs.forEach((lang, index) => {
        const item = document.createElement('div');
        item.className = `language-dropdown-item${hiddenSelect.value === lang.code ? ' selected' : ''}`;
        item.setAttribute('data-code', lang.code);
        item.innerHTML = `
          <span class="flag">${lang.flag}</span>
          <span class="name">${lang.name}</span>
        `;
        
        // Add click handler with debugging
        const clickHandler = (e) => {
          console.log(`LLOT Modern: *** CLICK EVENT FIRED *** on language item ${lang.code} (${lang.name}) in ${dropdownId}`);
          console.log('LLOT Modern: Click event details:', e.type, e.target, e.currentTarget);
          e.preventDefault();
          e.stopPropagation();
          selectLanguage(lang);
          closeDropdown();
        };
        
        // Use multiple event types for maximum reliability
        item.addEventListener('click', clickHandler, { passive: false });
        item.addEventListener('mousedown', clickHandler, { passive: false });
        item.addEventListener('touchstart', clickHandler, { passive: false });
        item.onclick = clickHandler;
        
        // Add mouse hover debugging
        item.addEventListener('mouseenter', () => {
          console.log(`LLOT Modern: MOUSE ENTERED ${lang.name} in ${dropdownId}`);
        });
        
        item.addEventListener('mouseleave', () => {
          console.log(`LLOT Modern: MOUSE LEFT ${lang.name} in ${dropdownId}`);
        });
        
        // Test if element receives any mouse events
        item.addEventListener('mouseover', (e) => {
          console.log(`LLOT Modern: MOUSE OVER ${lang.name} in ${dropdownId}`, e.target);
        });
        
        console.log(`LLOT Modern: *** ADDED ALL HANDLERS *** to ${lang.name} in ${dropdownId}`);
        content.appendChild(item);
      });
      console.log(`LLOT Modern: *** POPULATED *** dropdown ${dropdownId} with ${content.children.length} items`);
    };

    const selectLanguage = (lang) => {
      console.log(`LLOT Modern: *** SELECTING LANGUAGE *** in dropdown ${dropdownId}:`, lang.code, lang.name);
      console.log('LLOT Modern: Before update - hidden select value:', hiddenSelect.value);
      console.log('LLOT Modern: Before update - displayed text:', selectedLanguageSpan.textContent);
      
      hiddenSelect.value = lang.code;
      selectedLanguageSpan.textContent = lang.name;
      
      console.log('LLOT Modern: After update - hidden select value:', hiddenSelect.value);
      console.log('LLOT Modern: After update - displayed text:', selectedLanguageSpan.textContent);
      
      console.log(`LLOT Modern: Updated hidden select value to:`, hiddenSelect.value);
      
      // Update selected state in current dropdown content
      content.querySelectorAll('.language-dropdown-item').forEach(item => {
        item.classList.remove('selected');
      });
      
      // Find and mark current selection
      const currentItem = content.querySelector(`[data-code="${lang.code}"]`);
      if (currentItem) {
        currentItem.classList.add('selected');
      }
      
      // Trigger change event for existing functionality
      console.log(`LLOT Modern: Triggering change event for ${selectId}`);
      hiddenSelect.dispatchEvent(new Event('change'));
      
      // Also trigger translation if text exists
      if (selectId === 'target_lang') {
        console.log('LLOT Modern: Target language changed, checking if translation needed');
        const sourceText = document.getElementById('source_text')?.value?.trim();
        if (sourceText) {
          console.log('LLOT Modern: Source text exists, scheduling translation');
          // Get the app instance and trigger translation
          if (window.llotApp && typeof window.llotApp.scheduleTranslation === 'function') {
            window.llotApp.scheduleTranslation();
          }
        }
      }
    };

    const openDropdown = () => {
      console.log(`LLOT Modern: Opening dropdown ${dropdownId}`);
      dropdown.classList.add('open');
      
      // Close other dropdowns first
      document.querySelectorAll('.language-dropdown.open').forEach(d => {
        if (d !== dropdown) d.classList.remove('open');
      });
      
      // Ensure dropdown is fully populated before focusing search
      if (content.children.length === 0) {
        console.log(`LLOT Modern: Content empty, populating ${dropdownId} before open`);
        populateDropdown();
      }
      
      // Focus search input but prevent immediate events
      setTimeout(() => {
        searchInput.focus();
      }, 100);
      console.log(`LLOT Modern: Dropdown ${dropdownId} opened, content has ${content.children.length} items`);
      
      // Debug: Test if first item is clickable after a small delay
      setTimeout(() => {
        const firstItem = content.querySelector('.language-dropdown-item');
        if (firstItem) {
          console.log(`LLOT Modern: First item in ${dropdownId}:`, firstItem);
          console.log(`LLOT Modern: First item clickable test - onclick:`, typeof firstItem.onclick);
          
          // Add a test button that can programmatically click the first item
          if (dropdownId === 'target-lang-dropdown') {
            console.log(`LLOT Modern: Adding test click for ${dropdownId} first item`);
            window.testTargetDropdownClick = () => {
              console.log('LLOT Modern: TEST CLICK on first target item');
              firstItem.click();
            };
            console.log('LLOT Modern: Test available - run testTargetDropdownClick() in console');
          }
        }
      }, 50);
    };

    const closeDropdown = () => {
      console.log(`LLOT Modern: Closing dropdown ${dropdownId}`);
      dropdown.classList.remove('open');
      
      // Check if search was used before clearing it
      const hadSearch = searchInput.value.trim() !== '';
      searchInput.value = '';
      
      // Only repopulate if search was used (to restore full list)
      if (hadSearch) {
        console.log(`LLOT Modern: Restoring full list for ${dropdownId} after search`);
        populateDropdown();
      } else {
        console.log(`LLOT Modern: No search used, keeping existing items for ${dropdownId}`);
      }
    };

    // Bind events
    trigger.addEventListener('click', (e) => {
      console.log(`LLOT Modern: Trigger clicked for dropdown ${dropdownId}`);
      e.stopPropagation();
      if (dropdown.classList.contains('open')) {
        console.log(`LLOT Modern: Closing dropdown ${dropdownId}`);
        closeDropdown();
      } else {
        console.log(`LLOT Modern: Opening dropdown ${dropdownId}`);
        openDropdown();
      }
    });

    // Search functionality
    searchInput.addEventListener('input', (e) => {
      console.log(`LLOT Modern: Search input in ${dropdownId}:`, e.target.value);
      const query = e.target.value.toLowerCase();
      const filtered = languages.filter(lang => 
        lang.name.toLowerCase().includes(query) || 
        lang.code.toLowerCase().includes(query)
      );
      console.log(`LLOT Modern: Re-populating ${dropdownId} with ${filtered.length} filtered results`);
      populateDropdown(filtered);
    });

    // Store close function globally for document handler
    window.closeDropdownCallbacks = window.closeDropdownCallbacks || [];
    window.closeDropdownCallbacks.push({
      dropdownId: dropdownId,
      dropdown: dropdown,
      closeDropdown: closeDropdown
    });

    // Add multiple levels of event delegation
    content.addEventListener('click', (e) => {
      console.log(`LLOT Modern: *** CONTENT CONTAINER CLICK *** in ${dropdownId}:`, e.target, e.currentTarget);
      
      const item = e.target.closest('.language-dropdown-item');
      if (item) {
        const langCode = item.getAttribute('data-code');
        console.log(`LLOT Modern: *** CONTENT DELEGATION CLICK *** on ${langCode} in ${dropdownId}`);
        
        const languages = [
          { code: 'auto', name: 'Detect language', flag: '🔍', sourceOnly: true },
          { code: 'en', name: 'English', flag: '🇺🇸' },
          { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
          { code: 'es', name: 'Español', flag: '🇪🇸' },
          { code: 'fr', name: 'Français', flag: '🇫🇷' },
          { code: 'it', name: 'Italiano', flag: '🇮🇹' },
          { code: 'pt', name: 'Português', flag: '🇵🇹' },
          { code: 'ru', name: 'Русский', flag: '🇷🇺' },
          { code: 'pl', name: 'Polski', flag: '🇵🇱' },
          { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
          { code: 'ja', name: '日本語', flag: '🇯🇵' },
          { code: 'ko', name: '한국어', flag: '🇰🇷' },
          { code: 'zh', name: '中文', flag: '🇨🇳' },
          { code: 'ar', name: 'العربية', flag: '🇦🇪' },
          { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' }
        ];
        
        const lang = languages.find(l => l.code === langCode);
        if (lang) {
          e.preventDefault();
          e.stopPropagation();
          selectLanguage(lang);
          closeDropdown();
        }
      } else {
        console.log(`LLOT Modern: Content click but no item found in ${dropdownId}`);
      }
    }, { capture: true });
    
    // Also add to panel level
    panel.addEventListener('click', (e) => {
      console.log(`LLOT Modern: *** PANEL CLICK *** in ${dropdownId}:`, e.target);
      
      const item = e.target.closest('.language-dropdown-item');
      if (item) {
        const langCode = item.getAttribute('data-code');
        console.log(`LLOT Modern: *** PANEL DELEGATION CLICK *** on ${langCode} in ${dropdownId}`);
        
        const languages = [
          { code: 'auto', name: 'Detect language', flag: '🔍', sourceOnly: true },
          { code: 'en', name: 'English', flag: '🇺🇸' },
          { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
          { code: 'es', name: 'Español', flag: '🇪🇸' },
          { code: 'fr', name: 'Français', flag: '🇫🇷' },
          { code: 'it', name: 'Italiano', flag: '🇮🇹' },
          { code: 'pt', name: 'Português', flag: '🇵🇹' },
          { code: 'ru', name: 'Русский', flag: '🇷🇺' },
          { code: 'pl', name: 'Polski', flag: '🇵🇱' },
          { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
          { code: 'ja', name: '日本語', flag: '🇯🇵' },
          { code: 'ko', name: '한국어', flag: '🇰🇷' },
          { code: 'zh', name: '中文', flag: '🇨🇳' },
          { code: 'ar', name: 'العربية', flag: '🇦🇪' },
          { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' }
        ];
        
        const lang = languages.find(l => l.code === langCode);
        if (lang) {
          e.preventDefault();
          e.stopPropagation();
          selectLanguage(lang);
          closeDropdown();
        }
      }
    }, { capture: true });

    // Initial population
    populateDropdown();
    
    // Set default language
    const defaultLang = languages.find(lang => lang.code === defaultValue);
    if (defaultLang) {
      selectLanguage(defaultLang);
    }
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.llotApp = new LLOTApp();
  
  // Additional direct event listener for swap button - DISABLED FOR DEBUGGING
  console.log('LLOT Modern: Swap button handlers DISABLED for debugging');
  /*
  const swapButtonDirect = document.getElementById('swap_languages');
  console.log('LLOT Modern: Direct swap button check:', !!swapButtonDirect, swapButtonDirect);
  
  if (swapButtonDirect) {
    swapButtonDirect.addEventListener('click', function(e) {
      console.log('LLOT Modern: Direct swap button clicked!');
      e.preventDefault();
      alert('Swap button clicked!'); // Visible feedback for debugging
      if (window.llotApp && typeof window.llotApp.swapLanguages === 'function') {
        window.llotApp.swapLanguages();
      } else {
        console.error('LLOT Modern: App or swapLanguages method not available');
      }
    });
    console.log('LLOT Modern: Direct event listener attached to swap button');
  } else {
    console.error('LLOT Modern: Could not find swap button element!');
  }
  */
  
  // Test function for debugging
  window.testSwap = function() {
    console.log('=== SWAP TEST ===');
    console.log('swapButton element:', document.getElementById('swap_languages'));
    console.log('sourceLang element:', document.getElementById('source_lang'));
    console.log('targetLang element:', document.getElementById('target_lang'));
    console.log('App instance:', window.llotApp);
    if (window.llotApp && window.llotApp.elements) {
      console.log('App elements:', window.llotApp.elements);
    }
    console.log('=== END TEST ===');
  };

  // Direct test of swap functionality
  window.testSwapDirect = function() {
    console.log('=== DIRECT SWAP TEST ===');
    if (window.llotApp && typeof window.llotApp.swapLanguages === 'function') {
      window.llotApp.swapLanguages();
    } else {
      console.error('LLOT app or swapLanguages not available');
    }
    console.log('=== END DIRECT TEST ===');
  };
});

// Add CSS for spinner animation
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);

// Global document click handler for all dropdowns - DISABLED FOR DEBUGGING
document.addEventListener('click', (e) => {
  console.log('LLOT Modern: Global document click DISABLED for debugging:', e.target);
  
  // Temporarily disabled to test if this is blocking item clicks
  return;
  
  if (!window.closeDropdownCallbacks) return;
  
  console.log('LLOT Modern: Global document click:', e.target);
  
  // Don't close if clicking on a language dropdown item - but let the click propagate
  const clickedItem = e.target.closest('.language-dropdown-item');
  if (clickedItem) {
    console.log('LLOT Modern: Click on dropdown item, letting it propagate');
    // Don't return here - let the item click handlers execute first
    // We'll close the dropdown after the item handlers run
    setTimeout(() => {
      const dropdown = clickedItem.closest('.language-dropdown');
      if (dropdown && dropdown.classList.contains('open')) {
        console.log('LLOT Modern: Closing dropdown after item click');
        dropdown.classList.remove('open');
        const searchInput = dropdown.querySelector('.language-dropdown-search input');
        if (searchInput) {
          searchInput.value = '';
        }
      }
    }, 0);
    return;
  }
  
  // Close all dropdowns that don't contain the clicked element
  window.closeDropdownCallbacks.forEach(({dropdownId, dropdown, closeDropdown}) => {
    if (!dropdown.contains(e.target)) {
      console.log(`LLOT Modern: Closing ${dropdownId} from global handler`);
      closeDropdown();
    }
  });
});

// Debug function to compare dropdowns
window.debugDropdowns = () => {
  console.log('=== DROPDOWN DEBUG COMPARISON ===');
  
  const source = document.getElementById('source-lang-dropdown');
  const target = document.getElementById('target-lang-dropdown');
  
  console.log('Source dropdown:', source);
  console.log('Target dropdown:', target);
  
  if (source) {
    const sourceContent = source.querySelector('.language-dropdown-content');
    console.log('Source content:', sourceContent);
    console.log('Source items:', sourceContent?.children.length || 0);
  }
  
  if (target) {
    const targetContent = target.querySelector('.language-dropdown-content');
    console.log('Target content:', targetContent);
    console.log('Target items:', targetContent?.children.length || 0);
  }
  
  console.log('Close callbacks:', window.closeDropdownCallbacks);
};

// Debug function to test target dropdown events
window.testTargetEvents = () => {
  console.log('=== TESTING TARGET DROPDOWN EVENTS ===');
  
  const target = document.getElementById('target-lang-dropdown');
  if (!target) {
    console.log('Target dropdown not found!');
    return;
  }
  
  const items = target.querySelectorAll('.language-dropdown-item');
  console.log(`Found ${items.length} target dropdown items`);
  
  if (items.length > 0) {
    const firstItem = items[0];
    console.log('First target item:', firstItem);
    console.log('First item data-code:', firstItem.getAttribute('data-code'));
    console.log('First item onclick:', typeof firstItem.onclick);
    
    // Test if we can manually trigger mouse events
    console.log('Testing mouse events on first item...');
    
    // Create and dispatch mouse events
    const mouseEnter = new MouseEvent('mouseenter', { bubbles: true });
    const mouseOver = new MouseEvent('mouseover', { bubbles: true });
    const click = new MouseEvent('click', { bubbles: true });
    
    console.log('Dispatching mouseenter...');
    firstItem.dispatchEvent(mouseEnter);
    
    console.log('Dispatching mouseover...');
    firstItem.dispatchEvent(mouseOver);
    
    console.log('Dispatching click...');
    firstItem.dispatchEvent(click);
  }
};

console.log('LLOT Modern: JavaScript file loaded completely');
console.log('LLOT Modern: Available functions:', {
  jsLoaded: typeof window.jsLoaded,
  debugDropdowns: typeof window.debugDropdowns,
  testTargetEvents: typeof window.testTargetEvents
});
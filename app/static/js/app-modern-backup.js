/**
 * LLOT Modern JavaScript 2025 - Clean Rewrite
 * Simple, functional JavaScript without unnecessary complexity
 */

class LLOTApp {
  constructor() {
    this.translationTimeout = null;
    this.historyTimeout = null;
    this.currentAudio = null;
    this.history = this.loadHistory();
    this.lastDetectedLanguage = 'en';
    
    this.init();
  }
  
  init() {
    this.initTheme();
    this.initElements();
    this.bindEvents();
    this.initHistory();
    this.setupAutoTranslation();
    this.startHealthMonitoring();
    this.initLanguageDropdowns();
    this.updateCharCount();
    this.initializeTTS();
  }
  
  initTheme() {
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
    
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
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
        const currentTheme = document.documentElement.getAttribute('data-theme');
        this.setTheme(currentTheme === 'dark' ? 'light' : 'dark');
      });
    }

    // Language change handlers
    if (this.elements.sourceLang) {
      this.elements.sourceLang.addEventListener('change', () => {
        this.scheduleTranslation();
      });
    }

    if (this.elements.targetLang) {
      this.elements.targetLang.addEventListener('change', () => {
        this.scheduleTranslation();
        this.updateTTSButton();
        this.updateCopyButton();
      });
    }

    if (this.elements.tone) {
      this.elements.tone.addEventListener('change', () => {
        this.scheduleTranslation();
      });
    }

    // Language swap - handle both desktop and mobile buttons
    if (this.elements.swapButton) {
      this.elements.swapButton.addEventListener('click', () => {
        this.swapLanguages();
      });
    }
    
    const swapButtonTop = document.getElementById('swap_languages_top');
    if (swapButtonTop) {
      swapButtonTop.addEventListener('click', () => {
        this.swapLanguages();
      });
    }

    // Options dropdown - inicjalizacja w output panel header
    if (this.elements.outputOptionsDropdown) {
      this.initOutputOptionsDropdown();
    }

    // Tone change handler
    if (this.elements.tone) {
      this.elements.tone.addEventListener('change', () => {
        this.scheduleTranslation();
      });
    }

    // Copy button
    document.addEventListener('click', (e) => {
      if (e.target.closest('#copy-btn')) {
        this.copyToClipboard();
      }
    });


    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'Enter' && e.shiftKey) {
          e.preventDefault();
          this.scheduleTranslation();
        }
        if (e.key === 'c' && e.shiftKey) {
          e.preventDefault();
          this.copyToClipboard();
        }
      }
      
      // Close dropdowns with Escape key
      if (e.key === 'Escape') {
        document.querySelectorAll('.language-dropdown.open').forEach(d => {
          d.classList.remove('open');
        });
        document.querySelectorAll('.header-dropdown.open').forEach(d => {
          d.classList.remove('open');
        });
      }
    });
  }

  scheduleTranslation() {
    if (this.translationTimeout) {
      clearTimeout(this.translationTimeout);
    }
    
    const sourceText = this.elements.sourceText?.value?.trim();
    
    // Different delays based on content length and completion
    let delay;
    if (!sourceText) {
      delay = 0; // Clear immediately when empty
    } else if (sourceText.length < 10) {
      delay = 500; // Wait longer for short text (might still be typing)
    } else if (sourceText.endsWith(' ') || sourceText.endsWith('.') || sourceText.endsWith('!') || sourceText.endsWith('?')) {
      delay = 150; // Quick translation after space or punctuation (word/sentence complete)
    } else {
      delay = 400; // Medium delay for ongoing typing
    }
    
    this.translationTimeout = setTimeout(() => {
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
        headers: {
          'Content-Type': 'application/json',
        },
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
        this.lastDetectedLanguage = data.source_lang;
      }

      // Add to history with delay
      this.scheduleHistoryAdd(sourceText, data.translated_text, sourceLang, targetLang);

    } catch (error) {
      console.error('Translation error:', error);
      this.showError('Translation failed');
    }
  }

  showResult(translation) {
    if (this.elements.result) {
      this.elements.result.classList.remove('translating');
      this.makeWordsClickable(translation);
    }
    this.hideLoading();
    this.updateCharCount();
    this.updateFontSize(); // Update font size for both input and output
    this.updateTTSButton();
    this.updateCopyButton();
  }

  makeWordsClickable(translation) {
    const parts = translation.split(/(\s+|[^\p{L}\p{N}\p{M}]+)/u);
    
    const clickableHtml = parts.map(part => 
      /[\p{L}\p{N}]/u.test(part) 
        ? `<span class="clickable-word" data-word="${part}">${part}</span>`
        : part
    ).join('');
    
    this.elements.result.innerHTML = clickableHtml;
    
    // Always ensure TTS button after changing innerHTML
    if (window.ttsEnabled) {
      this.ensureTTSButton();
      this.updateTTSButton();
    }
    this.ensureCopyButton();
    this.updateCopyButton();
    
    // Preserve font size after changing innerHTML
    this.updateFontSize();
    
    this.elements.result.querySelectorAll('.clickable-word').forEach(wordElement => {
      wordElement.addEventListener('click', (e) => {
        e.stopPropagation();
        this.handleWordClick(wordElement);
      });
    });
  }

  ensureTTSButton() {
    let ttsBtn = this.elements.result.querySelector('#tts-btn');
    
    if (!ttsBtn) {
      // Check if output-actions container exists
      let actionsContainer = this.elements.result.querySelector('.output-actions');
      
      if (!actionsContainer) {
        actionsContainer = document.createElement('div');
        actionsContainer.className = 'output-actions';
        this.elements.result.appendChild(actionsContainer);
      }
      
      ttsBtn = document.createElement('button');
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
    
    return ttsBtn;
  }

  ensureCopyButton() {
    let copyBtn = this.elements.result.querySelector('#copy-btn');
    
    if (!copyBtn) {
      // Check if output-actions container exists
      let actionsContainer = this.elements.result.querySelector('.output-actions');
      
      if (!actionsContainer) {
        actionsContainer = document.createElement('div');
        actionsContainer.className = 'output-actions';
        this.elements.result.appendChild(actionsContainer);
      }
      
      copyBtn = document.createElement('button');
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
      
      // Add copy button first, then TTS button if it exists
      const ttsBtn = actionsContainer.querySelector('#tts-btn');
      if (ttsBtn) {
        actionsContainer.insertBefore(copyBtn, ttsBtn);
      } else {
        actionsContainer.appendChild(copyBtn);
      }
    }
    
    return copyBtn;
  }

  async handleWordClick(wordElement) {
    const clickedWord = wordElement.dataset.word;
    const sourceText = this.elements.sourceText?.value?.trim();
    const currentTranslation = this.getPlainTextFromResult();
    const targetLang = this.elements.targetLang?.value || 'de';
    const tone = this.elements.tone?.value || 'neutral';

    if (!sourceText || !currentTranslation || !clickedWord) return;

    this.closeWordAlternatives();
    this.closeValidationPopup();

    document.querySelectorAll('.clickable-word.selected').forEach(el => el.classList.remove('selected'));
    wordElement.classList.add('selected');

    this.originalTranslationState = {
      html: this.elements.result.innerHTML,
      text: currentTranslation
    };

    this.showWordAlternatives(wordElement, clickedWord, sourceText, currentTranslation, targetLang, tone);
  }

  getPlainTextFromResult() {
    if (!this.elements.result) return '';
    // Get text content while preserving spaces properly
    return this.elements.result.textContent || '';
  }

  async showWordAlternatives(wordElement, clickedWord, sourceText, currentTranslation, targetLang, tone) {
    // Create popup element
    const popup = document.createElement('div');
    popup.className = 'word-alternatives show';
    popup.innerHTML = `
      <div class="alternatives-header">Alternatives for "${clickedWord}"</div>
      <div class="alternatives-loading">
        <div class="spinner"></div>
        Loading alternatives...
      </div>
    `;

    // Position popup near the clicked word
    const rect = wordElement.getBoundingClientRect();
    popup.style.left = `${rect.left}px`;
    popup.style.top = `${rect.bottom + 8}px`;

    document.body.appendChild(popup);

    try {
      // Fetch alternatives
      const response = await fetch('/api/alternatives', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_text: sourceText,
          current_translation: currentTranslation,
          clicked_word: clickedWord,
          target_lang: targetLang,
          tone: tone
        })
      });

      const data = await response.json();
      const alternatives = data.alternatives || [];

      // Update popup with alternatives
      if (alternatives.length > 0) {
        const listHtml = alternatives.map(alt => `
          <div class="alternative-item ${alt === clickedWord ? 'current' : ''}" data-alternative="${alt}">
            ${alt}
          </div>
        `).join('');

        popup.innerHTML = `
          <div class="alternatives-header">Alternatives for "${clickedWord}"</div>
          <div class="alternatives-list">${listHtml}</div>
        `;

        // Add click handlers for alternatives
        popup.querySelectorAll('.alternative-item').forEach(item => {
          item.addEventListener('click', () => {
            const alternative = item.dataset.alternative;
            this.replaceWord(wordElement, alternative);
            this.closeWordAlternatives();
          });
        });
      } else {
        popup.innerHTML = `
          <div class="alternatives-header">Alternatives for "${clickedWord}"</div>
          <div class="alternatives-loading">No alternatives found</div>
        `;
      }
    } catch (error) {
      console.error('Error fetching alternatives:', error);
      popup.innerHTML = `
        <div class="alternatives-header">Alternatives for "${clickedWord}"</div>
        <div class="alternatives-loading">Error loading alternatives</div>
      `;
    }

    // Close popup when clicking outside
    const closeHandler = (e) => {
      if (!popup.contains(e.target) && !wordElement.contains(e.target)) {
        this.closeWordAlternatives();
        document.removeEventListener('click', closeHandler);
      }
    };
    setTimeout(() => document.addEventListener('click', closeHandler), 100);
  }

  async replaceWord(wordElement, newWord) {
    const originalWord = wordElement.dataset.word;
    
    // Replace the word immediately
    wordElement.textContent = newWord;
    wordElement.dataset.word = newWord;
    wordElement.classList.remove('selected');
    wordElement.classList.add('validating');
    
    // Show validation status
    this.showValidationStatus('Validating translation...');
    
    try {
      // Get the new full translation as plain text
      const newTranslation = this.getPlainTextFromResult();
      const sourceText = this.elements.sourceText?.value?.trim();
      const targetLang = this.elements.targetLang?.value || 'de';
      const tone = this.elements.tone?.value || 'neutral';
      
      // Validate entire sentence coherence with backend
      const response = await fetch('/api/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_text: sourceText,
          current_translation: newTranslation,
          target_lang: targetLang,
          tone: tone,
          enforced_phrases: [], // No enforced phrases for validation
          replacements: [{
            from: originalWord,
            to: newWord
          }]
        })
      });
      
      const data = await response.json();
      
      if (data.translated && data.translated.trim() !== newTranslation.trim()) {
        // Model refined the translation - auto-accept it
        this.makeWordsClickable(data.translated);
        this.hideValidationStatus();
      } else if (data.faithful === false) {
        // Translation is unfaithful - revert to original
        this.rollbackToOriginal();
      } else {
        // Translation is coherent and faithful
        wordElement.classList.remove('validating');
        this.hideValidationStatus();
      }
      
    } catch (error) {
      console.error('Validation error:', error);
      // On validation error, keep the user's change
      wordElement.classList.remove('validating');
      this.hideValidationStatus();
    }
  }
  
  rollbackToOriginal() {
    if (this.originalTranslationState) {
      this.elements.result.innerHTML = this.originalTranslationState.html;
      
      // Re-attach event listeners to clickable words
      this.elements.result.querySelectorAll('.clickable-word').forEach(wordElement => {
        wordElement.addEventListener('click', (e) => {
          e.stopPropagation();
          this.handleWordClick(wordElement);
        });
      });
      
      // Ensure TTS button is restored if needed
      if (window.ttsEnabled) {
        this.ensureTTSButton();
        this.updateTTSButton();
      }
      this.ensureCopyButton();
      this.updateCopyButton();
      
      // Restore font size
      this.updateFontSize();
    }
    this.clearValidatingStates();
    this.hideValidationStatus();
  }
  
  showValidationStatus(message) {
    if (this.elements.statusText) {
      this.elements.statusText.textContent = message;
    }
    if (this.elements.spinner) {
      this.elements.spinner.style.display = 'block';
    }
  }
  
  showValidationResult(message, acceptCallback, rejectCallback, keepCallback) {
    this.closeValidationPopup(); // Close any existing popup
    this.hideValidationStatus();
    
    // Create validation popup
    const popup = document.createElement('div');
    popup.className = 'validation-popup show';
    popup.id = 'validation-popup';
    
    const buttons = [];
    if (acceptCallback) {
      buttons.push('<button class="validation-btn accept">Accept Suggestion</button>');
    }
    buttons.push('<button class="validation-btn reject">Revert to Original</button>');
    if (keepCallback) {
      buttons.push('<button class="validation-btn dismiss">Keep My Change</button>');
    }
    
    popup.innerHTML = `
      <div class="validation-message">${message}</div>
      <div class="validation-actions">
        ${buttons.join('')}
      </div>
    `;
    
    // Position popup
    popup.style.left = '50%';
    popup.style.top = '50%';
    popup.style.transform = 'translate(-50%, -50%)';
    
    document.body.appendChild(popup);
    
    // Add event listeners
    if (acceptCallback && popup.querySelector('.accept')) {
      popup.querySelector('.accept').addEventListener('click', () => {
        acceptCallback();
        this.closeValidationPopup();
      });
    }
    
    if (popup.querySelector('.reject')) {
      popup.querySelector('.reject').addEventListener('click', () => {
        if (rejectCallback) rejectCallback();
        this.closeValidationPopup();
      });
    }
    
    if (keepCallback && popup.querySelector('.dismiss')) {
      popup.querySelector('.dismiss').addEventListener('click', () => {
        keepCallback();
        this.closeValidationPopup();
      });
    }
    
    // Auto-dismiss after 15 seconds
    setTimeout(() => {
      this.closeValidationPopup();
    }, 15000);
  }

  closeValidationPopup() {
    const popup = document.getElementById('validation-popup');
    if (popup) {
      popup.remove();
    }
    this.clearValidatingStates();
  }
  
  hideValidationStatus() {
    if (this.elements.statusText) {
      this.elements.statusText.textContent = 'Ready to translate';
    }
    if (this.elements.spinner) {
      this.elements.spinner.style.display = 'none';
    }
  }
  
  clearValidatingStates() {
    document.querySelectorAll('.clickable-word.validating').forEach(word => {
      word.classList.remove('validating');
    });
  }

  closeWordAlternatives() {
    document.querySelectorAll('.word-alternatives').forEach(popup => {
      popup.remove();
    });
    document.querySelectorAll('.clickable-word.selected').forEach(word => {
      word.classList.remove('selected');
    });
  }

  clearResult() {
    if (this.elements.result) {
      this.elements.result.textContent = '';
    }
    this.updateFontSize(); // Update font size when result is cleared
    this.hideLoading();
  }

  showLoading() {
    if (this.elements.spinner) {
      this.elements.spinner.style.display = 'block';
    }
    if (this.elements.statusText) {
      this.elements.statusText.textContent = 'Translating...';
    }
    
    // Add translating state to result area
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
    
    // Remove translating state
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
    
    // Remove all font size classes from both input and output
    this.elements.sourceText.classList.remove('font-large', 'font-medium', 'font-normal', 'font-small');
    this.elements.result.classList.remove('font-large', 'font-medium', 'font-normal', 'font-small');
    
    // Determine font size class based on character count - similar to DeepL's behavior
    let fontSizeClass;
    if (charCount === 0) {
      fontSizeClass = 'font-large'; // Large placeholder text when empty
    } else if (charCount < 50) {
      fontSizeClass = 'font-large'; // Large font for short text
    } else if (charCount < 150) {
      fontSizeClass = 'font-medium'; // Medium font for moderate text
    } else if (charCount < 300) {
      fontSizeClass = 'font-normal'; // Normal font for longer text
    } else {
      fontSizeClass = 'font-small'; // Small font for very long text
    }
    
    // Apply font size to both input and output
    this.elements.sourceText.classList.add(fontSizeClass);
    this.elements.result.classList.add(fontSizeClass);
    
    // Force reflow to ensure changes are applied
    this.elements.sourceText.offsetHeight;
    this.elements.result.offsetHeight;
  }

  swapLanguages() {
    const sourceLang = this.elements.sourceLang?.value;
    const targetLang = this.elements.targetLang?.value;
    const sourceText = this.elements.sourceText?.value;
    const resultText = this.elements.result?.textContent;

    if (!sourceLang || !targetLang) return;

    // Handle auto-detect language
    let actualSourceLang = sourceLang;
    if (sourceLang === 'auto') {
      actualSourceLang = this.lastDetectedLanguage || 'en';
    }

    // Don't allow swapping to auto
    if (targetLang === 'auto') return;

    // Swap languages
    this.elements.sourceLang.value = targetLang;
    this.elements.targetLang.value = actualSourceLang;

    // Update dropdown displays for both desktop and mobile
    this.updateDropdownDisplay('source-lang-dropdown', targetLang);
    this.updateDropdownDisplay('target-lang-dropdown', actualSourceLang);
    this.updateDropdownDisplay('source-lang-dropdown-top', targetLang);
    this.updateDropdownDisplay('target-lang-dropdown-top', actualSourceLang);

    // Swap text if there's a valid translation
    if (resultText && resultText.trim() && !resultText.startsWith('Error:')) {
      this.elements.sourceText.value = resultText;
      this.elements.result.textContent = '';
      this.elements.result.style.color = '';
      this.updateFontSize();
      this.scheduleTranslation();
    } else if (sourceText && sourceText.trim()) {
      this.scheduleTranslation();
    }
  }

  updateDropdownDisplay(dropdownId, languageCode) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;
    
    const selectedSpan = dropdown.querySelector('.selected-language');
    if (!selectedSpan) return;
    
    const languages = this.getLanguages();
    const language = languages.find(lang => lang.code === languageCode);
    if (language) {
      selectedSpan.textContent = language.name;
    }
  }

  synchronizeDropdowns(selectId, languageCode, languageName) {
    // Get all dropdowns that control the same select element
    const dropdownIds = [];
    if (selectId === 'source_lang') {
      dropdownIds.push('source-lang-dropdown', 'source-lang-dropdown-top');
    } else if (selectId === 'target_lang') {
      dropdownIds.push('target-lang-dropdown', 'target-lang-dropdown-top');
    }
    
    // Update all related dropdowns
    dropdownIds.forEach(dropdownId => {
      const dropdown = document.getElementById(dropdownId);
      if (!dropdown) return;
      
      const selectedSpan = dropdown.querySelector('.selected-language');
      if (selectedSpan) {
        selectedSpan.textContent = languageName;
      }
      
      // Update selected items in dropdown content
      const content = dropdown.querySelector('.language-dropdown-content');
      if (content) {
        content.querySelectorAll('.language-dropdown-item').forEach(item => {
          if (item.getAttribute('data-code') === languageCode) {
            item.classList.add('selected');
          } else {
            item.classList.remove('selected');
          }
        });
      }
    });
  }

  setupAutoTranslation() {
    if (!this.elements.sourceText) return;
    
    this.elements.sourceText.addEventListener('input', () => {
      this.updateCharCount();
      this.updateFontSize(); // Update font size first
      this.scheduleTranslation();
      this.autoResizeTextarea();
    });
    
    // Also translate on blur (when user clicks away)
    this.elements.sourceText.addEventListener('blur', () => {
      if (this.translationTimeout) {
        clearTimeout(this.translationTimeout);
      }
      this.performTranslation();
    });

    this.elements.sourceText.addEventListener('paste', () => {
      setTimeout(() => {
        this.updateCharCount();
        this.updateFontSize();
        this.scheduleTranslation();
        this.autoResizeTextarea();
      }, 100);
    });
    
    // Also handle keyup for better responsiveness (catches delete, backspace, etc.)
    this.elements.sourceText.addEventListener('keyup', () => {
      this.updateCharCount();
      this.updateFontSize();
      this.scheduleTranslation();
    });
    
    // Initial resize and font size
    this.autoResizeTextarea();
    this.updateFontSize();
  }

  autoResizeTextarea() {
    if (!this.elements.sourceText) return;
    
    const textarea = this.elements.sourceText;
    const minHeight = 400; // Match CSS min-height
    
    // Temporarily remove height to get accurate scrollHeight
    const currentHeight = textarea.style.height;
    textarea.style.height = 'auto';
    
    // Calculate new height based on content
    const scrollHeight = textarea.scrollHeight;
    const newHeight = Math.max(minHeight, scrollHeight);
    
    // Set new height with proper box-sizing consideration
    textarea.style.height = `${newHeight}px`;
    textarea.style.minHeight = `${newHeight}px`;
    
    // Also update output panel to match height - account for padding
    if (this.elements.result) {
      const outputPadding = 24; // 1.5rem * 16px = 24px padding
      this.elements.result.style.minHeight = `${newHeight - outputPadding}px`;
    }
  }

  async checkConnectionStatus() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.querySelector('.status-indicator .status-text');
    
    if (!statusDot || !statusText) return;
    
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      
      // Update status based on overall status
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
      
      // Update tooltip with detailed status
      const statusIndicator = document.getElementById('connection-status');
      if (statusIndicator) {
        let tooltip = 'Service Status:\n';
        tooltip += `Ollama: ${data.ollama.status}`;
        if (data.ollama.error) tooltip += ` (${data.ollama.error})`;
        tooltip += `\nTTS: ${data.tts.status}`;
        if (data.tts.error) tooltip += ` (${data.tts.error})`;
        statusIndicator.title = tooltip;
      }
      
    } catch (error) {
      console.error('Health check failed:', error);
      statusDot.classList.remove('pulse', 'connected', 'warning');
      statusDot.classList.add('error');
      statusText.textContent = 'Error';
    }
  }

  startHealthMonitoring() {
    // Initial check
    this.checkConnectionStatus();
    
    // Check every 30 seconds
    setInterval(() => {
      this.checkConnectionStatus();
    }, 30000);
  }

  getLanguages() {
    return [
      { code: 'auto', name: 'Detect language', flag: '🔍', sourceOnly: true },
      
      // Major world languages (well-supported by most LLMs)
      { code: 'en', name: 'English', flag: '🇺🇸' },
      { code: 'zh', name: '中文', flag: '🇨🇳' },
      { code: 'es', name: 'Español', flag: '🇪🇸' },
      { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
      { code: 'ar', name: 'العربية', flag: '🇦🇪' },
      { code: 'pt', name: 'Português', flag: '🇵🇹' },
      { code: 'bn', name: 'বাংলা', flag: '🇧🇩' },
      { code: 'ru', name: 'Русский', flag: '🇷🇺' },
      { code: 'ja', name: '日本語', flag: '🇯🇵' },
      { code: 'pa', name: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
      { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
      { code: 'jv', name: 'Basa Jawa', flag: '🇮🇩' },
      { code: 'ko', name: '한국어', flag: '🇰🇷' },
      { code: 'fr', name: 'Français', flag: '🇫🇷' },
      { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
      { code: 'ur', name: 'اردو', flag: '🇵🇰' },
      { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
      { code: 'it', name: 'Italiano', flag: '🇮🇹' },
      { code: 'th', name: 'ไทย', flag: '🇹🇭' },
      { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳' },
      { code: 'fa', name: 'فارسی', flag: '🇮🇷' },
      { code: 'pl', name: 'Polski', flag: '🇵🇱' },
      { code: 'uk', name: 'Українська', flag: '🇺🇦' },
      { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
      { code: 'ml', name: 'മലയാളം', flag: '🇮🇳' },
      { code: 'kn', name: 'ಕನ್ನಡ', flag: '🇮🇳' },
      { code: 'or', name: 'ଓଡିଆ', flag: '🇮🇳' },
      { code: 'te', name: 'తెలుగు', flag: '🇮🇳' },
      { code: 'as', name: 'অসমীয়া', flag: '🇮🇳' },
      { code: 'bh', name: 'भोजपुरी', flag: '🇮🇳' },
      { code: 'ne', name: 'नेपाली', flag: '🇳🇵' },
      { code: 'si', name: 'සිංහල', flag: '🇱🇰' },
      { code: 'ka', name: 'ქართული', flag: '🇬🇪' },
      { code: 'am', name: 'አማርኛ', flag: '🇪🇹' },
      { code: 'he', name: 'עברית', flag: '🇮🇱' },
      { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
      { code: 'id', name: 'Bahasa Indonesia', flag: '🇮🇩' },
      { code: 'ms', name: 'Bahasa Melayu', flag: '🇲🇾' },
      { code: 'tl', name: 'Filipino', flag: '🇵🇭' },
      { code: 'sw', name: 'Kiswahili', flag: '🇰🇪' },
      { code: 'ro', name: 'Română', flag: '🇷🇴' },
      { code: 'cs', name: 'Čeština', flag: '🇨🇿' },
      { code: 'sk', name: 'Slovenčina', flag: '🇸🇰' },
      { code: 'hu', name: 'Magyar', flag: '🇭🇺' },
      { code: 'bg', name: 'Български', flag: '🇧🇬' },
      { code: 'hr', name: 'Hrvatski', flag: '🇭🇷' },
      { code: 'sr', name: 'Српски', flag: '🇷🇸' },
      { code: 'sl', name: 'Slovenščina', flag: '🇸🇮' },
      { code: 'lv', name: 'Latviešu', flag: '🇱🇻' },
      { code: 'lt', name: 'Lietuvių', flag: '🇱🇹' },
      { code: 'et', name: 'Eesti', flag: '🇪🇪' },
      { code: 'fi', name: 'Suomi', flag: '🇫🇮' },
      { code: 'da', name: 'Dansk', flag: '🇩🇰' },
      { code: 'no', name: 'Norsk', flag: '🇳🇴' },
      { code: 'sv', name: 'Svenska', flag: '🇸🇪' },
      { code: 'is', name: 'Íslenska', flag: '🇮🇸' },
      { code: 'el', name: 'Ελληνικά', flag: '🇬🇷' },
      { code: 'mk', name: 'Македонски', flag: '🇲🇰' },
      { code: 'sq', name: 'Shqip', flag: '🇦🇱' },
      { code: 'ca', name: 'Català', flag: '🏴󠁥󠁳󠁣󠁴󠁿' },
      { code: 'eu', name: 'Euskera', flag: '🏴󠁥󠁳󠁰󠁶󠁿' },
      { code: 'gl', name: 'Galego', flag: '🏴󠁥󠁳󠁧󠁡󠁿' },
      { code: 'cy', name: 'Cymraeg', flag: '🏴󠁧󠁢󠁷󠁬󠁳󠁿' },
      { code: 'ga', name: 'Gaeilge', flag: '🇮🇪' },
      { code: 'mt', name: 'Malti', flag: '🇲🇹' },
      { code: 'lb', name: 'Lëtzebuergesch', flag: '🇱🇺' }
    ];
  }

  initLanguageDropdowns() {
    const languages = this.getLanguages();

    // Initialize source language dropdown (with auto-detect)
    this.initDropdown('source-lang-dropdown', 'source_lang', languages, 'auto');
    this.initDropdown('source-lang-dropdown-top', 'source_lang', languages, 'auto');
    
    // Initialize target language dropdown (without auto-detect)
    const targetLanguages = languages.filter(lang => !lang.sourceOnly);
    this.initDropdown('target-lang-dropdown', 'target_lang', targetLanguages, 'de');
    this.initDropdown('target-lang-dropdown-top', 'target_lang', targetLanguages, 'de');
  }

  initOutputOptionsDropdown() {
    const dropdown = this.elements.outputOptionsDropdown;
    if (!dropdown) return;

    const trigger = dropdown.querySelector('.options-trigger');
    if (!trigger) return;

    // Initialize options dropdown without the conflicting document listener
    this.initOptionsDropdownSpecial(dropdown, trigger);

    // Handle tone changes
    if (this.elements.toneOutput) {      
      this.elements.toneOutput.addEventListener('change', () => {
        // Sync with main tone selector
        if (this.elements.tone) {
          this.elements.tone.value = this.elements.toneOutput.value;
        }
        this.scheduleTranslation();
      });
    }

    // Handle model changes  
    if (this.elements.modelSelectOutput) {
      this.elements.modelSelectOutput.addEventListener('change', (e) => {
        this.changeModel(e.target.value);
      });
    }

    // Load models immediately when initializing dropdown (not on click)
    this.loadAvailableModels();
  }

  initOptionsDropdownSpecial(dropdown, trigger) {
    const panel = dropdown.querySelector('.language-dropdown-panel');
    if (!panel) return;

    // Toggle dropdown open/close
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      
      // Close other dropdowns
      document.querySelectorAll('.language-dropdown.open').forEach(d => {
        if (d !== dropdown) d.classList.remove('open');
      });
      
      // Toggle current dropdown
      dropdown.classList.toggle('open');
    });
    
    // Prevent menu from closing when trigger loses focus
    trigger.addEventListener('blur', (e) => {
      // If blur is caused by clicking inside our panel, don't close
      setTimeout(() => {
        const activeElement = document.activeElement;
        if (activeElement && dropdown.contains(activeElement)) {
          // Focus moved inside our dropdown, keep it open
          return;
        }
        // Otherwise, let the normal outside click handler deal with it
      }, 10);
    });

    // Handle all events inside the panel to prevent menu closing
    // Use capturing phase to catch events before other handlers
    ['click', 'mousedown', 'mouseup', 'focus', 'blur'].forEach(eventType => {
      panel.addEventListener(eventType, (e) => {
        // Stop propagation immediately to prevent other handlers
        e.stopPropagation();
        
        // For select elements, allow normal functionality
        if (e.target.tagName === 'SELECT' && eventType === 'click') {
          // Don't prevent default for select clicks - they need to open
          return;
        }
      }, true); // Capturing phase
    });
    
    // Also add protective handlers to the dropdown element itself
    ['focus', 'blur'].forEach(eventType => {
      dropdown.addEventListener(eventType, (e) => {
        e.stopPropagation();
      }, true);
    });

    // Custom document click handler that respects the options menu
    const outsideClickHandler = (e) => {
      // Check if click is outside the entire options menu structure
      if (!dropdown.contains(e.target) && 
          !e.target.closest('.options-menu') && 
          !e.target.closest('#output-options-dropdown')) {
        dropdown.classList.remove('open');
      }
    };

    // Add the listener with high priority (capturing phase)
    document.addEventListener('click', outsideClickHandler, true);
    
    // Store reference to remove later if needed
    dropdown._outsideClickHandler = outsideClickHandler;
  }

  initOptionsDropdownBasic(dropdown, trigger) {
    const panel = dropdown.querySelector('.language-dropdown-panel');
    if (!panel) return;

    // Toggle dropdown open/close
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      
      // Close other dropdowns
      document.querySelectorAll('.language-dropdown.open').forEach(d => {
        if (d !== dropdown) d.classList.remove('open');
      });
      
      // Toggle current dropdown
      dropdown.classList.toggle('open');
    });

    // Close on outside click - but not when clicking on select elements inside
    document.addEventListener('click', (e) => {
      // Don't interfere with options menu
      if (e.target.closest('.options-menu') || e.target.closest('#output-options-dropdown')) {
        return;
      }
      
      // Don't close if clicking inside the dropdown panel or on select elements
      if (!dropdown.contains(e.target) && 
          !e.target.closest('.language-dropdown-panel') &&
          !e.target.closest('select')) {
        dropdown.classList.remove('open');
      }
    });
  }

  initDropdown(dropdownId, selectId, languages, defaultValue) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;

    const trigger = dropdown.querySelector('.language-dropdown-trigger');
    const panel = dropdown.querySelector('.language-dropdown-panel');
    const content = dropdown.querySelector('.language-dropdown-content');
    const searchInput = dropdown.querySelector('.language-dropdown-search input');
    const hiddenSelect = document.getElementById(selectId);
    const selectedSpan = trigger.querySelector('.selected-language');

    if (!trigger || !panel || !content || !hiddenSelect || !selectedSpan) return;

    // Populate dropdown
    const populateDropdown = (langs = languages) => {
      content.innerHTML = '';
      
      langs.forEach(lang => {
        const item = document.createElement('div');
        item.className = `language-dropdown-item${hiddenSelect.value === lang.code ? ' selected' : ''}`;
        item.setAttribute('data-code', lang.code);
        item.innerHTML = `
          <span class="flag">${lang.flag}</span>
          <span class="name">${lang.name}</span>
        `;
        
        item.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          // Update values
          hiddenSelect.value = lang.code;
          selectedSpan.textContent = lang.name;
          
          // Synchronize with other dropdowns for the same select
          this.synchronizeDropdowns(selectId, lang.code, lang.name);
          
          // Update selected state
          content.querySelectorAll('.language-dropdown-item').forEach(i => {
            i.classList.remove('selected');
          });
          item.classList.add('selected');
          
          // Close dropdown
          dropdown.classList.remove('open');
          if (searchInput) {
            searchInput.value = '';
          }
          populateDropdown();
          
          // Trigger change event
          hiddenSelect.dispatchEvent(new Event('change'));
        });
        
        content.appendChild(item);
      });
    };

    // Open/close dropdown
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      
      // Close other dropdowns
      document.querySelectorAll('.language-dropdown.open').forEach(d => {
        if (d !== dropdown) d.classList.remove('open');
      });
      
      // Toggle current dropdown
      dropdown.classList.toggle('open');
      
      if (dropdown.classList.contains('open')) {
        populateDropdown();
        setTimeout(() => {
          if (searchInput) searchInput.focus();
        }, 100);
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

    // Close on outside click
    document.addEventListener('click', (e) => {
      // Don't interfere with options menu
      if (e.target.closest('.options-menu') || e.target.closest('#output-options-dropdown')) {
        return;
      }
      
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
        if (searchInput) {
          searchInput.value = '';
        }
      }
    });

    // Populate hidden select with all available languages
    hiddenSelect.innerHTML = '';
    languages.forEach(lang => {
      const option = document.createElement('option');
      option.value = lang.code;
      option.textContent = lang.name;
      if (lang.code === defaultValue) {
        option.selected = true;
      }
      hiddenSelect.appendChild(option);
    });

    // Set initial value
    populateDropdown();
    const defaultLang = languages.find(lang => lang.code === defaultValue);
    if (defaultLang) {
      hiddenSelect.value = defaultValue;
      selectedSpan.textContent = defaultLang.name;
    }
  }

  // History functionality
  loadHistory() {
    try {
      return JSON.parse(localStorage.getItem('llot-history') || '[]').slice(0, 10);
    } catch {
      return [];
    }
  }

  saveHistory() {
    localStorage.setItem('llot-history', JSON.stringify(this.history));
  }

  scheduleHistoryAdd(sourceText, translatedText, sourceLang, targetLang) {
    // Clear existing timeout
    if (this.historyTimeout) {
      clearTimeout(this.historyTimeout);
    }
    
    // Schedule history add after 4 seconds of no new translations
    this.historyTimeout = setTimeout(() => {
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
    this.history = this.history.filter(h => h.sourceText !== entry.sourceText);
    
    // Add to beginning and limit to 10
    this.history.unshift(entry);
    this.history = this.history.slice(0, 10);
    
    this.saveHistory();
    this.renderHistory();
  }

  renderHistory() {
    if (!this.elements.historyList || this.history.length === 0) return;

    if (this.elements.historyPanel) {
      this.elements.historyPanel.style.display = 'block';
    }

    this.elements.historyList.innerHTML = this.history.map(item => `
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
        const historyItem = this.history.find(h => h.id === id);
        if (historyItem && this.elements.sourceText) {
          this.elements.sourceText.value = historyItem.sourceText;
          this.elements.sourceLang.value = historyItem.sourceLang;
          this.elements.targetLang.value = historyItem.targetLang;
          
          // Update dropdown displays for both desktop and mobile
          this.updateDropdownDisplay('source-lang-dropdown', historyItem.sourceLang);
          this.updateDropdownDisplay('target-lang-dropdown', historyItem.targetLang);
          this.updateDropdownDisplay('source-lang-dropdown-top', historyItem.sourceLang);
          this.updateDropdownDisplay('target-lang-dropdown-top', historyItem.targetLang);
          
          this.updateCharCount();
          this.updateFontSize();
          this.scheduleTranslation();
        }
      });
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  initHistory() {
    if (this.history.length > 0) {
      this.renderHistory();
    }
  }
  initializeTTS() {
    // Use event delegation to handle dynamically created TTS buttons
    this.streamingPlayer = new StreamingTTSPlayer();
    
    // Add event listener to result container using delegation
    if (this.elements.result) {
      this.elements.result.addEventListener('click', async (e) => {
        const ttsBtn = e.target.closest('#tts-btn');
        if (!ttsBtn) return;
      const resultText = this.getPlainTextFromResult().trim();
      if (!resultText) {
        return;
      }
      
        // Stop current audio if playing
        if (this.streamingPlayer.isPlaying) {
          this.streamingPlayer.stop();
          ttsBtn.classList.remove('playing');
          return;
        }
        
        try {
          ttsBtn.classList.add('loading');
          ttsBtn.classList.remove('disabled');
          
          // Get target language for TTS
          const targetLang = this.elements.targetLang?.value || 'de';
          
          // Map language codes to supported TTS languages
          const langMap = {
            'en': 'en', 'de': 'de', 'fr': 'fr', 'es': 'es', 'pt': 'pt',
            'nl': 'nl', 'da': 'da', 'fi': 'fi', 'no': 'no', 'pl': 'pl',
            'cs': 'cs', 'sk': 'sk', 'hu': 'hu', 'ro': 'ro', 'ru': 'ru',
            'ar': 'ar', 'hi': 'hi', 'tr': 'tr', 'vi': 'vi', 'zh': 'zh',
            'id': 'id'
          };
          
          const ttsLang = langMap[targetLang] || 'en';
          
          const audioElement = await this.streamingPlayer.playStreaming(resultText, ttsLang);
          
          ttsBtn.classList.remove('loading');
          ttsBtn.classList.add('playing');
          this.streamingPlayer.isPlaying = true;
          
          if (audioElement) {
            audioElement.addEventListener('ended', () => {
              ttsBtn.classList.remove('playing');
              this.streamingPlayer.isPlaying = false;
            });
            
            audioElement.addEventListener('error', (error) => {
              console.error('TTS: Audio error:', error);
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

  updateTTSButton() {
    const ttsBtn = document.getElementById('tts-btn');
    if (!ttsBtn) return;
    
    const resultText = this.getPlainTextFromResult().trim();
    const targetLang = this.elements.targetLang?.value || 'de';
    
    // Supported TTS languages
    const supportedTtsLanguages = {
      'en': true, 'de': true, 'fr': true, 'es': true, 'pt': true, 'nl': true,
      'da': true, 'fi': true, 'no': true, 'pl': true, 'cs': true, 'sk': true,
      'hu': true, 'ro': true, 'ru': true, 'ar': true, 'hi': true, 'tr': true,
      'vi': true, 'zh': true, 'id': true
    };
    
    const languageSupported = supportedTtsLanguages[targetLang];
    
    if (resultText && languageSupported && window.ttsEnabled) {
      ttsBtn.style.display = 'flex';
      ttsBtn.classList.remove('disabled');
    } else {
      ttsBtn.style.display = 'none';
    }
  }

  async copyToClipboard() {
    const copyBtn = document.getElementById('copy-btn');
    if (!copyBtn) return;

    const resultText = this.getPlainTextFromResult().trim();
    if (!resultText) return;

    try {
      await navigator.clipboard.writeText(resultText);
      
      // Visual feedback
      copyBtn.classList.add('copied');
      const originalSVG = copyBtn.innerHTML;
      
      // Show checkmark
      copyBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      `;
      
      setTimeout(() => {
        copyBtn.classList.remove('copied');
        copyBtn.innerHTML = originalSVG;
      }, 2000);
      
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      
      // Fallback for older browsers
      try {
        const textArea = document.createElement('textarea');
        textArea.value = resultText;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Visual feedback for fallback
        copyBtn.classList.add('copied');
        setTimeout(() => {
          copyBtn.classList.remove('copied');
        }, 2000);
        
      } catch (fallbackError) {
        console.error('Fallback copy failed:', fallbackError);
      }
    }
  }

  updateCopyButton() {
    const copyBtn = document.getElementById('copy-btn');
    if (!copyBtn) return;
    
    const resultText = this.getPlainTextFromResult().trim();
    
    if (resultText) {
      copyBtn.style.display = 'flex';
    } else {
      copyBtn.style.display = 'none';
    }
  }


  async loadAvailableModels() {
    // Get model select from output options dropdown
    const modelSelect = this.elements.modelSelectOutput;
    if (!modelSelect) return;
    
    try {
      // Get models from Ollama via our backend
      const response = await fetch('/api/health');
      const data = await response.json();
      
      if (data.ollama && data.ollama.models && Array.isArray(data.ollama.models)) {
        // Clear existing options except the current one
        const currentModel = modelSelect.value;
        modelSelect.innerHTML = '';
        
        // Add all available models from Ollama
        data.ollama.models.forEach(model => {
          const option = document.createElement('option');
          option.value = model;
          option.textContent = model;
          option.selected = model === currentModel;
          modelSelect.appendChild(option);
        });
      } else {
        console.warn('No models found in health response');
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      // Fallback - try alternative API endpoint
      try {
        const response = await fetch('/api/models');
        const data = await response.json();
        if (data.models && Array.isArray(data.models)) {
          const currentModel = modelSelect.value;
          modelSelect.innerHTML = '';
          
          data.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            option.selected = model === currentModel;
            modelSelect.appendChild(option);
          });
        }
      } catch (fallbackError) {
        console.error('Fallback model loading failed:', fallbackError);
      }
    }
  }

  async changeModel(newModel) {
    try {
      const response = await fetch('/api/change_model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model: newModel })
      });
      
      if (response.ok) {
        console.log('Model changed to:', newModel);
        // Optionally show a success message
      } else {
        console.error('Failed to change model');
      }
    } catch (error) {
      console.error('Error changing model:', error);
    }
  }
}

// Progressive Streaming TTS Implementation
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

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.llotApp = new LLOTApp();
});
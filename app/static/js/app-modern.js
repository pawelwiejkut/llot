/**
 * LLOT Modern JavaScript 2025
 * Enhanced UX with smooth animations and modern interactions
 */

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
    
    // Initialize with any existing translation
    if (window.initialTranslated) {
      this.showTTSButton();
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
      copyButton: document.getElementById('copy-btn'),
      ttsButton: document.getElementById('tts-btn'),
      historyPanel: document.getElementById('history-panel'),
      historyList: document.getElementById('history-list')
    };
  }
  
  bindEvents() {
    // Theme toggle
    this.elements.themeToggle?.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      this.setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });
    
    // Auto-translation
    this.elements.sourceText?.addEventListener('input', () => {
      this.updateCharCount();
      this.scheduleTranslation();
    });
    
    // Language and tone changes
    [this.elements.sourceLang, this.elements.targetLang, this.elements.tone].forEach(element => {
      element?.addEventListener('change', () => this.scheduleTranslation());
    });
    
    // Language swap
    this.elements.swapButton?.addEventListener('click', () => {
      this.swapLanguages();
    });
    
    // Copy functionality
    this.elements.copyButton?.addEventListener('click', () => {
      this.copyTranslation();
    });
    
    // TTS functionality
    this.elements.ttsButton?.addEventListener('click', () => {
      this.playTTS();
    });
    
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
              this.copyTranslation();
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
    const count = this.elements.sourceText?.value.length || 0;
    if (this.elements.charCount) {
      this.elements.charCount.textContent = `${count.toLocaleString()} characters`;
    }
  }
  
  scheduleTranslation() {
    if (this.translationTimeout) {
      clearTimeout(this.translationTimeout);
    }
    
    const text = this.elements.sourceText?.value.trim();
    if (!text) {
      this.clearResult();
      return;
    }
    
    this.translationTimeout = setTimeout(() => {
      this.translate();
    }, 300); // Debounce translation requests
  }
  
  async translate() {
    const text = this.elements.sourceText?.value.trim();
    if (!text) return;
    
    this.showLoading();
    
    try {
      const formData = new FormData();
      formData.append('source_text', text);
      formData.append('source_lang', this.elements.sourceLang?.value || 'auto');
      formData.append('target_lang', this.elements.targetLang?.value || 'en');
      formData.append('tone', this.elements.tone?.value || 'neutral');
      
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
    this.showTTSButton();
    
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
    if (this.elements.ttsButton) this.elements.ttsButton.style.display = 'none';
    this.hideLoading();
  }
  
  swapLanguages() {
    if (this.elements.sourceLang?.value === 'auto') {
      // Can't swap with auto-detect
      return;
    }
    
    const sourceLang = this.elements.sourceLang?.value;
    const targetLang = this.elements.targetLang?.value;
    const sourceText = this.elements.sourceText?.value;
    const resultText = this.elements.result?.textContent;
    
    if (sourceLang && targetLang) {
      this.elements.sourceLang.value = targetLang;
      this.elements.targetLang.value = sourceLang;
      
      if (sourceText && resultText) {
        this.elements.sourceText.value = resultText;
        this.scheduleTranslation();
      }
    }
    
    // Add animation feedback
    this.elements.swapButton?.style.setProperty('transform', 'rotate(180deg)');
    setTimeout(() => {
      this.elements.swapButton?.style.setProperty('transform', 'rotate(0deg)');
    }, 200);
  }
  
  async copyTranslation() {
    const text = this.elements.result?.textContent;
    if (!text) return;
    
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback dla starszych przeglądarek
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      
      // Visual feedback
      const originalIcon = this.elements.copyButton?.innerHTML;
      if (this.elements.copyButton) {
        this.elements.copyButton.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
        `;
        
        setTimeout(() => {
          this.elements.copyButton.innerHTML = originalIcon;
        }, 1000);
      }
      
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  }
  
  showTTSButton() {
    if (window.ttsEnabled && this.elements.ttsButton && this.elements.result?.textContent) {
      this.elements.ttsButton.style.display = 'flex';
    }
  }
  
  async playTTS() {
    const text = this.elements.result?.textContent;
    const language = this.elements.targetLang?.value;
    
    if (!text || !language) return;
    
    // Stop current audio if playing
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
    
    try {
      // Show loading state
      const originalIcon = this.elements.ttsButton?.innerHTML;
      if (this.elements.ttsButton) {
        this.elements.ttsButton.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
          </svg>
        `;
        this.elements.ttsButton.style.animation = 'spin 1s linear infinite';
      }
      
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          language: language,
          streaming: false
        })
      });
      
      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        this.currentAudio = new Audio(audioUrl);
        
        this.currentAudio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          this.currentAudio = null;
        };
        
        await this.currentAudio.play();
      }
      
      // Restore button
      if (this.elements.ttsButton) {
        this.elements.ttsButton.innerHTML = originalIcon;
        this.elements.ttsButton.style.animation = '';
      }
      
    } catch (error) {
      console.error('TTS error:', error);
      
      // Restore button on error
      if (this.elements.ttsButton) {
        this.elements.ttsButton.innerHTML = originalIcon;
        this.elements.ttsButton.style.animation = '';
      }
    }
  }
  
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
        this.showTTSButton();
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
    this.elements.sourceText?.focus();
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.llotApp = new LLOTApp();
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
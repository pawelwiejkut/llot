#!/usr/bin/env python3
# translator_app.py
"""
llot — local llm ollama translator
Jednoplikiowa aplikacja Flask (UI po polsku) — lokalny frontend tłumaczeń na Ollama.

Zmiany (2025-08-13):
- POWIĘKSZENIE UI (tylko frontend/CSS):
  * Pole „Tekst do tłumaczenia” i „Wynik” mają 26 px.
  * Większe etykiety (Źródło/Docelowy/Ton/Historia…), status, badge, chipy historii.
  * Większe selecty i przycisk zamiany; poprawione odstępy, wysokości i strzałka selecta.
  * Zachowana responsywność i zachowanie aplikacji. Brak zmian w backendzie.
"""

import os
import json
import re
from flask import Flask, request, render_template_string, jsonify,Response,make_response
import requests
from langdetect import detect
import base64


# Konfiguracja
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://10.0.20.123:11434")
DEFAULT_MODEL = os.environ.get("OL_MODEL", "gemma3:27b")
LISTEN_HOST = os.environ.get("APP_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("APP_PORT", "8080"))

# Pamięć historii (ostatnie N pozycji)
HISTORY_LIMIT = 5
history = []

app = Flask(__name__)

# --- Favicons (Safari-friendly) ---
def _nocache(resp: Response) -> Response:
    resp.headers["Cache-Control"] = "no-store, max-age=0, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# Nowoczesny favicon - symbol tłumaczenia z gradientem
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="16" ry="16" fill="url(#bg)"/>
  <!-- Strzałki tłumaczenia -->
  <path d="M16 24 L28 24 M25 21 L28 24 L25 27" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 40 L36 40 M39 37 L36 40 L39 43" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Nowoczesny tekst "lt" -->
  <text x="32" y="35" font-family="SF Pro Display, -apple-system, system-ui, sans-serif" font-size="18" font-weight="600" text-anchor="middle" fill="#ffffff">lt</text>
  <!-- Dekoracyjne kropki -->
  <circle cx="20" cy="48" r="2" fill="url(#accent)" opacity="0.8"/>
  <circle cx="44" cy="16" r="2" fill="url(#accent)" opacity="0.8"/>
</svg>"""

# Safari pinned tab - uproszczona monochromatyczna wersja
SAFARI_PINNED_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <path d="M0 0h64v64H0z" fill="black"/>
  <!-- Strzałki tłumaczenia (uproszczone) -->
  <path d="M16 24 L28 24 M25 21 L28 24 L25 27" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 40 L36 40 M39 37 L36 40 L39 43" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Tekst "lt" -->
  <circle cx="26" cy="35" r="3" fill="white"/>
  <circle cx="38" cy="35" r="3" fill="white"/>
  <rect x="24" y="32" width="4" height="12" fill="white"/>
  <rect x="36" y="44" width="8" height="4" fill="white"/>
</svg>"""

# Proste PNG/ICO (wystarczą do Safari). Mogą być niskiej rozdzielczości – ważne, że są poprawne.
FAVICON_PNG_32_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAyUlEQVR4nGNkQAOqya//o4tRE9yeK8qIzGeip+XY7GDCJUEvRzDR23J0RzAOhOXIgImwklEHDHMHsKALmKuzMiwu5Yfzs6Z+Ythz/hdWzcf6hBhE+Ij3w6PXfxlcKt+jiA2+ECAFWBW9Q+G7GLIxTMvmg/MT+j4yHLv2G68ZAx4Cow4YdcCoA0YdQLAkRC7ZkMGKgz8Y6hZ/odgBAx4Co02yUQcMvAPQ+2r0BLfnijIywRgDYTkDA1IU0NMRyHYx4ZKgh+UMDAwMAHYHPWPQsMhRAAAAAElFTkSuQmCC"
FAVICON_PNG_16_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAnElEQVR4nGNkgALV5Nf/GUgAt+eKMjIwMDAwkaMZWQ8jOZqRARMlmhkYGBhYGBgYGNSkmRm2NAoyTN/6jaF//Te45MWpwgyc7IwYmqyL3zG8/vgPYQAuoJ/9loGBgYFhdZUAg7wYM4NZwVsMNRR7YbgZkOnNxXBrjgjDrTkiDFk+XEQZMPAJiXIDYLmKHHB7rigjE4xBjmYGBgYGABaIKTu/xoclAAAAAElFTkSuQmCC"
FAVICON_ICO_BASE64 = "AAABAAIAEBAAAAAAIABgAgAAJgAAACAgAAAAACAA8wAAAIYCAACJUE5HDQoaCgAAAA1JSERSAAAAEAAAABAIBgAAAB/z/2EAAAInSURBVHichZI9a1RBFIafMzM7637c3XwQAy6xigh2AYtY2UQhFklrrQg2+QUW/gf1N6SxS2GzKwREsBK7NFaCAROU7Hf23jtzLG52zQbRFwYGzpxn3vNy5P5Ldcfff70zrrIVs2EELP9WMKWaifm4c6O19EjWn5y0rU+2QtqLIsb8pxkA1Ritb5iQ9jty+/lIQ9pXZ62IKCGCavHQCPwdKeR5UOMTcSEbBmOM7Y0ik0xp1gzWFM2Dc2UwVkTAmgIcYnFfahiJ2TA4I9hJpuxslrlz07F/OOa0q4xTZWvD83CjTJor/bHinZBUhO4o8uZgTJqrNSKQZrC7WWZvp8rqgiHPFQEEyIKyumjY26mye6/MJC8cTeUARKA3UvIAeYCoUL8mvP+Ssn94zt1bjgcbZdqfJzx71WOxJizUDCIXACjmcpYZfQpxy4aVpsFZSCpCa9mQVIQ0uwj6ar5TkLOgFI5C/AOdupwbASDGonDajRz/jFTLQrMmiBTpXwZd1gxQrwrOwovHdU7OIt4Jbz+c8/Eoxbui1qjKbEdmAFXwJTj4NOHrcaBeEbwTlGKEkhV+nEVeH4w4+pbjHXMQWX96mhvBDsbKJJvfxGZNqHghC9AdRsoloV6ZcxGcLdVsSPvaqBarfFkhFsE5C9cXzGwTAdCoxifWhHTQsb4heQhxmvD0TH+6GqJqjMY3JKSDjmmtrWzHfNS2PhEg8H8F6xOJ+ajdWlvZ/g0k+g0JEl7M2gAAAABJRU5ErkJggg=="
APPLE_TOUCH_PNG_BASE64 = FAVICON_PNG_32_BASE64  # wystarczy jako fallback; iOS i tak wyświetli

# Różne rozmiary Apple Touch Icon dla lepszej kompatybilności z Safari/iOS
APPLE_TOUCH_PNG_57_BASE64 = FAVICON_PNG_32_BASE64  # Fallback dla starszych iOS
APPLE_TOUCH_PNG_120_BASE64 = FAVICON_PNG_32_BASE64  # iPhone Retina
APPLE_TOUCH_PNG_152_BASE64 = FAVICON_PNG_32_BASE64  # iPad Retina 
APPLE_TOUCH_PNG_180_BASE64 = FAVICON_PNG_32_BASE64  # iPhone 6/7/8 Plus

def _png_response(b64: str) -> Response:
    data = base64.b64decode(b64)
    resp = make_response(data)
    resp.mimetype = "image/png"
    return _nocache(resp)

@app.route("/favicon.ico")
def _favicon_ico():
    resp = make_response(base64.b64decode(FAVICON_ICO_BASE64))
    resp.mimetype = "image/x-icon"
    return _nocache(resp)

@app.route("/favicon-32.png")
def _favicon_png_32():
    return _png_response(FAVICON_PNG_32_BASE64)

@app.route("/favicon-16.png")
def _favicon_png_16():
    return _png_response(FAVICON_PNG_16_BASE64)

@app.route("/apple-touch-icon.png")
def _apple_touch_icon():
    return _png_response(APPLE_TOUCH_PNG_BASE64)

@app.route("/apple-touch-icon-57x57.png")
def _apple_touch_icon_57():
    return _png_response(APPLE_TOUCH_PNG_57_BASE64)

@app.route("/apple-touch-icon-120x120.png")
def _apple_touch_icon_120():
    return _png_response(APPLE_TOUCH_PNG_120_BASE64)

@app.route("/apple-touch-icon-152x152.png")
def _apple_touch_icon_152():
    return _png_response(APPLE_TOUCH_PNG_152_BASE64)

@app.route("/apple-touch-icon-180x180.png")
def _apple_touch_icon_180():
    return _png_response(APPLE_TOUCH_PNG_180_BASE64)

@app.route("/favicon.svg")
def _favicon_svg():
    resp = make_response(FAVICON_SVG)
    resp.mimetype = "image/svg+xml"
    return _nocache(resp)

@app.route("/safari-pinned-tab.svg")
def _safari_pinned():
    resp = make_response(SAFARI_PINNED_SVG)
    resp.mimetype = "image/svg+xml"
    resp.headers['Content-Type'] = 'image/svg+xml'
    return _nocache(resp)

# Web App Manifest dla lepszej integracji z iOS
@app.route("/manifest.json")
def _manifest():
    manifest = {
        "name": "llot - local llm ollama translator",
        "short_name": "llot",
        "description": "Lokalny translator używający Ollama",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f7f8fb",
        "theme_color": "#2563eb",
        "icons": [
            {
                "src": "/apple-touch-icon-57x57.png",
                "sizes": "57x57",
                "type": "image/png"
            },
            {
                "src": "/apple-touch-icon-120x120.png",
                "sizes": "120x120",
                "type": "image/png"
            },
            {
                "src": "/apple-touch-icon-152x152.png",
                "sizes": "152x152",
                "type": "image/png"
            },
            {
                "src": "/apple-touch-icon-180x180.png",
                "sizes": "180x180",
                "type": "image/png"
            }
        ]
    }
    resp = make_response(json.dumps(manifest, indent=2))
    resp.mimetype = "application/json"
    return _nocache(resp)



# Dostępne języki (ograniczone)
LANGUAGES = [
    ("auto", "Auto (wykryj)"),
    ("pl", "Polski"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("cs", "Čeština"),
]

# TONY
TONES = [
    ("neutral", "Neutralny"),
    ("formal", "Formalny"),
    ("informal", "Nieformalny"),
    ("friendly", "Przyjazny"),
    ("technical", "Techniczny"),
    ("poetic", "Poetycki"),
]

# Szablon HTML (PL)
TEMPLATE = r"""
<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />

<title>llot — local llm ollama translator</title>
<!-- Favicons zgodne z Safari/Firefox/Chrome + bust cache -->
<link rel="shortcut icon" href="/favicon.ico?v=5" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png?v=5" />
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png?v=5" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=5" />
<!-- Apple Touch Icons dla różnych urządzeń iOS/Safari -->
<link rel="apple-touch-icon" sizes="57x57" href="/apple-touch-icon-57x57.png?v=5" />
<link rel="apple-touch-icon" sizes="120x120" href="/apple-touch-icon-120x120.png?v=5" />
<link rel="apple-touch-icon" sizes="152x152" href="/apple-touch-icon-152x152.png?v=5" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180x180.png?v=5" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=5" />
<!-- Safari-specific i Web App Manifest -->
<link rel="mask-icon" href="/safari-pinned-tab.svg?v=5" color="#2563eb" />
<link rel="manifest" href="/manifest.json?v=5" />
<meta name="theme-color" content="#2563eb" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
<meta name="apple-mobile-web-app-title" content="llot" />
<meta name="format-detection" content="telephone=no" />

<style>
  :root{
    --ring: rgba(59,130,246,.25);
    --border:#e5e7eb; --shadow:0 8px 22px rgba(0,0,0,0.08); --bg:#f7f8fb;

    /* Skala fontów */
    --fs-base: 18px;
    --fs-label: 20px;
    --fs-control: 20px;
    --fs-small: 18px;
    --fs-input: 26px;
    --fs-result: 26px;

    /* Odstępy */
    --pad-card-x: 28px;
    --pad-card-y: 28px;
    --gap-row: 20px;
  }

  * { box-sizing: border-box; }
  html, body { height:100%; }
  body {
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    background:var(--bg); color:#111; margin:0; padding:16px; font-size:var(--fs-base);
  }

  /* ✅ Brak 96vw — koniec z poziomowym scrollem na telefonach */
  .container { max-width: 1680px; width: 100%; margin: 0 auto; }

  header { display:flex; align-items:center; gap:12px; margin-bottom:18px; }
  .card { background:white; border-radius:12px; padding:14px; box-shadow:0 6px 18px rgba(15,15,15,0.06); }

  /* ✅ Większe marginesy wewnątrz białej karty (tylko w „workspace”) */
  .workspace.card { padding: var(--pad-card-y) var(--pad-card-x); }
  .workspace { min-height: calc(100dvh - 120px); display:flex; flex-direction:column; }

  .row { display:flex; gap: var(--gap-row); }
  /* Nadpisuje inline style="margin-top:12px" z HTML, żeby było bardziej przestrzennie */
  .workspace .row { margin-top: 18px !important; }

  .col { flex:1; display:flex; flex-direction:column; position:relative; min-height:0; }

  /* Etykiety + spójne odstępy */
  label.small { display:inline-block; margin-bottom:14px; color:#475569; font-size:var(--fs-label); }
  .topbar { display:flex; justify-content:space-between; align-items:end; gap:14px; margin-bottom:18px; flex-wrap:wrap; }
  .topbar .left-group { display:flex; gap:14px; flex-wrap:wrap; align-items:flex-end; width:100%; }

  /* Historia pod dropdownami */
  .history-block { margin-top:16px; }
  .history { margin-top:12px; display:flex; gap:10px; flex-wrap:wrap; }

  /* Pola tekstowe */
  textarea {
    width:100%; min-height:280px; padding:14px 14px;
    border-radius:10px; border:1px solid #e6e9ef;
    font-size:var(--fs-input); line-height:1.6;
    overflow:hidden; resize:none; background:#fff;
  }
  textarea::placeholder { color:#9aa5b1; }
  textarea:focus { outline: none; border-color:#93c5fd; box-shadow: 0 0 0 3px var(--ring); position:relative; z-index:1; }

  /* Płaskie selecty + ikona */
  .select-wrap { position:relative; display:inline-block; }
  .select-wrap select,
  .btn-icon {
    appearance:none; -webkit-appearance:none; -moz-appearance:none;
    padding:10px 42px 10px 14px; border-radius:10px; border:1px solid var(--border);
    background:#f9fafb; box-shadow:none; font-size:var(--fs-control); cursor:pointer; color:#111;
    height:48px;
  }
  .btn-icon { padding:10px 14px; display:inline-flex; align-items:center; justify-content:center; gap:10px; }
  .select-wrap select:hover, .btn-icon:hover { border-color:#d1d5db; background:#f3f4f6; }
  .select-wrap:after{
    content:""; position:absolute; right:14px; top:50%; width:0; height:0;
    border-left:7px solid transparent; border-right:7px solid transparent; border-top:7px solid #64748b;
    transform: translateY(-35%); pointer-events:none;
  }
  .select-wrap select:focus, .btn-icon:focus { outline:none; border-color:#93c5fd; box-shadow: 0 0 0 3px var(--ring); background:#fff; }

  .controls { display:flex; gap:12px; margin-top:12px; align-items:center; flex-wrap:wrap; }
  .small { font-size:var(--fs-small); color:#5b6b7a; }

  /* Wynik — min-height synchronizowany do textarea; rośnie z treścią */
  .result-box {
    white-space:pre-wrap; overflow:auto; padding:14px;
    border-radius:10px; border:1px dashed #e3e7ee; background:#fbfcff;
    line-height:1.6; font-size:var(--fs-result);
  }

  /* Historia chipy */
  .chip { background:#eef3ff; padding:8px 12px; border-radius:999px; font-size:18px; color:#1b4ed8; cursor:pointer; }
  .chip:hover{ background:#e3ebff; }

  /* Dropdown alternatyw */
  .alt-menu { position:absolute; background:#fff; border:1px solid var(--border); border-radius:10px; box-shadow:var(--shadow); padding:6px; z-index:9999; }
  .alt-item { padding:8px 12px; border-radius:8px; font-size:20px; white-space:nowrap; cursor:pointer; }
  .alt-item:hover { background:#f3f4f6; }
  .token { padding:2px 3px; border-radius:6px; cursor:pointer; }
  .token:hover { background:#eef2ff; }
  .badge { display:inline-block; font-size:18px; background:#f3f4f6; padding:6px 8px; border-radius:8px; margin-left:10px; }

  /* Status */
  .status { display:none; align-items:center; gap:10px; font-size:var(--fs-small); color:#475569; }
  .spinner { width:18px; height:18px; border:2px solid #cbd5e1; border-top-color:#64748b; border-radius:50%; animation:spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* 📱 Mobile */
  @media (max-width: 900px){
    .row { flex-direction: column; gap: 16px; }
    .topbar { align-items:stretch; }
    .topbar .left-group {
      display:grid;
      grid-template-columns: 1fr auto 1fr;
      align-items:end;
      gap:10px;
      width:100%;
    }
    .topbar .left-group > :last-child { grid-column: 1 / -1; }
    .select-wrap select { width:100%; }
    .btn-icon { height:48px; }
    /* Trochę mniejsze wewnętrzne marginesy, żeby treść się mieściła */
    .workspace.card { padding: 20px 16px; }
    textarea { min-height: 260px; }
  }

  /* 📱 Bardzo wąskie telefony — drobna korekta skali aby wszystko się mieściło */
  @media (max-width: 420px){
    :root{ --fs-input: 24px; --fs-result: 24px; --fs-control: 18px; --fs-label: 18px; --fs-small: 16px; }
    .workspace.card { padding: 18px 14px; }
    textarea { min-height: 240px; }
  }
</style>

</head>
<body>
<div class="container">
  <header>
    <div class="card" style="padding:10px 14px;">
      <strong>llot</strong><div class="small">— local llm ollama translator</div>
    </div>
    <div style="flex:1"></div>
    <div class="small">Ollama: <code>{{ ollama_host }}</code> • Model: <code>{{ model }}</code></div>
  </header>

  <div class="card workspace">
    <div class="topbar">
      <div class="left-group">
        <div>
          <label class="small">Źródło</label><br/>
          <div class="select-wrap">
            <select id="source_lang" name="source_lang">
              {% for code,name in languages %}
                <option value="{{code}}" {% if code=='auto' %}selected{% endif %}>{{name}}{% if code!='auto' %} ({{code}}){% endif %}</option>
              {% endfor %}
            </select>
          </div>
        </div>

        <div class="swap-col" style="display:flex; align-items:flex-end;">
          <button id="swap_top" type="button" class="btn-icon" title="Zamień kierunek" aria-label="Zamień kierunek">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M7 7h13M17 3l3 4-3 4M17 17H4M7 13l-3 4 3 4" stroke="#334155" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <div>
          <label class="small">Docelowy</label><br/>
          <div class="select-wrap">
            <select id="target_lang" name="target_lang">
              {% for code,name in languages %}
                {% if code!='auto' %}
                  <option value="{{code}}" {% if code=='de' %}selected{% endif %}>{{name}} ({{code}})</option>
                {% endif %}
              {% endfor %}
            </select>
          </div>
        </div>

        <div>
          <label class="small">Ton</label><br/>
          <div class="select-wrap">
            <select id="tone" name="tone">
              {% for val,label in tones %}
                <option value="{{val}}" {% if val=='neutral' %}selected{% endif %}>{{label}}</option>
              {% endfor %}
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Historia pod dropdowny -->
    <div class="history-block">
      <div class="small">Historia ostatnich tłumaczeń:</div>
      <div class="history" id="history">
        {% for item in history %}
          <div class="chip" onclick="loadHistory({{loop.index0}})">{{ item.short }}</div>
        {% endfor %}
        {% if history|length == 0 %}
          <span class="small" style="color:#94a3b8">brak</span>
        {% endif %}
      </div>
    </div>

    <div class="row" style="margin-top:12px;">
      <div class="col">
        <label class="small">Tekst do tłumaczenia</label>
        <textarea name="source_text" id="source_text" placeholder="Wklej lub wpisz tekst...">{{ last_input|default('') }}</textarea>
        <div class="controls">
          <div class="small">Tłumaczenie uruchamia się automatycznie<span id="detected_badge" class="badge" style="display:none;"></span></div>
          <div id="status" class="status" aria-live="polite"><div class="spinner"></div><span id="status_text">W trakcie tłumaczenia…</span></div>
          <div style="flex:1"></div>
        </div>
      </div>
      <div class="col">
        <label class="small">Wynik</label>
        <div class="result-box" id="result">{{ translated|default('') }}</div>
      </div>
    </div>

    {% if error %}
      <div style="margin-top:10px;color:#b91c1c;"><strong>Błąd:</strong> {{ error }}</div>
    {% endif %}
  </div>
</div>

<script>
/* ——— cały JS bez zmian ——— */
function setStatus(text, timeoutMs){
  const box = document.getElementById('status');
  const t = document.getElementById('status_text');
  if(text){ t.textContent = text; box.style.display = 'inline-flex'; }
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

let historyItems = {{ history_json|safe }};

function renderHistoryChips(){
  const wrap = document.getElementById('history');
  if(!wrap) return;
  wrap.innerHTML = '';
  const items = historyItems.slice(0,5);
  if(items.length === 0){
    const span = document.createElement('span');
    span.className = 'small';
    span.style.color = '#94a3b8';
    span.textContent = 'brak';
    wrap.appendChild(span);
    return;
  }
  items.forEach((item, idx) => {
    const chip = document.createElement('div');
    chip.className = 'chip';
    const short = (item.source || '').replace(/\n/g,' ').slice(0,40) + ((item.source||'').length>40?'...':'');
    chip.textContent = short;
    chip.addEventListener('click', ()=>loadHistory(idx));
    wrap.appendChild(chip);
  });
}

let userChosenPhrases = [];
let altMenuEl = null;
let lastClickedToken = null;

function clearAltMenu(){ if(altMenuEl && altMenuEl.parentNode){ altMenuEl.parentNode.removeChild(altMenuEl); } altMenuEl = null; }

function tokenizeForUI(text){
  const parts = text.split(/(\s+|[.,!?;:()«»„”"“—–-])/g).filter(p => p !== undefined && p !== null && p !== '');
  return parts;
}

function renderResultInteractive(text){
  const box = document.getElementById('result');
  box.innerHTML = '';
  const frag = document.createDocumentFragment();
  const parts = tokenizeForUI(text);
  parts.forEach((p) => {
    if (/^\s+$/.test(p) || /^[.,!?;:()«»„”"“—–-]$/.test(p)) {
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
  menu.innerHTML = '<div class="small" style="padding:6px 10px;color:#64748b">Propozycje...</div>';
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
      menu.innerHTML = '<div class="small" style="padding:8px 12px;color:#64748b">Brak propozycji</div>';
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
    menu.innerHTML = '<div class="small" style="padding:8px 12px;color:#b91c1c">Błąd pobierania propozycji</div>';
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
    setStatus('Koryguję zdanie…');
    const r = await fetch('/api/refine', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    const j = await r.json();
    const finalTxt = (j && typeof j.translated === 'string') ? j.translated : '';
    const faithful = (j && typeof j.faithful === 'boolean') ? j.faithful : true;
    if(finalTxt && faithful){
      setResultPlain(finalTxt);
      setStatus('');
    } else {
      setResultPlain(before);
      setStatus('Zmiana cofnięta — niespójna ze źródłem', 1600);
      userChosenPhrases = userChosenPhrases.filter(p => p !== selectedPhrase);
    }
  }catch(e){
    setResultPlain(before);
    setStatus('Nie udało się skorygować — cofnięto', 1600);
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
  try{
    const r = await fetch('/api/history/save', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ source_text: currText, translated: currResult, target_lang: currTarget })
    });
    const j = await r.json();
    if(j && j.ok){
      const item = { source: currText, target: currTarget };
      historyItems = historyItems.filter(h => !(h.source === item.source && h.target === item.target));
      historyItems.unshift(item);
      if(historyItems.length > 5) historyItems.length = 5;
      renderHistoryChips();
    }
  } catch(e){ }
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
    setStatus('W trakcie tłumaczenia…');
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
      badge.textContent = 'Wykryto: ' + j.detected;
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
  savePrefs();
  triggerAutoTranslate();
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

(function init(){
  const ta = document.getElementById('source_text');
  loadPrefs();
  autoGrow(ta);
  const initial = {{ translated|tojson|safe if translated is defined else '""' }};
  if(initial){ renderResultInteractive(initial); }
  renderHistoryChips();
  syncResultMinHeight();

  if(ta.value.trim().length > 0){
    triggerAutoTranslate();
  }
})();
</script>
</body>
</html>
"""

def call_ollama_chat(prompt_text, model=DEFAULT_MODEL, max_tokens=2048, temperature=0.0):
    url_v1 = OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        r = requests.post(url_v1, json=payload, timeout=60)
        if r.ok:
            j = r.json()
            if isinstance(j, dict) and "choices" in j and isinstance(j["choices"], list) and j["choices"]:
                ch = j["choices"][0]
                if isinstance(ch, dict):
                    if "message" in ch and isinstance(ch["message"], dict) and "content" in ch["message"]:
                        return ch["message"]["content"]
                    if "text" in ch and isinstance(ch["text"], str):
                        return ch["text"]
                    if "content" in ch and isinstance(ch["content"], str):
                        return ch["content"]
            if isinstance(j, dict):
                for v in j.values():
                    if isinstance(v, str) and v:
                        return v
            return r.text
    except requests.RequestException:
        pass

    url_api = OLLAMA_HOST.rstrip("/") + "/api/generate"
    payload2 = {"model": model, "prompt": prompt_text, "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens}}
    r2 = requests.post(url_api, json=payload2, timeout=90)
    if not r2.ok:
        raise Exception(f"Ollama API error: {r2.status_code} - {r2.text}")
    try:
        j2 = r2.json()
    except ValueError:
        text = r2.text
        try:
            parts = [json.loads(line) for line in text.splitlines() if line.strip().startswith('{')]
            if parts:
                out = ''.join(p.get('response', '') for p in parts)
                if out:
                    return out
        except Exception:
            pass
        return text

    if isinstance(j2, dict):
        for key in ("output", "result", "generated", "text"):
            if key in j2 and isinstance(j2[key], str):
                return j2[key]
        if "choices" in j2 and isinstance(j2["choices"], list) and j2["choices"]:
            ch = j2["choices"][0]
            if isinstance(ch, dict):
                for k in ("content", "text"):
                    if k in ch and isinstance(ch[k], str):
                        return ch[k]
    return r2.text

def build_prompt(source_text, source_lang_code, target_lang_code, tone="neutral"):
    target_name = next((name for code, name in LANGUAGES if code == target_lang_code), target_lang_code)
    source_name = "auto-detected" if (not source_lang_code or source_lang_code == "auto") \
        else next((name for code, name in LANGUAGES if code == source_lang_code), source_lang_code)

    tone_map = {"neutral":"neutral","formal":"formal","informal":"informal","friendly":"friendly","technical":"technical","poetic":"poetic"}
    tone_desc = tone_map.get(tone, "neutral")

    instr = []
    instr.append(f"You are a professional translator. Translate the user's text to {target_name} ({target_lang_code}).")
    instr.append(f"Source language: {source_name}.")
    if tone_desc and tone_desc != "neutral":
        instr.append(f"Use a {tone_desc} tone in the translation. Adapt phrasing and formality accordingly for the target language.")
    instr.append("Keep formatting (line breaks). Do not add extra commentary, do not translate code tags, XML, or URLs.")
    instr.append("Return only the translated text, without explanations. Preserve punctuation and capitalization as appropriate.")
    return " ".join(instr) + "\n\nUser text:\n" + source_text

def detect_language_safe(text):
    try:
        return detect(text)
    except Exception:
        return None

@app.route("/", methods=["GET"])
def index():
    return render_template_string(
        TEMPLATE,
        ollama_host=OLLAMA_HOST,
        model=DEFAULT_MODEL,
        languages=LANGUAGES,
        tones=TONES,
        history=[{"short": (h["source"][:40].replace("\n", " ") + ("..." if len(h["source"]) > 40 else "")), "source": h["source"], "target": h["target"]} for h in history],
        history_json=json.dumps([{"source": h["source"], "target": h["target"]} for h in history]),
        last_input="",
        translated="",
        error=None,
    )

@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json(silent=True) or {}

    source_text = (data.get("source_text") or "").strip()
    if not source_text:
        return jsonify({"error": "EMPTY", "translated": ""})

    source_lang = (data.get("source_lang") or "auto").strip()
    target_lang = (data.get("target_lang") or "de").strip()
    tone = (data.get("tone") or "neutral").strip()

    detected = detect_language_safe(source_text) if source_lang == "auto" else source_lang
    prompt = build_prompt(source_text, detected if detected else "auto", target_lang, tone=tone)

    try:
        translated = call_ollama_chat(prompt_text=prompt, model=DEFAULT_MODEL, temperature=0.0)
    except Exception as e:
        return jsonify({"error": f"Ollama error: {str(e)}"})

    return jsonify({"translated": translated, "detected": detected})

@app.route("/api/history/save", methods=["POST"])
def api_history_save():
    data = request.get_json(silent=True) or {}
    source_text = (data.get("source_text") or "").strip()
    translated = (data.get("translated") or "").strip()
    target_lang = (data.get("target_lang") or "de").strip()

    if not source_text or not translated:
        return jsonify({"ok": False, "error": "EMPTY"})

    dup_idx = None
    for i, h in enumerate(history):
        if h.get("source") == source_text and h.get("target") == target_lang:
            dup_idx = i
            break
    if dup_idx is not None:
        history.pop(dup_idx)

    history.insert(0, {"source": source_text, "translated": translated, "target": target_lang})
    while len(history) > HISTORY_LIMIT:
        history.pop()

    return jsonify({"ok": True})

@app.route("/api/alternatives", methods=["POST"])
def api_alternatives():
    data = request.get_json(silent=True) or {}
    source_text = (data.get("source_text") or "").strip()
    current_translation = (data.get("current_translation") or "").strip()
    clicked_word = (data.get("clicked_word") or "").strip()
    target_lang = (data.get("target_lang") or "de").strip()
    tone = (data.get("tone") or "neutral").strip()

    if not source_text or not current_translation or not clicked_word:
        return jsonify({"alternatives": []})

    prompt = (
        "You are assisting with post-editing of a translation.\n"
        f"Target language code: {target_lang}.\n"
        f"Tone: {tone}.\n"
        "Given the source sentence and its current translation to the target language, "
        f"provide up to 6 alternative single-word or short-phrase (1–3 words) replacements for the clicked token:\n"
        f"CLICKED_TOKEN: \"{clicked_word}\"\n\n"
        "Rules:\n"
        "- Keep alternatives concise (<= 3 words), natural in context, and appropriate for the target language.\n"
        "- Prefer synonyms or close variants that fit the specific sentence.\n"
        "- Avoid duplicates and avoid repeating the original token unless an inflected form differs significantly.\n"
        "- Return STRICT JSON as: {\"alternatives\": [\"...\", \"...\"]} with no extra text.\n\n"
        f"Source:\n{source_text}\n\n"
        f"Current translation:\n{current_translation}\n"
    )
    try:
        raw = call_ollama_chat(prompt_text=prompt, model=DEFAULT_MODEL, temperature=0.0, max_tokens=512)
        m = re.search(r'\{.*\}', raw, flags=re.S)
        j = json.loads(m.group(0)) if m else json.loads(raw)
        alts = j.get("alternatives", [])
        out = []
        for a in alts:
            if isinstance(a, str):
                s = a.strip()
                if 0 < len(s) <= 60 and s not in out:
                    out.append(s)
        return jsonify({"alternatives": out[:6]})
    except Exception:
        return jsonify({"alternatives": []})

@app.route("/api/refine", methods=["POST"])
def api_refine():
    data = request.get_json(silent=True) or {}
    source_text = (data.get("source_text") or "").strip()
    target_lang = (data.get("target_lang") or "de").strip()
    tone = (data.get("tone") or "neutral").strip()
    enforced_phrases = [p for p in (data.get("enforced_phrases") or []) if isinstance(p, str) and p.strip()]
    enforced_phrases = [p.strip() for p in enforced_phrases]
    current_translation = (data.get("current_translation") or "").strip()
    raw_repls = data.get("replacements") or []
    replacements = []
    for r in raw_repls:
        if isinstance(r, dict):
            f = (r.get("from") or "").strip()
            t = (r.get("to") or "").strip()
            if f and t:
                replacements.append({"from": f, "to": t})

    if not source_text:
        return jsonify({"translated": ""})

    target_name = next((name for code, name in LANGUAGES if code == target_lang), target_lang)
    tone_desc = tone
    constraint_list = "\n".join(f"- {p}" for p in enforced_phrases) if enforced_phrases else "- (none)"
    repl_list = "\n".join(f"- replace '{r['from']}' → '{r['to']}'" for r in replacements) if replacements else "- (none)"

    prompt = (
        "You are a professional translator.\n"
        f"Task: Produce a corrected, fluent translation of the source text into {target_name} ({target_lang}).\n"
        f"Tone: {tone_desc}.\n"
        "Return STRICT JSON ONLY:\n"
        '{"translated": "<final translation>", "faithful": true|false}'
        "\nNo explanations, no extra keys, no markdown.\n\n"
        "CONSTRAINTS:\n"
        "- The final translation MUST be faithful to the meaning of the source text.\n"
        "- You MUST include each of the following user-chosen phrases EXACTLY as written (verbatim):\n"
        f"{constraint_list}\n"
        "- Apply the following replacements to the current translation (they are user edits):\n"
        f"{repl_list}\n"
        "- Ensure each 'to' phrase appears and the corresponding 'from' token no longer appears.\n"
        "- If the enforced phrase changes the nuance, ADJUST the rest so the translation still matches the source meaning.\n"
        "- If you CANNOT keep it faithful while keeping the enforced phrase, set faithful=false and still output best-effort in 'translated'.\n"
        "- Do NOT introduce information absent from the source; you may paraphrase to keep it idiomatic.\n"
        "- You may inflect surrounding words and adjust word order, but DO NOT alter the chosen phrases themselves.\n\n"
        f"Source text:\n{source_text}\n"
        f"\nCurrent translation (user-edited draft):\n{current_translation}\n"
    )
    try:
        raw = call_ollama_chat(prompt_text=prompt, model=DEFAULT_MODEL, temperature=0.0, max_tokens=768)
        m = re.search(r'\{.*\}', raw, flags=re.S)
        j = json.loads(m.group(0)) if m else json.loads(raw)
        translated = j.get("translated", "") if isinstance(j, dict) else ""
        faithful = bool(j.get("faithful", True)) if isinstance(j, dict) else True
        return jsonify({"translated": translated, "faithful": faithful})
    except Exception as e:
        return jsonify({"translated": current_translation, "faithful": False, "error": str(e)})

if __name__ == "__main__":
    print(f"Starting llot on http://{LISTEN_HOST}:{LISTEN_PORT} — Ollama: {OLLAMA_HOST} Model: {DEFAULT_MODEL}")
    app.run(host=LISTEN_HOST, port=LISTEN_PORT)

import json

import pytest
from playwright.sync_api import expect

from tests.e2e.conftest import pick_target_language

pytestmark = pytest.mark.e2e


def _fulfill_json(route, body):
    route.fulfill(status=200, content_type="application/json", body=json.dumps(body))


def test_page_loads_without_errors(page, base_url, console_errors):
    page.goto(base_url)
    expect(page.locator("#source_text")).to_be_visible()
    page.wait_for_timeout(1000)
    assert console_errors == []


def test_translation_output_is_not_rendered_as_html(page, base_url):
    payload = '<img src=x onerror="window.__xss=1"> "quoted" & done'
    page.route(
        "**/api/translate", lambda r: _fulfill_json(r, {"translated_text": payload, "source_lang": "en"})
    )
    page.goto(base_url)
    page.fill("#source_text", "anything")
    expect(page.locator("#result")).to_contain_text("<img src=x")
    assert page.evaluate("window.__xss") is None
    assert page.locator("#result img").count() == 0


def test_default_model_comes_from_server_not_first_listed(page, base_url):
    page.goto(base_url)
    default_model = page.evaluate("window.defaultModel")
    page.route(
        "**/api/models", lambda r: _fulfill_json(r, {"models": ["zzz-ocr:1b", default_model, "other:7b"]})
    )
    page.evaluate("localStorage.clear()")
    page.reload()
    expect(page.locator("#model-select-output")).to_have_value(default_model)


def test_speaker_only_for_languages_with_voice(page, base_url):
    page.route("**/api/tts/languages", lambda r: _fulfill_json(r, {"enabled": True, "languages": ["pl"]}))
    page.route(
        "**/api/translate", lambda r: _fulfill_json(r, {"translated_text": "Cześć", "source_lang": "en"})
    )
    page.goto(base_url)
    if not page.evaluate("window.ttsEnabled"):
        pytest.skip("TTS not configured on this instance")
    page.fill("#source_text", "Hello")
    pick_target_language(page, "pl")
    expect(page.locator("#tts-btn")).to_be_visible()
    pick_target_language(page, "de")
    expect(page.locator("#tts-btn")).to_be_hidden()


def test_live_translate_and_speak(page, base_url, console_errors):
    """Smoke test against the real Ollama + TTS backends configured on the instance."""
    health = page.request.get(f"{base_url}/api/health").json()
    if health["ollama"]["status"] != "ok":
        pytest.skip("Ollama not reachable")
    tts_langs = page.request.get(f"{base_url}/api/tts/languages").json()["languages"]
    if not tts_langs:
        pytest.skip("No TTS voices available")

    # Media events don't bubble and the player's Audio element isn't in the DOM,
    # so hook play() to observe playback finishing.
    page.add_init_script(
        """
        window.__ended = 0;
        const play = HTMLMediaElement.prototype.play;
        HTMLMediaElement.prototype.play = function () {
          if (this.src.startsWith('blob:')) {
            this.addEventListener('ended', () => window.__ended++, { once: true });
          }
          return play.call(this);
        };
        """
    )
    page.goto(base_url)
    pick_target_language(page, tts_langs[0])
    page.fill("#source_text", "Good morning")
    expect(page.locator("#tts-btn")).to_be_visible(timeout=120_000)
    page.click("#tts-btn")
    page.wait_for_function("window.__ended > 0", timeout=60_000)
    assert [e for e in console_errors if "TTS" in e] == []


def test_options_menu_reachable_on_phone(browser, base_url):
    """Tone/model/think options must be usable on narrow screens too."""
    context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    page = context.new_page()
    page.goto(base_url)
    trigger = page.locator("#output-options-dropdown .options-trigger")
    expect(trigger).to_be_visible()
    trigger.click()
    expect(page.locator("#think-select")).to_be_visible()
    context.close()


FAKE_SPEECH = """
window.__spoken = [];
const voices = [
  { name: 'Anna', lang: 'de-DE', localService: true, default: false },
  { name: 'Google čeština', lang: 'cs-CZ', localService: false, default: false },
];
const synth = {
  getVoices: () => voices,
  addEventListener: () => {},
  cancel: () => {},
  speak: (u) => { window.__spoken.push({ text: u.text, voice: u.voice.name }); setTimeout(() => u.onend && u.onend(), 10); },
};
Object.defineProperty(window, 'speechSynthesis', { value: synth });
window.SpeechSynthesisUtterance = function (text) { this.text = text; };
"""


def test_browser_voice_fallback_uses_only_local_voices(page, base_url):
    page.add_init_script(FAKE_SPEECH)
    page.route("**/api/tts/languages", lambda r: _fulfill_json(r, {"enabled": True, "languages": ["pl"]}))
    page.route(
        "**/api/translate",
        lambda r: _fulfill_json(r, {"translated_text": "Guten Morgen", "source_lang": "en"}),
    )
    page.goto(base_url)
    page.fill("#source_text", "Good morning")
    pick_target_language(page, "de")
    expect(page.locator("#tts-btn")).to_be_visible()
    page.click("#tts-btn")
    page.wait_for_function("window.__spoken.length > 0")
    assert page.evaluate("window.__spoken") == [{"text": "Guten Morgen", "voice": "Anna"}]

    pick_target_language(page, "cs")  # only a network voice exists -> no speaker
    expect(page.locator("#tts-btn")).to_be_hidden()

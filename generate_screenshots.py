#!/usr/bin/env python3
"""
Screenshot generator for LLOT application README
Generates comprehensive screenshots showing all features
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def setup_driver():
    """Set up Chrome driver with optimal settings for screenshots."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,900")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def take_screenshot(driver, filename, description=""):
    """Take a screenshot and save it."""
    print(f"📸 Taking screenshot: {filename} - {description}")
    time.sleep(1)  # Wait for animations
    
    # Ensure screenshots directory exists
    os.makedirs("docs/images", exist_ok=True)
    
    # Take screenshot
    driver.save_screenshot(f"docs/images/{filename}")
    print(f"✅ Screenshot saved: docs/images/{filename}")

def wait_for_translation(driver, timeout=30):
    """Wait for translation to complete."""
    print("⏳ Waiting for translation to complete...")
    try:
        # Wait for the translate button to not have "translating" state
        WebDriverWait(driver, timeout).until(
            lambda d: "translating" not in d.find_element(By.ID, "translate-btn").get_attribute("class")
        )
        time.sleep(2)  # Extra wait for result to display
        print("✅ Translation completed")
        return True
    except Exception as e:
        print(f"⚠️ Translation timeout or error: {e}")
        return False

def generate_main_interface_screenshot(driver):
    """Generate main interface screenshot."""
    print("\n🎯 Generating main interface screenshot...")
    
    driver.get("http://localhost:8080")
    time.sleep(3)
    
    # Fill in some sample text
    source_text = driver.find_element(By.ID, "source-text")
    source_text.clear()
    source_text.send_keys("Hello! This is LLOT - Local LLM Ollama Translator. It provides privacy-first translation using local AI models.")
    
    # Set target language to Polish
    target_select = Select(driver.find_element(By.ID, "target-lang"))
    target_select.select_by_value("pl")
    
    time.sleep(1)
    take_screenshot(driver, "main-interface.png", "Main interface with sample text")

def generate_translation_screenshot(driver):
    """Generate translation in progress screenshot."""
    print("\n🌍 Generating translation screenshot...")
    
    # Click translate button
    translate_btn = driver.find_element(By.ID, "translate-btn")
    translate_btn.click()
    
    # Wait for translation to complete
    if wait_for_translation(driver):
        take_screenshot(driver, "translation-result.png", "Translation completed")
    else:
        take_screenshot(driver, "translation-loading.png", "Translation in progress")

def generate_dark_mode_screenshot(driver):
    """Generate dark mode screenshot."""
    print("\n🌙 Generating dark mode screenshot...")
    
    try:
        # Toggle dark mode
        theme_toggle = driver.find_element(By.ID, "theme-toggle")
        theme_toggle.click()
        time.sleep(2)
        
        take_screenshot(driver, "dark-mode.png", "Dark mode interface")
        
        # Toggle back to light mode
        theme_toggle.click()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Could not toggle dark mode: {e}")

def generate_options_menu_screenshot(driver):
    """Generate options menu screenshot."""
    print("\n⚙️ Generating options menu screenshot...")
    
    try:
        # Open options menu
        options_btn = driver.find_element(By.ID, "options-btn")
        options_btn.click()
        time.sleep(2)
        
        take_screenshot(driver, "options-menu.png", "Options menu with settings")
        
        # Close options menu by clicking elsewhere
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Could not open options menu: {e}")

def generate_history_screenshot(driver):
    """Generate history screenshot."""
    print("\n📚 Generating history screenshot...")
    
    # First make sure we have some translations in history
    source_text = driver.find_element(By.ID, "source-text")
    
    # Add a few translations to history
    translations = [
        ("Good morning", "de"),
        ("How are you?", "es"),
        ("Thank you", "fr")
    ]
    
    for text, lang in translations:
        source_text.clear()
        source_text.send_keys(text)
        
        target_select = Select(driver.find_element(By.ID, "target-lang"))
        target_select.select_by_value(lang)
        
        translate_btn = driver.find_element(By.ID, "translate-btn")
        translate_btn.click()
        
        wait_for_translation(driver)
        time.sleep(1)
    
    # Now show history
    try:
        history_btn = driver.find_element(By.ID, "history-btn")
        history_btn.click()
        time.sleep(2)
        
        take_screenshot(driver, "history-panel.png", "Translation history")
        
        # Close history
        history_btn.click()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Could not show history: {e}")

def generate_mobile_screenshot(driver):
    """Generate mobile responsive screenshot."""
    print("\n📱 Generating mobile screenshot...")
    
    # Change to mobile viewport
    driver.set_window_size(375, 812)  # iPhone X size
    time.sleep(2)
    
    take_screenshot(driver, "mobile-interface.png", "Mobile responsive design")
    
    # Reset to desktop viewport
    driver.set_window_size(1400, 900)
    time.sleep(1)

def generate_tts_screenshot(driver):
    """Generate TTS feature screenshot."""
    print("\n🔊 Generating TTS screenshot...")
    
    try:
        # Make sure we have translation result
        source_text = driver.find_element(By.ID, "source-text")
        source_text.clear()
        source_text.send_keys("Hello, this is a test of text-to-speech functionality.")
        
        translate_btn = driver.find_element(By.ID, "translate-btn")
        translate_btn.click()
        
        if wait_for_translation(driver):
            # Hover over TTS button to show it's available
            try:
                tts_btn = driver.find_element(By.CLASS_NAME, "tts-btn")
                ActionChains(driver).move_to_element(tts_btn).perform()
                time.sleep(1)
                
                take_screenshot(driver, "tts-feature.png", "Text-to-speech feature")
            except Exception as e:
                print(f"⚠️ TTS button not found: {e}")
    except Exception as e:
        print(f"⚠️ Could not demonstrate TTS: {e}")

def main():
    """Main function to generate all screenshots."""
    print("🚀 LLOT Screenshot Generator")
    print("=" * 50)
    
    driver = None
    try:
        driver = setup_driver()
        
        # Generate all screenshots
        generate_main_interface_screenshot(driver)
        generate_translation_screenshot(driver)
        generate_dark_mode_screenshot(driver)
        generate_options_menu_screenshot(driver)
        generate_history_screenshot(driver)
        generate_mobile_screenshot(driver)
        generate_tts_screenshot(driver)
        
        print("\n🎉 All screenshots generated successfully!")
        print("📁 Screenshots saved in: docs/images/")
        
    except Exception as e:
        print(f"❌ Error generating screenshots: {e}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simplified screenshot generator for LLOT application
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Set up Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,900")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    return driver

def take_screenshot(driver, filename, description=""):
    """Take a screenshot."""
    print(f"📸 {description}")
    time.sleep(2)
    os.makedirs("docs/images", exist_ok=True)
    driver.save_screenshot(f"docs/images/{filename}")
    print(f"✅ Screenshot saved: docs/images/{filename}")

def main():
    """Generate screenshots."""
    print("🚀 LLOT Screenshot Generator")
    print("=" * 50)
    
    driver = None
    try:
        driver = setup_driver()
        
        # 1. Main interface
        print("\n🎯 Main interface...")
        driver.get("http://localhost:8080")
        time.sleep(3)
        take_screenshot(driver, "main-interface.png", "Main interface")
        
        # 2. Add some text
        print("\n✍️ Adding sample text...")
        source_text = driver.find_element(By.ID, "source_text")
        source_text.send_keys("Hello! This is LLOT - a privacy-first translation service powered by local LLM. No cloud services, 100% self-hosted.")
        time.sleep(1)
        take_screenshot(driver, "with-text.png", "Interface with sample text")
        
        # 3. Wait for translation
        print("\n⏳ Waiting for translation...")
        time.sleep(10)
        take_screenshot(driver, "translation-result.png", "Translation result")
        
        # 4. Dark mode
        print("\n🌙 Testing dark mode...")
        try:
            theme_toggle = driver.find_element(By.ID, "theme-toggle")
            theme_toggle.click()
            time.sleep(2)
            take_screenshot(driver, "dark-mode.png", "Dark mode interface")
        except Exception as e:
            print(f"⚠️ Dark mode failed: {e}")
        
        # 5. Mobile view
        print("\n📱 Mobile view...")
        driver.set_window_size(375, 812)
        time.sleep(2)
        take_screenshot(driver, "mobile-interface.png", "Mobile responsive design")
        
        print("\n🎉 All screenshots generated!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
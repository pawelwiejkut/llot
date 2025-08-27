#!/usr/bin/env python3

import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def setup_chrome_driver():
    """Setup Chrome driver with options for full browser view"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1400,1000')  # Larger window for better browser view
    chrome_options.add_argument('--force-device-scale-factor=1')
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.binary_location = '/opt/homebrew/bin/chromium'  # Point to Chromium
    
    # Use webdriver-manager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def take_browser_screenshot(driver, filename, step_description):
    """Take a full browser screenshot including the address bar and browser chrome"""
    print(f"Taking screenshot: {step_description}")
    
    # Ensure we're capturing the full browser window
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.3)  # Short pause to ensure rendering
    
    # Take screenshot of entire browser window
    driver.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")

def gradual_type(element, text, delay=0.05):
    """Type text gradually with delays between characters"""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def create_smooth_demo():
    """Create a smooth, detailed demo with many more screenshots"""
    
    # Create output directory
    output_dir = "docs/smooth_demo_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    driver = setup_chrome_driver()
    
    try:
        # Navigate to the application
        print("Opening LLOT application...")
        driver.get("http://localhost:8082/modern")
        
        # Wait for page to fully load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "source-text"))
        )
        
        screenshot_count = 0
        
        # Screenshot 1: Initial page load
        screenshot_count += 1
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Initial application load")
        time.sleep(1)
        
        # Screenshot 2: Hover over source language dropdown
        screenshot_count += 1
        source_lang_dropdown = driver.find_element(By.ID, "source-lang")
        ActionChains(driver).move_to_element(source_lang_dropdown).perform()
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Hover over source language")
        time.sleep(0.5)
        
        # Screenshot 3: Click source language dropdown
        screenshot_count += 1
        source_lang_dropdown.click()
        time.sleep(0.5)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Source language dropdown opened")
        
        # Screenshot 4: Select French
        screenshot_count += 1
        Select(source_lang_dropdown).select_by_value("fr")
        time.sleep(0.5)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "French selected as source")
        
        # Screenshot 5: Start typing in source text
        screenshot_count += 1
        source_text = driver.find_element(By.ID, "source-text")
        source_text.click()
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Click in source text area")
        time.sleep(0.3)
        
        # Screenshots 6-12: Type "Bonjour!" character by character
        text_to_type = "Bonjour!"
        for i, char in enumerate(text_to_type, 6):
            source_text.send_keys(char)
            time.sleep(0.1)
            if i % 2 == 0 or i == len(text_to_type) + 5:  # Take screenshot every 2 chars or at end
                screenshot_count += 1
                take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", f"Typing: '{text_to_type[:i-5]}'")
                time.sleep(0.3)
        
        # Screenshot 13: Wait for translation to appear
        screenshot_count += 1
        time.sleep(2)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Translation appears")
        
        # Screenshot 14: Add more text
        screenshot_count += 1
        gradual_type(source_text, "Bonjour! Comment allez-vous aujourd'hui?", 0.03)
        time.sleep(1)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Full sentence typed")
        
        # Screenshot 15: Wait for full translation
        screenshot_count += 1
        time.sleep(2)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Full translation appears")
        
        # Screenshot 16: Change target language
        screenshot_count += 1
        target_lang_dropdown = driver.find_element(By.ID, "target-lang")
        target_lang_dropdown.click()
        time.sleep(0.5)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Target language dropdown opened")
        
        # Screenshot 17: Select Spanish
        screenshot_count += 1
        Select(target_lang_dropdown).select_by_value("es")
        time.sleep(1)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Spanish selected as target")
        
        # Screenshot 18: Wait for retranslation
        screenshot_count += 1
        time.sleep(2)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Retranslated to Spanish")
        
        # Screenshot 19: Change tone
        screenshot_count += 1
        try:
            tone_dropdown = driver.find_element(By.ID, "tone")
            tone_dropdown.click()
            time.sleep(0.5)
            take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Tone dropdown opened")
            
            # Screenshot 20: Select formal tone
            screenshot_count += 1
            Select(tone_dropdown).select_by_value("formal")
            time.sleep(1)
            take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Formal tone selected")
            
            # Screenshot 21: Wait for formal translation
            screenshot_count += 1
            time.sleep(2)
            take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Formal tone translation")
        except:
            print("Tone selector not found, skipping...")
        
        # Screenshot 22: Toggle dark mode
        screenshot_count += 1
        try:
            theme_toggle = driver.find_element(By.ID, "theme-toggle")
            theme_toggle.click()
            time.sleep(1)
            take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Dark mode activated")
            
            # Screenshot 23: Dark mode view
            screenshot_count += 1
            time.sleep(0.5)
            take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Dark mode interface")
            
            # Screenshot 24: Toggle back to light mode
            screenshot_count += 1
            theme_toggle.click()
            time.sleep(1)
            take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Back to light mode")
        except:
            print("Theme toggle not found, skipping...")
        
        # Screenshot 25: Final view
        screenshot_count += 1
        time.sleep(1)
        take_browser_screenshot(driver, f"{output_dir}/frame_{screenshot_count:03d}.png", "Final demo state")
        
        print(f"Created {screenshot_count} screenshots for smooth animation")
        return screenshot_count
        
    except Exception as e:
        print(f"Error during demo creation: {e}")
        return 0
    finally:
        driver.quit()

def create_optimized_gif(frame_count, output_filename):
    """Create optimized GIF from screenshots with smooth timing"""
    input_dir = "docs/smooth_demo_frames"
    
    if frame_count == 0:
        print("No frames to process")
        return
    
    print(f"Creating smooth GIF from {frame_count} frames...")
    
    # Create GIF with variable delays for more natural pacing
    # Faster for typing, slower for reading translations
    typing_delay = "50"      # 0.5s for typing actions
    reading_delay = "200"    # 2.0s for reading translations
    transition_delay = "100" # 1.0s for UI transitions
    
    # Build the convert command with different delays for different frame ranges
    cmd = ["magick"]
    
    for i in range(1, frame_count + 1):
        frame_path = f"{input_dir}/frame_{i:03d}.png"
        
        # Determine delay based on frame content/position
        if 6 <= i <= 12:  # Typing frames - faster
            delay = typing_delay
        elif i in [13, 15, 18, 21, 25]:  # Translation result frames - slower
            delay = reading_delay
        else:  # Transition frames - medium
            delay = transition_delay
            
        cmd.extend(["-delay", delay, frame_path])
    
    # Add optimization options
    cmd.extend([
        "-loop", "0",           # Infinite loop
        "-layers", "optimize",  # Optimize layers
        "-colors", "256",       # Limit colors for smaller file
        f"docs/images/{output_filename}"
    ])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"Smooth GIF created successfully: docs/images/{output_filename}")
            
            # Check file size
            file_size = os.path.getsize(f"docs/images/{output_filename}")
            print(f"File size: {file_size // 1024} KB")
            
            return True
        else:
            print(f"Error creating GIF: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("GIF creation timed out")
        return False
    except Exception as e:
        print(f"Error running ImageMagick: {e}")
        return False

def main():
    print("Creating smooth LLOT demo with browser context...")
    
    # Check if app is running
    try:
        import requests
        response = requests.get("http://localhost:8082/modern", timeout=5)
        if response.status_code != 200:
            print("Application not responding. Make sure LLOT is running on port 8082")
            return
    except:
        print("Cannot connect to application. Make sure LLOT is running on port 8082")
        return
    
    # Create smooth demo
    frame_count = create_smooth_demo()
    
    if frame_count > 0:
        # Create the optimized smooth GIF
        success = create_optimized_gif(frame_count, "llot-demo-smooth.gif")
        
        if success:
            print("\n✅ Smooth demo GIF created successfully!")
            print("📁 Location: docs/images/llot-demo-smooth.gif")
            print("🎬 This GIF shows natural typing and smooth transitions")
        else:
            print("❌ Failed to create GIF")
    else:
        print("❌ Failed to create demo screenshots")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
LLOT Demo GIF Generator
Creates animated GIF showcasing all main features
"""

import time
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class LLOTDemoRecorder:
    def __init__(self):
        self.screenshots = []
        self.frame_count = 0
        self.demo_dir = "docs/demo_frames"
        os.makedirs(self.demo_dir, exist_ok=True)
        
        # Setup Chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(3)
        
    def capture_frame(self, description="", pause=1.5):
        """Capture a frame for the GIF."""
        print(f"📸 Frame {self.frame_count:03d}: {description}")
        time.sleep(pause)
        
        filename = f"{self.demo_dir}/frame_{self.frame_count:03d}.png"
        self.driver.save_screenshot(filename)
        self.screenshots.append(filename)
        self.frame_count += 1
        
    def wait_for_translation(self, timeout=15):
        """Wait for translation to complete."""
        try:
            # Wait for loading spinner to appear and disappear
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.ID, "loading-spinner"))
            )
            time.sleep(2)  # Extra pause for result to display
            return True
        except:
            return False
    
    def smooth_type(self, element, text, typing_speed=0.1):
        """Type text smoothly character by character."""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(typing_speed)
    
    def create_demo_sequence(self):
        """Create the complete demo sequence."""
        
        # 1. Load the application
        print("\n🎬 Starting LLOT Demo Recording...")
        self.driver.get("http://localhost:8080")
        self.capture_frame("LLOT Application Loaded", 2)
        
        # 2. Show initial interface
        self.capture_frame("Clean Modern Interface", 1.5)
        
        # 3. Type first text slowly to show real-time feel
        print("\n✍️ Demonstrating text input...")
        source_text = self.driver.find_element(By.ID, "source_text")
        
        # Type text character by character for animation effect
        demo_text = "Hello! Welcome to LLOT - your privacy-first local translator."
        for i in range(0, len(demo_text), 8):  # Type in chunks for smooth animation
            chunk = demo_text[:i+8]
            source_text.clear()
            source_text.send_keys(chunk)
            self.capture_frame(f"Typing: '{chunk[-8:]}'...", 0.3)
        
        # 4. Show auto-translation happening
        print("\n🌍 Waiting for auto-translation...")
        if self.wait_for_translation():
            self.capture_frame("Translation Completed - English to German", 2)
        else:
            self.capture_frame("Translation in Progress", 1)
        
        # 5. Change target language
        print("\n🔄 Changing target language...")
        try:
            # Click on target language dropdown
            target_dropdown = self.driver.find_element(By.ID, "target-lang-dropdown")
            target_dropdown.click()
            self.capture_frame("Target Language Menu Opened", 1)
            
            # Wait for dropdown to be visible and select Polish
            time.sleep(0.5)
            try:
                polish_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Polski')]")
                polish_option.click()
                self.capture_frame("Selected Polish Language", 1)
            except:
                # Fallback to hidden select
                target_select = Select(self.driver.find_element(By.ID, "target_lang"))
                target_select.select_by_value("pl")
                self.capture_frame("Selected Polish Language", 1)
                
            # Wait for re-translation
            if self.wait_for_translation():
                self.capture_frame("Re-translated to Polish", 2)
                
        except Exception as e:
            print(f"Language change failed: {e}")
            
        # 6. Show tone selection
        print("\n🎭 Demonstrating tone selection...")
        try:
            # Open options menu
            options_btn = self.driver.find_element(By.CSS_SELECTOR, ".options-trigger")
            options_btn.click()
            self.capture_frame("Options Menu Opened", 1.5)
            
            # Change tone to formal
            tone_select = Select(self.driver.find_element(By.ID, "tone-output"))
            tone_select.select_by_value("formal")
            self.capture_frame("Selected Formal Tone", 1)
            
            # Close options menu
            options_btn.click()
            time.sleep(0.5)
            
            # Wait for re-translation with new tone
            if self.wait_for_translation():
                self.capture_frame("Formal Tone Translation", 2)
                
        except Exception as e:
            print(f"Tone selection failed: {e}")
            
        # 7. Try different text and language pair
        print("\n🌏 Trying different language pair...")
        source_text.clear()
        self.smooth_type(source_text, "Bonjour! Comment allez-vous aujourd'hui?", 0.08)
        self.capture_frame("French Text Entered", 1)
        
        # Change to English target
        try:
            target_dropdown = self.driver.find_element(By.ID, "target-lang-dropdown") 
            target_dropdown.click()
            time.sleep(0.5)
            english_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'English')]")
            english_option.click()
            self.capture_frame("Changed to English Target", 1)
            
            if self.wait_for_translation():
                self.capture_frame("French to English Translation", 2)
        except:
            pass
        
        # 8. Show dark mode toggle
        print("\n🌙 Demonstrating dark mode...")
        try:
            theme_toggle = self.driver.find_element(By.ID, "theme-toggle")
            theme_toggle.click()
            self.capture_frame("Switching to Dark Mode", 1)
            self.capture_frame("Dark Mode Active", 2)
            
            # Switch back to light mode
            theme_toggle.click()
            self.capture_frame("Back to Light Mode", 1.5)
        except Exception as e:
            print(f"Theme toggle failed: {e}")
            
        # 9. Show mobile responsive (resize window)
        print("\n📱 Showing mobile responsiveness...")
        self.driver.set_window_size(375, 667)  # iPhone size
        self.capture_frame("Mobile Layout - Portrait", 2)
        
        # Back to desktop
        self.driver.set_window_size(1200, 800)
        self.capture_frame("Desktop Layout Restored", 1.5)
        
        # 10. Final showcase
        print("\n✨ Final showcase...")
        source_text.clear()
        self.smooth_type(source_text, "LLOT: Privacy-first AI translation!", 0.08)
        self.capture_frame("Final Message", 2)
        
        if self.wait_for_translation():
            self.capture_frame("Complete Demo - All Features Shown!", 3)
    
    def create_gif(self, output_filename="docs/images/llot-demo.gif"):
        """Convert screenshots to animated GIF using ImageMagick."""
        print(f"\n🎞️ Creating animated GIF from {len(self.screenshots)} frames...")
        
        try:
            # Create GIF with ImageMagick
            cmd = [
                "convert",
                "-delay", "100",  # 1 second per frame
                "-loop", "0",     # Loop forever
                "-resize", "800x533",  # Reasonable size for web
                *self.screenshots,
                output_filename
            ]
            
            subprocess.run(cmd, check=True)
            print(f"✅ GIF created: {output_filename}")
            
            # Create optimized version
            optimized_filename = output_filename.replace('.gif', '-optimized.gif')
            optimize_cmd = [
                "convert",
                output_filename,
                "-fuzz", "2%",
                "-layers", "optimize-plus",
                optimized_filename
            ]
            
            subprocess.run(optimize_cmd, check=True)
            print(f"✅ Optimized GIF created: {optimized_filename}")
            
            return optimized_filename
            
        except subprocess.CalledProcessError as e:
            print(f"❌ GIF creation failed: {e}")
            print("Make sure ImageMagick is installed: brew install imagemagick")
            return None
        except FileNotFoundError:
            print("❌ ImageMagick not found. Install with: brew install imagemagick")
            return None
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
    
    def run_demo(self):
        """Run the complete demo recording."""
        try:
            self.create_demo_sequence()
            gif_path = self.create_gif()
            
            if gif_path:
                # Get file size
                file_size = os.path.getsize(gif_path) / 1024 / 1024
                print(f"\n🎉 Demo GIF complete!")
                print(f"📄 File: {gif_path}")
                print(f"📏 Size: {file_size:.1f} MB")
                print(f"🖼️  Frames: {len(self.screenshots)}")
                
                return gif_path
            else:
                print("❌ Failed to create GIF")
                return None
                
        except Exception as e:
            print(f"❌ Demo recording failed: {e}")
            return None
        finally:
            self.cleanup()

def main():
    """Main function."""
    print("🎬 LLOT Demo GIF Generator")
    print("=" * 50)
    
    # Check if ImageMagick is available
    try:
        subprocess.run(["convert", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ImageMagick not found!")
        print("Please install: brew install imagemagick")
        return
    
    # Create demo
    recorder = LLOTDemoRecorder()
    gif_path = recorder.run_demo()
    
    if gif_path:
        print(f"\n🎯 Demo GIF ready for README!")
        print(f"Add to README: ![LLOT Demo]({gif_path})")
    
if __name__ == "__main__":
    main()
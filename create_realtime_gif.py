#!/usr/bin/env python3

import os
import subprocess
import time
from datetime import datetime

def take_screenshot(filename, description=""):
    """Take a screenshot of the current screen"""
    print(f"📸 {description}")
    
    # Use macOS screencapture - capture specific window or area
    cmd = [
        "screencapture", 
        "-x",  # No sound
        "-t", "png",  # PNG format
        filename
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Screenshot saved: {filename}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Screenshot failed: {e}")
        return False

def create_realtime_demo():
    """Create a real-time demo GIF with human-like timing"""
    
    output_dir = "docs/realtime_demo"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎬 Creating real-time LLOT demo...")
    print("📝 Instructions:")
    print("   1. Open your browser to http://localhost:8082/modern")
    print("   2. Follow the prompts and perform actions slowly")
    print("   3. Press Enter after each action to continue")
    print()
    
    input("Press Enter when you're ready to start recording...")
    
    screenshots = []
    step = 0
    
    def capture_step(description, pause_time=2):
        nonlocal step
        step += 1
        filename = f"{output_dir}/realtime_{step:03d}.png"
        
        print(f"\n🎬 Step {step}: {description}")
        input("   Press Enter when ready to capture this step...")
        
        if take_screenshot(filename, description):
            screenshots.append((filename, description))
            time.sleep(pause_time)
        
        return filename
    
    # Demo sequence with human-like timing
    print("\n🚀 Starting demo sequence...")
    
    # Step 1: Initial page
    capture_step("Initial application page - clean interface", 3)
    
    # Step 2: Click on source language dropdown  
    capture_step("Click on 'Detect language' dropdown", 1)
    
    # Step 3: Language dropdown opened
    capture_step("Language dropdown opened - show options", 2)
    
    # Step 4: Select French
    capture_step("Select 'Français' from dropdown", 1)
    
    # Step 5: French selected
    capture_step("French selected as source language", 2)
    
    # Step 6: Start typing
    capture_step("Click in text area - cursor visible", 1)
    
    # Step 7: Type some text
    capture_step("Type: 'Bonjour!' - short text", 2)
    
    # Step 8: Translation appears
    capture_step("Translation appears: 'Hello!' in German", 3)
    
    # Step 9: Add more text
    capture_step("Add more text: 'Comment allez-vous?'", 2)
    
    # Step 10: Full translation
    capture_step("Full translation visible", 3)
    
    # Step 11: Change target language
    capture_step("Click on target language (Deutsch)", 1)
    
    # Step 12: Target dropdown open
    capture_step("Target language dropdown opened", 2)
    
    # Step 13: Select Spanish
    capture_step("Select 'Español' from target languages", 1)
    
    # Step 14: Spanish translation
    capture_step("Translation updated to Spanish", 3)
    
    # Step 15: Open tone options
    capture_step("Click on options menu (three dots)", 1)
    
    # Step 16: Tone dropdown
    capture_step("Tone options visible", 2)
    
    # Step 17: Select formal tone
    capture_step("Select 'Formal' tone", 1)
    
    # Step 18: Formal translation
    capture_step("Translation updated with formal tone", 3)
    
    # Step 19: Dark mode toggle
    capture_step("Click dark mode toggle", 1)
    
    # Step 20: Dark mode active
    capture_step("Dark mode interface", 3)
    
    # Step 21: Light mode back
    capture_step("Toggle back to light mode", 2)
    
    # Step 22: Final state
    capture_step("Final demo state - ready for use", 3)
    
    print(f"\n✅ Captured {len(screenshots)} screenshots")
    
    return screenshots

def create_realtime_gif(screenshots):
    """Create a GIF from real-time screenshots"""
    
    if not screenshots:
        print("❌ No screenshots to process")
        return False
    
    print("\n🎞️ Creating real-time GIF...")
    
    # Build ImageMagick command with natural human timing
    cmd = ["magick"]
    
    for i, (filename, description) in enumerate(screenshots):
        # Variable timing based on action type
        if "dropdown" in description.lower() or "click" in description.lower():
            delay = "80"  # Quick UI responses - 0.8s
        elif "translation" in description.lower() or "updated" in description.lower():
            delay = "250"  # Wait for translation - 2.5s
        elif "typing" in description.lower() or "type" in description.lower():
            delay = "120"  # Typing speed - 1.2s
        elif "select" in description.lower():
            delay = "100"  # Selection actions - 1.0s
        else:
            delay = "150"  # Default pause - 1.5s
        
        cmd.extend(["-delay", delay, filename])
    
    # Add GIF options
    output_file = "docs/images/llot-demo-realtime.gif"
    cmd.extend([
        "-loop", "0",           # Infinite loop
        "-layers", "optimize",  # Optimize for size
        "-colors", "256",       # Limit colors
        "-quality", "95",       # High quality
        output_file
    ])
    
    try:
        print("🔄 Running ImageMagick...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print(f"✅ Real-time GIF created: {output_file}")
            print(f"📦 File size: {file_size // 1024} KB")
            print(f"🎬 Duration: ~{len(screenshots) * 1.5:.1f} seconds")
            return True
        else:
            print(f"❌ ImageMagick error: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ GIF creation timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function for real-time demo creation"""
    
    print("🎬 LLOT Real-Time Demo Creator")
    print("=" * 40)
    print()
    
    # Check if app is running
    try:
        import requests
        response = requests.get("http://localhost:8082/modern", timeout=5)
        if response.status_code != 200:
            print("❌ LLOT not running on port 8082")
            print("   Please start the application first:")
            print("   python run.py")
            return
    except:
        print("❌ Cannot connect to LLOT application")
        print("   Make sure it's running on http://localhost:8082")
        return
    
    print("✅ LLOT application is running")
    print()
    
    # Record real-time demo
    screenshots = create_realtime_demo()
    
    if screenshots:
        # Create GIF
        success = create_realtime_gif(screenshots)
        
        if success:
            print("\n🎉 Real-time demo completed!")
            print("📁 Output: docs/images/llot-demo-realtime.gif")
            print("✨ This GIF shows natural human interaction with LLOT")
        else:
            print("\n❌ Failed to create GIF")
    else:
        print("\n❌ No screenshots captured")

if __name__ == "__main__":
    main()
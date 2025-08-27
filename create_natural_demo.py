#!/usr/bin/env python3

import os
import time
import subprocess
import json
from datetime import datetime

def take_window_screenshot(window_title="", filename="", description=""):
    """Take a screenshot of a specific window or full screen"""
    print(f"📸 {description}")
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    # Use macOS screencapture for full screen (will crop later)
    cmd = ["screencapture", "-x", "-t", "png", filename]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Screenshot: {filename}")
        return True
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return False

def simulate_browser_interaction():
    """Simulate natural browser interactions using AppleScript"""
    
    # AppleScript to interact with browser
    def click_at_position(x, y, description=""):
        script = f'''
        tell application "System Events"
            -- Click at coordinates {x}, {y}
            click at {{{x}, {y}}}
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            print(f"🖱️ {description}")
            return True
        except:
            return False
    
    def type_text_slowly(text, delay=0.1):
        """Type text with natural human delays"""
        for char in text:
            script = f'''
            tell application "System Events"
                keystroke "{char}"
            end tell
            '''
            try:
                subprocess.run(["osascript", "-e", script], check=True)
                time.sleep(delay)  # Natural typing delay
            except:
                pass
        print(f"⌨️ Typed: {text}")
    
    def press_key(key):
        """Press a specific key"""
        script = f'''
        tell application "System Events"
            key code {key}
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        except:
            return False
    
    return click_at_position, type_text_slowly, press_key

def create_natural_demo():
    """Create a natural demo by automating browser interactions"""
    
    output_dir = "docs/natural_demo"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎬 Creating natural LLOT demo...")
    print("📝 Make sure:")
    print("   1. Browser is open to http://localhost:8082/modern")
    print("   2. Browser window is visible and active")
    print("   3. You won't move the mouse during recording")
    print()
    
    input("Press Enter when ready to start automated demo...")
    
    click_at, type_slowly, press_key = simulate_browser_interaction()
    screenshots = []
    
    def capture_and_wait(filename, description, wait_time=2):
        """Capture screenshot and wait"""
        if take_window_screenshot(filename=filename, description=description):
            screenshots.append((filename, description))
        time.sleep(wait_time)
        return filename
    
    step = 0
    
    def demo_step(action_func, description, wait_before=1, wait_after=2):
        """Execute a demo step with natural timing"""
        nonlocal step
        step += 1
        
        time.sleep(wait_before)  # Natural pause before action
        
        # Take screenshot before action
        before_file = f"{output_dir}/step_{step:03d}_before.png"
        capture_and_wait(before_file, f"Before: {description}", 0.5)
        
        # Perform action
        if action_func:
            action_func()
        
        # Take screenshot after action
        after_file = f"{output_dir}/step_{step:03d}_after.png"
        capture_and_wait(after_file, f"After: {description}", wait_after)
        
        return before_file, after_file
    
    # Demo sequence with natural human-like timing
    print("🚀 Starting natural demo sequence...")
    
    # Initial state
    capture_and_wait(f"{output_dir}/initial.png", "Initial LLOT interface", 2)
    
    # Click on source language dropdown
    demo_step(
        lambda: click_at(486, 145),  # Approximate coordinates for source lang dropdown
        "Click source language dropdown",
        1, 2
    )
    
    # Select French
    demo_step(
        lambda: click_at(486, 200),  # Approximate coordinates for French option
        "Select French language",
        1, 2
    )
    
    # Click in text area
    demo_step(
        lambda: click_at(300, 300),  # Approximate coordinates for text area
        "Click in text input area",
        1, 1
    )
    
    # Type "Bonjour!" slowly
    demo_step(
        lambda: type_slowly("Bonjour!", 0.15),
        "Type 'Bonjour!' naturally",
        0.5, 3  # Wait longer for translation
    )
    
    # Add more text
    demo_step(
        lambda: type_slowly(" Comment allez-vous aujourd'hui?", 0.12),
        "Add more French text",
        1, 3
    )
    
    # Change target language
    demo_step(
        lambda: click_at(700, 145),  # Target language dropdown
        "Click target language dropdown",
        2, 1
    )
    
    # Select Spanish
    demo_step(
        lambda: click_at(700, 180),  # Spanish option
        "Select Spanish as target",
        1, 3
    )
    
    # Open options menu
    demo_step(
        lambda: click_at(750, 200),  # Options menu
        "Open translation options",
        2, 1
    )
    
    # Select formal tone
    demo_step(
        lambda: click_at(750, 250),  # Formal tone option
        "Select formal tone",
        1, 3
    )
    
    # Toggle dark mode
    demo_step(
        lambda: click_at(800, 60),  # Theme toggle
        "Toggle dark mode",
        2, 2
    )
    
    # Toggle back to light
    demo_step(
        lambda: click_at(800, 60),  # Theme toggle again
        "Return to light mode",
        2, 2
    )
    
    # Final state
    capture_and_wait(f"{output_dir}/final.png", "Final demo state", 3)
    
    print(f"✅ Captured {len(screenshots)} screenshots")
    return screenshots

def create_natural_gif(screenshots):
    """Create GIF with natural timing from screenshots"""
    
    if not screenshots:
        return False
    
    print("🎞️ Creating natural GIF...")
    
    cmd = ["magick"]
    
    for filename, description in screenshots:
        # Natural human timing based on action
        if "before" in filename.lower():
            delay = "50"   # Quick preview
        elif "typing" in description.lower() or "type" in description.lower():
            delay = "200"  # Watch typing
        elif "translation" in description.lower() or "after" in filename.lower():
            delay = "180"  # See results
        elif "click" in description.lower():
            delay = "120"  # UI interaction
        else:
            delay = "150"  # Default
        
        cmd.extend(["-delay", delay, filename])
    
    output_file = "docs/images/llot-demo-natural.gif"
    cmd.extend([
        "-loop", "0",
        "-layers", "optimize",
        "-colors", "128",  # Smaller file
        "-resize", "1000x600>",  # Reasonable size
        output_file
    ])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print(f"✅ Natural GIF: {output_file}")
            print(f"📦 Size: {file_size // 1024} KB")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Create natural demo"""
    
    # Simple approach - just use the morphed GIF but make it faster
    print("🎬 Making morphed GIF faster...")
    
    # Faster version of existing morphed GIF - skip some frames and reduce delays
    cmd = [
        "magick", "docs/images/llot-demo-morphed.gif",
        "-coalesce",  # Convert to individual frames
        "-delete", "1-3,5-7,9-11,13-15,17-19",  # Remove some interpolated frames
        "-delay", "60",  # Faster - 0.6s per frame
        "-loop", "0",
        "-layers", "optimize",
        "docs/images/llot-demo-morphed-fast.gif"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            file_size = os.path.getsize("docs/images/llot-demo-morphed-fast.gif")
            print(f"✅ Fast morphed GIF created!")
            print(f"📦 Size: {file_size // 1024} KB")
            print("🚀 This version is faster while keeping smooth morphing")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
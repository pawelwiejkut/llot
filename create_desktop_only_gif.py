#!/usr/bin/env python3

import os
import subprocess
import shutil
import cv2
import numpy as np

def create_desktop_only_morphed_gif():
    """Create morphed GIF excluding mobile frames"""
    
    input_dir = "docs/demo_frames"
    output_dir = "docs/desktop_morphing_frames"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all frame files and filter out mobile frames
    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    
    # Remove mobile frame (frame_019 has dimensions 500x528)
    desktop_frames = []
    for frame_file in frame_files:
        frame_path = os.path.join(input_dir, frame_file)
        
        # Check frame dimensions
        img = cv2.imread(frame_path)
        if img is not None:
            height, width = img.shape[:2]
            
            # Skip mobile/tablet frames (smaller than desktop)
            if width >= 1000 and height >= 600:  # Desktop frames
                desktop_frames.append(frame_file)
                print(f"✅ Including desktop frame: {frame_file} ({width}x{height})")
            else:
                print(f"❌ Skipping mobile frame: {frame_file} ({width}x{height})")
    
    if len(desktop_frames) < 2:
        print("❌ Need at least 2 desktop frames for morphing")
        return False
    
    print(f"📱 Processing {len(desktop_frames)} desktop frames...")
    
    morphed_count = 0
    
    for i in range(len(desktop_frames) - 1):
        current_path = os.path.join(input_dir, desktop_frames[i])
        next_path = os.path.join(input_dir, desktop_frames[i + 1])
        
        current = cv2.imread(current_path)
        next_frame = cv2.imread(next_path)
        
        if current is None or next_frame is None:
            continue
        
        # Ensure both frames have same dimensions
        if current.shape != next_frame.shape:
            next_frame = cv2.resize(next_frame, (current.shape[1], current.shape[0]))
        
        # Save original frame
        morphed_count += 1
        cv2.imwrite(f"{output_dir}/desktop_{morphed_count:04d}.png", current)
        
        # Create 6 morphing steps for smooth transition
        for step in range(1, 7):
            t = step / 7.0
            
            # Ease-in-out function for natural motion
            smooth_t = t * t * (3.0 - 2.0 * t)
            
            # Advanced blending with gamma correction
            gamma = 2.2
            current_linear = np.power(current.astype(np.float32) / 255.0, gamma)
            next_linear = np.power(next_frame.astype(np.float32) / 255.0, gamma)
            
            blended_linear = (1 - smooth_t) * current_linear + smooth_t * next_linear
            blended = np.power(blended_linear, 1/gamma) * 255.0
            blended = blended.astype(np.uint8)
            
            morphed_count += 1
            cv2.imwrite(f"{output_dir}/desktop_{morphed_count:04d}.png", blended)
    
    # Add final frame
    final = cv2.imread(os.path.join(input_dir, desktop_frames[-1]))
    if final is not None:
        morphed_count += 1
        cv2.imwrite(f"{output_dir}/desktop_{morphed_count:04d}.png", final)
    
    print(f"✅ Created {morphed_count} desktop morphed frames")
    
    # Create optimized GIF
    return create_desktop_gif(output_dir, morphed_count)

def create_desktop_gif(input_dir, frame_count):
    """Create optimized desktop-only GIF"""
    
    output_file = "docs/images/llot-demo-desktop-only.gif"
    
    print(f"🎞️ Creating desktop-only GIF with {frame_count} frames...")
    
    cmd = [
        "magick",
        "-delay", "80",  # 0.8s per frame - good speed
        f"{input_dir}/desktop_*.png",
        "-loop", "0",
        "-layers", "optimize-transparency",
        "-colors", "192",  # Good quality
        "-ordered-dither", "o4x4,4",
        "-resize", "1100x650>",  # Reasonable size
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print(f"✅ Desktop-only GIF created: {output_file}")
            print(f"📦 File size: {file_size // 1024} KB")
            print("🖥️ Desktop frames only - no mobile/tablet inconsistencies")
            return True
        else:
            print(f"❌ ImageMagick error: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Create desktop-only morphed GIF"""
    
    print("🖥️ Creating desktop-only morphed GIF...")
    print("📱 This will exclude mobile/tablet frames with inconsistent dimensions")
    print()
    
    try:
        import cv2
    except ImportError:
        print("❌ OpenCV not found. Installing...")
        subprocess.run(["pip3", "install", "--user", "opencv-python"], check=True)
        import cv2
    
    success = create_desktop_only_morphed_gif()
    
    if success:
        print("\n🎉 Desktop-only demo completed!")
        print("📁 Output: docs/images/llot-demo-desktop-only.gif")
        print("✨ Smooth morphing with consistent desktop frames only")
    else:
        print("\n❌ Failed to create desktop GIF")

if __name__ == "__main__":
    main()
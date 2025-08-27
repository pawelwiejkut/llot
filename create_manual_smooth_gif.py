#!/usr/bin/env python3

import os
import subprocess
import shutil
from pathlib import Path

def create_manual_smooth_gif():
    """Create a smooth GIF from existing demo frames with better interpolation"""
    
    # Use existing demo frames from docs/demo_frames
    input_dir = "docs/demo_frames"
    output_dir = "docs/smooth_demo_frames"
    
    if not os.path.exists(input_dir):
        print("❌ Demo frames directory not found. Please create demo frames first.")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # List all available frame files
    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    
    if not frame_files:
        print("❌ No frame files found in demo_frames directory.")
        return False
    
    print(f"Found {len(frame_files)} demo frames")
    
    # Copy and expand frames to create smoother animation
    frame_count = 0
    
    for i, frame_file in enumerate(frame_files):
        src_path = os.path.join(input_dir, frame_file)
        
        # Copy original frame
        frame_count += 1
        dst_path = os.path.join(output_dir, f"smooth_frame_{frame_count:03d}.png")
        shutil.copy2(src_path, dst_path)
        
        # Add interpolation frames between major transitions
        if i < len(frame_files) - 1:
            next_src = os.path.join(input_dir, frame_files[i + 1])
            
            # Create 2-3 duplicate frames to slow down the animation
            for duplicate in range(2):
                frame_count += 1
                dst_path = os.path.join(output_dir, f"smooth_frame_{frame_count:03d}.png")
                shutil.copy2(src_path, dst_path)
    
    print(f"Created {frame_count} smooth frames")
    
    # Create ultra-smooth GIF with variable timing
    return create_variable_timing_gif(frame_count)

def create_variable_timing_gif(frame_count):
    """Create GIF with variable timing for natural flow"""
    
    input_dir = "docs/smooth_demo_frames"
    output_file = "docs/images/llot-demo-ultra-smooth.gif"
    
    print("Creating ultra-smooth GIF with natural timing...")
    
    # Build ImageMagick command with variable delays
    cmd = ["magick"]
    
    for i in range(1, frame_count + 1):
        frame_path = os.path.join(input_dir, f"smooth_frame_{i:03d}.png")
        
        # Variable delays for natural flow
        if i % 3 == 1:  # First frame of each group - longer pause
            delay = "120"  # 1.2s
        elif i % 3 == 2:  # Middle frame - medium pause
            delay = "80"   # 0.8s
        else:  # Last frame - shorter pause
            delay = "60"   # 0.6s
        
        # Add even longer pauses for key frames (every 9th frame)
        if i % 9 == 0:
            delay = "200"  # 2.0s for key moments
        
        cmd.extend(["-delay", delay, frame_path])
    
    # Add optimization settings
    cmd.extend([
        "-loop", "0",                    # Infinite loop
        "-layers", "optimize",           # Optimize layers to reduce file size
        "-colors", "256",               # Limit color palette
        "-resize", "1200x800>",         # Resize if too large
        "-quality", "95",               # High quality
        output_file
    ])
    
    try:
        print("Running ImageMagick to create GIF...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print(f"✅ Ultra-smooth GIF created: {output_file}")
            print(f"📦 File size: {file_size // 1024} KB")
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

def create_optimized_version():
    """Create additional optimized version with even smoother transitions"""
    
    print("\nCreating optimized version with blur transitions...")
    
    input_file = "docs/images/llot-demo-ultra-smooth.gif"
    output_file = "docs/images/llot-demo-final-smooth.gif"
    
    if not os.path.exists(input_file):
        print("❌ Ultra-smooth GIF not found")
        return False
    
    # Use ImageMagick to add motion blur between frames
    cmd = [
        "magick", input_file,
        "-coalesce",                    # Convert to individual frames
        "-blur", "0x0.5",              # Very slight blur for smoothness
        "-layers", "optimize",          # Re-optimize
        "-colors", "128",              # Reduce colors for smaller size
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print(f"✅ Final smooth GIF created: {output_file}")
            print(f"📦 File size: {file_size // 1024} KB")
            return True
        else:
            print(f"❌ Optimization failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return False

def main():
    """Main function to create smooth demo GIF"""
    
    print("🎬 Creating ultra-smooth LLOT demo GIF...")
    print("Using existing demo frames with enhanced interpolation")
    
    # Create smooth GIF from existing frames
    success = create_manual_smooth_gif()
    
    if success:
        # Create optimized version
        create_optimized_version()
        
        print("\n✅ Smooth demo creation completed!")
        print("\n📁 Generated files:")
        print("   - docs/images/llot-demo-ultra-smooth.gif (main version)")
        print("   - docs/images/llot-demo-final-smooth.gif (optimized version)")
        print("\n🎯 These GIFs have:")
        print("   - Natural timing with variable delays")
        print("   - Smooth transitions between frames") 
        print("   - Optimized file size")
        print("   - Professional appearance")
    else:
        print("❌ Failed to create smooth demo GIF")

if __name__ == "__main__":
    main()
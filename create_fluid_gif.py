#!/usr/bin/env python3

import os
import subprocess
import cv2
import numpy as np
from pathlib import Path

def create_interpolated_frames():
    """Use OpenCV to create smooth interpolated frames between existing ones"""
    
    input_dir = "docs/demo_frames"
    output_dir = "docs/fluid_frames"
    
    if not os.path.exists(input_dir):
        print("❌ Demo frames directory not found")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all frame files
    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    
    if len(frame_files) < 2:
        print("❌ Need at least 2 frames for interpolation")
        return False
    
    print(f"Creating fluid animation from {len(frame_files)} frames...")
    
    interpolated_count = 0
    
    for i in range(len(frame_files) - 1):
        # Load current and next frame
        current_path = os.path.join(input_dir, frame_files[i])
        next_path = os.path.join(input_dir, frame_files[i + 1])
        
        current_frame = cv2.imread(current_path)
        next_frame = cv2.imread(next_path)
        
        if current_frame is None or next_frame is None:
            continue
        
        # Add original frame
        interpolated_count += 1
        output_path = os.path.join(output_dir, f"fluid_{interpolated_count:04d}.png")
        cv2.imwrite(output_path, current_frame)
        
        # Ensure both frames have same dimensions
        if current_frame.shape != next_frame.shape:
            # Resize next frame to match current frame
            next_frame = cv2.resize(next_frame, (current_frame.shape[1], current_frame.shape[0]))
        
        # Create 4 interpolated frames between current and next
        for step in range(1, 5):
            alpha = step / 5.0
            
            # Morphing/blending between frames
            blended = cv2.addWeighted(current_frame, 1-alpha, next_frame, alpha, 0)
            
            interpolated_count += 1
            output_path = os.path.join(output_dir, f"fluid_{interpolated_count:04d}.png")
            cv2.imwrite(output_path, blended)
    
    # Add final frame
    final_frame = cv2.imread(os.path.join(input_dir, frame_files[-1]))
    if final_frame is not None:
        interpolated_count += 1
        output_path = os.path.join(output_dir, f"fluid_{interpolated_count:04d}.png")
        cv2.imwrite(output_path, final_frame)
    
    print(f"✅ Created {interpolated_count} interpolated frames")
    return interpolated_count

def create_video_first_approach(frame_count):
    """Create smooth MP4 first, then convert to high-quality GIF"""
    
    input_dir = "docs/fluid_frames"
    video_file = "docs/temp_demo.mp4"
    gif_file = "docs/images/llot-demo-fluid.gif"
    
    print("Creating smooth MP4 video first...")
    
    # Create MP4 with high frame rate for smoothness
    ffmpeg_cmd = [
        "ffmpeg", "-y",  # Overwrite output
        "-framerate", "12",  # 12 FPS for smooth motion
        "-i", f"{input_dir}/fluid_%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",  # High quality
        video_file
    ]
    
    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
        
        print("✅ MP4 created successfully")
    except Exception as e:
        print(f"❌ Error creating MP4: {e}")
        return False
    
    # Convert MP4 to high-quality GIF with dithering
    print("Converting to high-quality GIF...")
    
    gif_cmd = [
        "ffmpeg", "-y",
        "-i", video_file,
        "-vf", "fps=10,scale=1200:-1:flags=lanczos,palettegen",
        "docs/temp_palette.png"
    ]
    
    try:
        subprocess.run(gif_cmd, capture_output=True, text=True, timeout=60)
        
        # Use palette for better quality GIF
        final_gif_cmd = [
            "ffmpeg", "-y",
            "-i", video_file,
            "-i", "docs/temp_palette.png",
            "-filter_complex", "fps=10,scale=1200:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5",
            gif_file
        ]
        
        result = subprocess.run(final_gif_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            file_size = os.path.getsize(gif_file)
            print(f"✅ Fluid GIF created: {gif_file}")
            print(f"📦 File size: {file_size // 1024} KB")
            
            # Cleanup temp files
            for temp_file in [video_file, "docs/temp_palette.png"]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return True
        else:
            print(f"❌ GIF conversion error: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error in GIF conversion: {e}")
        return False

def create_morphing_gif():
    """Advanced morphing technique for ultra-smooth transitions"""
    
    print("Creating morphing-based smooth GIF...")
    
    input_dir = "docs/demo_frames"
    output_dir = "docs/morphing_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    
    if len(frame_files) < 2:
        return False
    
    morphed_count = 0
    
    # Use more sophisticated morphing
    for i in range(len(frame_files) - 1):
        current_path = os.path.join(input_dir, frame_files[i])
        next_path = os.path.join(input_dir, frame_files[i + 1])
        
        current = cv2.imread(current_path)
        next_frame = cv2.imread(next_path)
        
        if current is None or next_frame is None:
            continue
        
        # Save original frame
        morphed_count += 1
        cv2.imwrite(f"{output_dir}/morph_{morphed_count:04d}.png", current)
        
        # Ensure both frames have same dimensions
        if current.shape != next_frame.shape:
            next_frame = cv2.resize(next_frame, (current.shape[1], current.shape[0]))
        
        # Create 8 morphing steps for ultra-smooth transition
        for step in range(1, 9):
            t = step / 9.0
            
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
            cv2.imwrite(f"{output_dir}/morph_{morphed_count:04d}.png", blended)
    
    # Add final frame
    final = cv2.imread(os.path.join(input_dir, frame_files[-1]))
    if final is not None:
        morphed_count += 1
        cv2.imwrite(f"{output_dir}/morph_{morphed_count:04d}.png", final)
    
    print(f"✅ Created {morphed_count} morphed frames")
    
    # Convert to smooth GIF using ImageMagick with advanced settings
    return create_advanced_gif(output_dir, morphed_count, "llot-demo-morphed.gif")

def create_advanced_gif(input_dir, frame_count, output_name):
    """Create GIF with advanced ImageMagick techniques"""
    
    output_file = f"docs/images/{output_name}"
    
    print(f"Creating advanced GIF with {frame_count} frames...")
    
    cmd = [
        "magick",
        "-delay", "8",  # 8/100 second = 12.5 FPS
        f"{input_dir}/morph_*.png",
        "-loop", "0",
        "-layers", "optimize-transparency",  # Advanced optimization
        "-colors", "256",
        "-ordered-dither", "o8x8,8",  # Better dithering
        "-resize", "1200x800>",
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print(f"✅ Advanced GIF created: {output_file}")
            print(f"📦 File size: {file_size // 1024} KB")
            return True
        else:
            print(f"❌ Advanced GIF error: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function to create fluid GIF using advanced techniques"""
    
    print("🎬 Creating fluid LLOT demo using advanced techniques...")
    
    # Install opencv if needed
    try:
        import cv2
    except ImportError:
        print("Installing OpenCV...")
        subprocess.run(["pip3", "install", "--user", "opencv-python"], check=True)
        import cv2
    
    # Method 1: Interpolated frames + FFmpeg
    print("\n🔄 Method 1: Creating interpolated frames...")
    frame_count = create_interpolated_frames()
    
    if frame_count > 0:
        print("\n🎥 Converting to fluid GIF via MP4...")
        success1 = create_video_first_approach(frame_count)
    else:
        success1 = False
    
    # Method 2: Advanced morphing
    print("\n🔄 Method 2: Creating morphed frames...")
    success2 = create_morphing_gif()
    
    if success1 or success2:
        print("\n✅ Fluid demo creation completed!")
        
        if success1:
            print("   - docs/images/llot-demo-fluid.gif (FFmpeg method)")
        if success2:
            print("   - docs/images/llot-demo-morphed.gif (Morphing method)")
        
        print("\n🎯 These GIFs feature:")
        print("   - True frame interpolation (not just duplicated frames)")
        print("   - Smooth morphing transitions")  
        print("   - Higher frame rates for fluid motion")
        print("   - Advanced dithering and optimization")
    else:
        print("❌ Failed to create fluid GIFs")

if __name__ == "__main__":
    main()
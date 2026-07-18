import argparse
import sys
import json
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from renderer import render_storyboard_to_video

def main():
    parser = argparse.ArgumentParser(
        description="Compile a structured storyboard JSON file into an MP4 video."
    )
    parser.add_argument(
        "--storyboard", 
        required=True, 
        help="Path to the storyboard JSON file."
    )
    parser.add_argument(
        "--output", 
        default="output.mp4", 
        help="Path to save the compiled MP4 video (default: output.mp4)."
    )
    parser.add_argument(
        "--quality", 
        choices=["low_quality", "medium_quality"], 
        default="low_quality", 
        help="Render quality (low_quality=480p, medium_quality=720p. Default is low_quality for speed)."
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.storyboard):
        print(f"Error: Storyboard file '{args.storyboard}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    try:
        print(f"Reading storyboard from {args.storyboard}...")
        with open(args.storyboard, "r", encoding="utf-8") as f:
            storyboard_data = json.load(f)
            
        print(f"Starting video rendering (quality: {args.quality})...")
        render_storyboard_to_video(
            storyboard_data=storyboard_data,
            output_path=args.output,
            quality=args.quality
        )
        print(f"Success! Video compiled successfully to: {os.path.abspath(args.output)}")
        
    except Exception as e:
        print(f"Error occurred during video rendering: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

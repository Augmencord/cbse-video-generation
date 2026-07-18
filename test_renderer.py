import os
import sys
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from renderer import render_storyboard_to_video

# Use very short durations (3 seconds per scene) to keep test render time extremely fast!
TEST_STORYBOARD = {
  "topic": "Matrices",
  "overall_analogy": "Grid organizer",
  "scenes": [
    {
      "scene_number": 1,
      "title": "Pixel Hook",
      "focus": "application_hook",
      "visual_description": "Pixel grid rotations",
      "narration": "This is a quick hook showing how screens rotate pixels.",
      "estimated_duration_seconds": 3
    },
    {
      "scene_number": 2,
      "title": "Grid Concept",
      "focus": "analogy_concept",
      "visual_description": "Spreadsheet grid container",
      "narration": "Think of it as a spreadsheet grid where items are organized.",
      "estimated_duration_seconds": 3
    },
    {
      "scene_number": 3,
      "title": "Theory Math",
      "focus": "theory_math",
      "visual_description": "Vector rotation on NumberPlane",
      "narration": "In theory, we multiply and shift vectors in the grid.",
      "estimated_duration_seconds": 3
    },
    {
      "scene_number": 4,
      "title": "Wrap Up",
      "focus": "wrap_up",
      "visual_description": "Success checkmark",
      "narration": "Now you know how matrices organize the digital world!",
      "estimated_duration_seconds": 3
    }
  ],
  "total_estimated_duration_seconds": 12
}

def main():
    output_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output.mp4")
    
    # Remove old test file if exists
    if os.path.exists(output_filepath):
        try:
            os.remove(output_filepath)
        except Exception as e:
            print(f"Warning: could not remove old test file: {e}")

    print("--- Starting Render Engine Automated Test ---")
    try:
        render_storyboard_to_video(
            storyboard_data=TEST_STORYBOARD,
            output_path=output_filepath,
            quality="low_quality"
        )
        
        # Verify file creation
        if os.path.exists(output_filepath):
            file_size = os.path.getsize(output_filepath)
            print(f"Test Success! Video file created at: {output_filepath}")
            print(f"File size: {file_size} bytes")
            if file_size > 0:
                print("Verification PASSED!")
                sys.exit(0)
            else:
                print("Verification FAILED: Video file size is 0 bytes.")
                sys.exit(1)
        else:
            print("Verification FAILED: Video file was not created.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Verification FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

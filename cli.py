import argparse
import sys
import json
from generator import generate_storyboard
from config import validate_config

def main():
    parser = argparse.ArgumentParser(
        description="Generate a CBSE Class 12 micro-learning storyboard using Gemini."
    )
    parser.add_argument(
        "--topic", 
        required=True, 
        help="The CBSE Class 12 topic to generate (e.g. 'Capacitors and Capacitance')."
    )
    parser.add_argument(
        "--model", 
        default="gemini-2.5-flash", 
        help="The Gemini model to use (default: gemini-2.5-flash)."
    )
    parser.add_argument(
        "--output", 
        help="Optional file path to save the generated JSON output."
    )
    
    args = parser.parse_args()
    
    # Check config
    validate_config()
    
    print(f"Generating storyboard for: '{args.topic}' using model: '{args.model}'...")
    try:
        storyboard = generate_storyboard(topic=args.topic, model_name=args.model)
        
        # Pretty print the resulting storyboard
        storyboard_json = storyboard.model_dump()
        pretty_json = json.dumps(storyboard_json, indent=2)
        
        print("\n=== GENERATED STORYBOARD ===")
        print(f"Topic: {storyboard.topic}")
        print(f"Overall Analogy: {storyboard.overall_analogy}")
        print(f"Total Estimated Duration: {storyboard.total_estimated_duration_seconds} seconds")
        print("\nScenes:")
        for scene in storyboard.scenes:
            print(f"\n  [Scene {scene.scene_number}] {scene.title} ({scene.estimated_duration_seconds}s) [Focus: {scene.focus}]")
            print(f"  Visuals: {scene.visual_description}")
            print(f"  Narration: {scene.narration}")
            
        print("============================\n")
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(pretty_json)
            print(f"Saved JSON storyboard to {args.output}")
            
    except Exception as e:
        print(f"Error occurred during generation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

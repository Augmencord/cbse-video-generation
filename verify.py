import sys
import os
import json
from pydantic import ValidationError

# Add current directory to path so we can import from files directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import GEMINI_API_KEY
from schemas import Storyboard, Scene
from generator import generate_storyboard

# Sample mock JSON that simulates what Gemini should return
MOCK_GEMINI_RESPONSE = {
  "topic": "Capacitors and Capacitance",
  "subject": "Physics",
  "chapter": "Electrostatic Potential and Capacitance",
  "overall_analogy": "Comparing a capacitor to a small overhead water storage tank.",
  "scenes": [
    {
      "scene_number": 1,
      "title": "The Touchscreen Tap",
      "focus": "application_hook",
      "visual_description": "Close-up of a human finger pressing an icon on a glowing smartphone screen. Subtly show the glass layer and an electrical field changing as the finger approaches.",
      "narration": "Have you ever wondered how your smartphone knows exactly where your finger touches? It's not magic. It relies on a tiny electrical 'sandwich' called a capacitor, which stores charge and senses the change when your finger gets close.",
      "estimated_duration_seconds": 25
    },
    {
      "scene_number": 2,
      "title": "The Water Tank Analogy",
      "focus": "analogy_concept",
      "visual_description": "An animation comparing an electrical capacitor to a small water tank. Water is pumped in, stored, and then quickly released when a valve is opened.",
      "narration": "Think of a capacitor like a small overhead water tank. It stores water (charge) and releases it when you open the tap. Just as a tank stores water pressure, a capacitor stores electric potential.",
      "estimated_duration_seconds": 35
    },
    {
      "scene_number": 3,
      "title": "The Formula of Capacity",
      "focus": "theory_math",
      "visual_description": "Diagram of two parallel metal plates separated by a gap. The formula C = Q/V appears clearly, showing charge Q accumulating on the plates and voltage V across them.",
      "narration": "Formally, capacitance is the ability to store charge per unit voltage, written as C equals Q over V. In Class 12, we study parallel plates where the capacitance increases with plate size and decreases with plate separation.",
      "estimated_duration_seconds": 40
    },
    {
      "scene_number": 4,
      "title": "Powering the Flash",
      "focus": "wrap_up",
      "visual_description": "Show a camera flash firing brightly. Zoom out to show the circuit board inside the camera where the capacitor dumps its stored energy in a split second.",
      "narration": "So, whether it is sensing your touches or releasing a quick burst of energy for a camera flash, capacitors are the silent power reservoirs of modern electronics. Now you know the whole picture!",
      "estimated_duration_seconds": 30
    }
  ],
  "total_estimated_duration_seconds": 130
}

def verify_storyboard_logic(storyboard: Storyboard) -> bool:
    """Verifies that the storyboard adheres to all our pedagogical and duration constraints."""
    print(f"\n[Verifying Storyboard for Topic: '{storyboard.topic}']")
    
    # 1. Check Scene count (3-5)
    scene_count = len(storyboard.scenes)
    print(f" - Scenes count: {scene_count} (Expected: 3-5)")
    if scene_count < 3 or scene_count > 5:
        print(f"   [FAIL] Scene count {scene_count} is out of bounds [3-5].")
        return False
        
    # 2. Check total duration
    total_duration = sum(s.estimated_duration_seconds for s in storyboard.scenes)
    reported_total = storyboard.total_estimated_duration_seconds
    print(f" - Total duration: calculated={total_duration}s, reported={reported_total}s (Expected: < 180s)")
    if total_duration >= 180:
        print(f"   [FAIL] Calculated total duration ({total_duration}s) exceeds 3-minute cap (180s).")
        return False
    if reported_total != total_duration:
        print(f"   [WARN] Reported total duration ({reported_total}s) does not match sum of scene durations ({total_duration}s).")
        
    # 3. Check Jeremy Howard's Principle: first scene must be application_hook
    first_scene = storyboard.scenes[0]
    print(f" - First scene focus: '{first_scene.focus}' (Expected: 'application_hook')")
    if first_scene.focus != "application_hook":
        print(f"   [FAIL] First scene focus must be 'application_hook'.")
        return False
        
    # 4. Check Jargon and Analogies
    print(f" - Overall analogy defined: '{storyboard.overall_analogy}'")
    if not storyboard.overall_analogy:
        print(f"   [FAIL] Overall analogy must be defined.")
        return False
        
    print(" [PASS] All pedagogical constraints validated successfully!")
    return True

def run_mock_validation():
    print("--- Running Mock Schema and Constraint Validation ---")
    try:
        storyboard = Storyboard.model_validate(MOCK_GEMINI_RESPONSE)
        success = verify_storyboard_logic(storyboard)
        if success:
            print("Mock validation passed successfully!")
            return True
        else:
            print("Mock validation failed constraints checks.")
            return False
    except ValidationError as e:
        print(f"Pydantic Validation Error on mock response: {e}")
        return False

def run_live_test():
    print("--- Running Live Integration Test with Gemini API ---")
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY is not set. Skipping live test.")
        print("Please set the GEMINI_API_KEY environment variable or write it in a .env file to enable live integration testing.")
        return True
        
    test_topic = "Matrices and Determinants"
    print(f"Generating live storyboard for topic: '{test_topic}'...")
    try:
        storyboard = generate_storyboard(test_topic)
        success = verify_storyboard_logic(storyboard)
        if success:
            print("\nLive Integration Test Passed!")
            print("---------------------------")
            print(f"Overall Analogy: {storyboard.overall_analogy}")
            print(f"Total Duration: {storyboard.total_estimated_duration_seconds}s")
            print("---------------------------")
            return True
        else:
            print("Live Integration Test Failed constraints checks.")
            return False
    except Exception as e:
        print(f"Live Integration Test failed with exception: {e}")
        return False

def main():
    mock_ok = run_mock_validation()
    print()
    live_ok = run_live_test()
    
    if mock_ok and live_ok:
        print("\nALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nVERIFICATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()

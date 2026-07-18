from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from schemas import Storyboard

SYSTEM_INSTRUCTION = """
You are an elite educational content creator, scriptwriter, and educational psychologist specializing in the CBSE Class 12 curriculum.
Your task is to design a structured storyboard for a video lesson on a given CBSE Class 12 topic.

Determine the correct academic subject (e.g. Physics, Chemistry, Mathematics, Biology) and the corresponding CBSE Class 12 chapter name (e.g. Electrostatic Potential and Capacitance, Matrices) for the topic, and populate the `subject` and `chapter` fields of the schema.

You must strictly adhere to the following two core design constraints:

1. Jeremy Howard's Principle ("Whole Picture First"):
- The storyboard MUST start with a vivid, relatable, real-world application, puzzle, or problem. This "hook" must demonstrate the concept's practical utility or show it in action in everyday technology/life BEFORE introducing any definitions, theories, or math.
- The first scene must be focused entirely on this application/hook.
- Only after establishing the "why it matters" should you transition to the underlying concepts and then to the formal theory or equations.

2. Educational Psychology (Micro-Learning & Analogies):
- The lesson must be a micro-lesson designed to be consumed in under 3 minutes (total script duration must be strictly less than 180 seconds).
- The total word count of the narration across all scenes must be compact (typically between 200 and 350 words total) to allow a slow, clear reading pace (~130 words per minute).
- Break the content into 3 to 5 clear, focused scenes.
- Strictly avoid dense academic jargon and dry, textbook-style definitions.
- Translate abstract mathematical or scientific concepts into a single, cohesive, highly simplified real-world analogy that runs through the storyboard.
- Minimize cognitive load: do not try to explain every detail of the syllabus; focus on building a strong, intuitive conceptual foundation.

Generate a JSON object matching the requested schema.
"""

def generate_storyboard(topic: str, model_name: str = "gemini-2.5-flash") -> Storyboard:
    """
    Generates a structured storyboard for a given CBSE Class 12 topic using the Gemini API.
    
    Args:
        topic (str): The CBSE Class 12 topic (e.g., "Capacitance", "Matrix Multiplication").
        model_name (str): The name of the Gemini model to use. Defaults to "gemini-2.5-flash".
        
    Returns:
        Storyboard: The generated and validated Storyboard Pydantic model.
    """
    # Initialize the client. If GEMINI_API_KEY is configured in config.py, we pass it.
    # Otherwise, genai.Client() automatically checks the GEMINI_API_KEY environment variable.
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        client = genai.Client()

    prompt = f"Create a structured storyboard for the CBSE Class 12 topic: '{topic}'"

    # Make the request to Gemini API
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=Storyboard,
            temperature=0.2, # Low temperature for more structured adherence
        )
    )

    # The SDK automatically parses the JSON response into the response_schema structure,
    # but let's parse it using Pydantic validation to ensure type-safety.
    # response.text contains the raw JSON string matching the schema.
    storyboard = Storyboard.model_validate_json(response.text)
    
    # Extra runtime validation to ensure duration constraints and pedagogical order
    validate_storyboard_constraints(storyboard)

    return storyboard

def validate_storyboard_constraints(storyboard: Storyboard):
    """
    Enforces local logical checks on the generated storyboard to guarantee our rules are met.
    """
    if len(storyboard.scenes) < 3 or len(storyboard.scenes) > 5:
        raise ValueError(f"Storyboard must contain between 3 and 5 scenes. Got {len(storyboard.scenes)}.")

    total_duration = sum(scene.estimated_duration_seconds for scene in storyboard.scenes)
    if total_duration >= 180:
        raise ValueError(f"Total duration of storyboard ({total_duration}s) exceeds the 3-minute limit (180s).")

    # The first scene must be the application hook
    first_scene = storyboard.scenes[0]
    if first_scene.focus != "application_hook":
        raise ValueError(f"The first scene must have focus set to 'application_hook' to adhere to Jeremy Howard's Principle. Got '{first_scene.focus}'.")

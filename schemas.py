from pydantic import BaseModel, Field
from typing import List, Literal

class Scene(BaseModel):
    scene_number: int = Field(
        ..., 
        description="The sequential number of the scene (starting from 1)."
    )
    title: str = Field(
        ..., 
        description="A short, catchy title for the scene."
    )
    focus: Literal["application_hook", "analogy_concept", "theory_math", "wrap_up"] = Field(
        ..., 
        description="The pedagogical purpose of this scene. Must start with 'application_hook' for the first scene."
    )
    visual_description: str = Field(
        ..., 
        description="Detailed description of the visual scene, graphics, animations, or live action to display. Be specific, vivid, and concrete."
    )
    narration: str = Field(
        ..., 
        description="The spoken script for this scene. Must be written in highly simplified language, avoiding dense academic jargon, using a clear analogy, and keeping sentences short and easy to understand."
    )
    estimated_duration_seconds: int = Field(
        ..., 
        description="The estimated reading duration for the narration script (assuming a standard reading rate of ~130-150 words per minute, e.g. ~2-2.5 words per second). Must be an integer."
    )

class Storyboard(BaseModel):
    topic: str = Field(
        ..., 
        description="The CBSE Class 12 topic being taught."
    )
    subject: str = Field(
        ..., 
        description="The academic subject (e.g. Physics, Chemistry, Mathematics, Biology)."
    )
    chapter: str = Field(
        ..., 
        description="The specific CBSE Class 12 chapter name (e.g. Electrostatic Potential and Capacitance, Matrices)."
    )
    overall_analogy: str = Field(
        ..., 
        description="The primary, simple real-world analogy used to explain the complex technical topic (e.g. comparing electric current to water flow, or a matrix to a spreadsheet)."
    )
    scenes: List[Scene] = Field(
        ..., 
        description="A list of 3 to 5 scenes that build the storyboard sequence."
    )
    total_estimated_duration_seconds: int = Field(
        ..., 
        description="The sum of the estimated_duration_seconds of all scenes. Must be strictly under 180 seconds."
    )

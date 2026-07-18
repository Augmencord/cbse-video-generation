import os
import sys
import tempfile
import textwrap
import shutil

# 1. Dynamically locate FFmpeg using imageio-ffmpeg and add it to PATH
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
    print(f"[FFmpeg Setup] Dynamically added FFmpeg to PATH from: {ffmpeg_dir}")
except ImportError:
    print("[FFmpeg Setup] Warning: imageio-ffmpeg is not installed. Relying on system-wide FFmpeg.", file=sys.stderr)

# 2. Import Manim and MoviePy
from manim import *
from moviepy import VideoFileClip, concatenate_videoclips

# Configure Manim global logging to be less noisy
config.log_to_file = False
config.verbosity = "WARNING"

def slow_into_fast(t: float) -> float:
    """A rate function that starts slowly and accelerates."""
    return t * t

class CBSEStoryboardScene(Scene):
    def __init__(self, scene_data: dict, **kwargs):
        self.scene_data = scene_data
        super().__init__(**kwargs)

    def construct(self):
        # Time tracker for animations
        elapsed_time = 0.0
        total_duration = float(self.scene_data.get("estimated_duration_seconds", 30))

        # --- Title Rendering ---
        title_text = self.scene_data.get("title", f"Scene {self.scene_data.get('scene_number')}")
        title = Text(title_text, font="sans-serif", font_size=32, color=BLUE_B).to_edge(UP, buff=0.5)
        self.play(FadeIn(title), run_time=1.0)
        elapsed_time += 1.0

        # --- Subtitle Narration Rendering ---
        narration_text = self.scene_data.get("narration", "")
        # Wrap text at 55 characters to fit on screen
        wrapped_narration = "\n".join(textwrap.wrap(narration_text, width=55))
        subtitles_lbl = Text(wrapped_narration, font="sans-serif", font_size=20, color=WHITE, line_spacing=1.3)
        
        # Translucent background card for subtitles
        subtitle_box = SurroundingRectangle(
            subtitles_lbl, 
            color=GRAY_A, 
            fill_color=BLACK, 
            fill_opacity=0.7, 
            buff=0.4, 
            corner_radius=0.15
        )
        subtitles_group = VGroup(subtitle_box, subtitles_lbl).to_edge(DOWN, buff=0.6)
        
        # Write animation for narration text
        write_time = min(4.0, max(2.0, total_duration * 0.3))
        self.play(FadeIn(subtitle_box), Write(subtitles_lbl, run_time=write_time))
        elapsed_time += write_time

        # --- Geometric Animations based on Scene Focus ---
        focus = self.scene_data.get("focus", "application_hook")
        animation_duration = 0.0

        # Visual elements center group
        visual_group = VGroup()

        if focus == "application_hook":
            # 1. Hook: Concentric expanding radar rings (interaction/pulse)
            dot = Dot(color=PINK).scale(2).move_to(ORIGIN)
            self.play(FadeIn(dot), run_time=1.0)
            animation_duration += 1.0
            visual_group.add(dot)

            # Play expanding rings
            for _ in range(2):
                ring1 = Circle(radius=0.2, color=PINK).move_to(ORIGIN)
                ring2 = Circle(radius=0.2, color=PINK).move_to(ORIGIN)
                self.play(
                    ring1.animate.scale(15).set_stroke(opacity=0),
                    ring2.animate.scale(25).set_stroke(opacity=0),
                    run_time=2.5,
                    rate_func=slow_into_fast
                )
                animation_duration += 2.5
                self.remove(ring1, ring2)

        elif focus == "analogy_concept":
            # 2. Concept Analogy: Cylinder/Rectangle filling up (container/tank storing things)
            tank = Rectangle(width=2.2, height=3.2, color=WHITE, stroke_width=4).move_to(ORIGIN)
            water = Rectangle(width=2.1, height=0.1, color=BLUE_D, fill_color=BLUE_D, fill_opacity=0.8, stroke_width=0)
            water.align_to(tank, DOWN).shift(UP * 0.05)

            self.play(Create(tank), run_time=1.0)
            self.play(FadeIn(water), run_time=0.5)
            animation_duration += 1.5
            visual_group.add(tank, water)

            # Grow the water/storage level
            self.play(
                water.animate.stretch_to_fit_height(3.1, about_edge=DOWN),
                run_time=4.0
            )
            animation_duration += 4.0

        elif focus == "theory_math":
            # 3. Mathematical Theory: Rotating and transforming coordinate system
            grid = NumberPlane(
                x_range=[-4, 4, 1], 
                y_range=[-3, 3, 1], 
                background_line_style={"stroke_color": GRAY_C, "stroke_opacity": 0.4}
            )
            vector = Arrow(start=ORIGIN, end=[2, 1, 0], color=YELLOW, buff=0)
            
            self.play(Create(grid), run_time=1.5)
            self.play(GrowArrow(vector), run_time=1.0)
            animation_duration += 2.5
            visual_group.add(grid, vector)

            # Rotate and stretch the vector
            self.play(
                Rotate(vector, angle=PI/2, about_point=ORIGIN),
                run_time=2.5
            )
            self.play(vector.animate.scale(1.4), run_time=1.5)
            animation_duration += 4.0

        elif focus == "wrap_up":
            # 4. Wrap Up: Glowing checkmark inside a growing circle
            success_circle = Circle(radius=1.3, color=GREEN, stroke_width=6).move_to(ORIGIN)
            checkmark = VMobject(color=GREEN, stroke_width=8)
            checkmark.set_points_as_corners([
                [-0.5, -0.15, 0],
                [-0.1, -0.6, 0],
                [0.6, 0.35, 0]
            ])
            
            self.play(Create(success_circle), run_time=1.0)
            self.play(Create(checkmark), run_time=1.5)
            animation_duration += 2.5
            visual_group.add(success_circle, checkmark)

            # Quick pop zoom
            self.play(
                success_circle.animate.scale(1.2),
                checkmark.animate.scale(1.2),
                rate_func=there_and_back,
                run_time=1.5
            )
            animation_duration += 1.5

        elapsed_time += animation_duration

        # Clean up visual group
        if visual_group:
            self.play(FadeOut(visual_group), run_time=1.0)
            elapsed_time += 1.0

        # Wait out the rest of the duration to meet constraints exactly
        remaining_time = total_duration - elapsed_time
        if remaining_time > 0:
            self.wait(remaining_time)

def render_storyboard_to_video(storyboard_data: dict, output_path: str, quality: str = "low_quality"):
    """
    Renders a JSON storyboard into an MP4 video.
    
    Args:
        storyboard_data (dict): The parsed storyboard JSON object.
        output_path (str): The file path where the final MP4 will be saved.
        quality (str): Render quality ('low_quality' = 480p, 'medium_quality' = 720p).
    """
    scenes = storyboard_data.get("scenes", [])
    if not scenes:
        raise ValueError("Storyboard contains no scenes.")

    # Create temporary directories for individual scene renders
    temp_dir = tempfile.mkdtemp(prefix="cbse_render_")
    rendered_clips = []
    
    try:
        print(f"[Renderer] Rendering {len(scenes)} scenes in temporary folder: {temp_dir}")
        for idx, scene_data in enumerate(scenes):
            scene_num = scene_data.get("scene_number", idx + 1)
            filename = f"scene_{scene_num}"
            
            print(f"[Renderer] Rendering Scene {scene_num}/{len(scenes)}: '{scene_data.get('title')}'")
            
            # Run Manim renderer programmatically for this scene
            with tempconfig({
                "quality": quality,
                "write_to_movie": True,
                "preview": False,
                "output_file": filename,
                "media_dir": temp_dir,
                "video_dir": temp_dir,
            }):
                scene = CBSEStoryboardScene(scene_data=scene_data)
                scene.render()

            # The exact filepath rendered by Manim depends on quality.
            # Manim structure: temp_dir/videos/scene_name/480p15/filename.mp4 or 720p30/filename.mp4
            # Let's search recursively for the rendered file.
            expected_file = None
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    if f == f"{filename}.mp4":
                        expected_file = os.path.join(root, f)
                        break
                if expected_file:
                    break
            
            if not expected_file or not os.path.exists(expected_file):
                raise FileNotFoundError(f"Failed to find rendered video file for Scene {scene_num}")
            
            rendered_clips.append(expected_file)
            print(f"[Renderer] Successfully rendered Scene {scene_num} to {expected_file}")

        # Assemble the clips together using MoviePy
        print("[Renderer] Assembling scenes with MoviePy...")
        video_clips = [VideoFileClip(clip_path) for clip_path in rendered_clips]
        
        # Concatenate clips
        final_clip = concatenate_videoclips(video_clips, method="compose")
        
        # Ensure output directory exists
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        print(f"[Renderer] Compiling final video to: {output_path}")
        # Write final file. We disable audio since we are not adding TTS voiceover.
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio=False, 
            logger=None # Disable moviepy logging to keep terminal clean
        )
        
        # Close clips to release files
        for clip in video_clips:
            clip.close()
        final_clip.close()
        print("[Renderer] Video compilation complete!")

    finally:
        # Clean up temporary renders directory
        try:
            shutil.rmtree(temp_dir)
            print(f"[Renderer] Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"[Renderer] Warning: Failed to clean up temp dir {temp_dir}: {e}", file=sys.stderr)

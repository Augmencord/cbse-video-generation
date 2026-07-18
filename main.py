from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import re
import os
import json
import shutil
import asyncio

from generator import generate_storyboard
from config import validate_config, OUTPUT_DIR, MEDIA_ROOT
from schemas import Storyboard
from renderer import render_storyboard_to_video

# Validate configuration on startup
validate_config()

app = FastAPI(
    title="CBSE Class 12 Storyboard Generator API",
    description="A microservice that generates educational storyboards and compiles them into Manim/MoviePy videos.",
    version="1.0.0"
)

# Ensure media folder exists and mount it as a static folder for range-request streaming
os.makedirs(MEDIA_ROOT, exist_ok=True)
app.mount("/static/media", StaticFiles(directory=MEDIA_ROOT), name="media")

class StoryboardRequest(BaseModel):
    topic: str = Field(
        ..., 
        description="The CBSE Class 12 topic to generate a storyboard for.",
        examples=["Electromagnetic Induction", "DNA Replication", "Matrix Multiplication"]
    )
    model: str = Field(
        "gemini-2.5-flash", 
        description="The Gemini model to use for generation.",
        examples=["gemini-2.5-flash", "gemini-2.0-flash"]
    )

def sanitize_folder_name(name: str) -> str:
    """Removes characters that are unsafe for directories, keeping spaces and dashes."""
    return re.sub(r'[^a-zA-Z0-9_\-\s]', '', name).strip()

async def watch_output_folder():
    """Background task that monitors OUTPUT_DIR for rendered videos and organizes them."""
    print(f"[Watcher] Starting background file monitor on: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    while True:
        try:
            if not os.path.exists(OUTPUT_DIR):
                await asyncio.sleep(2.0)
                continue
                
            for file_name in os.listdir(OUTPUT_DIR):
                if file_name.endswith(".mp4"):
                    video_path = os.path.join(OUTPUT_DIR, file_name)
                    base_name = os.path.splitext(file_name)[0]
                    meta_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")
                    
                    # Process only if both the video and its sidecar metadata exist
                    if os.path.exists(meta_path):
                        # Ensure the file is fully written (size hasn't changed for 1 second)
                        try:
                            initial_size = os.path.getsize(video_path)
                            await asyncio.sleep(1.0)
                            current_size = os.path.getsize(video_path)
                            if initial_size != current_size or current_size == 0:
                                continue  # Video is still writing
                        except OSError:
                            continue  # File locked
                        
                        # Read the metadata and move files to structured directory
                        try:
                            with open(meta_path, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                            
                            subject = sanitize_folder_name(meta.get("subject", "Uncategorized"))
                            chapter = sanitize_folder_name(meta.get("chapter", "Uncategorized"))
                            
                            dest_dir = os.path.join(MEDIA_ROOT, subject, chapter)
                            os.makedirs(dest_dir, exist_ok=True)
                            
                            dest_video_path = os.path.join(dest_dir, file_name)
                            dest_meta_path = os.path.join(dest_dir, f"{base_name}.json")
                            
                            # Clean old files if present
                            if os.path.exists(dest_video_path):
                                os.remove(dest_video_path)
                            if os.path.exists(dest_meta_path):
                                os.remove(dest_meta_path)
                                
                            shutil.move(video_path, dest_video_path)
                            shutil.move(meta_path, dest_meta_path)
                            print(f"[Watcher] Successfully organized video: {file_name} -> {dest_video_path}")
                        except Exception as e:
                            print(f"[Watcher] Error organizing file {file_name}: {e}")
        except Exception as err:
            print(f"[Watcher] Critical error in watcher loop: {err}")
            
        await asyncio.sleep(2.0)

@app.on_event("startup")
def startup_event():
    asyncio.create_task(watch_output_folder())

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "CBSE Storyboard Generator",
        "docs": "/docs"
    }

def trigger_video_render(storyboard: Storyboard):
    """Compiles the storyboard into a video and creates the JSON sidecar metadata."""
    try:
        # Generate safe filename from topic
        safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '_', storyboard.topic.lower())
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        output_filename = f"storyboard_{safe_topic}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        print(f"[Renderer] Starting render for topic '{storyboard.topic}' to: {output_path}")
        render_storyboard_to_video(
            storyboard_data=storyboard.model_dump(),
            output_path=output_path,
            quality="low_quality"
        )
        
        # Write sidecar JSON file for the file monitoring pipeline AFTER successful render
        meta_filename = f"storyboard_{safe_topic}.json"
        meta_path = os.path.join(OUTPUT_DIR, meta_filename)
        meta_data = {
            "subject": storyboard.subject,
            "chapter": storyboard.chapter,
            "topic": storyboard.topic,
            "video_filename": output_filename
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)
            
        print(f"[Renderer] Wrote sidecar metadata to: {meta_path}")
        return output_path, output_filename
    except Exception as e:
        print(f"[Renderer] Error rendering video for '{storyboard.topic}': {e}")
        raise e

@app.post("/api/storyboard")
def create_storyboard(request: StoryboardRequest, background_tasks: BackgroundTasks):
    try:
        storyboard = generate_storyboard(topic=request.topic, model_name=request.model)
        # Queue the video rendering to run in the background
        background_tasks.add_task(trigger_video_render, storyboard)
        return storyboard
    except ValueError as val_err:
        raise HTTPException(
            status_code=422,
            detail=f"Storyboard constraints validation failed: {str(val_err)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate storyboard: {str(e)}"
        )

@app.post("/api/render")
def render_video(storyboard: Storyboard):
    try:
        output_path, output_filename = trigger_video_render(storyboard)
        return {
            "status": "success",
            "message": "Video successfully rendered and queued for organization",
            "file_path": output_path,
            "filename": output_filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render video: {str(e)}"
        )

@app.get("/api/videos")
def list_videos():
    """Lists all successfully organized educational videos in the media root."""
    videos_list = []
    if os.path.exists(MEDIA_ROOT):
        for root, dirs, files in os.walk(MEDIA_ROOT):
            for file in files:
                if file.endswith(".mp4"):
                    base_name = os.path.splitext(file)[0]
                    json_file = f"{base_name}.json"
                    json_path = os.path.join(root, json_file)
                    
                    # Reconstruct path and stream URL (normalized for URLs)
                    rel_path = os.path.relpath(os.path.join(root, file), MEDIA_ROOT)
                    url_path = rel_path.replace(os.sep, "/")
                    stream_url = f"/static/media/{url_path}"
                    
                    subject = "Unknown"
                    chapter = "Unknown"
                    topic = base_name.replace("storyboard_", "").replace("_", " ").title()
                    
                    if os.path.exists(json_path):
                        try:
                            with open(json_path, "r", encoding="utf-8") as jf:
                                meta = json.load(jf)
                                subject = meta.get("subject", subject)
                                chapter = meta.get("chapter", chapter)
                                topic = meta.get("topic", topic)
                        except Exception:
                            pass
                    else:
                        rel_dir = os.path.relpath(root, MEDIA_ROOT)
                        parts = rel_dir.split(os.sep)
                        if len(parts) >= 2:
                            subject = parts[0]
                            chapter = parts[1]
                            
                    videos_list.append({
                        "subject": subject,
                        "chapter": chapter,
                        "topic": topic,
                        "filename": file,
                        "stream_url": stream_url
                    })
    return videos_list

# CBSE Class 12 Storyboard Generator & Video Compiler

An AI-powered microservice that automatically generates structured CBSE Class 12 educational storyboards and compiles them into animated videos. Powered by **Gemini 2.5 Flash (via the google-genai SDK)**, **Manim**, **MoviePy**, and **FastAPI**.

---

## 🌟 Key Features

* **Pedagogy-First Scriptwriting**: Incorporates *Jeremy Howard's Principle ("Whole Picture First")* by starting each topic with a real-world application/hook before introducing formal theories or math.
* **Micro-Learning Design**: Constrains video scripts to a clear reading pace (~130 words per minute) spanning 3 to 5 scenes, keeping the total duration strictly under 3 minutes (180 seconds).
* **Structured Output Validation**: Utilizes Pydantic schemas to validate JSON structures returned by Gemini, enforcing academic subject and chapter alignment automatically.
* **Dynamic Video Assembly**: Translates visual storyboard cues into dynamic animations programmatically using **Manim** and compiles them using **MoviePy**.
* **Asynchronous Folder Watcher**: Automatically monitors background video compiler outputs, organizing rendered `.mp4` and sidecar metadata JSONs into structured directory folders: `/media/cbse12/{Subject}/{Chapter}/`.

---

## 📁 Project Structure

* `main.py` - The FastAPI application containing endpoints for storyboard generation, manual video triggering, video listing, and the asynchronous file watcher.
* `generator.py` - Sets up the Gemini API client using `google-genai` and defines prompt templates and structured output schemas.
* `renderer.py` - Programmatic Manim visual engine mapping scene focuses (`application_hook`, `analogy_concept`, `theory_math`, `wrap_up`) to visual animations.
* `render_video.py` - A utility CLI script to render a JSON storyboard into an MP4 file.
* `schemas.py` - Pydantic definitions for `Storyboard` and `Scene` validation.
* `verify.py` - A testing suite running mock data checks and live API integration tests.
* `config.py` - Project environment variables and directory setups.
* `requirements.txt` - Python package dependencies list.

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** and **FFmpeg** installed. (Note: The project uses `imageio-ffmpeg` to automatically detect FFmpeg, which resolves path issues in virtual environments).

### 2. Install Dependencies
Create a virtual environment and install the required libraries:

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\activate.ps1

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure the Environment
Create a `.env` file in the root of the project and add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 💻 How to Run

### Run the Validation Tests
You can run the built-in mock validation and live API integration checks with:
```bash
python verify.py
```

### Start the FastAPI Server
Launch the server using Uvicorn:
```bash
uvicorn main:app --reload
```
Once running, you can explore the interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Compile a Video via the CLI
If you already have a generated storyboard JSON, compile it manually using:
```bash
python render_video.py --storyboard path/to/storyboard.json --output output.mp4 --quality low_quality
```
*(Options for `--quality` are `low_quality` [480p] or `medium_quality` [720p]).*
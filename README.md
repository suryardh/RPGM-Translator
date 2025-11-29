# RPG Maker AI Translator

A full-stack application designed to automate the translation of RPG Maker MV/MZ games using the Google Gemini API. This tool processes game files, preserves game code integrity, and generates `.zip` patch files compatible with JoiPlay (Android) and PC.

## Project Architecture

The project is divided into two distinct parts:

- **backend/**: A Flask (Python) server that handles file processing, Gemini API communication, text masking, and file packaging.
- **frontend/**: A React.js client that provides a drag-and-drop interface, real-time logging, and an editing suite.

## Prerequisites

Before starting, ensure your system meets the following requirements:

- **Python 3.10** or higher (Required for library compatibility).
- **Node.js** (v16+) and **npm**.
- **Google Gemini API Key** (Available from [Google AI Studio](https://aistudio.google.com/)).

## Setup Instructions

Follow these steps to configure the development environment.

### 1. Backend Setup

Navigate to the backend directory and set up the Python environment.

```bash
cd backend

# Create a virtual environment (Python 3.10+ recommended)
# Windows:
python -m venv venv
# Linux/Mac:
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration:**
Create a `.env` file in the `backend/` directory:

```env
FLASK_PORT=5000
FLASK_DEBUG=1
GEMINI_API_KEY=your_actual_api_key_here
REACT_APP_BACKEND_URL=http://localhost:3000
```

### 2. Frontend Setup

Open a new terminal, navigate to the frontend directory, and install dependencies.

```bash
cd frontend

# Install Node modules
npm install
```

**Configuration:**
Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_BACKEND_URL=http://localhost:5000
```

## Running the Application

You need to run both the backend and frontend servers simultaneously.

### Option 1: Two Terminals (Recommended)

**Terminal 1 (Backend):**
```bash
cd backend
# Ensure venv is active
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

Access the application at `http://localhost:3000`.

### Option 2: Unified Environment (Advanced)

If you have configured `nodeenv` inside your Python virtual environment:

1.  Activate the backend `venv`.
2.  Navigate to the `frontend` directory.
3.  Run `npm run dev` (Requires `concurrently` to be configured in `package.json`).

## Usage Workflow

1.  **Upload:** Drag and drop an RPG Maker `.json` file (e.g., `Map001.json`) or a zipped `data` folder.
2.  **Configure:** Select the source language and target language.
3.  **Translate:** Start the process. The tool will batch requests to Gemini to respect rate limits.
4.  **Review:** Monitor logs in the console. Errors or anomalies will be flagged.
5.  **Edit (Optional):** Open the Review modal to manually correct specific lines.
6.  **Download:** Download the generated `.zip` file and apply it to the game via JoiPlay.

## License

This project is open-source. Feel free to use and modify.

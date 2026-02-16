# Marine Debris Backtracking & Visualization Platform

This project is a full-stack application designed to simulate and visualize the backtracking of marine debris using the **OpenDrift** library, and detect marine debris using **YOLO** models. It combines a Python/Flask backend for simulation processing and object detection with a React/Vite frontend for an interactive user experience.

## Project Structure

*   **`MarineTraceApp/backend`**: Flask server handling simulation requests, job management, OpenDrift execution, and YOLO inference.
    *   **`simulation/`**: Core simulation engine (formerly `pair-particle-drift`).
    *   **`models/`**: Directory for YOLO models.
*   **`MarineTraceApp/frontend`**: React application providing the user interface.
*   **`docs/`**: Additional documentation and guides.

## Prerequisites

*   **Python 3.10+** (Recommended to use Conda)
*   **Node.js 18+** & **npm**
*   **Git**

## Installation

### 1. Backend Setup

It is highly recommended to use a dedicated Conda environment for the backend dependencies, especially for geospatial libraries like `gdal`, `netCDF4`, and `opendrift`.

```bash
# Create and activate conda environment
conda create -n webdev-pair python=3.11
conda activate webdev-pair

# Install system dependencies (if needed for Linux)
# sudo apt-get install libnetcdf-dev libgdal-dev

# Install Python dependencies
pip install flask flask-cors apscheduler netCDF4 xarray numpy pandas opendrift ultralytics opencv-python-headless pillow
```

### 2. Frontend Setup

```bash
cd MarineTraceApp/frontend
npm install
```

## Usage

### Running the Application Locally

#### 1. Start the Backend Server

```bash
# Activate your environment
conda activate webdev-pair

# Navigate to backend directory
cd MarineTraceApp/backend

# Run the Flask app
python app.py
```
The server will start at `http://localhost:5000`.

#### 2. Start the Frontend Development Server

```bash
# Open a new terminal
cd MarineTraceApp/frontend

# Run the dev server
npm run dev
```
The application will be accessible at `http://localhost:5173`.

### Running a Simulation

1.  Open the web interface (`http://localhost:5173`).
2.  Click on **"Mulai Tracking"** or navigate to the simulation page.
3.  Select a **Location** (e.g., Takalar, Mamuju) or manually enter **Latitude** and **Longitude**.
4.  Set the **Start Date**, **Duration (Days)**, and **Number of Particles**.
5.  Click **"Mulai Tracking"**.
6.  Wait for the simulation to complete. The system will display:
    *   **Animation**: A GIF showing the particle drift over time.
    *   **Statistics**: Mean drift distance, speed, and dominant direction.
    *   **Static Map**: An OpenStreetMap overlay of the final particle positions.

### Object Detection (YOLO)

1.  Ensure you have a YOLO model (`best.pt`) in `MarineTraceApp/backend/models/`.
2.  Navigate to the detection page.
3.  Upload an image to detect marine debris.
4.  The system supports both Object Detection and Segmentation models.

## Features

*   **Backtracking Simulation**: Traces the path of particles backwards in time to identify potential sources.
*   **Interactive Visualization**: Animated particle trajectories.
*   **Statistics**: Auto-calculation of drift metrics (distance, speed, direction).
*   **Object Detection**: Identify plastic pollution types using AI.
*   **Job Management**: Asynchronous job processing with status polling.

## License

[Your License Here]

# MarineTrace Backend (Flask API)

This is the backend service for the MarineTrace application, powered by **Flask**. It provides two main capabilities:
1.  **Marine Debris Backtracking**: Simulates the movement of marine litter backwards in time using **OpenDrift** (with ERA5 and HYCOM data) to identify potential sources.
2.  **Waste Detection**: Uses **YOLOv8** to detect and classify plastic waste in uploaded images.

## Prerequisites

-   **Python 3.10+** (Recommended via Conda)
-   **Conda** (Anaconda or Miniconda)
-   **Copernicus Climate Data Store (CDS) Account** (for ERA5 data access)

## Installation

### 1. Set up Conda Environment

It is **highly recommended** to use a dedicated Conda environment to manage complex geospatial dependencies (GDAL, NetCDF4, OpenDrift).

```bash
# Create environment
conda create -n webdev-pair python=3.11
conda activate webdev-pair

# Install system dependencies (if on Linux/WSL)
# sudo apt-get install libnetcdf-dev libgdal-dev
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure ERA5 Access

To download atmospheric data for simulations, you need a `.cdsapirc` file in your home directory (`C:\Users\Username\.cdsapirc` or `~/.cdsapirc`).

1.  Register at [CDS](https://cds.climate.copernicus.eu/).
2.  Create the file with your URL and Key:
    ```
    url: https://cds.climate.copernicus.eu/api/v2
    key: YOUR_UID:YOUR_API_KEY
    ```

### 4. Setup YOLO Model

Place your trained YOLOv8 model file (`.pt`) in the `models/` directory.

```bash
# Example
cp /path/to/your/best.pt backend/models/best.pt
```

## Running the Server

Ensure your Conda environment is activated:

```bash
conda activate webdev-pair
cd backend
python app.py
```

The server will start at `http://localhost:5000`.

## API Endpoints

### Simulation (Backtracking)

The simulation runs as an asynchronous background job.

1.  **Start Simulation**
    *   `POST /api/simulate`
    *   Body:
        ```json
        {
          "latitude": -5.15,
          "longitude": 119.42,
          "start_time": "2024-01-01",
          "days": 3,
          "particles": 30
        }
        ```
    *   Response: `{"job_id": "uuid-string", "status": "queued"}`

2.  **Check Status**
    *   `GET /api/simulation/status/<job_id>`
    *   Response: `{"status": "running"}` or `{"status": "completed", "result": {...}}`

3.  **Get Results**
    *   `GET /api/simulation/result/<job_id>`
    *   Returns JSON with paths to generated files (Animation, NetCDF, Stats, OSM Plot).

### Waste Detection

1.  **Detect Waste**
    *   `POST /api/detect`
    *   Body: JSON with Base64 image or Multipart Form Data.
    *   Response: JSON with detection counts and result image path.

### Utilities

*   `GET /api/health`: Check if API and models are ready.
*   `GET /serve_simulation_file/<filename>`: Serves generated static files (images, GIFs).

## Project Structure

*   `app.py`: Main Flask application entry point.
*   `simulation/`: Core simulation logic (OpenDrift integration).
    *   `litter_simulation.py`: Main simulation script.
    *   `modules/`: Physics, data preparation, and visualization modules.
*   `static/simulations/`: Stores generated simulation outputs (GIFs, PNGs, NC files).
*   `models/`: Directory for YOLO `.pt` files.
*   `uploads/`: Temporary storage for uploaded images.

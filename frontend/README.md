# MarineTrace Frontend (React + Vite)

This is the frontend interface for the MarineTrace application, built with **React** and **Vite**. It allows users to interact with the marine debris simulation and waste detection capabilities provided by the backend.

## Prerequisites

-   **Node.js 18+**
-   **npm**

## Installation

```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

To start the development server with hot-reload:

```bash
npm run dev
```

The application will be accessible at `http://localhost:5173`.

### Production Build

To create a production-ready build:

```bash
npm run build
```

To preview the production build:

```bash
npm run preview
```

## Features & Pages

### 1. Landing Page (`MainPage.jsx`)
-   Introduction to the project.
-   Navigation to Tracking and Detection features.

### 2. Debris Tracking (`TrackingPage.jsx`)
-   **Input**:
    -   Select Location (Takalar, Mamuju) or manual Latitude/Longitude.
    -   Start Date & Duration (Days).
    -   Number of Particles.
-   **Output**:
    -   **Animation**: GIF showing particle backtracking.
    -   **Statistics**: Mean drift distance (km), speed (m/s), and dominant direction.
    -   **Map**: OpenStreetMap overlay of the simulation result.

### 3. Waste Detection (`DetectionPage.jsx`)
-   **Input**: Upload an image of marine debris.
-   **Output**:
    -   Processed image with bounding boxes.
    -   Count of detected items (Plastic Bag, Bottle, Wrapper).
    -   Confidence scores.

## Configuration

The frontend is configured to communicate with the backend at `http://localhost:5000`.

To change this, update the API calls in:
-   `src/components/TrackingPage.jsx`
-   `src/components/DetectionPage.jsx`

(Or use a `.env` file with `VITE_API_URL` if configured).

## Project Structure

-   `src/`: Source code.
    -   `components/`: React components (Pages and UI elements).
    -   `App.jsx`: Main application router.
    -   `main.jsx`: Entry point.
-   `public/`: Static assets.
-   `vite.config.js`: Vite configuration.

# Weird Stuff In Traffic - Backend

This directory contains the necessary backend code for running the generation and detection processes, and interacting with the user interface.

## 📁 Backend Structure

-   **`images/`** - The images directory for storing background images used during generation and storing images where detection failed.
-   **`models/`** - Used for storing the detection model weights and the configuration file.
-   **`schemas/`** - Schemas used for api responses between the frontend and backend.
-   **`services/`** - The detection and generation functionalities are handled within the services directory.
-   **`tests/`** - Contains testing scripts used to test overall detection and generation functionality within the backend.
-   `main.py` - The intial entry for the backend, where models are initialized and enpoints are exposed.

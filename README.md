# Weird-Stuff-In-Traffic

### Project Summary

The "Weird Stuff In Traffic" projects presents a gamified, web-based application designed to enhance the training of object detection models for autonomous driving systems. In the game, users are encouraged to create unusual or "weird" traffic scenes through textual prompts. A fine-tuned AI model then attempts to identify unusual objects within the generated images. The core objective is to identify gaps in the model’s recognition capabilities by encouraging users to create scenes that the AI fails to detect correctly.

<p align="center">
  <img src="Documentation/images/explodingcow.png" alt="Exploding Cow" width="400">
  <img src="Documentation/images/neonparrots.jpg" alt="Neon Parrots" width="400">
</p>
<p align="center"><em>Figure 1: Generated Images for an "Exploding Cow" and "Neon stringed parrots".</em></p>

<p align="center">
  <img src="Documentation/images/Scoring.png" alt="User Frontend" width="600">
</p>
<p align="center"><em>Figure 2: User Intefrace".</em></p>

### 🚀 Getting Started
#### 📦 Install Dependencies
1. To install all the necessary python libraries, run the following in your terminal of choice from the project's home directory: `pip install requirements.txt`
2. To then install all necessary node packages, navigate to `Weird-Stuff-In-Traffic/App/Frontend` and run `npm install`

#### 🧠 Running the App
1. From the home project directory, run the following bash script to simultanously launch the NextJS Frontend and FastAPI backend: `bash start_app.sh`

### 🖥️ Hardware Requirements
- Nvidia GPU with a minimum of 24GB (Nvidia 4090)

### 👥 Contributors
Thomas Cansfield, Hannah Simson, Ludwig Gallmeier, Ahmed Ibrahim, Albert Didkovski, Andreas Kolbinger, Anja Schlaak, Benjamin Kass, Daniel Shaquille, Hamza Dursun, Kevin Kuhn, \ Martin Lauff, Selin Durmus, Surkhay Khanmammadli, Syed Abidi, Tobias Kerner, Vanessa Rieger



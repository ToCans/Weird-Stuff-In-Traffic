#!/bin/bash

# --- Start Frontend ---
echo "Starting frontend..."
cd /home/ai-team2/Weird-Stuff-In-Traffic/App/Frontend/weird-traffic-app
npm run dev -- -H 0.0.0.0 &

# --- Start Backend ---
echo "Starting backend..."
cd /home/ai-team2/Weird-Stuff-In-Traffic/App/Backend
/home/ai-team2/miniconda3/envs/application/bin/python main.py
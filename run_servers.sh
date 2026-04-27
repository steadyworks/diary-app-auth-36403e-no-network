#!/bin/bash
set -e

# Backend
cd /app/backend
pip install -r requirements.txt 2>/dev/null || true
python main.py &

# Frontend
cd /app/frontend
npm install
npm run build && npx next start --port 3000 --hostname 0.0.0.0 &

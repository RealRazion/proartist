#!/bin/bash

# Starte Backend
echo "Starte Backend..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver &
BACKEND_PID=$!

# Starte Frontend
echo "Starte Frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo "Server gestartet:"
echo "Backend: http://127.0.0.1:8000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo "Drücke Ctrl+C, um zu stoppen."

# Warte auf Interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
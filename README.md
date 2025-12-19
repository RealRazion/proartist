# ProArtist

Kuratierte Arbeitsoberfläche für Projekte, Tasks und Team-Kommunikation.

## Setup

1. **Backend**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm install
   ```

## Tests & Builds

- Backend: `venv\Scripts\python.exe manage.py test`
- Frontend: `cd frontend && npm run build`

Bitte beides vor jedem Push laufen lassen – der Server migriert beim Deploy automatisch.

## Realtime & Benachrichtigungen

- Websocket-Server (Daphne/Uvicorn) muss laufen; Projekte/Tasks aktualisieren sich ohne kompletten Reload.
- Mail-Versand benötigt ein konfiguriertes Django-Mailbackend (`DEFAULT_FROM_EMAIL`, SMTP-Creds etc.).
- Profile verwalten persönliche `notification_settings`, die im neuen Abschnitt „Benachrichtigungen“ der Profilseite gepflegt werden.

## Nützliche Endpunkte

- `GET /api/projects/timeline/` – Daten für die Timeline-Ansicht.
- `GET /api/tasks/calendar/` – komprimierter Kalenderfeed.
- `WS /ws/updates/` – Echtzeit-Events für Projekte & Tasks; Zugriff nur für Team-Rollen.

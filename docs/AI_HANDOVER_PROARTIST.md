# ProArtist AI Handover (detailliert)

Diese Datei ist eine technische Uebergabe fuer eine weitere KI, die in diesem Projekt effektiv und sicher arbeiten soll.
Ziel: schnell produktiv werden, keine blinden Annahmen, keine regressionsreichen Aenderungen.

---

## 1) Produktbild in 90 Sekunden

ProArtist ist eine Django + Vue Anwendung fuer Team/Artist Collaboration:

- Team verwaltet Projekte, Tasks, Reviews, GrowPro-Ziele, News, Plugin Guides, Team Points, Admin und API-Center.
- Artists sehen ihr Dashboard, Profile, Chats, News, Guides und eigene GrowPro-Ziele.
- Realtime:
  - Team bekommt Projekt/Task Updates ueber WebSocket (`/ws/updates/`).
  - Chat nutzt eigenen WebSocket pro Thread (`/ws/chat/<thread_id>/`).

Wichtige Leitidee:
- Rollensteuerung laeuft ueber `Profile.roles` mit `Role.key="TEAM"` als zentrale Berechtigung.
- Viele UI-Bereiche sind Team-only, aber API muss trotzdem serverseitig sauber absichern.

---

## 2) Repo-Topologie (wichtigste Pfade)

```text
proartist/
  backend/
    settings.py
    urls.py
    asgi.py
  core/
    models.py
    serializers.py
    views.py
    assignment.py
    automation.py
    realtime.py
    consumers.py
    ws_auth.py
    permissions.py
    migrations/
    test_suites/
  frontend/
    src/
      api.js
      router/index.js
      assets/styles.css
      layouts/MainLayout.vue
      config/version.js
      views/*.vue
      composables/*
      components/*
  docs/
```

Empfohlene Lesereihenfolge fuer neue KI:
1. `backend/urls.py`
2. `core/models.py`
3. `core/views.py`
4. `core/assignment.py`
5. `frontend/src/router/index.js`
6. `frontend/src/api.js`
7. `frontend/src/layouts/MainLayout.vue`
8. Kernviews (`Tasks.vue`, `ProjectDetail.vue`, `ReviewQueue.vue`, `GrowPro.vue`, `Dashboard.vue`, `Timeline.vue`)

---

## 3) Lokales Setup und Start

### Backend

```powershell
cd proartist
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```powershell
cd proartist\frontend
npm install
npm run dev
```

### Build/Test Mindest-Check

```powershell
# Backend
cd proartist
venv\Scripts\python.exe manage.py test

# Frontend
cd proartist\frontend
npm run build
```

Hinweis:
- Fehler `no such table: core_pluginguide` bedeutet praktisch immer: Migrationen nicht ausgefuehrt.

---

## 4) ENV und Konfiguration (serverseitig relevant)

Aus `backend/settings.py` und Views:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS` (comma-separated)
- `CORS_ALLOWED_ORIGINS` (comma-separated)
- `THROTTLE_ANON`
- `THROTTLE_USER`
- `API_CENTER_OFFLINE` (standardmaessig effektiv offline)
- `HSTS_SECONDS`, `HSTS_INCLUDE_SUBDOMAINS`, `HSTS_PRELOAD`
- `REFERRER_POLICY`
- `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_SECURE`
- `FRONTEND_URL` (wichtig fuer Invite-Link in `set-password`)
- E-Mail Backend Variablen (fuer Benachrichtigungen/Einladungen)

Wichtige Defaults:
- DB default: SQLite (`db.sqlite3`) via `dj-database-url`.
- Channel layer: InMemory (Dev).
- REST default permission: authenticated.

---

## 5) Datenmodell und Kernobjekte

In `core/models.py`:

- Identity/Roles:
  - `Role`, `Profile`, `RegistrationRequest`
- Collaboration:
  - `Project`, `Task`, `TaskComment`, `TaskAttachment`, `ProjectAttachment`
- Communication:
  - `ChatThread`, `ChatMessage`
- Content:
  - `NewsPost`, `PluginGuide`, `Song`, `SongVersion`
- Growth/Scoring/Operations:
  - `GrowProGoal`, `GrowProUpdate`, `ActivityEntry`
  - `AutomationRule`, `SystemIntegration`

Wichtige Fachregeln:
- Task review:
  - `review_status` ist `REVIEWED` oder `NOT_REVIEWED`.
  - DONE ohne review-status wird serverseitig auf `NOT_REVIEWED` gesetzt.
- GrowPro:
  - Stale-Interpretation (72h ohne Update) ist aktuell v.a. im Frontend umgesetzt.
- Team Points:
  - LOW/MEDIUM=1, HIGH=2, CRITICAL=3
  - Projektteilnahme=2
  - GrowPro-Zuteilung=1

---

## 6) API-Landkarte (Backend)

Alle Routen kommen aus `backend/urls.py` + DRF Router.

### Auth/Invite

- `POST /api/token/`
- `POST /api/token/refresh/`
- `POST /api/register/`
- `POST /api/invite/` (TEAM)
- `POST /api/set-password/`

### Profile/Role/Admin

- `GET /api/profiles/me/`
- `POST /api/profiles/<id>/lock/` (TEAM)
- `POST /api/profiles/<id>/team-role/` (TEAM)
- `GET /api/admin/overview/` (TEAM)
- `GET /api/admin/dashboard/` (Alias auf overview)
- `GET /api/stats/`

### Projects

- Router: `/api/projects/`
- Zusatz:
  - `POST /api/projects/<id>/archive/`
  - `POST /api/projects/<id>/delete/`
  - `GET /api/projects/timeline/`
  - `GET /api/projects/summary/`
  - `GET /api/projects/export/`

### Tasks

- Router: `/api/tasks/`
- Zusatz:
  - `POST /api/tasks/<id>/archive/`
  - `POST /api/tasks/<id>/delete/`
  - `GET /api/tasks/calendar/`
  - `GET /api/tasks/summary/`
  - `GET /api/tasks/overdue/`
  - `GET /api/tasks/upcoming/`

Task Query-Parameter (wichtig):
- `include_archived`, `include_done`, `archived_only`
- `project`, `status`, `search`
- `assignee`, `stakeholder`
- `priority`, `task_type`, `review_status`
- `due_state`, `due_before`, `due_after`
- `ordering` in erlaubter Whitelist

### Review-Fluss (technisch)

- Kein eigener Review-Endpunkt; Review ist Task-Statusmodell.
- Frontend setzt i.d.R. via:
  - `PATCH /api/tasks/<id>/` mit `{ status: "DONE", review_status: "REVIEWED" }`
  - oder `{ status: "DONE", review_status: "NOT_REVIEWED" }`

### GrowPro

- Router: `/api/growpro/`
- Zusatz:
  - `POST /api/growpro/<id>/log/`
  - `GET /api/growpro/summary/`

Query-Parameter:
- `search`, `profile`, `assigned_team`, `status`, `ordering`

### Activity / Points / Analytics / Automation

- `GET /api/activity-feed/` (TEAM)
- `GET /api/activity/` (Legacy alias)
- `GET /api/team-points/` (TEAM)
- `GET /api/team-points/?format=csv` (TEAM)
- `GET /api/analytics/summary/` (TEAM)
- `POST /api/automation/task-reminders/` (TEAM)
- `GET /api/api-center/status/` (TEAM)

### Content

- News: `/api/news/` + `/api/news/<id>/publish/`
- Plugin Guides: `/api/plugin-guides/` + `/api/plugin-guides/<id>/publish/`

### Chat

- Threads: `/api/threads/`
- Messages: `/api/messages/`
- Spezial:
  - `POST /api/threads/ensure/`
  - `POST /api/threads/<id>/send/`

---

## 7) Frontend Architektur und Flow

### Routing

`frontend/src/router/index.js`:
- Guest: `/`, `/login`, `/register`, `/set-password`
- App shell: `/app/*` via `MainLayout`
- Legacy aliases auf direkte Pfade (`/dashboard`, `/tasks`, ...)
- Guard:
  - `requiresAuth` => Redirect zu Login
  - `guestOnly` + Token => Redirect zu Dashboard

### API Client

`frontend/src/api.js`:
- Basis-URL normalisiert auf `/api/`
- Request interceptor: JWT `Authorization` Header
- Response interceptor:
  - GET 5xx: 1 Retry nach kurzer Wartezeit
  - 401: Token refresh flow
  - Fehler-Toast (gedrosselt)

### Session-/Profil-Kontext

`useCurrentProfile.js`:
- globaler Profile-Cache
- `isTeam` computed aus Rollen

### Realtime

`useRealtimeUpdates.js`:
- verbindet auf `/ws/updates/?token=<jwt>`
- automatisch reconnect
- wird in Projects/Tasks genutzt

### Globales Styling/Theming

`assets/styles.css`:
- zentrale CSS-Variablen (`--bg`, `--card`, `--text`, ...)
- `:root.dark` Theme
- Sidebar/Topbar/mobile/responsive Basis
- Version in Sidebar Footer via `MainLayout` + `config/version.js`

---

## 8) Feature-Map (View -> Verantwortung -> API)

Kurzuebersicht der wichtigsten Views:

- `Dashboard.vue`
  - Priorisierte Slideshow (Fristen, Review, GrowPro stale/upcoming)
  - Team-Quick-Actions (Task erstellen, Invite)
  - API: projects, tasks, requests, growpro, invite

- `Tasks.vue`
  - Board, Filter, Details, Kommentare, Attachments, Review-Confirm-Modal
  - API: tasks, projects, profiles, task-comments, realtime

- `ProjectDetail.vue`
  - Projekt + Task-Verwaltung + Song Liste + Activity
  - Timeline deep-link highlight ueber `?taskId=...` inkl. Scroll/Pulse
  - API: projects, tasks, songs, activity-feed

- `ReviewQueue.vue`
  - Team Review Queue inkl. Bulk-Operationen
  - API: tasks list + patch

- `Timeline.vue`
  - 3 Layouts (`calendar`, `list`, `today`)
  - Filter fuer Prioritaet/Intern-Extern
  - Action Buttons deep-linken zu Task/Projekt/GrowPro
  - API: tasks/calendar, projects/timeline, growpro

- `GrowPro.vue`
  - Ziele, Logs, Zuweisung, Activity Panel per Toggle
  - API: growpro, profiles, activity-feed

- `Points.vue`
  - Team Punkte + Tagesplus/minus + CSV Export
  - API: team-points

- `ApiCenter.vue`
  - Integrationen + Automation Rules, simple/complex mode
  - Respektiert serverseitiges Offline-Flag
  - API: api-center/status, system-integrations, automation-rules

- `News.vue`
  - Team editor + clientseitiger image crop flow
  - API: news

- `PluginGuides.vue`
  - Analog zu News, aber mit backend image support
  - API: plugin-guides

- `Chats.vue`
  - Threadliste, WebSocket pro Thread, Typing/Read Receipts, Delete Thread
  - API: threads, messages, websocket

- `Admin.vue`
  - Overview-Metriken, profile lock/team toggle, registration requests/invites

- `Analytics.vue`
  - Aggregierte Kennzahlen, reminder trigger

---

## 9) Business-Logik, die nicht gebrochen werden darf

### Task Completion / Review

Serverlogik in `TaskViewSet.perform_create` und `perform_update`:
- Bei Wechsel auf `DONE`:
  - `completed_at` setzen
  - wenn `review_status` fehlt -> `NOT_REVIEWED`
  - bei `NOT_REVIEWED` -> `assign_task_for_review(task)`
- Bei Rueckwechsel von `DONE` auf anderen Status:
  - `completed_at`, `review_status`, `reviewed_at` werden wieder bereinigt

=> Dadurch ist "DONE wieder zurueckziehen" serverseitig moeglich.

### Team Score und GrowPro Rebalancing

In `core/assignment.py`:
- Score = offene Tasks + Projektbeteiligungen + GrowPro-Zuweisungen
- Review-Zuweisung nimmt niedrigsten Score
- GrowPro-Rebalance verschiebt Ziele, bis Score-Differenz <= 2 oder keine Moves mehr sinnvoll
- Alles in DB-Transaction, damit kein halb-konsistenter Zustand entsteht

### Activity Logging

Zentrale Persistenz via `log_activity(...)`.
Viele Features haengen am Activity Feed; bei neuer Funktion moeglichst Event loggen.

---

## 10) Realtime/WS Details

Backend:
- `backend/asgi.py` nutzt `JWTAuthMiddleware`.
- WS Routes:
  - `/ws/chat/<thread_id>/`
  - `/ws/updates/`

`/ws/updates/` ist TEAM-only (sonst close mit code 4403).

Wichtig:
- WS Auth nutzt JWT aus Query Parameter `token=...`.
- Bei API-Basis-URL Aenderungen muss WS URL Builder in Frontend konsistent bleiben.

---

## 11) Chat Delete: Datenbank-Semantik

UI in `Chats.vue` ruft:
- `DELETE /api/threads/<id>/`

Backend:
- `ChatThreadViewSet` basiert auf ModelViewSet.
- `get_queryset()` filtert auf Threads des aktuellen Profils.
- Destroy auf Thread loescht Thread-Record.
- `ChatMessage.thread` hat `on_delete=models.CASCADE`.

Folge:
- Loeschen im UI entfernt nicht nur Anzeige, sondern loescht Thread + zugehoerige Messages in der DB.

---

## 12) Bekannte Stolperfallen / aktuelle technische Schulden

1. News-Bildsupport ist inkonsistent:
   - Frontend sendet `image` (inkl. Cropper).
   - `NewsPost` Model/Serializer/Viewset hat aktuell kein `image` Feld und keine Multipart-Parser.
   - Ergebnis: Verhalten kann je nach Request scheitern oder Feld ignorieren.

2. Migrationspflicht:
   - Neue Features wie `PluginGuide`, `SystemIntegration`, `AutomationRule` brauchen aktuelle Migrationen.
   - Sonst 500er wie `no such table`.

3. Encoding-Anzeige:
   - Manche Konsolen zeigen Umlaute als Mojibake.
   - Vor "Fixes" erst Dateikodierung pruefen, nicht blind Strings austauschen.

4. Legacy-Endpunkte:
   - Historisch wurde `/api/activity/` genutzt.
   - Aktuell existiert Alias, aber Frontend sollte bevorzugt `activity-feed/` nutzen.

5. `users` App:
   - Enthalt `CustomUser`, wird aber nicht in `AUTH_USER_MODEL` aktiviert.
   - Derzeit arbeitet System mit Django Standard User + `Profile`.

---

## 13) Debug-Playbooks (schnelle Reparaturmuster)

### A) `404 /api/plugin-guides/` oder `500 no such table core_pluginguide`

1. `python manage.py migrate`
2. pruefen: `core/migrations/0015_pluginguide.py` vorhanden
3. Server neu starten

### B) Tasks laden/erstellen klappt nicht

1. Browser Network: Request/Response Payload pruefen
2. Backend logs fuer ValidationError/PermissionError checken
3. Queryparameter (`include_done`, `include_archived`, `status`) pruefen
4. `TaskSerializer` Felder vs Frontend payload abgleichen

### C) Analytics/Admin/GrowPro 404 oder 500

1. `backend/urls.py` Route vorhanden?
2. Team-Rolle am Userprofil vorhanden?
3. Migrationen aktuell?
4. API Base URL im Frontend korrekt?

### D) Chat-Probleme

1. REST `/api/threads/` erreichbar?
2. WS URL inklusive Token korrekt?
3. Token abgelaufen? Refresh flow in `api.js` checken

---

## 14) Arbeitsprotokoll fuer neue KI (empfohlen)

Bei jeder Aufgabe:
1. Scope schaetzen (nur UI? API? DB?)
2. Betroffene Dateien explizit auflisten
3. Vor Aenderungen bestehende Flows lesen
4. Kleine, testbare Schritte implementieren
5. Mindestens:
   - Backend tests
   - Frontend build
   - manuelle Smoke-Flows
6. Erst dann commit-vorschlag liefern

Smoke-Flows (manuell):
- Login/Refresh token
- Task erstellen -> Statuswechsel -> DONE mit Review-Dialog -> Rueckwechsel
- ReviewQueue bulk action
- Timeline action button -> springt an richtigen Ort
- GrowPro create/log/filter
- Chat senden + thread delete
- Dark mode + mobile sidebar

---

## 15) Release/Versioning Regel im Projekt

Quelle: `frontend/src/config/version.js`

- Schema: `MAJOR.MINOR.PATCH` + optionaler Suffix (z.B. `Alpha`)
- Bedeutungen:
  - `PATCH`: Bugfixes, keine neuen Konzepte
  - `MINOR`: neue Features, kompatibel
  - `MAJOR`: breaking changes

Aktuell (Stand dieser Doku):
- `1.9.7`

Beim Versions-Update:
1. `frontend/src/config/version.js` anpassen
2. Kurz changelog im Committext sauber benennen

---

## 16) "Wenn ich nur 30 Minuten habe" Plan fuer Folge-KI

1. Setup + `migrate` + `test` + `npm run build`
2. API Health:
   - token
   - profiles/me
   - tasks/summary
   - growpro/summary
   - plugin-guides
3. UI Health:
   - Dashboard
   - Tasks
   - ReviewQueue
   - GrowPro
   - Analytics
4. Danach erst Feature-Arbeit starten.

---

## 17) Schnellindex: wichtigste Dateien

- API routing: `backend/urls.py`
- Permissions: `core/permissions.py`
- Hauptlogik API: `core/views.py`
- Punkte/Zuteilung: `core/assignment.py`
- Reminder Automation: `core/automation.py`
- Realtime events: `core/realtime.py`
- WS consumer/auth: `core/consumers.py`, `core/ws_auth.py`
- Datenmodell: `core/models.py`
- Serialisierung: `core/serializers.py`
- Router Frontend: `frontend/src/router/index.js`
- API Client Frontend: `frontend/src/api.js`
- Globales UI/Theming: `frontend/src/assets/styles.css`
- Layout/Sidebar/Version: `frontend/src/layouts/MainLayout.vue`
- Version config: `frontend/src/config/version.js`
- Kernviews: `frontend/src/views/*.vue`

---

Wenn du diese Datei als Folge-KI liest: starte mit Abschnitt 14 und arbeite dann ueber Abschnitt 6+8 in die konkrete Aufgabe hinein.

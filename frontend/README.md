# ProArtist Frontend

Vue 3 + Vite Frontend fuer ProArtist.

## Setup

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Mobile (Capacitor)

```bash
npm run android:sync
npm run android:open
```

## Environment

- `VITE_API_BASE_URL`: Basis-URL fuer Web (z. B. `https://api.example.com`)
- `VITE_API_BASE_URL_MOBILE`: Basis-URL fuer native Builds

Hinweis:
- Die API-Basis wird intern auf `/api/` normalisiert.
- Ohne gesetzte Variable nutzt die Web-App lokal `http://127.0.0.1:8000/api/`.

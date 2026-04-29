# ProArtist APK Build Guide

## ✅ Setup Complete

Capacitor ist jetzt eingerichtet! Die Web-App kann als Android APK verpackt werden.

## Voraussetzungen

- **Android Studio**: https://developer.android.com/studio
- **Java JDK 11+**: Wird mit Android Studio installiert
- **Mindest SDK**: Android 7.0 (API 24)

## Backend-Verbindung fuer APK

Wichtig: Eine APK darf **nicht** auf `127.0.0.1`/`localhost` als Backend zeigen (das waere das Geraet selbst).

Lege vor dem Build in `frontend` eine Datei `.env.production` an:

```bash
VITE_API_BASE_URL=https://dein-backend.example.com
```

Beispiel:

```bash
VITE_API_BASE_URL=https://proartist.onrender.com
```

Danach immer neu bauen und kopieren:

```bash
npm run build
npx cap copy android
```

## Schritt-für-Schritt Build Guide

### 1. Frontend neu bauen
```bash
npm run build
```

### 2. Web-Assets in Android kopieren
```bash
npx cap copy android
```

### 3. Android Studio öffnen
```bash
npx cap open android
```

Dies öffnet das Android Studio mit dem vollständigen Projekt.

### 4. APK bauen (in Android Studio)

**Variante A - Debug APK (für Tests):**
- Menü: `Build` → `Build Bundle(s) / APK(s)` → `Build APK(s)`
- APK landet in: `android/app/build/outputs/apk/debug/app-debug.apk`

**Variante B - Release APK (für Play Store):**
- Menü: `Build` → `Generate Signed Bundle / APK...`
- Keystore erstellen (falls nicht vorhanden)
- Signieren & bauen
- APK landet in: `android/app/build/outputs/apk/release/app-release.apk`

### 5. APK auf Gerät testen
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

## Schnellbefehle

```bash
# Alles in einem (Web-build + Android sync + öffnen)
npm run build && npx cap copy android && npx cap open android

# Nur synchronisieren (nach Codeänderungen)
npx cap sync android

# Änderungen nur kopieren (schneller, ohne Sync)
npx cap copy android
```

## Deployment-Optionen

| Option | Aufwand | Verteilung | Pros |
|--------|---------|-----------|------|
| **Debug APK** | ⭐ Gering | Manuell (USB, Email, USB) | Schnelles Testen |
| **Release APK** | ⭐⭐ Mittel | Google Play Store | Offiziell, Updates |
| **Firebase Distribution** | ⭐⭐⭐ Hoch | Beta-Tester | Automatische Updates |

## Fehlerhafte Konfiguration?

Falls der Build fehlschlägt:
1. Gradle Sync durchführen (Android Studio: `Sync Now`)
2. Android SDK Tools aktualisieren
3. Neu bauen: `Build` → `Clean Project` → `Build APK`

## Version & Updates

Die Version ist derzeit: **2.1.0.1 Beta**

Für die nächste Version:
1. Version in `package.json` erhöhen
2. `npm run build` ausführen
3. `npx cap copy android` ausführen
4. Neuen APK bauen

## Weitere Infos

- Capacitor Docs: https://capacitorjs.com/docs/
- Android Studio Guide: https://developer.android.com/studio/intro
- Play Store Upload: https://play.google.com/console

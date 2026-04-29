#!/bin/bash
# Quick APK Build Script for Windows PowerShell
# Usage: .\build-apk.ps1

Write-Host "🔨 ProArtist APK Build Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Step 1: Build web assets
Write-Host "`n1️⃣  Building web assets..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Web build failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Sync with Android
Write-Host "`n2️⃣  Syncing with Android..." -ForegroundColor Yellow
npx cap sync android
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Sync failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Open Android Studio
Write-Host "`n3️⃣  Opening Android Studio..." -ForegroundColor Yellow
npx cap open android

Write-Host "`n✅ Setup complete! Android Studio is open." -ForegroundColor Green
Write-Host "📱 Next: Build → Build APK(s)" -ForegroundColor Green

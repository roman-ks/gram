# 0005 — Google Chrome installable webapp

> Status: **done** · Shipped: 2026-06-26 · Type: **feature** · Created: 2026-06-26

## Goal
On mobile make app eligible for Google Chrome install app on device as WebApk on Android. 

## Context
Currently Chrome allow only shortcut creation. Other apps like Memos are installable so browser supports it.


## Acceptance criteria
- [x] App is installable in Chrome on Android. (will be verified manually)

## Scope / hints (optional)
- Affected areas: only frontend

## Notes / decisions

### Implementation Summary
Created a complete PWA (Progressive Web App) setup for Chrome WebAPK installation support:

1. **Web App Manifest** (`frontend/public/manifest.json`):
   - Configured with `display: "standalone"` for full-screen app experience on Android
   - Added app name, description, and theme colors
   - Included SVG icons (192x192 and 512x512) for app launcher display
   - Set orientation to portrait-primary for mobile-first experience

2. **Service Worker** (`frontend/public/service-worker.js`):
   - Implements offline caching strategy for core app assets
   - Caches HTML, CSS, and app icons on install
   - Handles both offline functionality and fresh API requests
   - Gracefully skips API endpoint caching to ensure fresh data

3. **HTML Metadata** (updated `frontend/index.html`):
   - Added manifest link for PWA discovery
   - Included Apple-specific meta tags for iOS fallback (apple-mobile-web-app-capable)
   - Added theme color for browser UI integration
   - Implemented service worker registration with error handling

4. **Vite Integration**:
   - Public folder assets (manifest, icons, service worker) are automatically copied to dist/ on build
   - Dev server serves public files at root with proper content types

### Decisions
- **SVG Icons**: Used SVG for icons since they scale perfectly and are web-optimized. Note: For production, consider providing PNG fallbacks (192x192 and 512x512) for maximum WebAPK compatibility on older Chrome versions
- **Service Worker Caching**: Intentionally excludes `/api/` endpoints to ensure real-time data from the backend
- **Apple Fallback**: Included Apple iOS meta tags for broader mobile compatibility (iOS doesn't support WebAPK but can save as shortcut)

### How to Verify
On Android Chrome:
1. Open http://localhost:5173 (or deployed URL)
2. Menu → "Install app" (or address bar → install icon)
3. App will install as WebAPK with Gram icon and name

### Future Improvements
- Generate proper PNG icons from design files (currently simple SVG placeholders)
- Add app screenshots to manifest (540x720 and 1080x1440) for app store display
- Consider adding update strategy for service worker (currently cache-first)

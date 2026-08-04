const CACHE_NAME = 'gram-v2'
const urlsToCache = [
  '/icon-192.svg',
  '/icon-512.svg',
  '/manifest.json'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  )
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName)
          }
        })
      )
    }).then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', (event) => {
  const { request } = event

  // Don't cache API requests
  if (request.url.includes('/api/')) {
    return event.respondWith(fetch(request))
  }

  // Navigations (page loads) go network-first so a redeploy's index.html —
  // and the hashed /assets/* filenames it references — is picked up right
  // away, instead of serving a stale page from a previous version.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const responseToCache = response.clone()
          caches.open(CACHE_NAME).then((cache) => cache.put(request, responseToCache))
          return response
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match('/')))
    )
    return
  }

  // Build assets are content-hashed by Vite, so a cached response for a
  // given URL is always valid — cache-first is safe here.
  event.respondWith(
    caches.match(request).then((response) => {
      return response || fetch(request).then((response) => {
        const responseToCache = response.clone()
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseToCache)
        })
        return response
      })
    })
  )
})

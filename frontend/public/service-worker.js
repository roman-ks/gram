const CACHE_NAME = 'gram-v1'
const urlsToCache = [
  '/',
  '/index.html',
  '/icon-192.svg',
  '/icon-512.svg',
  '/manifest.json'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache)
    })
  )
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
    })
  )
})

self.addEventListener('fetch', (event) => {
  // Don't cache API requests
  if (event.request.url.includes('/api/')) {
    return event.respondWith(fetch(event.request))
  }

  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).then((response) => {
        // Cache new responses for static assets
        if (event.request.method === 'GET' && !event.request.url.includes('/api/')) {
          const responseToCache = response.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache)
          })
        }
        return response
      }).catch(() => {
        // Return offline fallback if available
        return caches.match('/')
      })
    })
  )
})

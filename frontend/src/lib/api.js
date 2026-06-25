// Single configurable base so a native (Capacitor) shell can point at the server.
// Empty string => same-origin (browser/PWA, dev via Vite proxy).
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

async function req(path, opts = {}) {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`)
  return res.status === 204 ? null : res.json()
}

export const api = {
  todaySummary: () => req('/today/summary'),
  todayEntries: () => req('/entries/today'),
  addEntry: (body) => req('/entries', { method: 'POST', body: JSON.stringify(body) }),
  addFood: (body) => req('/foods', { method: 'POST', body: JSON.stringify(body) }),
  sameMeal: (meal, days = 5) => req(`/suggestions/same-meal?meal=${meal}&days=${days}`),
  popular: (meal) => req(`/suggestions/popular${meal ? `?meal=${meal}` : ''}`),
  allFoods: () => req('/foods'),
}

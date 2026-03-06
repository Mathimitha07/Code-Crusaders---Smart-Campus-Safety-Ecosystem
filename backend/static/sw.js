const CACHE = "sch-cache-v2";

// App Shell: cache pages + static assets
const ASSETS = [
  "/login",
  "/student",
  "/student/attendance",
  "/student/safety",
  "/student/report",
  "/admin",
  "/admin/attendance/sessions",
  "/admin/reports",

  "/static/styles.css",
  "/static/app.js",
  "/static/offline.js",
  "/static/pwa.js",
  "/static/manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(k => (k !== CACHE ? caches.delete(k) : null)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle same-origin
  if (url.origin !== location.origin) return;

  // For HTML pages: network-first, fallback to cache
  if (req.headers.get("accept")?.includes("text/html")) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then(cache => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then(r => r || caches.match("/login")))
    );
    return;
  }

  // For static files: cache-first
  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req))
  );
});
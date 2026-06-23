/* kakol.pro service worker — small, offline-friendly, no tracking.
   Cache-first for same-origin GET; network fallback; offline -> cached page or /404.html. */
var CACHE = "kakolpro-v5";
var CORE = ["/", "/index.html", "/assets/style.css", "/assets/main.js", "/assets/index.json",
  "/projects.html", "/notes.html", "/research.html", "/cv.html", "/contact.html", "/404.html"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE).catch(function () {}); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.map(function (k) { if (k !== CACHE) return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) { fetch(req).then(function (res) { caches.open(CACHE).then(function (c) { c.put(req, res.clone()); }); }).catch(function () {}); return hit; }
      return fetch(req).then(function (res) {
        var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, copy); }); return res;
      }).catch(function () { return caches.match("/404.html"); });
    })
  );
});

// Caches the guide so it still opens on the bus with no signal.
// It only ever stores files from this site. It sends nothing anywhere.

var CACHE = "id-guide-__VERSION__";
var FILES = ["./", "./index.html", "./print.html"];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) {
    return cache.addAll(FILES);
  }).then(function () {
    return self.skipWaiting();
  }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (names) {
    return Promise.all(names.map(function (name) {
      return name === CACHE ? null : caches.delete(name);
    }));
  }).then(function () {
    return self.clients.claim();
  }));
});

self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;
  // Only this site's own files are ever stored.
  if (new URL(event.request.url).origin !== self.location.origin) return;

  event.respondWith(
    fetch(event.request)
      .then(function (response) {
        if (response.ok) {
          var copy = response.clone();
          caches.open(CACHE).then(function (cache) {
            cache.put(event.request, copy);
          }).catch(function () {});
        }
        return response;
      })
      .catch(function () {
        return caches.match(event.request).then(function (hit) {
          return hit || caches.match("./index.html");
        });
      })
  );
});

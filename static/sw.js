const CACHE_NAME = 'nutrifyke-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/manifest.json',
    '/static/sw.js',
    // Add other static assets here if you have CSS/JS files in static
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

self.addEventListener('fetch', (event) => {
    // Network first, fall back to cache
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});

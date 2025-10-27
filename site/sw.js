// StructKit Service Worker for Offline Support

const CACHE_NAME = 'struct-site-v1';
const STATIC_CACHE_URLS = [
  '/structkit/',
  '/structkit/index.html',
  '/structkit/css/main.css',
  '/structkit/css/components.css',
  '/structkit/css/animations.css',
  '/structkit/css/advanced.css',
  '/structkit/js/main.js',
  '/structkit/js/advanced.js',
  '/structkit/images/favicon.svg',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css',
];

const DEMO_CACHE_URLS = [
  '/structkit/demos/basic-usage.gif',
  '/structkit/demos/yaml-config.gif',
  '/structkit/demos/mappings-demo.gif',
  '/structkit/demos/remote-content.gif',
  '/structkit/demos/advanced-features.gif',
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');

  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(
          STATIC_CACHE_URLS.map(
            (url) =>
              new Request(url, {
                cache: 'reload',
              })
          )
        );
      }),

      // Cache demo files (optional, fail silently)
      caches.open(`${CACHE_NAME}-demos`).then((cache) => {
        console.log('Service Worker: Caching demo files');
        return Promise.allSettled(
          DEMO_CACHE_URLS.map((url) =>
            cache
              .add(new Request(url, { cache: 'reload' }))
              .catch((err) => console.log(`Failed to cache ${url}:`, err))
          )
        );
      }),
    ]).then(() => {
      console.log('Service Worker: Installation complete');
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (
              cacheName !== CACHE_NAME &&
              cacheName !== `${CACHE_NAME}-demos`
            ) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip external API calls (let them go through normally)
  if (url.hostname === 'api.github.com') {
    return;
  }

  // Skip Google Analytics
  if (
    url.hostname === 'www.googletagmanager.com' ||
    url.hostname === 'www.google-analytics.com'
  ) {
    return;
  }

  event.respondWith(handleFetchRequest(request));
});

async function handleFetchRequest(request) {
  const url = new URL(request.url);

  try {
    // For navigation requests, try cache first, then network
    if (request.mode === 'navigate') {
      return await handleNavigationRequest(request);
    }

    // For demo files, try cache first
    if (url.pathname.startsWith('/demos/')) {
      return await handleDemoRequest(request);
    }

    // For static assets, try cache first, then network
    if (isStaticAsset(url.pathname)) {
      return await handleStaticAssetRequest(request);
    }

    // For everything else, network first with cache fallback
    return await handleNetworkFirstRequest(request);
  } catch (error) {
    console.error('Service Worker: Fetch error:', error);
    return await handleOfflineFallback(request);
  }
}

async function handleNavigationRequest(request) {
  try {
    // Try network first for navigation
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      // Cache successful navigation responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }

    throw new Error('Network response not ok');
  } catch (error) {
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Fallback to offline page
    return await caches.match('/index.html');
  }
}

async function handleDemoRequest(request) {
  // Try cache first for demo files
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    // Try network if not in cache
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(`${CACHE_NAME}-demos`);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    throw new Error('Demo file not found');
  } catch (error) {
    // Return placeholder for missing demo files
    return new Response(createDemoPlaceholder(request.url), {
      headers: {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache',
      },
    });
  }
}

async function handleStaticAssetRequest(request) {
  // Try cache first for static assets
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  // Try network and cache the response
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    throw new Error('Asset not found');
  } catch (error) {
    throw error;
  }
}

async function handleNetworkFirstRequest(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

async function handleOfflineFallback(request) {
  const url = new URL(request.url);

  // For HTML pages, return the main page
  if (request.mode === 'navigate') {
    const mainPage = await caches.match('/index.html');
    if (mainPage) {
      return mainPage;
    }
  }

  // For images, return a placeholder
  if (request.destination === 'image') {
    return new Response(createImagePlaceholder(), {
      headers: {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache',
      },
    });
  }

  // For other resources, return a basic offline message
  return new Response('Offline - Content not available', {
    status: 503,
    statusText: 'Service Unavailable',
    headers: {
      'Content-Type': 'text/plain',
    },
  });
}

function isStaticAsset(pathname) {
  return pathname.startsWith('/css/') ||
         pathname.startsWith('/js/') ||
         pathname.startsWith('/images/') ||
         pathname.endsWith('.css') ||
         pathname.endsWith('.js') ||
         pathname.endsWith('.svg') ||
         pathname.endsWith('.png') ||
         pathname.endsWith('.jpg') ||
         pathname.endsWith('.gif');
}

function createDemoPlaceholder(url) {
  const filename = url.split('/').pop();
  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
      <rect width="800" height="450" fill="#1a1a1a"/>
      <rect x="50" y="50" width="700" height="350" fill="#2a2a2a" stroke="#333" stroke-width="2" rx="8"/>
      <text x="400" y="200" text-anchor="middle" fill="#666" font-family="Arial, sans-serif" font-size="24">
        Demo: ${filename}
      </text>
      <text x="400" y="250" text-anchor="middle" fill="#888" font-family="Arial, sans-serif" font-size="16">
        Offline - Demo not available
      </text>
      <circle cx="400" cy="300" r="20" fill="none" stroke="#666" stroke-width="2"/>
      <path d="M390 300 L400 290 L410 300 L400 310 Z" fill="#666"/>
    </svg>
  `;
}

function createImagePlaceholder() {
  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
      <rect width="400" height="300" fill="#2a2a2a"/>
      <rect x="20" y="20" width="360" height="260" fill="#1a1a1a" stroke="#444" stroke-width="2" rx="4"/>
      <text x="200" y="140" text-anchor="middle" fill="#666" font-family="Arial, sans-serif" font-size="18">
        Image Offline
      </text>
      <text x="200" y="170" text-anchor="middle" fill="#888" font-family="Arial, sans-serif" font-size="14">
        Content not available
      </text>
    </svg>
  `;
}

// Background sync for form submissions (future enhancement)
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background sync triggered');
    event.waitUntil(handleBackgroundSync());
  }
});

async function handleBackgroundSync() {
  // Handle any pending form submissions or data sync
  console.log('Service Worker: Performing background sync');
}

// Push notifications (future enhancement)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/images/favicon.svg',
      badge: '/images/favicon.svg',
      actions: [
        {
          action: 'view',
          title: 'View',
          icon: '/images/favicon.svg',
        },
        {
          action: 'dismiss',
          title: 'Dismiss',
        },
      ],
    };

    event.waitUntil(self.registration.showNotification(data.title, options));
  }
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(clients.openWindow('/'));
  }
});

// Message handler for cache updates
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'UPDATE_CACHE') {
    event.waitUntil(updateCache());
  }
});

async function updateCache() {
  console.log('Service Worker: Updating cache...');
  const cache = await caches.open(CACHE_NAME);

  try {
    await cache.addAll(
      STATIC_CACHE_URLS.map(
        (url) =>
          new Request(url, {
            cache: 'reload',
          })
      )
    );
    console.log('Service Worker: Cache updated successfully');
  } catch (error) {
    console.error('Service Worker: Cache update failed:', error);
  }
}

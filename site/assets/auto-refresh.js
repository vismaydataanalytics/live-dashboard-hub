/* Check a tiny same-origin release marker instead of downloading the dashboard. */
(() => {
  'use strict';
  const script = document.currentScript;
  const version = document.querySelector('meta[name="dashboard-version"]')?.content;
  if (!script || !/^[a-f0-9]{40}$/.test(version || '') || !/^https?:$/.test(location.protocol)) return;
  const marker = new URL('../version.json', script.src);
  if (marker.origin !== location.origin) return;
  const parameter = '_dashboard_version';
  const storageKey = 'dashboard-auto-refresh:' + location.pathname;
  const current = new URL(location.href);
  if (current.searchParams.get(parameter) === version) {
    current.searchParams.delete(parameter);
    history.replaceState(history.state, '', current.href);
    try { sessionStorage.removeItem(storageKey); } catch (_) { /* Storage may be disabled. */ }
  }
  let busy = false;
  async function check() {
    if (busy) return;
    busy = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const request = new URL(marker.href);
      request.searchParams.set('t', String(Date.now()));
      const response = await fetch(request.href, {
        cache: 'no-store', mode: 'same-origin', credentials: 'omit', signal: controller.signal
      });
      if (!response.ok) return;
      const release = await response.json();
      if (!/^[a-f0-9]{40}$/.test(release.version || '') || release.version === version) return;
      // If an edge temporarily serves old HTML, limit repeated reload attempts.
      try {
        const attempt = JSON.parse(sessionStorage.getItem(storageKey) || 'null');
        if (attempt?.version === release.version && attempt.until > Date.now()) return;
        sessionStorage.setItem(storageKey, JSON.stringify({version: release.version, until: Date.now() + 120000}));
      } catch (_) { /* Refresh still works when browser storage is unavailable. */ }
      const target = new URL(location.href);
      target.searchParams.set(parameter, release.version);
      location.replace(target.href);
    } catch (_) {
      // An offline viewer keeps the working dashboard; retry on the next check.
    } finally {
      clearTimeout(timeout);
      busy = false;
    }
  }
  setInterval(check, 30000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) check(); });
  window.addEventListener('focus', check);
  window.addEventListener('pageshow', check);
  check();
})();

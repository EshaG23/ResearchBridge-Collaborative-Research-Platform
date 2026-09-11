(() => {
  const trigger = document.querySelector('[data-notification-poll]');
  if (!trigger) return;
  let busy = false;
  let firstIds = null;
  async function refresh() {
    if (busy || document.hidden) return;
    busy = true;
    try {
      const response = await fetch(trigger.dataset.notificationPoll, {credentials:'same-origin', headers:{Accept:'application/json'}, cache:'no-store'});
      if (!response.ok || !(response.headers.get('content-type') || '').includes('application/json')) return;
      const data = await response.json();
      document.querySelectorAll('[data-unread-count]').forEach(el => { el.textContent = data.unread_count; });
      trigger.setAttribute('aria-label', 'Notifications, ' + data.unread_count + ' unread');
      const ids = data.items.map(item => item.id).join(',');
      const refreshNote = document.querySelector('[data-notification-refresh]');
      if (refreshNote && firstIds !== null && ids !== firstIds) refreshNote.hidden = false;
      if (firstIds === null) firstIds = ids;
    } catch (_) { /* Retain last known count; retry on the next interval. */ }
    finally { busy = false; }
  }
  refresh();
  setInterval(refresh, 30000);
  document.addEventListener('visibilitychange', refresh);
})();

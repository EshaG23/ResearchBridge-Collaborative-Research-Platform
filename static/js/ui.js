(() => {
  const toggle = document.querySelector('[data-nav-toggle]');
  const sidebar = document.querySelector('#sidebar');
  const closeNavigation = () => { document.body.classList.remove('nav-open'); toggle?.setAttribute('aria-expanded', 'false'); };
  toggle?.addEventListener('click', () => { const open = document.body.classList.toggle('nav-open'); toggle.setAttribute('aria-expanded', String(open)); });
  document.addEventListener('click', (event) => {
    document.querySelectorAll('details.popover[open]').forEach(panel => { if (!panel.contains(event.target)) panel.open = false; });
    if (sidebar && !sidebar.contains(event.target) && !toggle?.contains(event.target)) closeNavigation();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const open = document.querySelector('details.popover[open]');
    if (open) { open.open = false; open.querySelector('summary').focus(); }
    if (document.body.classList.contains('nav-open')) { closeNavigation(); toggle?.focus(); }
  });
  document.querySelectorAll('details.popover').forEach(panel => panel.addEventListener('toggle', () => { if (panel.open) document.querySelectorAll('details.popover[open]').forEach(other => { if (other !== panel) other.open = false; }); }));
  const feedback = document.querySelector('[data-demo-feedback]');
  const status = document.querySelector('[data-demo-status]');
  let timer;
  feedback?.addEventListener('click', () => {
    feedback.disabled = true; feedback.setAttribute('aria-busy', 'true'); feedback.textContent = 'Showing feedback…';
    status.textContent = 'Loading example…';
    timer = setTimeout(() => { feedback.disabled = false; feedback.removeAttribute('aria-busy'); feedback.textContent = 'Try feedback'; status.textContent = 'Feedback example complete. No data was saved.'; }, 700);
  });
  document.querySelector('[data-demo-reset]')?.addEventListener('click', () => { clearTimeout(timer); feedback.disabled = false; feedback.removeAttribute('aria-busy'); feedback.textContent = 'Try feedback'; status.textContent = 'This interaction does not save data.'; });
})();

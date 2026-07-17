(() => {
  const root = document.documentElement;
  const sidebar = document.querySelector('[data-sidebar]');
  const scrim = document.querySelector('[data-scrim]');
  const menu = document.querySelector('[data-menu]');
  const theme = document.querySelector('[data-theme]');

  let savedTheme = null;
  try { savedTheme = localStorage.getItem('spec-theme'); } catch (_) { savedTheme = null; }
  if (savedTheme === 'dark' || savedTheme === 'light') root.dataset.theme = savedTheme;

  const closeMenu = () => {
    document.body.classList.remove('nav-open');
    menu?.setAttribute('aria-expanded', 'false');
  };
  menu?.addEventListener('click', () => {
    const open = document.body.classList.toggle('nav-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  scrim?.addEventListener('click', closeMenu);
  sidebar?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
  theme?.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('spec-theme', next); } catch (_) { /* Theme still applies for this page. */ }
  });
})();

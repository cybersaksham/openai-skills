(() => {
  const root = document.documentElement;
  const body = document.body;
  const storedTheme = window.localStorage.getItem('product-specs-theme');
  const preferredDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  root.dataset.theme = storedTheme || (preferredDark ? 'dark' : 'light');

  const sectionRedirect = [...document.querySelectorAll('[data-section-redirect]')]
    .find((link) => `#${link.id}` === window.location.hash);
  if (sectionRedirect) {
    window.location.replace(sectionRedirect.href);
    return;
  }

  const closeNavigation = () => body.classList.remove('nav-open');
  document.querySelector('[data-menu]')?.addEventListener('click', () => body.classList.toggle('nav-open'));
  document.querySelector('[data-nav-close]')?.addEventListener('click', closeNavigation);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeNavigation();
  });
  document.querySelectorAll('.sidebar a').forEach((link) => link.addEventListener('click', closeNavigation));

  const themeToggle = document.querySelector('[data-theme-toggle]');
  const updateThemeLabel = () => {
    if (themeToggle) themeToggle.textContent = root.dataset.theme === 'dark' ? 'Light mode' : 'Dark mode';
  };
  updateThemeLabel();
  themeToggle?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    window.localStorage.setItem('product-specs-theme', root.dataset.theme);
    updateThemeLabel();
  });

  const activeSidebarLink = document.querySelector('.sidebar [aria-current="page"]');
  if (activeSidebarLink) {
    requestAnimationFrame(() => {
      const navigation = activeSidebarLink.closest('.documentation-nav');
      const navigationBounds = navigation?.getBoundingClientRect();
      const activeBounds = activeSidebarLink.getBoundingClientRect();
      if (
        navigationBounds
        && (activeBounds.top < navigationBounds.top + 36 || activeBounds.bottom > navigationBounds.bottom - 36)
      ) {
        activeSidebarLink.scrollIntoView({ block: 'center' });
      }
    });
  }

  document.querySelectorAll('table').forEach((table) => {
    if (table.parentElement?.classList.contains('table-wrap')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrap';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  document.querySelectorAll('pre').forEach((pre) => {
    if (pre.parentElement?.classList.contains('pre-wrap')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'pre-wrap';
    const button = document.createElement('button');
    button.className = 'copy-code';
    button.type = 'button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code block');
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);
    wrapper.appendChild(button);
    button.addEventListener('click', async () => {
      await navigator.clipboard.writeText(pre.innerText);
      button.textContent = 'Copied';
      window.setTimeout(() => { button.textContent = 'Copy'; }, 1200);
    });
  });

  const tocLinks = [...document.querySelectorAll('.page-toc a')];
  const tocTargets = tocLinks
    .map((link) => document.getElementById(decodeURIComponent(link.hash.slice(1))))
    .filter(Boolean);
  if (tocLinks.length && tocTargets.length && 'IntersectionObserver' in window) {
    const byId = new Map(tocLinks.map((link) => [decodeURIComponent(link.hash.slice(1)), link]));
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top)[0];
      if (!visible) return;
      tocLinks.forEach((link) => link.classList.remove('is-active'));
      byId.get(visible.target.id)?.classList.add('is-active');
    }, { rootMargin: '-72px 0px -72% 0px', threshold: [0, 1] });
    tocTargets.forEach((target) => observer.observe(target));
  }
})();

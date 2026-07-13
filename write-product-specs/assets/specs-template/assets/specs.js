(() => {
  const body = document.body;
  const menu = document.querySelector('[data-menu]');
  if (menu) menu.addEventListener('click', () => body.classList.toggle('nav-open'));

  document.querySelectorAll('.sidebar a').forEach((link) => {
    link.addEventListener('click', () => body.classList.remove('nav-open'));
  });

  const search = document.querySelector('[data-spec-search]');
  if (search) {
    search.addEventListener('input', (event) => {
      const query = event.target.value.trim().toLowerCase();
      document.querySelectorAll('[data-searchable]').forEach((element) => {
        element.dataset.hidden = !query || element.textContent.toLowerCase().includes(query) ? 'false' : 'true';
      });
    });
  }

  document.querySelectorAll('table').forEach((table) => {
    if (table.parentElement?.classList.contains('table-wrap')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrap';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });
})();

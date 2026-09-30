// ---- Dark mode ----
document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('theme-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      const html = document.documentElement;
      const current = html.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      toggleBtn.textContent = next === 'dark' ? '☀️ Light' : '🌙 Dark';
      fetch(`/core/theme/?theme=${next}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    });
  }

  // ---- Live search ----
  const searchInput = document.getElementById('global-search');
  const searchResults = document.getElementById('search-results');
  if (searchInput && searchResults) {
    let debounceTimer;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const q = this.value.trim();
      if (q.length < 2) {
        searchResults.classList.remove('active');
        searchResults.innerHTML = '';
        return;
      }
      debounceTimer = setTimeout(() => {
        fetch(`/core/search/?q=${encodeURIComponent(q)}`)
          .then(r => r.json())
          .then(data => renderSearchResults(data));
      }, 250);
    });

    document.addEventListener('click', function (e) {
      if (!searchResults.contains(e.target) && e.target !== searchInput) {
        searchResults.classList.remove('active');
      }
    });
  }

  function renderSearchResults(data) {
    const sections = [
      { key: 'notes', label: 'Notes' },
      { key: 'tasks', label: 'Tasks' },
      { key: 'resources', label: 'Resources' },
    ];
    let html = '';
    let hasAny = false;
    sections.forEach(({ key, label }) => {
      const items = data[key] || [];
      if (items.length) {
        hasAny = true;
        html += `<h5>${label}</h5>`;
        items.forEach(item => {
          html += `<a href="${item.url}">${item.title}</a>`;
        });
      }
    });
    if (!hasAny) {
      html = '<div class="search-empty">No results found.</div>';
    }
    searchResults.innerHTML = html;
    searchResults.classList.add('active');
  }

  // ---- Task complete toggle (AJAX) ----
  document.querySelectorAll('.task-toggle').forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
      const url = this.dataset.url;
      const row = this.closest('.task-row');
      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      })
        .then(r => r.json())
        .then(data => {
          if (row) row.classList.toggle('completed', data.is_completed);
        });
    });
  });

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }
  window.getCookie = getCookie;
});

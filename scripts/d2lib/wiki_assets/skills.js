/* Progressive enhancement: source comparisons remain readable without JS. */
(() => {
  const root = document.querySelector('[data-skill-explorer]');
  if (!root) return;
  const search = root.querySelector('#skill-search');
  const status = root.querySelector('#skill-status');
  const cards = [...root.querySelectorAll('[data-skill-card]')];
  const header = document.querySelector('.masthead');
  function headerOffset() {
    const sticky = header && ['sticky', 'fixed'].includes(getComputedStyle(header).position);
    root.style.setProperty('--skill-scroll-offset', `${sticky ? header.getBoundingClientRect().height + 16 : 16}px`);
  }
  headerOffset();
  if (header) new ResizeObserver(headerOffset).observe(header);
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  const selected = params.get('status');
  if ([...status.options].some(option => option.value === selected)) status.value = selected;
  function apply() {
    const mastSearch = document.querySelector('#mast-search-input');
    if (mastSearch) mastSearch.value = search.value;
    const terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const haystack = card.dataset.search.toLowerCase();
      card.hidden = !terms.every(term => haystack.includes(term)) ||
        (status.value !== 'all' && status.value !== card.dataset.status);
      if (!card.hidden) visible++;
    }
    root.querySelector('#skill-results').textContent = `${visible} of ${cards.length} skills`;
    root.querySelector('#skill-empty').hidden = visible !== 0;
    root.querySelector('.item-family-section').hidden = visible === 0;
    const url = new URL(location.href);
    for (const [name, val, fallback] of [['q', search.value.trim(), ''], ['status', status.value, 'all']]) {
      if (val === fallback) url.searchParams.delete(name);
      else url.searchParams.set(name, val);
    }
    if (url.href !== location.href) history.replaceState(null, '', url);
  }
  search.addEventListener('input', apply);
  status.addEventListener('change', apply);
  root.querySelector('#skill-reset-filters').addEventListener('click', () => {
    search.value = '';
    status.value = 'all';
    apply();
  });
  function revealHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = cards.find(card => card.id === id);
    if (!target) return;
    if (target.hidden) {
      search.value = '';
      status.value = 'all';
      apply();
    }
    target.scrollIntoView({block: 'start'});
  }
  window.addEventListener('hashchange', revealHash);
  apply();
  if (location.hash) revealHash();
})();

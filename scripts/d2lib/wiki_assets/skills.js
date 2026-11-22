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
  const damageControls = root.querySelector('[data-damage-controls]');
  const damagePoints = root.querySelector('#skill-damage-points');
  const maxSynergies = root.querySelector('#skill-max-synergies');
  const damageRows = [...root.querySelectorAll('[data-skill-damage]')].map(row => ({
    row, data: JSON.parse(row.dataset.skillDamage)
  }));
  if (damageControls) {
    damageControls.hidden = false;
    const savedPoints = params.get('points');
    if (/^[1-9]\d?$/.test(savedPoints || '')) damagePoints.value = savedPoints;
    maxSynergies.checked = params.get('synergies') !== 'none';
  }
  function updateDamage() {
    if (!damageControls) return;
    const points = damagePoints.valueAsNumber;
    const preset = maxSynergies.checked ? 'max' : 'none';
    for (const {row, data} of damageRows) {
      for (const output of row.querySelectorAll('[data-damage-side]')) {
        const skill = data[output.dataset.damageSide];
        if (!skill) {
          output.textContent = '—';
          continue;
        }
        const level = Number.isFinite(points) ? Math.min(skill.cap, Math.max(1, Math.trunc(points))) : skill.cap;
        const lines = [`${level} hard points`];
        for (const component of skill.components) {
          const [min, max] = component.presets[preset][level - 1];
          lines.push(`${component.label} ${min}–${max}`);
        }
        if (skill.omitted.length) lines.push(`Unavailable here: ${skill.omitted.join(', ')}`);
        output.textContent = lines.join('\n');
      }
      row.hidden = false;
    }
  }
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
    if (damageControls) {
      if (damagePoints.value && damagePoints.validity.valid) url.searchParams.set('points', damagePoints.value);
      else url.searchParams.delete('points');
      if (maxSynergies.checked) url.searchParams.delete('synergies');
      else url.searchParams.set('synergies', 'none');
    }
    if (url.href !== location.href) history.replaceState(null, '', url);
  }
  search.addEventListener('input', apply);
  status.addEventListener('change', apply);
  damageControls?.addEventListener('input', () => {
    updateDamage();
    apply();
  });
  root.querySelector('#skill-reset-filters').addEventListener('click', () => {
    search.value = '';
    status.value = 'all';
    if (damageControls) {
      damagePoints.value = '';
      maxSynergies.checked = true;
      updateDamage();
    }
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
  updateDamage();
  apply();
  if (location.hash) revealHash();
})();

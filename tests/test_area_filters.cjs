const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function control(value) {
  return {
    value,
    checked: false,
    dataset: {},
    listeners: {},
    addEventListener(event, fn) {
      this.listeners[event] = fn;
    },
  };
}

test('area filters use integer act_id, canonical immunity codes, and localized labels', async () => {
  const immunityMeta = {
    fire: {label: 'Feuer', immunity_label: 'Immun gegen Feuer', chip_class: 'im-fire'},
    cold: {label: 'Kälte', immunity_label: 'Immun gegen Kälte', chip_class: 'im-cold'},
    physical: {label: 'Körperschäden', immunity_label: 'Immun gegen Körperschäden', chip_class: 'im-physical'},
  };
  const areas = [
    {
      display_name: 'Kalte Höhle',
      level_id: 10,
      act_id: 0,
      act: 'Akt 1',
      area_level: 87,
      monster_density: 5000,
      elite_min: 10,
      elite_max: 12,
      elite_avg: 11,
      estimated_area_tiles: 2304,
      maze_chunk_width: 24,
      maze_chunk_height: 24,
      maze_rooms: 4,
      maze_source: 'lvlmaze',
      has_super_chest: true,
      super_chest_count: 1,
      super_chest_sources: [{object_class: 'ConsolationChest', chest_kind: 'sparkly'}],
      possible_immunities: ['cold', 'fire'],
      immunity_counts: {cold: 1, fire: 2},
      immunity_labels: {cold: 'Kälte', fire: 'Feuer'},
      immunity_descriptions: {cold: 'Immun gegen Kälte', fire: 'Immun gegen Feuer'},
      monster_pool: [{id: 'coldbeast', name: 'Kältebestie', immunities: ['cold']}],
      search_text: 'Kalte Höhle Akt 1 Kältebestie Immun gegen Kälte',
    },
    {
      display_name: 'Unter-Kurast',
      level_id: 79,
      act_id: 2,
      act: 'Akt 3',
      area_level: 85,
      monster_density: 1200,
      elite_min: 2,
      elite_max: 4,
      elite_avg: 3,
      estimated_area_tiles: 40000,
      maze_chunk_width: 200,
      maze_chunk_height: 200,
      maze_rooms: 1,
      maze_source: 'levels',
      has_super_chest: true,
      super_chest_count: 2,
      super_chest_sources: [{object_class: 'PlaceUniqueChest', chest_kind: 'super'}],
      possible_immunities: ['physical'],
      immunity_counts: {physical: 1},
      immunity_labels: {physical: 'Körperschäden'},
      immunity_descriptions: {physical: 'Immun gegen Körperschäden'},
      monster_pool: [{id: 'stonebeast', name: 'Steinbestie', immunities: ['physical']}],
      search_text: 'Unter-Kurast Akt 3 Steinbestie Immun gegen Körperschäden',
    },
  ];

  const toolbar = {
    dataset: {
      areaIndexUrl: '../data/areas-index.json',
      immunityMeta: JSON.stringify(immunityMeta),
    },
  };
  const root = {innerHTML: ''};
  const cardRoot = {innerHTML: ''};
  const resultCount = {textContent: ''};
  const search = control('');
  const actSelect = control('all');
  const minLevelSelect = control('0');
  const sortSelect = control('density');
  const avoidFire = control('');
  avoidFire.dataset = {avoidImmunity: 'fire'};
  const avoidCold = control('');
  avoidCold.dataset = {avoidImmunity: 'cold'};

  const selectors = {
    '[data-area-index-url]': toolbar,
    '#area-index-root': root,
    '#area-card-root': cardRoot,
    '#area-result-count': resultCount,
    '#area-search': search,
    '#area-act-filter': actSelect,
    '#area-min-level-filter': minLevelSelect,
    '#area-sort-filter': sortSelect,
  };
  const document = {
    readyState: 'loading',
    addEventListener() {},
    querySelector: (selector) => selectors[selector] || null,
    querySelectorAll: (selector) => (selector === '[data-avoid-immunity]' ? [avoidFire, avoidCold] : []),
  };
  const context = {
    document,
    window: {location: {search: ''}},
    URLSearchParams,
    fetch: async () => ({json: async () => areas}),
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8'), context);
  await vm.runInContext('wireAreaIndex()', context);

  assert.equal(resultCount.textContent, '2');
  assert.ok(root.innerHTML.includes('Feuer (2)'));
  assert.ok(root.innerHTML.includes('Immun gegen Kälte'));
  assert.ok(!root.innerHTML.includes(' immune'));
  assert.ok(root.innerHTML.includes('area-badge-sparkly'));
  assert.ok(root.innerHTML.includes('Sparkly Chest'));
  assert.ok(root.innerHTML.includes('area-badge-super'));
  assert.ok(root.innerHTML.includes('Super Chest'));
  assert.ok(!root.innerHTML.includes('ConsolationChest'));
  assert.ok(!root.innerHTML.includes('PlaceUniqueChest'));
  assert.ok(cardRoot.innerHTML.includes('Sparkly Chest'));
  assert.ok(cardRoot.innerHTML.includes('Super Chest'));
  assert.ok(cardRoot.innerHTML.includes('Immun gegen Körperschäden'));

  // Act 1 uses integer act_id = 0 (must not treat 0 as falsy) even with localized act label 'Akt 1'
  actSelect.value = '0';
  actSelect.listeners.change();
  assert.equal(resultCount.textContent, '1');
  assert.ok(root.innerHTML.includes('Kalte Höhle'));
  assert.ok(!root.innerHTML.includes('Unter-Kurast'));

  // Avoid fire hides Kalte Höhle via canonical code 'fire' while keeping Unter-Kurast when act=all
  actSelect.value = 'all';
  avoidFire.checked = true;
  avoidFire.listeners.change();
  assert.equal(resultCount.textContent, '1');
  assert.ok(root.innerHTML.includes('Unter-Kurast'));
  assert.ok(!root.innerHTML.includes('Kalte Höhle'));
});

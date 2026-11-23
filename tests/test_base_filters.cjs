const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

test('runeword base links match every allowed type, exclusions and sockets', () => {
  const makeItem = (codes, sockets, loot) => ({
    dataset: {typeCodes: codes, maxSockets: String(sockets), lootCategory: loot}, style: {},
  });
  const items = [makeItem('mace|blun|mele|weap', 4, 'Maces'),
    makeItem('swor|mele|weap', 3, 'Swords'), makeItem('hamm|blun|mele|weap', 4, 'Maces'),
    makeItem('mace|blun|mele|weap', 2, 'Maces')];
  const family = {dataset: {baseGroup: 'Weapons'}, style: {}, querySelectorAll: () => items};
  const listeners = {};
  const loot = {value: 'all', addEventListener: (event, handler) => {listeners[event] = handler;}};
  const sockets = {value: '0', options: [{value: '3'}], addEventListener() {}};
  const notice = {hidden: true};
  const elements = {'[data-base-filters]': {}, '#base-loot-filter': loot,
    '#base-min-sockets-filter': sockets, '#base-runeword-notice': notice};
  const document = {readyState: 'loading', addEventListener() {},
    querySelector: selector => elements[selector] || null,
    querySelectorAll: selector => selector === '.family-container' ? [family] : []};
  const context = {document, window: {location: {search: '?types=blun%7Cswor&exclude=hamm&minSockets=3'}}, URLSearchParams};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8') + '\nwireBaseFilters();', context);
  assert.deepEqual(items.map(item => item.hidden), [false, false, true, true]);
  assert.equal(notice.hidden, false);
  loot.value = 'Maces';
  listeners.change();
  assert.deepEqual(items.map(item => item.hidden), [false, true, true, true]);
});

test('base filters match canonical tier keys with localized labels and numeric WSM speeds', () => {
  const makeItem = (tier, speed, codes = 'swor|mele|weap', lootCategory = 'Swords') => ({
    dataset: {typeCodes: codes, maxSockets: '4', lootCategory, tier, speed},
    style: {},
  });
  const items = [
    makeItem('normal', '0'),
    makeItem('elite', '-30'),
    makeItem('elite', '20'),
    makeItem('elite', '', 'helm|armo', 'Helms'),
  ];
  const family = {dataset: {baseGroup: 'Weapons'}, style: {}, querySelectorAll: () => items};
  const listeners = {};
  const tierSelect = {
    value: 'all',
    options: [
      {value: 'all', textContent: 'All tiers'},
      {value: 'normal', textContent: '보통'},
      {value: 'exceptional', textContent: '특급'},
      {value: 'elite', textContent: '정예'},
    ],
    addEventListener(event, handler) { listeners[`tier:${event}`] = handler; },
  };
  const speedSelect = {
    value: 'all',
    options: [
      {value: 'all', textContent: 'All speeds'},
      {value: '-30', textContent: '-30'},
      {value: '0', textContent: '0'},
      {value: '20', textContent: '20'},
    ],
    addEventListener(event, handler) { listeners[`speed:${event}`] = handler; },
  };
  const elements = {'[data-base-filters]': {}, '#base-tier-filter': tierSelect, '#base-speed-filter': speedSelect};
  const document = {
    readyState: 'loading',
    addEventListener() {},
    querySelector: selector => elements[selector] || null,
    querySelectorAll: selector => selector === '.family-container' ? [family] : [],
  };
  const context = {
    document,
    window: {location: {search: '?tier=%EC%A0%95%EC%98%88&speed=-30'}},
    URLSearchParams,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8') + '\nwireBaseFilters();', context);
  assert.equal(tierSelect.value, 'elite');
  assert.equal(speedSelect.value, '-30');
  assert.deepEqual(items.map(item => item.hidden), [true, false, true, true]);

  tierSelect.value = 'all';
  speedSelect.value = '0';
  listeners['speed:change']();
  assert.deepEqual(items.map(item => item.hidden), [false, true, true, true]);

  speedSelect.value = 'all';
  tierSelect.value = 'elite';
  listeners['tier:change']();
  assert.deepEqual(items.map(item => item.hidden), [true, false, false, false]);
});

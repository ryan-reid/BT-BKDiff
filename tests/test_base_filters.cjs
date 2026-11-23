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

test('base filters match canonical tier and speed keys with localized option labels and query params', () => {
  const makeItem = (tier, speed, speedLabel) => ({
    dataset: {typeCodes: 'swor|mele|weap', maxSockets: '4', lootCategory: 'Swords', tier, speed, speedLabel},
    style: {},
  });
  const items = [
    makeItem('normal', 'fast', '빠른 공격 속도'),
    makeItem('elite', 'very_fast', '매우 빠른 공격 속도'),
    makeItem('elite', 'slow', '느린 공격 속도'),
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
      {value: 'very_fast', textContent: '매우 빠른 공격 속도'},
      {value: 'fast', textContent: '빠른 공격 속도'},
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
    window: {location: {search: '?tier=%EC%A0%95%EC%98%88&speed=very_fast'}},
    URLSearchParams,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8') + '\nwireBaseFilters();', context);
  assert.equal(tierSelect.value, 'elite');
  assert.equal(speedSelect.value, 'very_fast');
  assert.deepEqual(items.map(item => item.hidden), [true, false, true]);

  speedSelect.value = 'all';
  listeners['speed:change']();
  assert.deepEqual(items.map(item => item.hidden), [true, false, false]);
});

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

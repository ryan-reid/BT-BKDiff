const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

test('item filters enhance existing server-rendered cards without downloading or replacing history', async () => {
  function control(value) {
    return {value, listeners: {}, addEventListener(event, fn) {this.listeners[event] = fn;}};
  }
  const search = control('');
  const type = control('all');
  const drop = control('0');
  const cards = [
    {dataset: {family: 'unique', itemGroup: 'Weapons', itemType: 'Maces', search: 'test mace', dropLevel: '90'}},
    {dataset: {family: 'runeword', itemGroup: 'Armor|Weapons', itemType: 'Maces|Shields', search: 'test word', dropLevel: '0'}},
    {dataset: {family: 'set', itemGroup: 'Armor', itemType: 'Helms', search: 'test helm', dropLevel: '75'}},
  ];
  const root = {set innerHTML(_) {throw Error('Must not replace server-rendered cards');}};
  const selectors = {'[data-item-index-url]': {}, '#item-index-root': root,
    '#page-search': search, '#item-type-filter': type, '#item-drop-level-filter': drop};
  const document = {readyState: 'loading', addEventListener() {},
    querySelector: selector => selectors[selector] || null,
    querySelectorAll: selector => selector === '.base-item-card[data-family]' ? cards : []};
  const context = {document, window: {location: {search: ''}}, URLSearchParams,
    fetch: () => {throw Error('Should not download the item index again');}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8'), context);
  await vm.runInContext('wireItemIndex()', context);
  assert.deepEqual(cards.map(card => card.hidden), [false, false, false]);
  type.value = 'Maces';
  type.listeners.change();
  assert.deepEqual(cards.map(card => card.hidden), [false, false, true]);
  drop.value = '85';
  drop.listeners.change();
  assert.deepEqual(cards.map(card => card.hidden), [false, true, true]);
  search.value = 'absent';
  search.listeners.input();
  assert.deepEqual(cards.map(card => card.hidden), [true, true, true]);
});

test('item filters match canonical group/type codes even when optgroup labels are localized', async () => {
  function control(value, extra = {}) {
    return {value, listeners: {}, addEventListener(event, fn) {this.listeners[event] = fn;}, ...extra};
  }
  const armorOptgroup = {tagName: 'OPTGROUP', label: '갑옷', dataset: {groupCode: 'armor'}};
  const weaponOptgroup = {tagName: 'OPTGROUP', label: '무기', dataset: {groupCode: 'weapons'}};
  const typeOptions = [
    {value: 'all', textContent: '모든 종류', parentElement: null},
    {value: 'hlms', textContent: '투구', parentElement: armorOptgroup},
    {value: 'mace', textContent: '철퇴', parentElement: weaponOptgroup},
  ];
  const group = control('all', {
    options: [
      {value: 'all', textContent: 'All Groups'},
      {value: 'armor', textContent: '갑옷'},
      {value: 'weapons', textContent: '무기'},
    ],
  });
  const type = control('all', {options: typeOptions});
  const drop = control('0');
  const cards = [
    {dataset: {family: 'unique', itemGroup: 'weapons', itemType: 'mace', search: '테스트 철퇴', dropLevel: '90'}},
    {dataset: {family: 'runeword', itemGroup: 'armor|weapons', itemType: 'mace|hlms', search: '룬워드', dropLevel: '0'}},
    {dataset: {family: 'set', itemGroup: 'armor', itemType: 'hlms', search: '세트 투구', dropLevel: '75'}},
  ];
  const root = {set innerHTML(_) {throw Error('Must not replace server-rendered cards');}};
  const selectors = {
    '[data-item-index-url]': {},
    '#item-index-root': root,
    '#item-group-filter': group,
    '#item-type-filter': type,
    '#item-drop-level-filter': drop,
  };
  const document = {
    readyState: 'loading',
    addEventListener() {},
    querySelector: selector => selectors[selector] || null,
    querySelectorAll: selector => selector === '.base-item-card[data-family]' ? cards : [],
  };
  const context = {
    document,
    window: {location: {search: ''}},
    URLSearchParams,
    fetch: () => {throw Error('Should not download the item index again');},
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8'), context);
  await vm.runInContext('wireItemIndex()', context);

  type.value = 'mace';
  type.listeners.change();
  assert.deepEqual(cards.map(card => card.hidden), [false, false, true]);

  group.value = 'armor';
  group.listeners.change();
  assert.equal(type.value, 'all');
  assert.deepEqual(cards.map(card => card.hidden), [true, false, false]);

  type.value = 'hlms';
  type.listeners.change();
  assert.deepEqual(cards.map(card => card.hidden), [true, false, false]);
});

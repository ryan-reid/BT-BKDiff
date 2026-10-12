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

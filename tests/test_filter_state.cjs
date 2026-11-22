const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8');

function setup(url, fields, collections = {}) {
  const handlers = {};
  const document = {
    readyState: 'loading',
    querySelector: selector => fields[selector] || null,
    querySelectorAll: selector => collections[selector] || [],
    addEventListener(event, handler) {(handlers[event] ||= []).push(handler);},
  };
  const window = {
    location: new URL(url),
    history: {replaceState(_state, _title, href) {window.location = new URL(href);}},
  };
  vm.runInNewContext(script + '\nwireFilterState();', {document, window, URL, URLSearchParams});
  return {window, fire(event, target) {for (const handler of handlers[event] || []) handler({target});}};
}
function select(values) {
  return {tagName: 'SELECT', value: values[0], options: values.map(value => ({value, textContent: value}))};
}

test('area choices restore on reload and remain in the comparison URL context', () => {
  const act = select(['all', 'Act 1', 'Act 2']);
  const level = select(['0', '85', '90']);
  const sort = select(['density', 'elite']);
  const fire = {type: 'checkbox', checked: false, dataset: {avoidImmunity: 'fire'}};
  const fields = {'#area-act-filter': act, '#area-min-level-filter': level, '#area-sort-filter': sort};
  const state = setup('https://example.com/areas/?act=Act+1&minLevel=85&sort=elite&avoid=fire&extra=keep#areas', fields,
    {'[data-avoid-immunity]': [fire]});
  assert.equal(act.value, 'Act 1');
  assert.equal(level.value, '85');
  assert.equal(sort.value, 'elite');
  assert.equal(fire.checked, true);
  act.value = 'Act 2';
  state.fire('change', act);
  assert.equal(state.window.location.searchParams.get('act'), 'Act 2');
  assert.equal(state.window.location.searchParams.get('extra'), 'keep');
  assert.equal(state.window.location.hash, '#areas');
  const reloadedAct = select(['all', 'Act 1', 'Act 2']);
  setup(state.window.location.href, {'#area-act-filter': reloadedAct});
  assert.equal(reloadedAct.value, 'Act 2');
});

test('rune clicks save the updated selection and clearing removes old aliases', () => {
  const rune = {dataset: {runeCode: 'r31'}, selected: false,
    getAttribute() {return this.selected ? 'true' : 'false';}};
  const state = setup('https://example.com/runewords/?have=Jah', {}, {'[data-rune-option]': [rune]});
  const target = {closest: () => rune};
  rune.selected = true;
  state.fire('click', target);
  assert.equal(state.window.location.searchParams.get('runes'), 'r31');
  assert.equal(state.window.location.searchParams.has('have'), false);
  rune.selected = false;
  state.fire('click', target);
  assert.equal(state.window.location.searchParams.has('runes'), false);
});

test('an empty quality selection survives reload rather than selecting everything', () => {
  const qualities = ['unique', 'set', 'runeword'].map(filterFamily =>
    ({checked: true, dataset: {filterFamily}}));
  const state = setup('https://example.com/items/?qualities=', {}, {'[data-filter-family]': qualities});
  assert.ok(qualities.every(control => !control.checked));
  state.fire('change', qualities[0]);
  assert.equal(state.window.location.searchParams.get('qualities'), '');
  qualities.forEach(control => {control.checked = true;});
  state.fire('change', qualities[0]);
  assert.equal(state.window.location.searchParams.has('qualities'), false);
});

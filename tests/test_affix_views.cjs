const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8');

function setup({url = 'https://example.test/references/affixes/', active = 'function',
  saved = null, defaultEntry = true, storageBlocked = false} = {}) {
  const preferences = new Map(saved === null ? [] : [['wiki.affixView', saved]]);
  const redirects = [];
  const root = url.includes('/compare-bt/') ? '/compare-bt/' : '/';
  const links = ['function', 'cards'].map(view => ({
    dataset: {affixViewLink: view},
    href: new URL(root + 'references/affixes/' + (view === 'cards' ? 'cards/' : ''), url).href,
    handlers: {},
    addEventListener(event, handler) {this.handlers[event] = handler;},
  }));
  const toggle = {
    dataset: {affixView: active},
    querySelectorAll() {return links;},
    hasAttribute() {return defaultEntry;},
  };
  const window = {
    location: new URL(url),
    localStorage: {
      getItem(key) {
        if (storageBlocked) throw new Error('Storage unavailable');
        return preferences.get(key) ?? null;
      },
      setItem(key, value) {
        if (storageBlocked) throw new Error('Storage unavailable');
        preferences.set(key, value);
      },
    },
  };
  window.location.replace = href => redirects.push(href);
  const document = {
    readyState: 'loading',
    querySelector: selector => selector === '[data-affix-view]' ? toggle : null,
    querySelectorAll: () => [],
    addEventListener() {},
  };
  const redirected = vm.runInNewContext(script + '\nwireAffixView();', {document, window, URL});
  return {links, preferences, redirects, redirected, window};
}

test('Affixes defaults to the function view without a saved preference', () => {
  const state = setup();
  assert.equal(state.redirected, false);
  assert.equal(state.preferences.get('wiki.affixView'), 'function');
});

test('returning to Affixes restores the chosen card view and query context', () => {
  const state = setup({saved: 'cards',
    url: 'https://example.test/compare-bt/references/affixes/?q=Frost&type=ring&rare=1#section'});
  assert.equal(state.redirects.length, 1);
  const target = new URL(state.redirects[0]);
  assert.equal(target.pathname, '/compare-bt/references/affixes/cards/');
  assert.equal(target.searchParams.get('q'), 'Frost');
  assert.equal(target.searchParams.get('type'), 'ring');
  assert.equal(target.searchParams.get('rare'), '1');
  assert.equal(target.hash, '#section');
});

test('explicit links override saved preferences without redirect loops', () => {
  const functionView = setup({saved: 'cards', url: 'https://example.test/references/affixes/?view=function'});
  assert.equal(functionView.redirected, false);
  assert.equal(functionView.preferences.get('wiki.affixView'), 'function');
  const cards = setup({saved: 'function', active: 'cards', defaultEntry: false,
    url: 'https://example.test/references/affixes/cards/?view=cards'});
  assert.equal(cards.redirected, false);
  assert.equal(cards.preferences.get('wiki.affixView'), 'cards');
});

test('clicking the view toggle saves the selection and current filters', () => {
  const state = setup();
  state.window.location = new URL('https://example.test/references/affixes/?q=Mana&type=amul&rare=1');
  const cards = state.links.find(link => link.dataset.affixViewLink === 'cards');
  cards.handlers.click();
  assert.equal(state.preferences.get('wiki.affixView'), 'cards');
  assert.equal(new URL(cards.href).searchParams.get('q'), 'Mana');
  assert.equal(new URL(cards.href).searchParams.get('view'), 'cards');
});

test('legacy function bookmarks remain explicit even with a saved card view', () => {
  const state = setup({saved: 'cards', defaultEntry: false,
    url: 'https://example.test/references/affixes-by-function/?q=Mana'});
  assert.equal(state.redirected, false);
  assert.equal(state.preferences.get('wiki.affixView'), 'function');
});

test('blocked storage and invalid preferences preserve working view links', () => {
  const blocked = setup({storageBlocked: true});
  assert.equal(blocked.redirected, false);
  assert.doesNotThrow(() => blocked.links[1].handlers.click());
  const invalid = setup({saved: 'invalid'});
  assert.equal(invalid.redirected, false);
  assert.equal(invalid.preferences.get('wiki.affixView'), 'function');
});

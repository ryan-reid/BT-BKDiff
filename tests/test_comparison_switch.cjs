const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

test('baseline switch keeps live search, query parameters and anchors', () => {
  const handlers = {};
  const link = {
    href: 'https://example.com/wiki/compare-bt/items/index.html',
    addEventListener: (event, handler) => { handlers[event] = handler; },
  };
  const search = {value: 'original'};
  const location = {search: '?q=original&extra=1', hash: '#first'};
  const document = {
    readyState: 'loading',
    addEventListener() {},
    querySelectorAll: () => [link],
    querySelector: () => search,
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8'),
    {document, window: {location}, URL});
  search.value = 'Grief & runes';
  location.hash = '#new-anchor';
  handlers.click();
  let target = new URL(link.href);
  assert.equal(target.pathname, '/wiki/compare-bt/items/index.html');
  assert.equal(target.searchParams.get('q'), 'Grief & runes');
  assert.equal(target.searchParams.get('extra'), '1');
  assert.equal(target.hash, '#new-anchor');
  search.value = '';
  handlers.auxclick();
  assert.equal(new URL(link.href).searchParams.has('q'), false);
});

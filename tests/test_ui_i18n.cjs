const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const SITE_JS = fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/site.js'), 'utf8');
const SKILLS_JS = fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/skills.js'), 'utf8');
const HISTORY_JS = fs.readFileSync(path.join(__dirname, '../scripts/d2lib/wiki_assets/history.js'), 'utf8');

function makeControl(value = '') {
  return {
    value,
    checked: false,
    hidden: false,
    disabled: false,
    dataset: {},
    style: {},
    listeners: {},
    options: [],
    addEventListener(event, fn) {
      this.listeners[event] = fn;
    },
    dispatchEvent() {},
    setAttribute() {},
    focus() {},
    classList: { toggle() {}, contains: () => false },
    insertAdjacentElement() {},
    closest() { return null; },
  };
}

test('site.js translates UI chrome from #wiki-i18n and falls back to defaults for missing keys', async () => {
  const catalog = {
    'status.modified': '변경됨',
    'status.mod_only': '{new_label} 전용',
    'common.no': '아니요',
    'areas.lvl_short': '레벨',
    'areas.sparkly_chest': '반짝이는 상자',
    'areas.super_chest': '슈퍼 상자',
    'areas.avg_short': '평균 {avg}',
    'areas.tiles_count': '{tiles} 타일',
    'areas.room_plural': '{count}개 방',
    'areas.density': '밀도',
    'areas.elite_packs': '정예 무리',
    'areas.special_chest': '특수 상자',
    'areas.possible_immunities': '등장 가능 면역',
    'areas.monster_pool': '등장 몬스터',
    'areas.more_monsters': '+{count}종 더 보기',
    'areas.no_matches': '일치하는 지역이 없습니다.',
    'search.no_matching_entries': '일치하는 항목이 없습니다.',
    'runewords.no_matches': '일치하는 룬어가 없습니다.',
  };
  const i18nEl = { textContent: JSON.stringify(catalog) };

  const toolbar = makeControl();
  toolbar.dataset = { areaIndexUrl: '../data/areas-index.json', immunityMeta: '{}' };
  const root = { innerHTML: '' };
  const cardRoot = { innerHTML: '' };
  const resultCount = { textContent: '' };
  const search = makeControl('없는검색어');

  const selectors = {
    '#wiki-i18n': i18nEl,
    '[data-area-index-url]': toolbar,
    '#area-index-root': root,
    '#area-card-root': cardRoot,
    '#area-result-count': resultCount,
    '#area-search': search,
  };
  const context = {
    document: {
      readyState: 'loading',
      body: { dataset: { newLabel: 'AscendedMod', siteRoot: '../' } },
      addEventListener() {},
      querySelector: (sel) => selectors[sel] || null,
      querySelectorAll: () => [],
    },
    window: { location: { search: '', href: 'https://example.test/koKR/areas/' } },
    URLSearchParams,
    URL,
    fetch: async () => ({
      json: async () => [
        {
          display_name: '냉기의 동굴',
          act: '1막',
          area_level: 85,
          monster_density: 1200,
          elite_min: 4,
          elite_max: 6,
          elite_avg: 5,
          estimated_area_tiles: 1024,
          maze_chunk_width: 32,
          maze_chunk_height: 32,
          maze_rooms: 3,
          maze_source: 'lvlmaze',
          has_super_chest: true,
          super_chest_sources: [{ chest_kind: 'sparkly' }, { chest_kind: 'super' }],
          possible_immunities: [],
          monster_pool: [],
          search_text: '냉기의 동굴',
        },
      ],
    }),
  };
  vm.createContext(context);
  vm.runInContext(SITE_JS, context);

  // statusLabel uses data-new-label & catalog
  assert.ok(vm.runInContext('statusLabel("added")', context).includes('AscendedMod 전용'));
  assert.ok(vm.runInContext('statusLabel("modified")', context).includes('변경됨'));

  await vm.runInContext('wireAreaIndex()', context);
  assert.ok(root.innerHTML.includes('일치하는 지역이 없습니다.'));
  assert.ok(cardRoot.innerHTML.includes('일치하는 지역이 없습니다.'));

  search.value = '';
  search.listeners.input();
  assert.ok(root.innerHTML.includes('레벨 85'));
  assert.ok(root.innerHTML.includes('평균 5'));
  assert.ok(root.innerHTML.includes('1024 타일'));
  assert.ok(root.innerHTML.includes('3개 방'));
  assert.ok(root.innerHTML.includes('반짝이는 상자'));
  assert.ok(root.innerHTML.includes('슈퍼 상자'));
  // Missing key areas.no_monster_pool falls back cleanly to English default.
  assert.ok(root.innerHTML.includes('No monster pool'));
  assert.ok(cardRoot.innerHTML.includes('밀도'));

  // >8 monsters exercises localized overflow summary
  const overflowHtml = vm.runInContext(
    'areaMonsterPoolMarkup({ monster_pool: Array.from({ length: 10 }, (_, idx) => ({ id: "m" + idx, name: "괴물" + idx, immunities: [] })) }, {})',
    context,
  );
  assert.ok(overflowHtml.includes('<summary>+2종 더 보기</summary>'));
});

test('skills.js translates visible result counter via #wiki-i18n', () => {
  const resultsEl = { textContent: '' };
  const emptyEl = { hidden: true };
  const sectionEl = { hidden: false };
  const search = makeControl('');
  const status = makeControl('all');
  status.options = [{ value: 'all' }];
  const reset = makeControl();
  const card = { id: 'holy-bolt', dataset: { search: '신성한 빛줄기', status: 'modified' }, hidden: false };
  const rootSelectors = {
    '#skill-search': search,
    '#skill-status': status,
    '#skill-results': resultsEl,
    '#skill-empty': emptyEl,
    '.item-family-section': sectionEl,
    '#skill-reset-filters': reset,
  };
  const root = {
    style: { setProperty() {} },
    querySelector: (sel) => rootSelectors[sel] || null,
    querySelectorAll: (sel) => (sel === '[data-skill-card]' ? [card] : []),
  };
  const docSelectors = {
    '#wiki-i18n': { textContent: JSON.stringify({ 'skills.visible_count': '{total}개 기술 중 {visible}개' }) },
    '[data-skill-explorer]': root,
  };
  const context = {
    document: {
      querySelector: (sel) => docSelectors[sel] || null,
    },
    window: { addEventListener() {} },
    location: { href: 'https://example.test/koKR/classes/paladin/', search: '', hash: '' },
    history: { replaceState() {} },
    getComputedStyle: () => ({ position: 'static' }),
    URLSearchParams,
    URL,
  };
  vm.runInNewContext(SKILLS_JS, context);
  assert.equal(resultsEl.textContent, '1개 기술 중 1개');
});

test('history.js translates dialog chrome and event labels via #wiki-i18n', async () => {
  const heading = { textContent: '' };
  const select = makeControl('');
  select.replaceChildren = () => { select.options = []; };
  select.append = (opt) => { select.options.push(opt); };
  const content = { textContent: '', innerHTML: '' };
  const meta = { replaceChildren() {}, append() {} };
  const prevBtn = makeControl();
  const nextBtn = makeControl();
  const closeBtn = makeControl();
  const dialogSelectors = {
    '#item-revision-select': select,
    '#item-revision-content': content,
    '#item-revision-meta': meta,
    '#item-revision-prev': prevBtn,
    '#item-revision-next': nextBtn,
    '[data-close-revisions]': closeBtn,
    'h2': heading,
  };
  const docListeners = {};
  const dialog = {
    open: false,
    showModal() { this.open = true; },
    close() { this.open = false; },
    addEventListener() {},
    querySelector: (sel) => dialogSelectors[sel] || null,
  };
  const i18n = {
    'history.dialog_title': '아이템 변경 이력',
    'history.loading': '이력을 불러오는 중…',
    'history.no_revisions': '이 아이템의 소스 이력이 없습니다.',
    'history.event.added': '추가됨',
  };
  const docSelectors = {
    '#wiki-i18n': { textContent: JSON.stringify(i18n) },
    '#item-revisions-dialog': dialog,
  };
  const context = {
    document: {
      documentElement: { classList: { add() {} } },
      body: { dataset: { siteRoot: '../' } },
      createElement: () => ({ value: '', textContent: '' }),
      querySelector: (sel) => docSelectors[sel] || null,
      addEventListener(event, handler) { docListeners[event] = handler; },
    },
    window: {},
    location: { href: 'https://example.test/koKR/items/' },
    URL,
    fetch: async () => ({
      ok: true,
      json: async () => ({
        title: '테스트 아이템',
        revisions: [{ date: '2026-01-01', short_commit: 'abc1234', kinds: ['added'], html: '<p>ok</p>', url: '#' }],
      }),
    }),
  };
  vm.runInNewContext(HISTORY_JS, context);

  const trigger = { dataset: { revisionsPath: 'data/item-revisions/kokr/123.json' } };
  await docListeners.click({
    button: 0,
    target: { closest: (sel) => (sel === '[data-revisions-path]' ? trigger : null) },
    preventDefault() {},
  });
  assert.equal(heading.textContent, '테스트 아이템');
  assert.equal(select.options[0].textContent, '2026-01-01 · abc1234 · 추가됨');

  // Re-check loading title & empty revision message on separate request
  context.fetch = async () => ({ ok: true, json: async () => ({ title: '빈 아이템', revisions: [] }) });
  const trigger2 = { dataset: { revisionsPath: 'data/item-revisions/kokr/456.json' } };
  const pending = docListeners.click({
    button: 0,
    target: { closest: (sel) => (sel === '[data-revisions-path]' ? trigger2 : null) },
    preventDefault() {},
  });
  assert.equal(heading.textContent, '아이템 변경 이력');
  assert.equal(content.textContent, '이력을 불러오는 중…');
  await pending;
  assert.equal(content.textContent, '이 아이템의 소스 이력이 없습니다.');
});

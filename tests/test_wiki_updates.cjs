const {test} = require('node:test');
const assert = require('node:assert/strict');
const check = require('../scripts/check_wiki_updates.cjs');

const revisions = {repository: 'a'.repeat(40), BKDiablo: 'b'.repeat(40), BTDiablo: 'c'.repeat(40)};
function fixture({event = 'schedule', deployed = revisions, status = 200, head = null} = {}) {
  const outputs = {};
  let requests = 0;
  const args = {
    context: {sha: revisions.repository, eventName: event, runId: 1, repo: {owner: 'owner', repo: 'wiki'}},
    github: {rest: {repos: {getPages: async () => ({data: {html_url: 'https://example.com/wiki/'}})}}},
    core: {
      setOutput: (key, value) => { outputs[key] = value; },
      summary: {addRaw() {return this;}, async write() {}},
    },
    exec: {getExecOutput: async (command, args) => {
      assert.equal(command, 'git');
      if (args[0] === 'config') return {stdout: args.at(-1).includes('bkdiablo.mpq') ? 'bk' : 'bt'};
      assert.equal(args[0], 'ls-remote');
      const sha = head ?? (args[2] === 'bk' ? revisions.BKDiablo : revisions.BTDiablo);
      return {stdout: `${sha}\t${args[3]}\n`};
    }},
    fetchImpl: async url => {
      requests++;
      assert.equal(url.pathname, '/wiki/source-revisions.json');
      assert.ok(url.searchParams.has('check'));
      return {ok: status === 200, status, json: async () => deployed};
    },
  };
  return {args, outputs, requests: () => requests};
}

test('unchanged deployed sources skip the build', async () => {
  const f = fixture();
  await check(f.args);
  assert.equal(f.outputs.rebuild, 'false');
  assert.deepEqual(JSON.parse(f.outputs.revisions), revisions);
});

for (const source of Object.keys(revisions)) {
  test(`changed ${source} rebuilds and keeps retrying until deployed`, async () => {
    const f = fixture({deployed: {...revisions, [source]: 'd'.repeat(40)}});
    await check(f.args);
    assert.equal(f.outputs.rebuild, 'true');
    await check(f.args);
    assert.equal(f.outputs.rebuild, 'true');
  });
}

test('missing marker bootstraps deployment', async () => {
  const f = fixture({status: 404});
  await check(f.args);
  assert.equal(f.outputs.rebuild, 'true');
});

for (const event of ['push', 'workflow_dispatch']) {
  test(`${event} forces a rebuild without depending on the live site`, async () => {
    const f = fixture({event});
    await check(f.args);
    assert.equal(f.outputs.rebuild, 'true');
    assert.equal(f.requests(), 0);
  });
}

test('server failures fail the check without producing a skip decision', async () => {
  const f = fixture({status: 503});
  await assert.rejects(check(f.args), /HTTP 503/);
  assert.deepEqual(f.outputs, {});
});

for (const checkOnly of [true, 'true']) {
  test(`homelab dispatch checks deployed revisions (${typeof checkOnly})`, async () => {
    const f = fixture({event: 'workflow_dispatch'});
    f.args.context.payload = {inputs: {check_only: checkOnly}};
    await check(f.args);
    assert.equal(f.outputs.rebuild, 'false');
    assert.equal(f.requests(), 1);
  });
}

test('homelab dispatch rebuilds changed sources', async () => {
  const f = fixture({event: 'workflow_dispatch', deployed: {...revisions, BKDiablo: 'd'.repeat(40)}});
  f.args.context.payload = {inputs: {check_only: 'true'}};
  await check(f.args);
  assert.equal(f.outputs.rebuild, 'true');
});

test('explicitly forced dispatch still rebuilds', async () => {
  const f = fixture({event: 'workflow_dispatch'});
  f.args.context.payload = {inputs: {check_only: 'false'}};
  await check(f.args);
  assert.equal(f.outputs.rebuild, 'true');
  assert.equal(f.requests(), 0);
});

test('network errors fail the check', async () => {
  const f = fixture();
  f.args.fetchImpl = async () => {throw new Error('network unavailable');};
  await assert.rejects(check(f.args), /network unavailable/);
  assert.deepEqual(f.outputs, {});
});

test('invalid upstream revisions cannot reach the build', async () => {
  const f = fixture({head: 'bad-revision'});
  await assert.rejects(check(f.args), /Invalid upstream revision/);
  assert.deepEqual(f.outputs, {});
});

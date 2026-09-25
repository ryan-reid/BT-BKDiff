// The live marker changes only when the Pages artifact is successfully deployed.
module.exports = async function checkWikiUpdates({github, context, core, exec, fetchImpl = fetch}) {
  async function git(args) {
    const result = await exec.getExecOutput('git', args, {silent: true});
    return result.stdout.trim();
  }

  const revisions = {repository: context.sha};
  for (const [mod, section] of [['BKDiablo', 'bkdiablo.mpq'], ['BTDiablo', 'BTDiablo']]) {
    const url = await git(['config', '-f', '.gitmodules', '--get', `submodule.${section}.url`]);
    const branch = await git(['config', '-f', '.gitmodules', '--get', `submodule.${section}.branch`]);
    const head = await git(['ls-remote', '--exit-code', url, `refs/heads/${branch}`]);
    const revision = head.split(/\s+/)[0];
    if (!/^[0-9a-f]{40}$/.test(revision)) throw new Error(`Invalid upstream revision for ${mod}`);
    revisions[mod] = revision;
  }

  let rebuild = true;
  const conditionalDispatch = context.eventName === 'workflow_dispatch'
    && [true, 'true'].includes(context.payload?.inputs?.check_only);
  if (context.eventName === 'schedule' || conditionalDispatch) {
    const {data: pages} = await github.rest.repos.getPages(context.repo);
    const url = new URL('source-revisions.json', pages.html_url.replace(/\/?$/, '/'));
    url.searchParams.set('check', `${context.runId}-${Date.now()}`);
    const response = await fetchImpl(url, {
      headers: {'Cache-Control': 'no-cache'},
      signal: AbortSignal.timeout(30000),
    });
    if (response.ok) {
      const deployed = await response.json();
      rebuild = !deployed || Object.keys(revisions).some(key => deployed[key] !== revisions[key]);
    } else if (response.status !== 404) {
      throw new Error(`Could not read deployed revisions: HTTP ${response.status}`);
    }
  }

  core.setOutput('revisions', JSON.stringify(revisions));
  core.setOutput('rebuild', String(rebuild));
  await core.summary.addRaw(rebuild
    ? `Rebuilding wiki from source revisions: ${JSON.stringify(revisions)}`
    : 'The live wiki already contains the current source revisions; skipping build and deployment.'
  ).write();
};

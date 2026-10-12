# BK item history

History describes BK source data, not release dates, dates of wiki edits, or proof
that an item could drop. Both comparison views use the same BK revision. No history
is inferred from the Retail or BT columns.

Cards show the Last changed date (falling back to the first-known source date with
an explanatory tooltip when no later change is recorded). Clicking a card or its View item revisions
button opens a dialog with a dated BK revision selector and the normal comparison
rows. Retail or BT stays fixed at the selected view's current comparison data.
Unique and set revisions also show underlying base damage, defense, requirements,
and socket capacity, explicitly before item bonuses. Availability shows source
presence, explicit enable/spawn flags, ladder/crafting restrictions and relative
drop-selection weight. These settings do not establish a drop probability.
Each item loads its own JSON on demand. Missing historical dependencies produce an
explicit unavailable revision, never current gameplay values. Native HTML history
remains available without JavaScript. The last-change event remains in the data.

Historical presentations use current analyzers over isolated Git tables; current
localization is used only for readable labels. Presentations are cached by revision,
analyzer sources, localization and alias configuration. A revision is included for
each recorded event or source gap, plus the exact BK revision used by the build.

The generator writes `output/wiki/data/item-history.json`. Each stable ID has
coverage, first recorded/added, last change, ordered events, and evidence gaps.
Events contain full and short commit IDs, the committer timestamp, a GitHub link,
an optional verified release, causes, and before/after source values.

## Evidence and identity

- IDs are `unique:<index>`, `set:<index>`, `runeword:<Name>`, and `base:<code>`.
- The first-parent chain ends at the checked-out BK commit. A merged change is
  dated at its merge onto that chain, not at an unmerged side-branch commit.
- Initial contents of each table are **First recorded**. Later records are
  **Added**. Reappearances and activation changes have their own events.
- Duplicate IDs are ambiguous. Affected items get coverage gaps instead of a
  guessed identity. Missing dependencies and unsupported snapshots also produce
  gaps. After a gap, a snapshot is recorded without pretending the change happened
  at the first readable commit.
- Missing Git history, shallow history, and local edits to BK data produce an
  unavailable result. The wiki still builds and emits a warning. Runtime history
  reads never use the repository's current Retail fallback or execute old code.

## Gameplay dependencies

The current history analyzer reads every snapshot with the same rules. It compares
normalized row dictionaries, not line numbers, rendered English, or file timestamps.
Whitespace, column order, row order, comment columns, localization, inventory art,
and wiki formatting do not update gameplay dates.

It follows item bases and type ancestry; sockets, requirements and each damage
mode; applicable automagic and superior bonuses (superior bonuses only for bases,
never unique or set items); set bonuses; referenced property and stat definitions;
and runeword rune effects and eligible bases. Granted/triggered skill names, levels,
and chances remain item properties, but changes inside skill definitions are
excluded. Missing skill-behavior data does not create an item-history gap.
Rune effects are restricted to compatible socket groups. Only referenced property
and stat records affect an item; an unrelated row edit does not update its date.

This is source-data history, not an emulation of the game engine. Engine changes
outside these data dependencies are not attributed to individual items.

## Reviewed mappings

Edit `data/item-history.json` only after reviewing the upstream evidence. Release
labels are intentionally empty initially: commit-message version guesses are not
verified releases.

`aliases` maps an old full ID to its canonical full ID. For example,
`"unique:Old internal index": "unique:New internal index"` preserves identity
through a verified rename. Alias cycles and collisions invalidate the collection;
do not use aliases to combine distinct items with the same display name.

Each `releases` entry has a `label` plus either `commits` (a list of full SHA-1s),
or `first` and `last` (inclusive full SHA-1 endpoints on the first-parent chain).
An entry may use both. Unknown, reversed, or overlapping mappings are rejected.
Do not extend a version range beyond commits explicitly verified to belong to it.

## Builds, cache, and local review

Normal wiki generation collects history automatically. GitHub Actions fetches
complete BK history and caches `.cache/item-history/`. Parsed tables are keyed by
blob ID and parser version. Final results also include the analyzer source hash,
BK revision, data path, and mapping hash in their cache key. A changed branch tip
cannot reuse another tip's results. Removing this ignored cache forces a cold scan.

Build locally from `scripts/` with `python -m cli.generate_wiki --compare-bt`.
Serve `output/wiki/` and inspect items, bases, sets, and runewords, including narrow
screens and JavaScript disabled. Expand History to inspect changes and gaps; audit
representative events with `git -C mods/BKDiablo show <commit> -- <table-path>`.

Do not publish this feature until local review is complete and the owner approves
the push. A local build does not change the live site.

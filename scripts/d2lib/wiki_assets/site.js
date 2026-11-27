const _WIKI_I18N = (() => {
  try {
    const el = typeof document !== "undefined" && typeof document.querySelector === "function"
      ? document.querySelector("#wiki-i18n")
      : null;
    if (el && el.textContent) {
      const parsed = JSON.parse(el.textContent);
      return parsed && typeof parsed === "object" ? parsed : {};
    }
  } catch {
    // Fall back to default English strings when catalog JSON is absent or malformed.
  }
  return {};
})();

function tUi(key, fallback, vars) {
  let template = Object.prototype.hasOwnProperty.call(_WIKI_I18N, key) && _WIKI_I18N[key]
    ? String(_WIKI_I18N[key])
    : String(fallback);
  if (vars) {
    Object.keys(vars).forEach((name) => {
      template = template.replaceAll(`{${name}}`, String(vars[name] ?? ""));
    });
  }
  return template;
}

function normalizeText(value) {
  return (value || "").toLowerCase().trim();
}

function statusLabel(status) {
  if (status === "modified") {
    return `<span class="item-card-status is-modified">${escapeHtml(tUi("status.modified", "Modified"))}</span>`;
  }
  if (status === "added") {
    const modLabel = (typeof document !== "undefined" && document.body && document.body.dataset && document.body.dataset.newLabel) || "BKDiablo";
    return `<span class="item-card-status is-added">${escapeHtml(tUi("status.mod_only", "{new_label} Only", { new_label: modLabel }))}</span>`;
  }
  return "";
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function areaBadgeMarkup(area) {
  return `<span class="area-badge area-badge-level">${escapeHtml(tUi("areas.lvl_short", "Lvl"))} ${escapeHtml(area.area_level)}</span>`;
}

const IMMUNITY_CLASS = {
  fire: "im-fire",
  cold: "im-cold",
  lightning: "im-lightning",
  poison: "im-poison",
  physical: "im-physical",
  magic: "im-magic",
};

function parseImmunityMeta(toolbar) {
  const raw = toolbar && toolbar.dataset ? toolbar.dataset.immunityMeta : "";
  if (!raw) {
    return {};
  }
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function immunityShortLabel(code, area, immunityMeta) {
  return (area && area.immunity_labels && area.immunity_labels[code])
    || (immunityMeta && immunityMeta[code] && immunityMeta[code].label)
    || code;
}

function immunityFullLabel(code, area, immunityMeta) {
  return (area && area.immunity_descriptions && area.immunity_descriptions[code])
    || (immunityMeta && immunityMeta[code] && immunityMeta[code].immunity_label)
    || immunityShortLabel(code, area, immunityMeta);
}

function areaImmunityMarkup(area, immunityMeta) {
  const immunities = areaMonsterImmunities(area);
  if (immunities.length === 0) {
    return '<span class="muted">—</span>';
  }
  return immunities
    .map((immunity) => {
      const count = area.immunity_counts && area.immunity_counts[immunity]
        ? ` (${area.immunity_counts[immunity]})`
        : "";
      const metaEntry = immunityMeta && immunityMeta[immunity];
      const cls = (metaEntry && metaEntry.chip_class) || IMMUNITY_CLASS[String(immunity).toLowerCase()] || "";
      const shortLabel = immunityShortLabel(immunity, area, immunityMeta);
      const fullLabel = immunityFullLabel(immunity, area, immunityMeta);
      return `<span class="immunity-chip ${cls}" title="${escapeHtml(fullLabel)}">${escapeHtml(shortLabel)}${escapeHtml(count)}</span>`;
    })
    .join("");
}

function areaMonsterImmunities(area) {
  const found = new Set(area.possible_immunities || []);
  (area.monster_pool || []).forEach((monster) => {
    (monster.immunities || []).forEach((immunity) => found.add(immunity));
  });
  return Array.from(found).sort();
}

function areaMonsterPoolMarkup(area, immunityMeta) {
  const monsters = area.monster_pool || [];
  if (monsters.length === 0) {
    return `<span class="muted">${escapeHtml(tUi("areas.no_monster_pool", "No monster pool"))}</span>`;
  }
  const formatImmunities = (codes) => codes.map((code) => immunityFullLabel(code, area, immunityMeta)).join(", ");
  const preview = monsters
    .slice(0, 8)
    .map((monster) => {
      const immunities = monster.immunities && monster.immunities.length
        ? `: ${formatImmunities(monster.immunities)}`
        : "";
      return `${escapeHtml(monster.name || monster.id)}${escapeHtml(immunities)}`;
    })
    .join("<br>");
  const hiddenMonsters = monsters.slice(8);
  if (hiddenMonsters.length === 0) {
    return preview;
  }
  return `
    ${preview}
    <details class="area-monster-more">
      <summary>${escapeHtml(tUi("areas.more_monsters", "+{count} more", { count: hiddenMonsters.length }))}</summary>
      ${hiddenMonsters.map((monster) => {
        const immunities = monster.immunities && monster.immunities.length
          ? `: ${formatImmunities(monster.immunities)}`
          : "";
        return `<span>${escapeHtml(monster.name || monster.id)}${escapeHtml(immunities)}</span>`;
      }).join("")}
    </details>
  `;
}

function areaMonsterListMarkup(area, immunityMeta) {
  const monsters = area.monster_pool || [];
  if (monsters.length === 0) {
    return `<p class="muted">${escapeHtml(tUi("areas.no_monster_pool_data", "No monster pool data."))}</p>`;
  }
  return `
    <ul class="area-monster-list">
      ${monsters.map((monster) => {
        const immunities = monster.immunities && monster.immunities.length
          ? `<span>${escapeHtml(monster.immunities.map((code) => immunityFullLabel(code, area, immunityMeta)).join(", "))}</span>`
          : "";
        return `<li><strong>${escapeHtml(monster.name || monster.id)}</strong>${immunities}</li>`;
      }).join("")}
    </ul>
  `;
}

function areaChestKinds(area) {
  const kinds = new Set();
  (area.super_chest_sources || []).forEach((source) => {
    const kind = source.chest_kind
      || (source.object_id === 397 || String(source.object_class || "").toLowerCase() === "consolationchest" ? "sparkly" : "super");
    kinds.add(kind);
  });
  if (kinds.size === 0 && area.has_super_chest) {
    kinds.add("super");
  }
  return Array.from(kinds);
}

function areaSuperChestMarkup(area) {
  if (!area.has_super_chest) {
    return `<span class="muted">${escapeHtml(tUi("common.no", "No"))}</span>`;
  }
  const sparklyLabel = escapeHtml(tUi("areas.sparkly_chest", "Sparkly Chest"));
  const sparklyTitle = escapeHtml(tUi("areas.sparkly_chest_title", "Sparkly golden chest — can roll Unique, Set, Rare, or Magic drops"));
  const superLabel = escapeHtml(tUi("areas.super_chest", "Super Chest"));
  const superTitle = escapeHtml(tUi("areas.super_chest_title", "Super chest — multi-drop Magic/Rare burst (5% Rare / 95% Magic)"));
  return areaChestKinds(area)
    .map((kind) => (
      kind === "sparkly"
        ? `<span class="area-badge area-badge-sparkly" title="${sparklyTitle}">${sparklyLabel}</span>`
        : `<span class="area-badge area-badge-super" title="${superTitle}">${superLabel}</span>`
    ))
    .join(" ");
}

function areaMazeMarkup(area) {
  if (!area.estimated_area_tiles) {
    return `<span class="muted">${escapeHtml(tUi("common.unknown", "Unknown"))}</span>`;
  }

  const chunk = area.maze_chunk_width && area.maze_chunk_height
    ? `${area.maze_chunk_width}x${area.maze_chunk_height}`
    : tUi("common.unknown", "Unknown");
  const rooms = area.maze_rooms
    ? (area.maze_rooms === 1
      ? tUi("areas.room_singular", "{count} room", { count: area.maze_rooms })
      : tUi("areas.room_plural", "{count} rooms", { count: area.maze_rooms }))
    : tUi("areas.unknown_rooms", "Unknown rooms");
  const source = area.maze_source === "lvlmaze" ? "LvlMaze" : "Levels";
  const tilesLabel = tUi("areas.tiles_count", "{tiles} tiles", { tiles: area.estimated_area_tiles });
  return `
    <strong>${escapeHtml(chunk)}</strong><br>
    <span class="muted">${escapeHtml(rooms)}</span><br>
    <span class="muted">${escapeHtml(tilesLabel)} &middot; ${escapeHtml(source)}</span>
  `;
}

function areaRowMarkup(area, immunityMeta) {
  const avgLabel = escapeHtml(tUi("areas.avg_short", "Avg {avg}", { avg: area.elite_avg }));
  return `
    <tr>
      <th>
        <span class="area-name">${escapeHtml(area.display_name)}</span>
        <span class="area-meta">${escapeHtml(area.act)}</span>
        <span class="area-badge-row">${areaBadgeMarkup(area)}</span>
      </th>
      <td>${escapeHtml(area.monster_density)}</td>
      <td>${areaMazeMarkup(area)}</td>
      <td>${escapeHtml(area.elite_min)}-${escapeHtml(area.elite_max)}<br><span class="muted">${avgLabel}</span></td>
      <td>${areaSuperChestMarkup(area)}</td>
      <td><span class="immunity-list">${areaImmunityMarkup(area, immunityMeta)}</span></td>
      <td>${areaMonsterPoolMarkup(area, immunityMeta)}</td>
    </tr>
  `;
}

function areaCardMarkup(area, immunityMeta) {
  const avgLabel = escapeHtml(tUi("areas.avg_short", "Avg {avg}", { avg: area.elite_avg }));
  return `
    <article class="area-card" data-search="${escapeHtml(area.search_text)}">
      <div class="area-card-head">
        <div>
          <h3>${escapeHtml(area.display_name)}</h3>
          <span>${escapeHtml(area.act)}</span>
        </div>
        <span class="area-level-pill">${escapeHtml(tUi("areas.lvl_short", "Lvl"))} ${escapeHtml(area.area_level)}</span>
      </div>
      <dl class="area-card-stats">
        <div><dt>${escapeHtml(tUi("areas.density", "Density"))}</dt><dd>${escapeHtml(area.monster_density)}</dd></div>
        <div><dt>${escapeHtml(tUi("areas.elite_packs", "Elite Packs"))}</dt><dd>${escapeHtml(area.elite_min)}-${escapeHtml(area.elite_max)} <span>${avgLabel}</span></dd></div>
        <div><dt>${escapeHtml(tUi("areas.special_chest", "Special Chest"))}</dt><dd>${areaSuperChestMarkup(area)}</dd></div>
      </dl>
      <div class="area-card-section">
        <span class="area-card-label">${escapeHtml(tUi("areas.possible_immunities", "Possible Immunities"))}</span>
        <div class="immunity-list">${areaImmunityMarkup(area, immunityMeta)}</div>
      </div>
      <details class="area-card-details">
        <summary>${escapeHtml(tUi("areas.monster_pool", "Monster Pool"))}</summary>
        ${areaMonsterListMarkup(area, immunityMeta)}
      </details>
    </article>
  `;
}

function wireStaticSearch() {
  const pageSearch = document.querySelector("#page-search");
  const hasLandingCards = Boolean(document.querySelector(".guide-card"));
  const searchInput = pageSearch || (hasLandingCards ? document.querySelector("#mast-search-input") : null);
  const cards = Array.from(document.querySelectorAll(".item-card, .base-item-card, .recipe-card, .guide-card, .set-piece, .corruption-summary-card, .portal[data-skill-class]"));
  const tableRows = Array.from(document.querySelectorAll("tbody tr[data-search]"));
  const sections = Array.from(document.querySelectorAll(".recipe-group, .recipe-group-section, .misc-group-section, .family-container, .set-block"));
  const filterButtons = Array.from(document.querySelectorAll("[data-recipe-filter], [data-search-filter]"));
  const filterControls = Array.from(document.querySelectorAll("[data-search-filter-control]"));
  let activeFilter = "all";
  let emptyMessage = null;
  
  if (!searchInput || document.querySelector("[data-item-index-url], [data-affix-index]") || document.querySelector("[data-base-filters]") || document.querySelector("[data-runeword-filters]")) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get("q");
  filterControls.forEach((control) => {
    const value = params.get(control.dataset.searchFilterParam);
    if (control.type === "checkbox") {
      control.checked = value === "1";
    } else if (Array.from(control.options).some((option) => option.value === value)) {
      control.value = value;
    }
  });
  if (initialQuery) {
    searchInput.value = initialQuery;
    const mastSearch = document.querySelector("#mast-search-input");
    if (mastSearch) {
      mastSearch.value = initialQuery;
    }
  }

  if (pageSearch) {
    emptyMessage = document.createElement("p");
    emptyMessage.className = "search-empty";
    emptyMessage.hidden = true;
    emptyMessage.textContent = tUi("search.no_matching_entries", "No matching entries.");
    (filterControls[0]?.closest(".filter-row") || pageSearch).insertAdjacentElement("afterend", emptyMessage);
  }

  function filterTags(element, key) {
    return normalizeText(element?.dataset?.[key])
      .split("|")
      .map((tag) => tag.trim())
      .filter(Boolean);
  }

  function matchesSearch(element, query) {
    return !query || normalizeText(element && element.dataset ? element.dataset.search : "").includes(query);
  }

  function ownerMatches(row, matcher) {
    const card = row.closest(".corruption-summary-card");
    const section = row.closest(".recipe-group, .recipe-group-section, .misc-group-section, .family-container, .set-block");
    return matcher(row) || matcher(card) || matcher(section);
  }

  function applySearch() {
    const query = normalizeText(searchInput.value);
    const activeControls = filterControls.filter((control) =>
      control.type === "checkbox" ? control.checked : control.value && control.value !== "all");
    function matchesFilter(element) {
      return (activeFilter === "all" || filterTags(element, "filterTags").includes(activeFilter))
        && activeControls.every((control) =>
          filterTags(element, control.dataset.searchFilterControl).includes(normalizeText(control.value)));
    }

    // Hide/show table rows
    tableRows.forEach((row) => {
      const match = ownerMatches(row, matchesFilter) && ownerMatches(row, (element) => matchesSearch(element, query));
      row.hidden = !match;
    });

    // Hide/show individual cards. Cards with matching visible rows stay visible.
    cards.forEach((card) => {
      const section = card.closest(".recipe-group, .recipe-group-section, .misc-group-section, .family-container, .set-block");
      const filterMatch = matchesFilter(card) || matchesFilter(section);
      const cardMatch = filterMatch && (matchesSearch(card, query) || matchesSearch(section, query));
      const hasVisibleRows = Array.from(card.querySelectorAll("tbody tr[data-search]"))
        .some((row) => !row.hidden);
      const match = cardMatch || hasVisibleRows;
      card.hidden = !match;
      // Also handle display property if hidden attribute isn't enough for the grid
      card.style.display = match ? "" : "none";
    });

    // Hide/show parent sections based on children or section metadata
    sections.forEach((section) => {
      const sectionMatch = matchesFilter(section) && matchesSearch(section, query);
      const hasVisibleChildren = Array.from(section.querySelectorAll(".item-card, .base-item-card, .recipe-card, .guide-card, .set-piece, .corruption-summary-card, tbody tr[data-search]"))
        .some(child => !child.hidden && child.style.display !== "none");
      
      const shouldShow = sectionMatch || hasVisibleChildren;
      section.hidden = !shouldShow;
      section.style.display = shouldShow ? "" : "none";
    });

    if (emptyMessage) {
      const topLevel = sections.length ? sections : (cards.length ? cards : tableRows);
      const hasResults = topLevel.some((element) => !element.hidden && element.style.display !== "none");
      emptyMessage.hidden = (!query && activeFilter === "all" && !activeControls.length) || hasResults;
    }
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = normalizeText(button.dataset.searchFilter || button.dataset.recipeFilter || "all") || "all";
      filterButtons.forEach((candidate) => {
        candidate.classList.toggle("is-active", candidate === button);
        candidate.setAttribute("aria-pressed", String(candidate === button));
      });
      applySearch();
    });
  });

  function updateSearch() {
    applySearch();
    if (!filterControls.length) return;

    const url = new URL(window.location.href);
    const query = searchInput.value.trim();
    if (query) url.searchParams.set("q", query);
    else url.searchParams.delete("q");
    filterControls.forEach((control) => {
      const key = control.dataset.searchFilterParam;
      const value = control.type === "checkbox" ? (control.checked ? "1" : "") : control.value;
      if (value && value !== "all") url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    });
    if (url.href !== window.location.href) window.history.replaceState(null, "", url.href);
  }

  filterControls.forEach((control) => control.addEventListener("change", updateSearch));
  searchInput.addEventListener("input", updateSearch);
  applySearch();
}

function parseRuneQueries(value) {
  return normalizeText(value)
    .split(/[,\s/]+/)
    .map((query) => query.trim())
    .filter(Boolean);
}

function wireRunewordFilters() {
  const toolbar = document.querySelector("[data-runeword-filters]");
  if (!toolbar) {
    return;
  }

  const searchInput = document.querySelector("#page-search");
  const prefixInput = document.querySelector("#runeword-prefix-filter");
  const baseSelect = document.querySelector("#runeword-base-filter");
  const resultCount = document.querySelector("#runeword-result-count");
  const selectedCount = document.querySelector("#runeword-selected-count");
  const clearRunesButton = document.querySelector("#runeword-clear-runes");
  const runeButtons = Array.from(document.querySelectorAll("[data-rune-option]"));
  const cards = Array.from(document.querySelectorAll("[data-runeword-card]"));
  const selectedRuneCodes = new Set();
  const emptyMessage = document.createElement("p");
  emptyMessage.className = "search-empty";
  emptyMessage.hidden = true;
  emptyMessage.textContent = tUi("runewords.no_matches", "No runewords match the current filters.");
  toolbar.insertAdjacentElement("afterend", emptyMessage);

  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get("q") || params.get("search") || "";
  const initialPrefix = params.get("prefix") || params.get("namePrefix") || "";
  const initialBase = params.get("base") || params.get("baseItem") || "";
  const initialRunes = params.get("runes") || params.get("rune") || params.get("have") || "";
  if (searchInput && initialQuery) {
    searchInput.value = initialQuery;
    const mastSearch = document.querySelector("#mast-search-input");
    if (mastSearch) {
      mastSearch.value = initialQuery;
    }
  }
  if (prefixInput && initialPrefix) {
    prefixInput.value = initialPrefix;
  }
  if (baseSelect && initialBase) {
    const normalizedBase = normalizeText(initialBase);
    const option = Array.from(baseSelect.options).find((candidate) =>
      normalizeText(candidate.value) === normalizedBase || normalizeText(candidate.textContent || "") === normalizedBase
    );
    if (option) {
      baseSelect.value = option.value;
    }
  }

  function setRuneSelected(button, selected) {
    const code = normalizeText(button.dataset.runeCode || "");
    if (!code) {
      return;
    }
    if (selected) {
      selectedRuneCodes.add(code);
    } else {
      selectedRuneCodes.delete(code);
    }
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
  }

  parseRuneQueries(initialRunes).forEach((query) => {
    const button = runeButtons.find((candidate) => {
      const code = normalizeText(candidate.dataset.runeCode || "");
      const terms = normalizeText(candidate.dataset.runeTerms || "").split("|").filter(Boolean);
      return code === query || terms.includes(query);
    });
    if (button) {
      setRuneSelected(button, true);
    }
  });

  function applyFilters() {
    const query = normalizeText(searchInput ? searchInput.value : "");
    const prefix = normalizeText(prefixInput ? prefixInput.value : "");
    const activeBase = baseSelect ? baseSelect.value : "all";
    const normalizedBase = normalizeText(activeBase);
    const hasSelectedRunes = selectedRuneCodes.size > 0;
    let visibleCount = 0;

    cards.forEach((card) => {
      const textOk = !query || normalizeText(card.dataset.search || "").includes(query);
      const prefixOk = !prefix || normalizeText(card.dataset.runewordTitle || "").startsWith(prefix);
      const baseItems = normalizeText(card.dataset.baseItems || "").split("|").filter(Boolean);
      const baseOk = activeBase === "all" || baseItems.includes(normalizedBase);
      const runeCodes = normalizeText(card.dataset.runeCodes || "").split("|").filter(Boolean);
      const runeOk = !hasSelectedRunes || runeCodes.every((code) => selectedRuneCodes.has(code));
      const visible = textOk && prefixOk && baseOk && runeOk;
      card.hidden = !visible;
      card.style.display = visible ? "" : "none";
      if (visible) {
        visibleCount += 1;
      }
    });

    if (resultCount) {
      resultCount.textContent = String(visibleCount);
    }
    if (selectedCount) {
      selectedCount.textContent = String(selectedRuneCodes.size);
    }
    if (clearRunesButton) {
      clearRunesButton.disabled = selectedRuneCodes.size === 0;
    }
    emptyMessage.hidden = visibleCount > 0 || (!query && !prefix && activeBase === "all" && !hasSelectedRunes);
  }

  [searchInput, prefixInput, baseSelect]
    .filter(Boolean)
    .forEach((control) => {
      control.addEventListener("input", applyFilters);
      control.addEventListener("change", applyFilters);
    });
  runeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const code = normalizeText(button.dataset.runeCode || "");
      setRuneSelected(button, !selectedRuneCodes.has(code));
      applyFilters();
    });
  });
  if (clearRunesButton) {
    clearRunesButton.addEventListener("click", () => {
      runeButtons.forEach((button) => setRuneSelected(button, false));
      applyFilters();
    });
  }

  applyFilters();
}

function wireMastSearch() {
  const mastSearch = document.querySelector("#mast-search-input");
  if (!mastSearch) {
    return;
  }

  function pageSearchInput() {
    return document.querySelector("#page-search, #area-search") || document.querySelector("#skill-search");
  }

  const initialTarget = pageSearchInput();
  if (initialTarget && initialTarget.value) {
    mastSearch.value = initialTarget.value;
  }

  mastSearch.addEventListener("input", () => {
    const target = pageSearchInput();
    if (!target) {
      return;
    }
    target.value = mastSearch.value;
    target.dispatchEvent(new Event("input", { bubbles: true }));
    target.dispatchEvent(new Event("change", { bubbles: true }));
  });

  mastSearch.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }
    const target = pageSearchInput();
    if (target) {
      target.focus();
      return;
    }
    const query = mastSearch.value.trim();
    if (query && document.querySelector(".guide-card")) {
      event.preventDefault();
      return;
    }
    if (query) {
      window.location.href = `${document.body.dataset.siteRoot || ""}items/?q=${encodeURIComponent(query)}`;
    }
  });
}

function wireBaseFilters() {
  const toolbar = document.querySelector("[data-base-filters]");
  if (!toolbar) {
    return;
  }

  const searchInput = document.querySelector("#page-search");
  const groupSelect = document.querySelector("#base-group-filter");
  const categorySelect = document.querySelector("#base-category-filter");
  const lootSelect = document.querySelector("#base-loot-filter");
  const ruleParams = new URLSearchParams(window.location.search);
  const includedTypes = (ruleParams.get("types") || "").split("|").filter(Boolean);
  const excludedTypes = (ruleParams.get("exclude") || "").split("|").filter(Boolean);
  const runewordNotice = document.querySelector("#base-runeword-notice");
  if (runewordNotice) runewordNotice.hidden = !includedTypes.length;
  const classSelect = document.querySelector("#base-class-filter");
  const tierSelect = document.querySelector("#base-tier-filter");
  const speedSelect = document.querySelector("#base-speed-filter");
  const minSocketsSelect = document.querySelector("#base-min-sockets-filter");
  const rollInput = document.querySelector("#base-roll-filter");
  const twoHandedCheckbox = document.querySelector("#base-two-handed-filter");
  const resultCount = document.querySelector("#base-result-count");
  const families = Array.from(document.querySelectorAll(".family-container"));

  function queryValue(params, names) {
    for (const name of names) {
      const value = params.get(name);
      if (value) {
        return value;
      }
    }
    return "";
  }

  function setSelectValue(select, value) {
    if (!select || !value) {
      return;
    }
    const normalizedValue = normalizeText(value);
    const option = Array.from(select.options).find((candidate) => {
      return normalizeText(candidate.value) === normalizedValue
        || normalizeText(candidate.textContent || "") === normalizedValue;
    });
    if (option) {
      select.value = option.value;
    }
  }

  function applyInitialQueryFilters() {
    const params = new URLSearchParams(window.location.search);
    setSelectValue(groupSelect, queryValue(params, ["group", "baseGroup"]));
    setSelectValue(lootSelect, queryValue(params, ["loot", "lootCategory"]));
    setSelectValue(categorySelect, queryValue(params, ["category", "baseCategory"]));
    setSelectValue(classSelect, queryValue(params, ["class", "baseClass"]));
    setSelectValue(tierSelect, queryValue(params, ["tier"]));
    setSelectValue(speedSelect, queryValue(params, ["speed"]));
    setSelectValue(minSocketsSelect, queryValue(params, ["minSockets", "sockets"]));
    if (searchInput) {
      searchInput.value = queryValue(params, ["q", "search"]);
      const mastSearch = document.querySelector("#mast-search-input");
      if (mastSearch && searchInput.value) {
        mastSearch.value = searchInput.value;
      }
    }
    if (rollInput) {
      rollInput.value = queryValue(params, ["roll"]);
    }
    if (twoHandedCheckbox) {
      twoHandedCheckbox.checked = queryValue(params, ["twoHanded"]) === "1";
    }
  }

  function applyFilters() {
    const query = normalizeText(searchInput ? searchInput.value : "");
    const activeGroup = groupSelect ? groupSelect.value : "all";
    const activeCategory = categorySelect ? categorySelect.value : "all";
    const activeClass = classSelect ? classSelect.value : "all";
    const activeTier = tierSelect ? tierSelect.value : "all";
    const activeSpeed = speedSelect ? speedSelect.value : "all";
    const minSockets = Number(minSocketsSelect ? minSocketsSelect.value : 0);
    const rollQuery = normalizeText(rollInput ? rollInput.value : "");
    const twoHandedOnly = Boolean(twoHandedCheckbox && twoHandedCheckbox.checked);
    let visibleFamilies = 0;

    families.forEach((family) => {
      const familyGroup = family.dataset.baseGroup || "";
      const familyClasses = normalizeText(family.dataset.baseClasses || "");
      const familySearch = normalizeText(family.dataset.search || "");
      const groupOk = activeGroup === "all" || normalizeText(familyGroup) === normalizeText(activeGroup);
      const classOk = activeClass === "all" || familyClasses.split(/\s+/).includes(normalizeText(activeClass));
      const familySearchOk = !query || familySearch.includes(query);
      
      const items = Array.from(family.querySelectorAll(".base-item-card"));
      let visibleItems = 0;

      items.forEach((item) => {
        const itemSearch = normalizeText(item.dataset.search || "");
        const itemCategories = normalizeText(item.dataset.typeCategories || "").split("|").filter(Boolean);
        const searchOk = !query || familySearchOk || itemSearch.includes(query);
        const codes = (item.dataset.typeCodes || "").split("|");
        const normalizedCodes = codes.map(normalizeText).filter(Boolean);
        const normalizedCategory = normalizeText(activeCategory);
        const rulesOk = (!includedTypes.length || includedTypes.some(code => codes.includes(code)))
          && !excludedTypes.some(code => codes.includes(code));
        const lootOk = !lootSelect || lootSelect.value === "all"
          || normalizeText(item.dataset.lootCategory || "") === normalizeText(lootSelect.value);
        const categoryOk = activeCategory === "all"
          || normalizedCodes.includes(normalizedCategory)
          || itemCategories.includes(normalizedCategory);
        const tierOk = activeTier === "all" || normalizeText(item.dataset.tier || "") === normalizeText(activeTier);
        const speedOk = activeSpeed === "all"
          || normalizeText(item.dataset.speed || "") === normalizeText(activeSpeed);
        const socketsOk = !minSockets || Number(item.dataset.maxSockets || 0) >= minSockets;
        const rollOk = !rollQuery || normalizeText(item.dataset.rollSearch || "").includes(rollQuery);
        const twoHandedOk = !twoHandedOnly || item.dataset.twoHanded === "1";
        
        const itemVisible = rulesOk && lootOk && groupOk && classOk && categoryOk && searchOk && tierOk && speedOk && socketsOk && rollOk && twoHandedOk;
        item.hidden = !itemVisible;
        item.style.display = itemVisible ? "" : "none";
        
        if (itemVisible) {
          visibleItems += 1;
        }
      });

      const familyVisible = visibleItems > 0;
      family.hidden = !familyVisible;
      family.style.display = familyVisible ? "" : "none";
      if (familyVisible) {
        visibleFamilies += 1;
      }
    });

    if (resultCount) {
      resultCount.textContent = String(visibleFamilies);
    }
  }

  [searchInput, groupSelect, categorySelect, lootSelect, classSelect, tierSelect, speedSelect, minSocketsSelect, rollInput, twoHandedCheckbox]
    .filter(Boolean)
    .forEach((control) => {
      control.addEventListener("input", applyFilters);
      control.addEventListener("change", applyFilters);
    });

  applyInitialQueryFilters();
  applyFilters();
}

async function wireAreaIndex() {
  const toolbar = document.querySelector("[data-area-index-url]");
  const root = document.querySelector("#area-index-root");
  const cardRoot = document.querySelector("#area-card-root");
  if (!toolbar || !root || !cardRoot) {
    return;
  }

  const immunityMeta = parseImmunityMeta(toolbar);
  const response = await fetch(toolbar.dataset.areaIndexUrl, { cache: "no-store" });
  const areas = await response.json();
  const searchInput = document.querySelector("#area-search");
  const actSelect = document.querySelector("#area-act-filter");
  const minLevelSelect = document.querySelector("#area-min-level-filter");
  const sortSelect = document.querySelector("#area-sort-filter");
  const avoidCheckboxes = Array.from(document.querySelectorAll("[data-avoid-immunity]"));
  const resultCount = document.querySelector("#area-result-count");

  function sortedAreas(rows) {
    const sortMode = sortSelect ? sortSelect.value : "density";
    const sorters = {
      density: (area) => area.monster_density,
      level: (area) => area.area_level,
      elite: (area) => area.elite_avg,
    };
    const score = sorters[sortMode] || sorters.density;
    return rows.slice().sort((left, right) => {
      const delta = score(right) - score(left);
      if (delta !== 0) {
        return delta;
      }
      return String(left.display_name).localeCompare(String(right.display_name));
    });
  }

  function applyFilters() {
    const query = normalizeText(searchInput ? searchInput.value : "");
    const act = actSelect ? actSelect.value : "all";
    const minLevel = Number(minLevelSelect ? minLevelSelect.value : 0);
    const avoidImmunities = avoidCheckboxes
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.dataset.avoidImmunity);

    const filtered = areas.filter((area) => {
      const immunities = areaMonsterImmunities(area);
      const searchOk = !query || normalizeText(area.search_text).includes(query);
      const actOk = act === "all"
        || (area.act_id !== undefined && area.act_id !== null && String(area.act_id) === String(act))
        || String(area.act || "") === String(act);
      const levelOk = area.area_level >= minLevel;
      const immunityOk = avoidImmunities.every((immunity) => !immunities.includes(immunity));
      return searchOk && actOk && levelOk && immunityOk;
    });

    const sorted = sortedAreas(filtered);
    const noMatches = escapeHtml(tUi("areas.no_matches", "No areas match the current filters."));
    root.innerHTML = sorted.map((area) => areaRowMarkup(area, immunityMeta)).join("")
      || `<tr><td colspan="7" class="muted">${noMatches}</td></tr>`;
    cardRoot.innerHTML = sorted.map((area) => areaCardMarkup(area, immunityMeta)).join("")
      || `<p class="muted">${noMatches}</p>`;
    if (resultCount) {
      resultCount.textContent = String(filtered.length);
    }
  }

  [searchInput, actSelect, minLevelSelect, sortSelect, ...avoidCheckboxes]
    .filter(Boolean)
    .forEach((control) => control.addEventListener("input", applyFilters));
  [actSelect, minLevelSelect, sortSelect, ...avoidCheckboxes]
    .filter(Boolean)
    .forEach((control) => control.addEventListener("change", applyFilters));

  applyFilters();
}

async function wireItemIndex() {
  const toolbar = document.querySelector("[data-item-index-url]");
  const affixIndex = document.querySelector("[data-affix-index]");
  const root = document.querySelector("#item-index-root");
  if ((!toolbar && !affixIndex) || !root) {
    return;
  }

  // Cards and their history are server-rendered; enhance them without a second download.
  const searchInput = document.querySelector("#page-search");
  const familyCheckboxes = Array.from(document.querySelectorAll("input[data-filter-family]"));
  const groupSelect = document.querySelector("#item-group-filter");
  const typeSelect = document.querySelector(affixIndex ? "#affix-item-type-filter" : "#item-type-filter");
  const rareOnly = document.querySelector("#affix-rare-filter");
  const showDisabled = document.querySelector("#affix-disabled-filter");
  const dropLevelSelect = document.querySelector("#item-drop-level-filter");
  const cards = Array.from(document.querySelectorAll(".base-item-card[data-family]"));
  const familySections = Array.from(document.querySelectorAll("[data-section-family]"));
  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get("q");
  const changesOnly = document.querySelector("#affix-changes-filter");
  const resultCount = document.querySelector("#item-result-count");
  const emptyMessage = document.querySelector("#item-empty-message");
  const resetButton = document.querySelector("#item-reset-filters");
  if (affixIndex && params.has("qualities")) {
    const selected = params.get("qualities").split(",");
    familyCheckboxes.forEach((control) => { control.checked = selected.includes(control.dataset.filterFamily); });
  }
  if (changesOnly) changesOnly.checked = params.get("changes") === "1";
  if (rareOnly) rareOnly.checked = params.get("rare") === "1";
  if (showDisabled) showDisabled.checked = params.get("disabled") === "1";
  if (affixIndex && typeSelect && params.has("type")
      && Array.from(typeSelect.options).some((option) => option.value === params.get("type"))) {
    typeSelect.value = params.get("type");
  }

  let activeGroup = "all";
  let activeType = affixIndex && typeSelect ? typeSelect.value : "all";
  let activeDropLevel = 0;

  function getActiveFamilies() {
    const checked = familyCheckboxes.filter((cb) => cb.checked).map((cb) => cb.dataset.filterFamily);
    if (affixIndex) return new Set(checked);
    // All checked (or none) → show everything
    return checked.length === 0 || checked.length === familyCheckboxes.length
      ? new Set()
      : new Set(checked);
  }

  function applyFilters() {
    const query = normalizeText(searchInput ? searchInput.value : "");
    const activeFamilies = getActiveFamilies();
    let visibleCount = 0;
    cards.forEach((card) => {
      const family = card.dataset.family || "";
      const itemGroup = card.dataset.itemGroup || "";
      const itemType = rareOnly?.checked ? card.dataset.affixRareTypes : card.dataset.itemType;
      const dropLevel = Number(card.dataset.dropLevel || 0);
      const haystack = normalizeText(card.dataset.search);
      const familyOk = !familyCheckboxes.length || activeFamilies.has(family)
        || (!affixIndex && activeFamilies.size === 0);
      const groupOk = activeGroup === "all" || normalizeText(itemGroup).split("|").includes(normalizeText(activeGroup));
      const typeOk = activeType === "all" || normalizeText(itemType).split("|").includes(normalizeText(activeType));
      const dropLevelOk = !activeDropLevel || dropLevel >= activeDropLevel;
      const searchOk = !query || haystack.includes(query);
      const changeOk = !changesOnly?.checked || card.dataset.status !== "unchanged";
      const rareOk = !rareOnly?.checked || card.dataset.affixRareTypes !== undefined;
      const spawnOk = !showDisabled || showDisabled.checked || card.dataset.affixSpawnable === "1";
      card.hidden = !(familyOk && groupOk && typeOk && dropLevelOk && searchOk && changeOk && rareOk && spawnOk);
      if (!card.hidden) visibleCount += 1;
    });
    familySections.forEach((section) => {
      section.hidden = section.querySelectorAll(".base-item-card[data-family]:not([hidden])").length === 0;
    });
    if (affixIndex && resultCount) {
      resultCount.textContent = tUi("common.count_of_total", "{visible} of {total} {noun}", {
        visible: visibleCount,
        total: cards.length,
        noun: affixIndex.dataset.affixIndex,
      });
    }
    if (emptyMessage) emptyMessage.hidden = visibleCount > 0;
  }

  function updateFilters() {
    applyFilters();
    if (!affixIndex) return;

    const url = new URL(window.location.href);
    if (searchInput.value.trim()) url.searchParams.set("q", searchInput.value.trim());
    else url.searchParams.delete("q");
    if (changesOnly.checked) url.searchParams.set("changes", "1");
    else url.searchParams.delete("changes");
    if (rareOnly?.checked) url.searchParams.set("rare", "1");
    else url.searchParams.delete("rare");
    if (showDisabled?.checked) url.searchParams.set("disabled", "1");
    else url.searchParams.delete("disabled");
    if (activeType !== "all") url.searchParams.set("type", activeType);
    else url.searchParams.delete("type");
    const selected = getActiveFamilies();
    if (selected.size !== familyCheckboxes.length) url.searchParams.set("qualities", Array.from(selected).join(","));
    else url.searchParams.delete("qualities");
    if (url.href !== window.location.href) window.history.replaceState(null, "", url.href);
  }

  if (searchInput) {
    if (initialQuery) {
      searchInput.value = initialQuery;
      const mastSearch = document.querySelector("#mast-search-input");
      if (mastSearch) {
        mastSearch.value = initialQuery;
      }
    }
    searchInput.addEventListener("input", updateFilters);
  }
  familyCheckboxes.forEach((cb) => cb.addEventListener("change", updateFilters));
  changesOnly?.addEventListener("change", updateFilters);
  rareOnly?.addEventListener("change", updateFilters);
  showDisabled?.addEventListener("change", updateFilters);
  resetButton?.addEventListener("click", () => {
    searchInput.value = "";
    const mastSearch = document.querySelector("#mast-search-input");
    if (mastSearch) mastSearch.value = "";
    familyCheckboxes.forEach((control) => { control.checked = true; });
    changesOnly.checked = false;
    if (rareOnly) rareOnly.checked = false;
    if (showDisabled) showDisabled.checked = false;
    if (affixIndex && typeSelect) {
      typeSelect.value = "all";
      activeType = "all";
    }
    updateFilters();
  });
  if (groupSelect) {
    groupSelect.addEventListener("change", () => {
      activeGroup = groupSelect.value || "all";
      if (typeSelect && activeGroup !== "all") {
        const currentType = typeSelect.value;
        const allowed = Array.from(typeSelect.options).some((option) => {
          const optgroupKey = option.parentElement?.dataset?.groupCode || option.parentElement?.label;
          return option.value === currentType
            && option.parentElement
            && option.parentElement.tagName === "OPTGROUP"
            && normalizeText(optgroupKey) === normalizeText(activeGroup);
        });
        if (!allowed && currentType !== "all") {
          typeSelect.value = "all";
          activeType = "all";
        }
      }
      applyFilters();
    });
  }
  if (typeSelect) {
    typeSelect.addEventListener("change", () => {
      activeType = typeSelect.value || "all";
      updateFilters();
    });
  }
  if (dropLevelSelect) {
    dropLevelSelect.addEventListener("change", () => {
      activeDropLevel = Number(dropLevelSelect.value || 0);
      applyFilters();
    });
  }
  applyFilters();
}

function wireAffixView() {
  const toggle = document.querySelector("[data-affix-view]");
  if (!toggle) return false;

  const links = Array.from(toggle.querySelectorAll("[data-affix-view-link]"));
  const activeView = toggle.dataset.affixView;
  const requestedView = new URL(window.location.href).searchParams.get("view");
  const storageKey = "wiki.affixView";
  const validView = (view) => view === "function" || view === "cards";
  let selectedView = activeView;

  if (validView(requestedView)) {
    selectedView = requestedView;
  } else if (toggle.hasAttribute("data-affix-default-entry")) {
    selectedView = "function";
    try {
      const savedView = window.localStorage.getItem(storageKey);
      if (validView(savedView)) selectedView = savedView;
    } catch {
      // The function view remains usable when browser storage is unavailable.
    }
  }

  function saveView(view) {
    try {
      window.localStorage.setItem(storageKey, view);
    } catch {
      // Explicit view links also work without persistent browser storage.
    }
  }

  function viewUrl(link) {
    const target = new URL(link.href, window.location.href);
    target.search = window.location.search;
    target.hash = window.location.hash;
    target.searchParams.set("view", link.dataset.affixViewLink);
    return target;
  }

  links.forEach((link) => {
    link.href = viewUrl(link).href;
    link.addEventListener("click", () => {
      saveView(link.dataset.affixViewLink);
      link.href = viewUrl(link).href;
    });
  });
  saveView(selectedView);
  if (selectedView !== activeView) {
    const link = links.find((link) => link.dataset.affixViewLink === selectedView);
    window.location.replace(viewUrl(link).href);
    return true;
  }
  return false;
}

function initWiki() {
  if (wireAffixView()) return;
  wireMastSearch();
  wireRunewordFilters();
  wireStaticSearch();
  wireBaseFilters();
  wireAreaIndex().catch((error) => {
    const root = document.querySelector("#area-index-root");
    if (root) {
      root.innerHTML = `<tr><td colspan="7" class="muted">${escapeHtml(tUi("areas.load_error", "Unable to load the area index."))}</td></tr>`;
    }
    console.error(error);
  });
  wireItemIndex().catch((error) => {
    // Preserve the server-rendered cards and history if enhancement fails.
    console.error(error);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initWiki);
} else {
  initWiki();
}

// Keep search and anchor context when changing comparison baselines or locales.
document.querySelectorAll("[data-comparison-link], [data-locale-link]").forEach((link) => {
  function updateComparisonTarget() {
    const target = new URL(link.href);
    target.search = window.location.search;
    target.hash = window.location.hash;
    const search = document.querySelector("#page-search, #area-search") || document.querySelector("#skill-search");
    if (search) {
      if (search.value.trim()) target.searchParams.set("q", search.value.trim());
      else target.searchParams.delete("q");
    }
    link.href = target.href;
  }
  // Read live state, including input or anchor changes after page load.
  link.addEventListener("click", updateComparisonTarget);
  link.addEventListener("auxclick", updateComparisonTarget);
  updateComparisonTarget();
});

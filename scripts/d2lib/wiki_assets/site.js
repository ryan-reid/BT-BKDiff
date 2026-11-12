function normalizeText(value) {
  return (value || "").toLowerCase().trim();
}

function statusLabel(status) {
  if (status === "modified") {
    return '<span class="item-card-status is-modified">Modified</span>';
  }
  if (status === "added") {
    return '<span class="item-card-status is-added">BK Only</span>';
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
  return `<span class="area-badge area-badge-level">Lvl ${escapeHtml(area.area_level)}</span>`;
}

const IMMUNITY_CLASS = {
  fire: "im-fire",
  cold: "im-cold",
  lightning: "im-lightning",
  poison: "im-poison",
  physical: "im-physical",
  magic: "im-magic",
};

function areaImmunityMarkup(area) {
  const immunities = areaMonsterImmunities(area);
  if (immunities.length === 0) {
    return '<span class="muted">—</span>';
  }
  return immunities
    .map((immunity) => {
      const count = area.immunity_counts && area.immunity_counts[immunity]
        ? ` (${area.immunity_counts[immunity]})`
        : "";
      const cls = IMMUNITY_CLASS[immunity.toLowerCase()] || "";
      return `<span class="immunity-chip ${cls}">${escapeHtml(immunity)}${escapeHtml(count)}</span>`;
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

function areaMonsterPoolMarkup(area) {
  const monsters = area.monster_pool || [];
  if (monsters.length === 0) {
    return '<span class="muted">No monster pool</span>';
  }
  const preview = monsters
    .slice(0, 8)
    .map((monster) => {
      const immunities = monster.immunities && monster.immunities.length
        ? `: ${monster.immunities.join(", ")} immune`
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
      <summary>+${hiddenMonsters.length} more</summary>
      ${hiddenMonsters.map((monster) => {
        const immunities = monster.immunities && monster.immunities.length
          ? `: ${monster.immunities.join(", ")} immune`
          : "";
        return `<span>${escapeHtml(monster.name || monster.id)}${escapeHtml(immunities)}</span>`;
      }).join("")}
    </details>
  `;
}

function areaMonsterListMarkup(area) {
  const monsters = area.monster_pool || [];
  if (monsters.length === 0) {
    return '<p class="muted">No monster pool data.</p>';
  }
  return `
    <ul class="area-monster-list">
      ${monsters.map((monster) => {
        const immunities = monster.immunities && monster.immunities.length
          ? `<span>${escapeHtml(monster.immunities.join(", "))} immune</span>`
          : "";
        return `<li><strong>${escapeHtml(monster.name || monster.id)}</strong>${immunities}</li>`;
      }).join("")}
    </ul>
  `;
}

function areaSuperChestMarkup(area) {
  if (!area.has_super_chest) {
    return '<span class="muted">No</span>';
  }

  const sources = area.super_chest_sources || [];
  const names = Array.from(new Set(sources.map((source) => source.object_class).filter(Boolean)));
  const label = area.super_chest_count > 1 ? `Yes (${area.super_chest_count})` : "Yes";
  const detail = names.length ? `<br><span class="muted">${escapeHtml(names.slice(0, 3).join(", "))}</span>` : "";
  return `<span class="area-badge area-badge-super">Super chest</span><br><strong>${escapeHtml(label)}</strong>${detail}`;
}

function areaMazeMarkup(area) {
  if (!area.estimated_area_tiles) {
    return '<span class="muted">Unknown</span>';
  }

  const chunk = area.maze_chunk_width && area.maze_chunk_height
    ? `${area.maze_chunk_width}x${area.maze_chunk_height}`
    : "Unknown";
  const rooms = area.maze_rooms ? `${area.maze_rooms} room${area.maze_rooms === 1 ? "" : "s"}` : "Unknown rooms";
  const source = area.maze_source === "lvlmaze" ? "LvlMaze" : "Levels";
  return `
    <strong>${escapeHtml(chunk)}</strong><br>
    <span class="muted">${escapeHtml(rooms)}</span><br>
    <span class="muted">${escapeHtml(area.estimated_area_tiles)} tiles &middot; ${escapeHtml(source)}</span>
  `;
}

function areaRowMarkup(area) {
  return `
    <tr>
      <th>
        <span class="area-name">${escapeHtml(area.display_name)}</span>
        <span class="area-meta">${escapeHtml(area.act)}</span>
        <span class="area-badge-row">${areaBadgeMarkup(area)}</span>
      </th>
      <td>${escapeHtml(area.monster_density)}</td>
      <td>${areaMazeMarkup(area)}</td>
      <td>${escapeHtml(area.elite_min)}-${escapeHtml(area.elite_max)}<br><span class="muted">Avg ${escapeHtml(area.elite_avg)}</span></td>
      <td>${areaSuperChestMarkup(area)}</td>
      <td><span class="immunity-list">${areaImmunityMarkup(area)}</span></td>
      <td>${areaMonsterPoolMarkup(area)}</td>
    </tr>
  `;
}

function areaCardMarkup(area) {
  return `
    <article class="area-card" data-search="${escapeHtml(area.search_text)}">
      <div class="area-card-head">
        <div>
          <h3>${escapeHtml(area.display_name)}</h3>
          <span>${escapeHtml(area.act)}</span>
        </div>
        <span class="area-level-pill">Lvl ${escapeHtml(area.area_level)}</span>
      </div>
      <dl class="area-card-stats">
        <div><dt>Density</dt><dd>${escapeHtml(area.monster_density)}</dd></div>
        <div><dt>Elite Packs</dt><dd>${escapeHtml(area.elite_min)}-${escapeHtml(area.elite_max)} <span>Avg ${escapeHtml(area.elite_avg)}</span></dd></div>
        <div><dt>Super Chest</dt><dd>${area.has_super_chest ? escapeHtml(area.super_chest_count || 1) : "No"}</dd></div>
      </dl>
      <div class="area-card-section">
        <span class="area-card-label">Possible Immunities</span>
        <div class="immunity-list">${areaImmunityMarkup(area)}</div>
      </div>
      <details class="area-card-details">
        <summary>Monster pool</summary>
        ${areaMonsterListMarkup(area)}
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
    emptyMessage.textContent = "No matching entries.";
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
    .map((query) => query.replace(/\brune\b/g, "").trim())
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
  emptyMessage.textContent = "No runewords match the current filters.";
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
      const groupOk = activeGroup === "all" || familyGroup === activeGroup;
      const classOk = activeClass === "all" || familyClasses.split(/\s+/).includes(normalizeText(activeClass));
      const familySearchOk = !query || familySearch.includes(query);
      
      const items = Array.from(family.querySelectorAll(".base-item-card"));
      let visibleItems = 0;

      items.forEach((item) => {
        const itemSearch = normalizeText(item.dataset.search || "");
        const itemCategories = normalizeText(item.dataset.typeCategories || "").split("|").filter(Boolean);
        const searchOk = !query || familySearchOk || itemSearch.includes(query);
        const codes = (item.dataset.typeCodes || "").split("|");
        const rulesOk = (!includedTypes.length || includedTypes.some(code => codes.includes(code)))
          && !excludedTypes.some(code => codes.includes(code));
        const lootOk = !lootSelect || lootSelect.value === "all" || item.dataset.lootCategory === lootSelect.value;
        const categoryOk = activeCategory === "all" || itemCategories.includes(normalizeText(activeCategory));
        const tierOk = activeTier === "all" || item.dataset.tier === activeTier;
        const speedOk = activeSpeed === "all" || item.dataset.speedLabel === activeSpeed;
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
      const actOk = act === "all" || area.act === act;
      const levelOk = area.area_level >= minLevel;
      const immunityOk = avoidImmunities.every((immunity) => !immunities.includes(immunity));
      return searchOk && actOk && levelOk && immunityOk;
    });

    const sorted = sortedAreas(filtered);
    root.innerHTML = sorted.map(areaRowMarkup).join("")
      || '<tr><td colspan="7" class="muted">No areas match the current filters.</td></tr>';
    cardRoot.innerHTML = sorted.map(areaCardMarkup).join("")
      || '<p class="muted">No areas match the current filters.</p>';
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
    if (affixIndex && resultCount) resultCount.textContent = `${visibleCount} of ${cards.length} ${affixIndex.dataset.affixIndex}`;
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
        const allowed = Array.from(typeSelect.options).some((option) =>
          option.value === currentType
          && option.parentElement
          && option.parentElement.tagName === "OPTGROUP"
          && option.parentElement.label === activeGroup
        );
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

function initWiki() {
  wireMastSearch();
  wireRunewordFilters();
  wireStaticSearch();
  wireBaseFilters();
  wireAreaIndex().catch((error) => {
    const root = document.querySelector("#area-index-root");
    if (root) {
      root.innerHTML = '<tr><td colspan="7" class="muted">Unable to load the area index.</td></tr>';
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

// Keep search and anchor context when changing comparison baselines.
document.querySelectorAll("[data-comparison-link]").forEach((link) => {
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

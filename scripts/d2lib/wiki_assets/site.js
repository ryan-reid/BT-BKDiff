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

function itemCardMarkup(item, siteRoot) {
  const nameColor = item.family === "set" ? "var(--q-set)" : "var(--q-unique)";
  const iconMarkup = item.icon_src
    ? `<img class="wiki-item-icon set-th-icon" src="${escapeHtml(siteRoot + item.icon_src)}" alt="${escapeHtml(item.title)} icon" />`
    : "";
  const dropMarkup = item.drop_level_label
    ? `<span class="item-drop-level">Drop ${escapeHtml(item.drop_level_label)}</span>`
    : "";
  const titleMarkup = item.family === "set"
    ? `<a class="set-th-name" href="${escapeHtml(siteRoot + item.href)}" style="color:${nameColor}">${escapeHtml(item.title)}</a>`
    : `<span class="set-th-name" style="color:${nameColor}">${escapeHtml(item.title)}</span>`;

  const statRowsHtml = (item.stat_rows || []).map((r) => `
    <div class="sp-row">
      <span class="sp-cell is-${escapeHtml(r.status)}"><strong>${escapeHtml(r.label)}:</strong> ${escapeHtml(r.old || "—")}</span>
      <span class="sp-cell is-${escapeHtml(r.status)}"><strong>${escapeHtml(r.label)}:</strong> ${escapeHtml(r.new || "—")}</span>
    </div>`).join("");

  const propRows = item.property_rows || [];
  const propRowsHtml = propRows.length
    ? `<div class="sp-sep">Properties</div>` + propRows.map((r) => `
    <div class="sp-row">
      <span class="sp-cell is-${escapeHtml(r.status)}">${escapeHtml(r.old || "(empty)")}</span>
      <span class="sp-cell is-${escapeHtml(r.status)}">${escapeHtml(r.new || "(removed)")}</span>
    </div>`).join("")
    : "";

  const oldLabel = document.body.dataset.oldLabel || "Retail";
  const newLabel = document.body.dataset.newLabel || "BK";

  return `
    <div class="base-item-card item-index-card" style="padding:0;overflow:hidden"
      data-family="${escapeHtml(item.family)}"
      data-status="${escapeHtml(item.status)}"
      data-item-group="${escapeHtml(item.item_group)}"
      data-item-type="${escapeHtml(item.item_type)}"
      data-drop-level="${escapeHtml(item.drop_level || 0)}"
      data-search="${escapeHtml(item.search_text)}">
      <div class="sp-head">
        ${iconMarkup}
        <div style="min-width:0;flex:1">
          ${titleMarkup}
          <span class="set-th-meta">${escapeHtml(item.summary)}</span>
          ${dropMarkup}
        </div>
      </div>
      <div class="sp-sub"><span>${escapeHtml(oldLabel)}</span><span>${escapeHtml(newLabel)}</span></div>
      ${statRowsHtml}
      ${propRowsHtml}
    </div>
  `;
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
  if (!area.possible_immunities || area.possible_immunities.length === 0) {
    return '<span class="muted">—</span>';
  }
  return area.possible_immunities
    .map((immunity) => {
      const count = area.immunity_counts && area.immunity_counts[immunity]
        ? ` (${area.immunity_counts[immunity]})`
        : "";
      const cls = IMMUNITY_CLASS[immunity.toLowerCase()] || "";
      return `<span class="immunity-chip ${cls}">${escapeHtml(immunity)}${escapeHtml(count)}</span>`;
    })
    .join("");
}

function areaMonsterPoolMarkup(area) {
  const monsters = area.monster_pool || [];
  if (monsters.length === 0) {
    return '<span class="muted">No monster pool</span>';
  }
  return monsters
    .slice(0, 8)
    .map((monster) => {
      const immunities = monster.immunities && monster.immunities.length
        ? `: ${monster.immunities.join(", ")} immune`
        : "";
      return `${escapeHtml(monster.name || monster.id)}${escapeHtml(immunities)}`;
    })
    .join("<br>");
}

function areaMonsterListMarkup(area) {
  const monsters = area.monster_pool || [];
  if (monsters.length === 0) {
    return '<p class="muted">No monster pool data.</p>';
  }
  return `
    <ul class="area-monster-list">
      ${monsters.slice(0, 8).map((monster) => {
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
  const cards = Array.from(document.querySelectorAll(".item-card, .base-item-card, .recipe-card, .guide-card, .set-piece, .corruption-summary-card"));
  const tableRows = Array.from(document.querySelectorAll("tbody tr[data-search]"));
  const sections = Array.from(document.querySelectorAll(".recipe-group, .recipe-group-section, .misc-group-section, .family-container, .set-block"));
  const filterButtons = Array.from(document.querySelectorAll("[data-recipe-filter]"));
  let activeRecipeFilter = "all";
  let emptyMessage = null;
  
  if (!searchInput || document.querySelector("[data-item-index-url]") || document.querySelector("[data-base-filters]")) {
    return;
  }

  const initialQuery = new URLSearchParams(window.location.search).get("q");
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
    pageSearch.insertAdjacentElement("afterend", emptyMessage);
  }

  function filterTags(element) {
    return normalizeText(element && element.dataset ? element.dataset.filterTags : "")
      .split("|")
      .map((tag) => tag.trim())
      .filter(Boolean);
  }

  function matchesFilter(element) {
    return activeRecipeFilter === "all" || filterTags(element).includes(activeRecipeFilter);
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
      emptyMessage.hidden = (!query && activeRecipeFilter === "all") || hasResults;
    }
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeRecipeFilter = normalizeText(button.dataset.recipeFilter || "all") || "all";
      filterButtons.forEach((candidate) => candidate.classList.toggle("is-active", candidate === button));
      applySearch();
    });
  });

  searchInput.addEventListener("input", applySearch);
  applySearch();
}

function wireMastSearch() {
  const mastSearch = document.querySelector("#mast-search-input");
  if (!mastSearch) {
    return;
  }

  function pageSearchInput() {
    return document.querySelector("#page-search, #area-search");
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
        const categoryOk = activeCategory === "all" || itemCategories.includes(normalizeText(activeCategory));
        const tierOk = activeTier === "all" || item.dataset.tier === activeTier;
        const speedOk = activeSpeed === "all" || item.dataset.speedLabel === activeSpeed;
        const socketsOk = !minSockets || Number(item.dataset.maxSockets || 0) >= minSockets;
        const rollOk = !rollQuery || normalizeText(item.dataset.rollSearch || "").includes(rollQuery);
        const twoHandedOk = !twoHandedOnly || item.dataset.twoHanded === "1";
        
        const itemVisible = groupOk && classOk && categoryOk && searchOk && tierOk && speedOk && socketsOk && rollOk && twoHandedOk;
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

  [searchInput, groupSelect, categorySelect, classSelect, tierSelect, speedSelect, minSocketsSelect, rollInput, twoHandedCheckbox]
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
      const immunities = area.possible_immunities || [];
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
  const root = document.querySelector("#item-index-root");
  if (!toolbar || !root) {
    return;
  }

  const siteRoot = document.body.dataset.siteRoot || "";
  const response = await fetch(toolbar.dataset.itemIndexUrl, { cache: "no-store" });
  const items = await response.json();
  const familyLabels = {
    unique: "Unique Items",
    set: "Set Items",
  };

  root.innerHTML = Object.entries(familyLabels)
    .map(([family, label]) => {
      const familyItems = items.filter((item) => item.family === family);
      return `
        <section class="item-family-section" data-section-family="${family}" style="display:grid;gap:12px">
          <div class="section-head"><h2>${label}</h2><p>${familyItems.length} pages</p></div>
          <div class="family-items-grid">
            ${familyItems.map((item) => itemCardMarkup(item, siteRoot)).join("")}
          </div>
        </section>
      `;
    })
    .join("");

  const searchInput = document.querySelector("#page-search");
  const familyCheckboxes = Array.from(document.querySelectorAll("input[data-filter-family]"));
  const groupSelect = document.querySelector("#item-group-filter");
  const typeSelect = document.querySelector("#item-type-filter");
  const dropLevelSelect = document.querySelector("#item-drop-level-filter");
  const cards = Array.from(document.querySelectorAll(".base-item-card[data-family]"));
  const familySections = Array.from(document.querySelectorAll("[data-section-family]"));
  const initialQuery = new URLSearchParams(window.location.search).get("q");

  let activeGroup = "all";
  let activeType = "all";
  let activeDropLevel = 0;

  function getActiveFamilies() {
    const checked = familyCheckboxes.filter((cb) => cb.checked).map((cb) => cb.dataset.filterFamily);
    // All checked (or none) → show everything
    return checked.length === 0 || checked.length === familyCheckboxes.length
      ? new Set()
      : new Set(checked);
  }

  function applyFilters() {
    const query = normalizeText(searchInput ? searchInput.value : "");
    const activeFamilies = getActiveFamilies();
    cards.forEach((card) => {
      const family = card.dataset.family || "";
      const itemGroup = card.dataset.itemGroup || "";
      const itemType = card.dataset.itemType || "";
      const dropLevel = Number(card.dataset.dropLevel || 0);
      const haystack = normalizeText(card.dataset.search);
      const familyOk = activeFamilies.size === 0 || activeFamilies.has(family);
      const groupOk = activeGroup === "all" || normalizeText(itemGroup) === normalizeText(activeGroup);
      const typeOk = activeType === "all" || normalizeText(itemType) === normalizeText(activeType);
      const dropLevelOk = !activeDropLevel || dropLevel >= activeDropLevel;
      const searchOk = !query || haystack.includes(query);
      card.hidden = !(familyOk && groupOk && typeOk && dropLevelOk && searchOk);
    });
    familySections.forEach((section) => {
      section.hidden = section.querySelectorAll(".base-item-card[data-family]:not([hidden])").length === 0;
    });
  }

  if (searchInput) {
    if (initialQuery) {
      searchInput.value = initialQuery;
      const mastSearch = document.querySelector("#mast-search-input");
      if (mastSearch) {
        mastSearch.value = initialQuery;
      }
    }
    searchInput.addEventListener("input", applyFilters);
  }
  familyCheckboxes.forEach((cb) => cb.addEventListener("change", applyFilters));
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
      applyFilters();
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
    const root = document.querySelector("#item-index-root");
    if (root) {
      root.innerHTML = '<p class="muted">Unable to load the item index.</p>';
    }
    console.error(error);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initWiki);
} else {
  initWiki();
}

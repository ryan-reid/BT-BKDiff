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
  const familyLabel = item.family.charAt(0).toUpperCase() + item.family.slice(1);
  return `
    <a class="item-card" href="${escapeHtml(siteRoot + item.href)}"
      data-family="${escapeHtml(item.family)}"
      data-status="${escapeHtml(item.status)}"
      data-item-group="${escapeHtml(item.item_group)}"
      data-item-type="${escapeHtml(item.item_type)}"
      data-search="${escapeHtml(item.search_text)}">
      <div class="item-card-meta">
        <span class="item-card-family">${escapeHtml(familyLabel)}</span>
        ${statusLabel(item.status)}
      </div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.summary)}</p>
    </a>
  `;
}

function areaBadgeMarkup(area) {
  const badges = [];
  if (area.area_level >= 87) {
    badges.push('<span class="area-badge">87+</span>');
  }
  if (area.can_drop_top_tier) {
    badges.push('<span class="area-badge area-badge-accent">Top-tier</span>');
  }
  if (area.monster_density >= 3000) {
    badges.push('<span class="area-badge">High density</span>');
  }
  return badges.join("");
}

function areaImmunityMarkup(area) {
  if (!area.possible_immunities || area.possible_immunities.length === 0) {
    return '<span class="muted">None flagged</span>';
  }
  return area.possible_immunities
    .map((immunity) => {
      const count = area.immunity_counts && area.immunity_counts[immunity]
        ? ` (${area.immunity_counts[immunity]})`
        : "";
      return `<span class="immunity-chip">${escapeHtml(immunity)}${escapeHtml(count)}</span>`;
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

function areaSuperChestMarkup(area) {
  if (!area.has_super_chest) {
    return '<span class="muted">No</span>';
  }

  const sources = area.super_chest_sources || [];
  const names = Array.from(new Set(sources.map((source) => source.object_class).filter(Boolean)));
  const label = area.super_chest_count > 1 ? `Yes (${area.super_chest_count})` : "Yes";
  const detail = names.length ? `<br><span class="muted">${escapeHtml(names.slice(0, 3).join(", "))}</span>` : "";
  return `<span class="area-badge area-badge-accent">Super Chest</span><br><strong>${escapeHtml(label)}</strong>${detail}`;
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
      <td><strong>${escapeHtml(area.farm_score)}</strong></td>
      <td>Area ${escapeHtml(area.area_level)}</td>
      <td>${escapeHtml(area.monster_density)}</td>
      <td>${areaMazeMarkup(area)}</td>
      <td>${escapeHtml(area.elite_min)}-${escapeHtml(area.elite_max)}<br><span class="muted">Avg ${escapeHtml(area.elite_avg)}</span></td>
      <td>${areaSuperChestMarkup(area)}</td>
      <td><span class="immunity-list">${areaImmunityMarkup(area)}</span></td>
      <td>${areaMonsterPoolMarkup(area)}</td>
    </tr>
  `;
}

function wireStaticSearch() {
  const searchInput = document.querySelector("#page-search");
  const cards = Array.from(document.querySelectorAll(".item-card"));
  if (!searchInput || cards.length === 0 || document.querySelector("[data-item-index-url]")) {
    return;
  }

  searchInput.addEventListener("input", () => {
    const query = normalizeText(searchInput.value);
    cards.forEach((card) => {
      card.hidden = Boolean(query) && !normalizeText(card.dataset.search).includes(query);
    });
  });
}

async function wireAreaIndex() {
  const toolbar = document.querySelector("[data-area-index-url]");
  const root = document.querySelector("#area-index-root");
  if (!toolbar || !root) {
    return;
  }

  const response = await fetch(toolbar.dataset.areaIndexUrl);
  const areas = await response.json();
  const searchInput = document.querySelector("#area-search");
  const actSelect = document.querySelector("#area-act-filter");
  const minLevelSelect = document.querySelector("#area-min-level-filter");
  const sortSelect = document.querySelector("#area-sort-filter");
  const topTierCheckbox = document.querySelector("#area-top-tier-filter");
  const avoidCheckboxes = Array.from(document.querySelectorAll("[data-avoid-immunity]"));
  const resultCount = document.querySelector("#area-result-count");

  function sortedAreas(rows) {
    const sortMode = sortSelect ? sortSelect.value : "score";
    const sorters = {
      score: (area) => area.farm_score,
      level: (area) => area.area_level,
      density: (area) => area.monster_density,
      elite: (area) => area.elite_avg,
    };
    const score = sorters[sortMode] || sorters.score;
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
    const topTierOnly = Boolean(topTierCheckbox && topTierCheckbox.checked);
    const avoidImmunities = avoidCheckboxes
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.dataset.avoidImmunity);

    const filtered = areas.filter((area) => {
      const immunities = area.possible_immunities || [];
      const searchOk = !query || normalizeText(area.search_text).includes(query);
      const actOk = act === "all" || area.act === act;
      const levelOk = area.area_level >= minLevel;
      const topTierOk = !topTierOnly || area.can_drop_top_tier;
      const immunityOk = avoidImmunities.every((immunity) => !immunities.includes(immunity));
      return searchOk && actOk && levelOk && topTierOk && immunityOk;
    });

    root.innerHTML = sortedAreas(filtered).map(areaRowMarkup).join("")
      || '<tr><td colspan="9" class="muted">No areas match the current filters.</td></tr>';
    if (resultCount) {
      resultCount.textContent = String(filtered.length);
    }
  }

  [searchInput, actSelect, minLevelSelect, sortSelect, topTierCheckbox, ...avoidCheckboxes]
    .filter(Boolean)
    .forEach((control) => control.addEventListener("input", applyFilters));
  [actSelect, minLevelSelect, sortSelect, topTierCheckbox, ...avoidCheckboxes]
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
  const response = await fetch(toolbar.dataset.itemIndexUrl);
  const items = await response.json();
  const familyLabels = {
    unique: "Unique Items",
    set: "Set Items",
    runeword: "Runewords",
  };

  root.innerHTML = Object.entries(familyLabels)
    .map(([family, label]) => {
      const familyItems = items.filter((item) => item.family === family);
      return `
        <section class="item-family-section" data-section-family="${family}">
          <div class="section-head"><h2>${label}</h2><p>${familyItems.length} generated pages</p></div>
          <div class="card-grid item-grid">
            ${familyItems.map((item) => itemCardMarkup(item, siteRoot)).join("")}
          </div>
        </section>
      `;
    })
    .join("");

  const searchInput = document.querySelector("#page-search");
  const familyButtons = Array.from(document.querySelectorAll("[data-filter-family]"));
  const statusButtons = Array.from(document.querySelectorAll("[data-filter-status]"));
  const groupSelect = document.querySelector("#item-group-filter");
  const typeSelect = document.querySelector("#item-type-filter");
  const cards = Array.from(document.querySelectorAll(".item-card"));
  const familySections = Array.from(document.querySelectorAll("[data-section-family]"));

  let activeFamily = "all";
  let activeStatus = "all";
  let activeGroup = "all";
  let activeType = "all";

  function applyFilters() {
    const query = normalizeText(searchInput ? searchInput.value : "");
    cards.forEach((card) => {
      const family = card.dataset.family || "all";
      const status = card.dataset.status || "unchanged";
      const itemGroup = card.dataset.itemGroup || "";
      const itemType = card.dataset.itemType || "";
      const haystack = normalizeText(card.dataset.search);
      const familyOk = activeFamily === "all" || family === activeFamily;
      const statusOk = activeStatus === "all" || status === activeStatus;
      const groupOk = activeGroup === "all" || normalizeText(itemGroup) === normalizeText(activeGroup);
      const typeOk = activeType === "all" || normalizeText(itemType) === normalizeText(activeType);
      const searchOk = !query || haystack.includes(query);
      card.hidden = !(familyOk && statusOk && groupOk && typeOk && searchOk);
    });

    familySections.forEach((section) => {
      section.hidden = section.querySelectorAll(".item-card:not([hidden])").length === 0;
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
  if (groupSelect) {
    groupSelect.addEventListener("change", () => {
      activeGroup = groupSelect.value || "all";
      if (typeSelect && activeGroup !== "all") {
        const currentType = typeSelect.value;
        const allowed = Array.from(typeSelect.options).some((option) => {
          return option.value === currentType
            && option.parentElement
            && option.parentElement.tagName === "OPTGROUP"
            && option.parentElement.label === activeGroup;
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
      applyFilters();
    });
  }
  familyButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFamily = button.dataset.filterFamily || "all";
      familyButtons.forEach((entry) => entry.classList.toggle("is-active", entry === button));
      applyFilters();
    });
  });
  statusButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeStatus = button.dataset.filterStatus || "all";
      statusButtons.forEach((entry) => entry.classList.toggle("is-active", entry === button));
      applyFilters();
    });
  });
  applyFilters();
}

document.addEventListener("DOMContentLoaded", () => {
  wireStaticSearch();
  wireAreaIndex().catch((error) => {
    const root = document.querySelector("#area-index-root");
    if (root) {
      root.innerHTML = '<tr><td colspan="9" class="muted">Unable to load the area index.</td></tr>';
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
});

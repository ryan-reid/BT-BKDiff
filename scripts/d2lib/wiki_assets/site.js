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
  wireItemIndex().catch((error) => {
    const root = document.querySelector("#item-index-root");
    if (root) {
      root.innerHTML = '<p class="muted">Unable to load the item index.</p>';
    }
    console.error(error);
  });
});

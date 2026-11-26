const main = document.getElementById("app");
const views = [...main.querySelectorAll(".view")];
const navigation = document.querySelectorAll(".mh nav a");
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
const homeTitle = document.title;
let activeView;
let transition;

// The document starts with a single heading outline for readers without JavaScript.
// With navigation enhanced, each displayed view has its own heading outline.
for (const heading of main.querySelectorAll("[data-view-heading]")) {
  const replacement = document.createElement("h" + heading.dataset.viewHeading);
  for (const attribute of heading.attributes) {
    if (attribute.name !== "data-view-heading") {
      replacement.setAttribute(attribute.name, attribute.value);
    }
  }
  replacement.append(...heading.childNodes);
  heading.replaceWith(replacement);
}

function createChapterReader(article) {
  const bar = article.querySelector(".chapter-bar");
  const mobile = bar.querySelector(".chapter-mobile");
  const label = bar.querySelector("[data-chapter-label]");
  const links = [...bar.querySelectorAll("nav a")];
  const chapters = [...article.querySelectorAll(".case-chapter")].map(section => {
    const heading = section.querySelector(".chapter-heading .case-section-title");
    const panel = section.querySelector(".chapter-panel");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "editorial-chapter-button";
    button.setAttribute("aria-controls", panel.id);
    const title = heading.querySelector(".editorial-chapter-title").textContent;
    const number = heading.querySelector(".editorial-chapter-number").lastChild.textContent;
    button.setAttribute("aria-label", "Chapter " + number + " — " + title);
    const description = heading.querySelector(".editorial-chapter-description");
    description.id = heading.id + "-description";
    button.setAttribute("aria-describedby", description.id);
    button.append(...heading.childNodes);
    heading.append(button);
    return {section, heading, panel, button};
  });
  let continuous = false;

  function setOpen(chapter, open) {
    if (!open && !chapter.panel.hidden) {
      for (const video of chapter.panel.querySelectorAll("video")) {
        if (!video.paused) video.pause();
      }
    }
    chapter.panel.hidden = !open;
    chapter.button.setAttribute("aria-expanded", String(open));
  }

  function updateNavigation(chapter) {
    for (const link of links) {
      if (link.hash === "#" + chapter?.heading.id) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
    label.textContent = chapter
      ? " / " + chapter.button.querySelector(".editorial-chapter-title").textContent
      : "";
    mobile.open = false;
  }

  function select(chapter) {
    continuous = false;
    for (const candidate of chapters) setOpen(candidate, candidate === chapter);
    updateNavigation(chapter);
  }

  for (const chapter of chapters) {
    chapter.button.addEventListener("click", () => {
      if (continuous) {
        setOpen(chapter, chapter.panel.hidden);
      } else if (!chapter.panel.hidden) {
        select(null);
        if (location.hash !== "#chapter-overview") history.pushState(null, "", "#chapter-overview");
      } else {
        location.hash = chapter.heading.id;
        return;
      }
      chapter.button.scrollIntoView({block: "start", behavior: "instant"});
    });
  }

  article.querySelector("[data-expand-chapters]").addEventListener("click", () => {
    updateNavigation(null);
    continuous = true;
    for (const chapter of chapters) setOpen(chapter, true);
    label.textContent = " / Continuous";
  });

  article.querySelector("[data-collapse-chapters]").addEventListener("click", () => {
    select(null);
    if (location.hash !== "#chapter-overview") history.pushState(null, "", "#chapter-overview");
  });

  article.addEventListener("click", event => {
    if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest(".chapter-bar a, .chapter-end a");
    if (link?.hash === location.hash) {
      event.preventDefault();
      navigate();
    }
  });

  mobile.addEventListener("keydown", event => {
    if (event.key === "Escape" && mobile.open) {
      mobile.open = false;
      mobile.querySelector("summary").focus();
    }
  });

  for (const campaign of article.querySelectorAll(".campaign-disclosure")) {
    campaign.addEventListener("toggle", () => {
      if (!campaign.open) {
        for (const video of campaign.querySelectorAll("video")) video.pause();
      }
    });
  }

  article.querySelector(".chapter-actions").hidden = false;
  article.classList.add("chapter-reader");
  select(null);
  return {
    reset: () => select(null),
    reveal(anchor) {
      const chapter = chapters.find(candidate => candidate.section.contains(anchor));
      select(chapter);
      article.style.setProperty("--chapter-anchor-offset", bar.offsetHeight + 12 + "px");
      if (anchor === chapter?.heading) return chapter.button;
      return anchor;
    },
  };
}

const chapterReaders = new Map();
for (const view of views) {
  const article = view.querySelector(".cfe:has(.chapter-actions)");
  if (article) chapterReaders.set(view, createChapterReader(article));
}

function openDisclosures(anchor) {
  for (let parent = anchor.parentElement; parent && !parent.classList.contains("view"); parent = parent.parentElement) {
    if (parent.tagName !== "DETAILS") continue;
    const summary = parent.querySelector(":scope > summary");
    if (!summary?.contains(anchor) || anchor.hasAttribute("data-open-disclosure")) parent.open = true;
  }
}

const writing = document.getElementById("writing");
const writingReader = writing ? createWritingReader(writing) : null;

function createWritingReader(view) {
  const gallery = view.querySelector(".writing-gallery");
  const filters = view.querySelector(".writing-filters");
  const status = view.querySelector(".writing-results");
  const entries = [...gallery.querySelectorAll("article[data-writing-group]")];
  const filterButtons = [...filters.querySelectorAll("button")];
  const samples = new Map();
  let current;

  function placePanel() {
    if (!current || view.hidden) return;
    const visible = entries.filter(entry => !entry.hidden);
    const index = visible.indexOf(current.entry);
    const columns = Number(getComputedStyle(gallery).getPropertyValue("--writing-columns"));
    const rowEnd = Math.min(index - index % columns + columns - 1, visible.length - 1);
    const lastEntry = visible[rowEnd];
    if (lastEntry.nextElementSibling !== current.panel) lastEntry.after(current.panel);
  }

  function close({restoreFocus = false, clearHash = false} = {}) {
    if (!current) return;
    const {entry, button, panel} = current;
    current = undefined;
    button.setAttribute("aria-expanded", "false");
    panel.hidden = true;
    if (clearHash && entry.contains(document.getElementById(location.hash.slice(1)))) {
      history.replaceState(null, "", "#writing");
    }
    if (restoreFocus) {
      button.focus({preventScroll: true});
      button.scrollIntoView({block: "nearest", behavior: "instant"});
    }
  }

  function open(sample) {
    if (!sample) return null;
    if (current !== sample) {
      close();
      current = sample;
      sample.button.setAttribute("aria-expanded", "true");
      sample.panel.hidden = false;
    }
    placePanel();
    return sample.heading;
  }

  function filter(group) {
    const accepts = entry => group === "all" || entry.dataset.writingGroup === group;
    if (current && !accepts(current.entry)) close({clearHash: true});
    let count = 0;
    for (const entry of entries) {
      entry.hidden = !accepts(entry);
      if (!entry.hidden) count++;
    }
    for (const button of filterButtons) {
      button.setAttribute("aria-pressed", String(button.dataset.writingFilter === group));
    }
    status.textContent = count === 1 ? "1 writing sample" : count + " writing samples";
    placePanel();
  }

  for (const entry of entries) {
    const disclosure = entry.querySelector(".writing-preview");
    if (!disclosure) continue;
    const title = entry.querySelector(".writing-title").textContent;
    const panel = document.createElement("section");
    panel.className = "writing-panel";
    panel.id = entry.id + "-panel";
    panel.hidden = true;
    const heading = document.createElement("h2");
    heading.id = entry.id + "-expanded";
    heading.tabIndex = -1;
    heading.textContent = title;
    panel.setAttribute("aria-labelledby", heading.id);
    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "writing-control";
    closeButton.textContent = "Close sample";
    closeButton.addEventListener("click", () => close({restoreFocus: true, clearHash: true}));
    const header = document.createElement("header");
    header.append(heading, closeButton);
    const detail = disclosure.querySelector(".writing-detail");
    const returnButton = closeButton.cloneNode();
    returnButton.textContent = "Return to writing gallery";
    returnButton.classList.add("writing-return");
    returnButton.addEventListener("click", () => close({restoreFocus: true, clearHash: true}));
    panel.append(header, detail, returnButton);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "writing-control";
    button.textContent = "Explore the sample";
    button.setAttribute("aria-label", disclosure.querySelector("summary").getAttribute("aria-label"));
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", panel.id);
    button.addEventListener("click", () => {
      if (current?.entry === entry) close({restoreFocus: true, clearHash: true});
      else if (location.hash === "#" + entry.id) navigate();
      else location.hash = entry.id;
    });
    disclosure.replaceWith(button);
    // Keep every aria-controls target in the document, even before it is opened.
    gallery.append(panel);
    samples.set(entry, {entry, button, panel, heading});
  }

  for (const button of filterButtons) {
    button.addEventListener("click", () => filter(button.dataset.writingFilter));
  }
  filters.hidden = false;
  filter("all");
  new ResizeObserver(placePanel).observe(gallery);

  return {
    reveal(anchor) {
      const entry = anchor?.closest("article[data-writing-group]");
      if (entry?.hidden) filter("all");
      if (entry) return open(samples.get(entry)) || anchor;
      if (!anchor || anchor === view) close();
      return anchor;
    }
  };
}

function showView(view, anchor, focusHeading) {
  if (activeView !== view) {
    chapterReaders.get(activeView)?.reset();
    const hero = view.querySelector("[data-view-hero]");
    if (hero) hero.loading = "eager";
    for (const candidate of views) {
      const visible = candidate === view;
      candidate.hidden = !visible;
      candidate.classList.toggle("is-active", visible);
    }
    activeView = view;
    document.title = view.id === "home"
      ? homeTitle
      : view.dataset.pageTitle + " | Mollie Sambrook · The Art of Being Noticed";
    const current = view.dataset.section || view.id;
    for (const link of navigation) {
      if (link.hash === "#" + current) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    }
  }
  const reader = chapterReaders.get(view);
  const destination = reader ? reader.reveal(anchor)
    : view === writing && writingReader ? writingReader.reveal(anchor) : anchor;
  if (destination && destination !== view) {
    openDisclosures(destination);
    if (reader && destination.tabIndex < 0 && !destination.hasAttribute("tabindex")) destination.tabIndex = -1;
    destination.focus({preventScroll: true});
    if (reader || view === writing) destination.scrollIntoView({block: "start", behavior: "instant"});
    else destination.scrollIntoView();
  } else if (focusHeading || reader) {
    if (focusHeading) view.querySelector(".view-title").focus({preventScroll: true});
    window.scrollTo({top: 0, behavior: "instant"});
  }
}

function navigate(initial = false) {
  const anchor = document.getElementById(location.hash.slice(1));
  if (anchor === main && activeView) return; // Native skip link.
  const view = anchor?.closest(".view") || views[0];
  const forward = anchor?.dataset.forward || view.dataset.forward;
  if (forward) {
    location.replace(forward);
    return;
  }
  const nestedAnchor = anchor && view.contains(anchor) ? anchor : null;
  const update = () => showView(view, nestedAnchor, !initial);
  transition?.skipTransition();
  if (!initial && activeView !== view && document.startViewTransition && !reducedMotion.matches) {
    const request = document.startViewTransition(() => {
      // A second route can supersede the first before its update callback runs.
      if (transition === request) update();
    });
    transition = request;
    // A browser may skip an animation while still applying its DOM update.
    void request.ready.catch(() => {});
  } else {
    transition = undefined;
    update();
  }
}

for (const image of main.querySelectorAll("img")) {
  const markUnavailable = () => image.classList.add("image-unavailable");
  image.addEventListener("error", markUnavailable);
  if (image.complete && !image.naturalWidth) markUnavailable();
}

window.addEventListener("hashchange", () => navigate());
navigate(true);

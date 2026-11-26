for (const calendar of document.querySelectorAll(".cs-calendar")) {
  const controls = calendar.querySelector(".kw-controls");
  const channel = controls.querySelector('[name="channel"]');
  const pillar = controls.querySelector('[name="pillar"]');
  const status = calendar.querySelector(".cs-calendar-status");
  const panel = calendar.querySelector(".cs-day-panel");
  const panelTitle = panel.querySelector(".cs-day-title");
  const agenda = panel.querySelector(".cs-agenda");
  let selection;
  const weeks = [...calendar.querySelectorAll(".cs-week")].map(week => {
    const grid = document.createElement("div");
    grid.className = "cs-date-grid";
    const days = [...week.querySelectorAll("details")].map(day => {
      const time = day.querySelector("time");
      const items = [...day.querySelectorAll("[data-channel]")];
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = time.dateTime.slice(-2).replace(/^0/, "");
      const production = items.every(item => item.dataset.channel === "Internal");
      button.setAttribute("aria-label", time.textContent + (production ? ", production and review" : ""));
      button.classList.toggle("is-production", production);
      button.addEventListener("click", () => {
        selection = day;
        filter();
      });
      grid.append(button);
      day.hidden = true;
      return {day, time, button, items};
    });
    week.append(grid);
    return {week, days};
  });

  function filter() {
    const visibleDays = [];
    let total = 0;
    for (const {week, days} of weeks) {
      for (const entry of days) {
        entry.matches = entry.items.filter(item => (!channel.value || item.dataset.channel === channel.value)
          && (!pillar.value || item.dataset.pillar === pillar.value));
        entry.button.disabled = !entry.matches.length;
        if (entry.matches.length) visibleDays.push(entry);
        total += entry.matches.length;
      }
      week.hidden = days.every(entry => entry.button.disabled);
    }
    const active = visibleDays.find(entry => entry.day === selection) || visibleDays[0];
    selection = active?.day;
    for (const {days} of weeks) {
      for (const {day, button} of days) button.setAttribute("aria-pressed", String(day === selection));
    }
    if (active) {
      panelTitle.replaceChildren(active.time.cloneNode(true));
      agenda.replaceChildren(...active.matches.map(item => item.cloneNode(true)));
    } else {
      panelTitle.textContent = "";
      agenda.replaceChildren();
    }
    panel.hidden = !active;
    status.textContent = total
      ? `${total} ${total === 1 ? "activity" : "activities"} across ${visibleDays.length} ${visibleDays.length === 1 ? "date" : "dates"}.`
      : "No activities match these filters.";
  }

  controls.addEventListener("change", filter);
  controls.hidden = false;
  status.hidden = false;
  filter();
}

for (const pillars of document.querySelectorAll(".cs-pillars")) {
  const chart = pillars.querySelector(".cs-donut");
  const centre = chart.querySelector("strong");
  const panel = pillars.querySelector(".cs-pillar-selection");
  const segments = [...chart.querySelectorAll("[data-pillar-index]")];
  const disclosures = [...pillars.querySelectorAll('details[name="cs-pillars"]')];

  function select(index) {
    const disclosure = disclosures[index];
    const summary = disclosure.querySelector("summary");
    centre.textContent = summary.querySelector(".cs-score").textContent;
    for (const [i, segment] of segments.entries()) segment.classList.toggle("is-selected", i === index);
    const heading = document.createElement("strong");
    heading.textContent = summary.firstChild.textContent.trim();
    panel.replaceChildren(heading, disclosure.querySelector("dl").cloneNode(true));
  }

  for (const [index, disclosure] of disclosures.entries()) {
    disclosure.querySelector("summary").addEventListener("click", event => {
      event.preventDefault();
      disclosure.open = true;
      select(index);
    });
    disclosure.addEventListener("toggle", () => {
      if (disclosure.open) select(index);
    });
    segments[index].addEventListener("click", () => {
      disclosure.open = true;
      select(index);
    });
  }
  select(Math.max(0, disclosures.findIndex(item => item.open)));
  pillars.classList.add("is-enhanced");
  chart.hidden = false;
  panel.hidden = false;
}

for (const bar of document.querySelectorAll(".chapter-bar")) {
  const mobile = bar.querySelector(".chapter-mobile");
  const label = bar.querySelector("[data-chapter-label]");
  const links = [...bar.querySelectorAll("nav a")];
  const chapters = links.slice(0, links.length / 2).map(link => ({
    link,
    section: document.getElementById(link.hash.slice(1)).closest(".case-chapter"),
  }));
  let frame;

  function highlightChapter() {
    frame = undefined;
    const limit = Math.max(144, bar.getBoundingClientRect().bottom + 28);
    let current;
    if (bar.getClientRects().length) {
      for (const chapter of chapters) {
        const bounds = chapter.section.getBoundingClientRect();
        if (bounds.top <= limit && bounds.bottom > 0) current = chapter.link;
      }
    }
    for (const link of links) {
      if (current && link.hash === current.hash) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
    label.textContent = current ? " / " + current.lastChild.textContent.trim() : "";
  }

  function schedule() {
    if (frame === undefined) frame = requestAnimationFrame(highlightChapter);
  }

  for (const link of bar.querySelectorAll("a")) link.addEventListener("click", () => { mobile.open = false; });
  mobile.addEventListener("keydown", event => {
    if (event.key === "Escape" && mobile.open) {
      mobile.open = false;
      mobile.querySelector("summary").focus();
    }
  });
  window.addEventListener("scroll", schedule, {passive: true});
  window.addEventListener("resize", schedule);
  window.addEventListener("hashchange", schedule);
  schedule();
}

for (const experience of document.querySelectorAll(".persona-experience")) {
  const tablist = experience.querySelector(".persona-tabs");
  const profiles = experience.querySelector(".persona-profiles");
  const entries = [...profiles.querySelectorAll("details")].map(disclosure => {
    const panel = disclosure.querySelector(".persona-profile");
    const button = document.createElement("button");
    button.type = "button";
    button.id = panel.id + "-tab";
    button.textContent = disclosure.querySelector("summary").textContent;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", panel.id);
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("aria-labelledby", button.id);
    disclosure.replaceWith(panel);
    tablist.append(button);
    return {button, panel};
  });

  function activate(index, focus = false) {
    for (const [i, {button, panel}] of entries.entries()) {
      const active = i === index;
      button.tabIndex = active ? 0 : -1;
      button.setAttribute("aria-selected", String(active));
      panel.toggleAttribute("inert", !active);
      panel.setAttribute("aria-hidden", String(!active));
      panel.tabIndex = active ? 0 : -1;
    }
    if (focus) entries[index].button.focus();
  }

  for (const [index, {button}] of entries.entries()) {
    button.addEventListener("click", () => activate(index));
    button.addEventListener("keydown", event => {
      const last = entries.length - 1;
      const targets = {
        ArrowRight: (index + 1) % entries.length,
        ArrowLeft: (index + last) % entries.length,
        Home: 0,
        End: last,
      };
      if (!(event.key in targets)) return;
      event.preventDefault();
      activate(targets[event.key], true);
    });
  }
  activate(0);
  experience.classList.add("is-enhanced");
  tablist.hidden = false;
}

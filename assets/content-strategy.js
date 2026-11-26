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
  const bar = pillars.querySelector(".cs-mix");
  const disclosures = [...pillars.querySelectorAll('details[name="cs-pillars"]')];
  [...bar.children].forEach((segment, index) => {
    const disclosure = disclosures[index];
    const button = document.createElement("button");
    button.type = "button";
    button.style.cssText = segment.style.cssText;
    button.setAttribute("aria-label", disclosure.querySelector("summary").textContent.trim());
    const updatePressed = () => button.setAttribute("aria-pressed", String(disclosure.open));
    button.addEventListener("click", () => {
      disclosure.open = !disclosure.open;
      updatePressed();
    });
    disclosure.addEventListener("toggle", updatePressed);
    updatePressed();
    segment.replaceWith(button);
  });
  bar.removeAttribute("aria-hidden");
  bar.setAttribute("role", "group");
  bar.setAttribute("aria-label", "Proposed content mix");
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

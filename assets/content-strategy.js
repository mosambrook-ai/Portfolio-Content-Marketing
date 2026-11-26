// Static disclosures remain usable without JavaScript. Only filtering is enhanced.
for (const calendar of document.querySelectorAll(".cs-calendar")) {
  const controls = calendar.querySelector(".kw-controls");
  const channel = controls.querySelector('[name="channel"]');
  const pillar = controls.querySelector('[name="pillar"]');
  const status = calendar.querySelector(".cs-calendar-status");
  const weeks = [...calendar.querySelectorAll(".cs-week")].map(week => ({
    week,
    days: [...week.querySelectorAll("details")].map(day => ({
      day,
      items: [...day.querySelectorAll("[data-channel]")],
    })),
  }));

  function filter() {
    let matches = 0;
    for (const {week, days} of weeks) {
      for (const {day, items} of days) {
        for (const item of items) {
          item.hidden = Boolean((channel.value && item.dataset.channel !== channel.value)
            || (pillar.value && item.dataset.pillar !== pillar.value));
          if (!item.hidden) matches++;
        }
        day.hidden = items.every(item => item.hidden);
      }
      week.hidden = days.every(({day}) => day.hidden);
    }
    status.textContent = matches
      ? `${matches} ${matches === 1 ? "activity" : "activities"} in the editorial plan.`
      : "No activities match these filters.";
  }

  controls.addEventListener("change", filter);
  controls.hidden = false;
  status.hidden = false;
  filter();
}

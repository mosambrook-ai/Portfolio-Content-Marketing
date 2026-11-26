// The research is already readable in HTML before these controls are enabled.
for (const explorer of document.querySelectorAll(".kw-explorer")) {
  const controls = explorer.querySelector(".kw-controls");
  const full = explorer.querySelector(".kw-full");
  const count = explorer.querySelector(".kw-count");
  const featured = explorer.querySelector(".kw-featured");
  const lists = [...explorer.querySelectorAll(".kw-bars")].map(list => ({
    list,
    items: [...list.children],
  }));
  const maxVolume = Math.max(...lists[1].items.map(item => Number(item.dataset.volume)));
  const picker = name => controls.querySelector(`[name="${name}"]`);

  function update() {
    const cluster = picker("cluster").value;
    const intent = picker("intent").value;
    const metric = picker("metric").value;
    const order = picker("sort").value;
    const activeList = full.open ? lists[1] : lists[0];
    let visible = 0;
    featured.hidden = full.open;
    for (const {list, items} of lists) {
      const ordered = order === "featured" ? items : [...items].sort((a, b) => {
        const first = a.dataset[order];
        const second = b.dataset[order];
        if (!first || !second) return Number(Boolean(second)) - Number(Boolean(first));
        return order === "volume" ? Number(second) - Number(first) : Number(first) - Number(second);
      });
      const currentlyOrdered = [...list.children];
      if (ordered.some((item, index) => item !== currentlyOrdered[index])) list.append(...ordered);
      for (const item of ordered) {
        const matchesIntent = intent === "unknown" ? !item.dataset.intent : item.dataset.intent.split("/").includes(intent);
        item.hidden = Boolean((cluster && item.dataset.cluster !== cluster) || (intent && !matchesIntent));
        if (list === activeList.list && !item.hidden) visible++;
        const raw = item.dataset[metric];
        const value = item.querySelector(".kw-value");
        const fill = item.querySelector(".kw-track span");
        const percentage = metric === "volume" ? 100 * Number(raw) / maxVolume : 100 * Number(raw);
        value.textContent = raw === "" ? "Unavailable"
          : metric === "volume" ? `${Number(raw).toLocaleString("en-GB")} UK/mo`
            : `${Math.round(percentage)}% KD`;
        fill.style.setProperty("--bar", `${raw === "" ? 0 : percentage}%`);
      }
    }
    const scope = full.open ? "full research" : "featured selection";
    count.textContent = visible ? `${visible} ${visible === 1 ? "keyword" : "keywords"} in the ${scope}.`
      : `No matches in the ${scope}.`;
  }

  controls.addEventListener("change", event => {
    if (["cluster", "intent"].includes(event.target.name) && event.target.value) full.open = true;
    update();
  });
  full.addEventListener("toggle", update);
  controls.hidden = false;
  count.hidden = false;
  update();
}

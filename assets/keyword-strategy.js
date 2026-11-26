// Static scores and the featured chart remain readable without JavaScript.
for (const explorer of document.querySelectorAll(".kw-explorer")) {
  const controls = explorer.querySelector(".kw-controls");
  const count = explorer.querySelector(".kw-count");
  const list = explorer.querySelector(".kw-bars");
  const items = [...list.children];
  const maxVolume = Math.max(...items.map(item => Number(item.dataset.volume)));
  const picker = name => controls.querySelector(`[name="${name}"]`);

  function update() {
    const cluster = picker("cluster").value;
    const intent = picker("intent").value;
    const metric = picker("metric").value;
    const order = picker("sort").value;
    let visible = 0;
    const ordered = order === "featured" ? items : [...items].sort((a, b) => {
      const first = a.dataset[order];
      const second = b.dataset[order];
      if (!first || !second) return Number(Boolean(second)) - Number(Boolean(first));
      return order === "volume" ? Number(second) - Number(first) : Number(first) - Number(second);
    });
    const current = [...list.children];
    if (ordered.some((item, index) => item !== current[index])) list.append(...ordered);
    for (const item of items) {
      const matchesIntent = intent === "unknown" ? !item.dataset.intent : item.dataset.intent.split("/").includes(intent);
      item.hidden = Boolean((cluster && item.dataset.cluster !== cluster) || (intent && !matchesIntent));
      if (!item.hidden) visible++;
      const raw = item.dataset[metric];
      const percentage = metric === "volume" ? 100 * Number(raw) / maxVolume : 100 * Number(raw);
      item.querySelector(".kw-value").textContent = raw === "" ? "Unavailable"
        : metric === "volume" ? `${Number(raw).toLocaleString("en-GB")} UK/mo`
          : `${Math.round(percentage)}% KD`;
      item.querySelector(".kw-track span").style.setProperty("--bar", `${raw === "" ? 0 : percentage}%`);
    }
    count.textContent = visible ? `${visible} ${visible === 1 ? "keyword" : "keywords"} in the full research.`
      : "No keywords match these filters.";
  }

  controls.addEventListener("change", update);
  controls.hidden = false;
  count.hidden = false;
  update();
}

for (const chart of document.querySelectorAll(".kw-scatter")) {
  const controls = chart.querySelector(".kw-controls");
  const picker = chart.querySelector(".kw-picker");
  const selection = picker.querySelector("select");
  const plot = chart.querySelector("svg");
  const points = [...plot.querySelectorAll("circle")];
  const detail = chart.querySelector(".kw-point-info");
  const control = name => controls.querySelector(`[name="${name}"]`).value;

  function showSelection() {
    const chosen = points.find(point => isVisible(point) && point.dataset.term === selection.value);
    for (const point of points) {
      point.classList.toggle("is-selected", point === chosen);
      point.setAttribute("r", point === chosen ? "7" : "5");
    }
    if (!chosen) {
      detail.textContent = "No plottable keywords match this selection.";
      return;
    }
    const {term, volume, kd, intent, page} = chosen.dataset;
    const title = document.createElement("strong");
    title.textContent = term;
    const summary = document.createElement("p");
    summary.append(`${volume} UK searches/month · ${kd} KD · ${intent}`, document.createElement("br"), page);
    detail.replaceChildren(title, summary);
  }

  function update() {
    const linear = control("scale") === "linear";
    const cluster = control("chart-cluster");
    const featured = control("scope") === "featured";
    const previous = selection.value;
    const options = [];
    plot.querySelector(".kw-log-axis").toggleAttribute("hidden", linear);
    plot.querySelector(".kw-linear-axis").toggleAttribute("hidden", !linear);
    for (const point of points) {
      const y = linear ? point.dataset.linearY : point.dataset.logY;
      const visible = Boolean(y && (!cluster || point.dataset.cluster === cluster)
        && (!featured || point.dataset.featured === "true"));
      point.toggleAttribute("hidden", !visible);
      if (visible) {
        point.setAttribute("cy", y);
        options.push(new Option(point.dataset.term, point.dataset.term));
      }
    }
    selection.replaceChildren(...options);
    if (options.some(option => option.value === previous)) selection.value = previous;
    selection.disabled = options.length === 0;
    showSelection();
  }

  // SVG elements use the hidden attribute via CSS rather than HTMLElement.hidden.
  function isVisible(point) {
    return !point.hasAttribute("hidden");
  }

  plot.addEventListener("click", event => {
    if (!points.includes(event.target) || !isVisible(event.target)) return;
    selection.value = event.target.dataset.term;
    showSelection();
  });
  selection.addEventListener("change", showSelection);
  controls.addEventListener("change", update);
  controls.hidden = false;
  picker.hidden = false;
  update();
}

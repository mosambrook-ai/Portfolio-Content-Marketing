// The native disclosures and timestamp links remain usable without this enhancement.
for (const feature of document.querySelectorAll(".anatomy-feature")) {
  const sequence = feature.querySelector(".anatomy-sequence");
  const panel = sequence.querySelector(".anatomy-selection");
  const video = feature.querySelector(".anatomy-film video");
  const scenes = [...sequence.querySelectorAll(".anatomy-scene details")].map(disclosure => {
    const summary = disclosure.querySelector("summary");
    const detail = disclosure.querySelector(".anatomy-scene-detail");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "anatomy-scene-button";
    button.setAttribute("aria-label", summary.getAttribute("aria-label"));
    button.setAttribute("aria-controls", panel.id);
    button.append(...summary.childNodes);
    disclosure.replaceWith(button);
    return {button, detail};
  });

  function selectScene(current) {
    for (const {button} of scenes) button.setAttribute("aria-pressed", String(button === current.button));
    panel.replaceChildren(current.detail);
  }

  let targetTime;
  function seek() {
    if (targetTime === undefined) return;
    video.currentTime = targetTime;
    targetTime = undefined;
  }
  video.addEventListener("loadedmetadata", seek);
  panel.addEventListener("click", event => {
    const link = event.target.closest("[data-anatomy-seek]");
    if (!link || event.button || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (video.error) return;
    event.preventDefault();
    // Seeking keeps a paused film paused. Loading starts only after a deliberate request.
    const alreadyWaiting = targetTime !== undefined;
    targetTime = Number(link.dataset.anatomySeek);
    if (video.readyState > 0) seek();
    else if (!alreadyWaiting) video.load();
    video.focus({preventScroll: true});
    video.scrollIntoView({block: "nearest"});
  });

  for (const scene of scenes) scene.button.addEventListener("click", () => selectScene(scene));
  if (scenes.length) {
    selectScene(scenes[0]);
    panel.hidden = false;
    sequence.classList.add("is-enhanced");
  }
}

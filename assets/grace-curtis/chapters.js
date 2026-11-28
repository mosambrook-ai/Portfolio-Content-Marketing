function revealChapter() {
  const anchor = document.getElementById(location.hash.slice(1));
  if (!anchor) return;
  for (let parent = anchor; parent; parent = parent.parentElement) {
    if (parent.tagName === "DETAILS") parent.open = true;
  }
  const destination = anchor.matches("details") ? anchor.querySelector("summary") : anchor;
  if (!destination.matches("summary")) destination.tabIndex = -1;
  destination.focus({preventScroll:true});
  destination.scrollIntoView({block:"start"});
}
window.addEventListener("hashchange", revealChapter);
if (location.hash) revealChapter();

for (const feature of document.querySelectorAll('.grace-strategy [data-switcher]')) {
  const group = feature.querySelector('.choices');
  const controls = Array.from(group.querySelectorAll('button[aria-controls]'));
  const panels = controls.map(control => document.getElementById(control.getAttribute('aria-controls')));
  const isTablist = group.classList.contains('persona-choices');

  if (isTablist) {
    group.setAttribute('role', 'tablist');
    controls.forEach((control, index) => {
      control.setAttribute('role', 'tab');
      panels[index].setAttribute('role', 'tabpanel');
      panels[index].setAttribute('aria-labelledby', control.id);
      panels[index].tabIndex = 0;
    });
    group.addEventListener('keydown', event => {
      const index = controls.indexOf(event.target);
      if (index < 0) return;
      const destinations = {
        ArrowLeft: (index - 1 + controls.length) % controls.length,
        ArrowRight: (index + 1) % controls.length,
        Home: 0,
        End: controls.length - 1,
      };
      if (!Object.hasOwn(destinations, event.key)) return;
      event.preventDefault();
      const next = destinations[event.key];
      select(next);
      controls[next].focus();
    });
  }

  function select(selected) {
    controls.forEach((control, index) => {
      const active = index === selected;
      control.setAttribute(isTablist ? 'aria-selected' : 'aria-pressed', String(active));
      if (isTablist) control.tabIndex = active ? 0 : -1;
      panels[index].hidden = !active;
    });
  }

  controls.forEach((control, index) => {
    control.addEventListener('click', () => select(index));
  });
  select(0);
  feature.classList.add('is-interactive');
}

document.querySelector('a[href="#mind-map-evidence"]')?.addEventListener('click', () => {
  document.getElementById('development-evidence').open = true;
});

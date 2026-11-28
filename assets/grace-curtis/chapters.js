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

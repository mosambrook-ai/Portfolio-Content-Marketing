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

function showView(view, anchor, focusHeading) {
  if (activeView !== view) {
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
  if (anchor && anchor !== view) {
    anchor.focus({preventScroll: true});
    anchor.scrollIntoView();
  } else if (focusHeading) {
    view.querySelector(".view-title").focus({preventScroll: true});
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

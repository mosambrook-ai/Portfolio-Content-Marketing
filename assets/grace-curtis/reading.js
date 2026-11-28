const choices = document.querySelector(".moods");
const output = document.querySelector(".recommendation");
const books = [...document.querySelectorAll(".book")];
if (choices && output) {
  choices.hidden = false;
  choices.addEventListener("click", event => {
    const button = event.target.closest("button[data-book]");
    if (!button) return;
    const book = books.find(item => item.id === button.dataset.book);
    for (const choice of choices.querySelectorAll("button")) {
      choice.setAttribute("aria-pressed", String(choice === button));
    }
    for (const item of books) item.toggleAttribute("data-selected", item === book);
    const link = document.createElement("a");
    link.href = "#" + book.id;
    link.textContent = book.querySelector("h3").textContent;
    output.replaceChildren("Start with ", link, ". " + book.dataset.reason);
    output.hidden = false;
  });
}

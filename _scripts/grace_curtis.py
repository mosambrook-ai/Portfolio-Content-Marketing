"""Generate two static, noindex preview pages from the private project source."""
import json
from html import escape

author = "https://www.hachette.co.uk/contributor/grace-curtis/"
interview = "https://hodderscape.co.uk/blogs/exclusive-author-content/grace-curtis-on-writing-characters-and-creating-different-worlds"
journalism = "https://www.eurogamer.net/someone-should-make-a-game-about-blackwater-dam"
imprint = "https://hodderscape.co.uk/collections/author-grace-curtis"


def page(title, desc, prefix, nav, content, script, metadata):
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{metadata}<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:type" content="website"><meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}"><meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{prefix}project.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&amp;family=Fraunces:ital,wght@0,500;1,500&amp;display=swap">
<script defer src="{prefix}{script}"></script></head>
<body><a class="skip" href="#main">Skip to content</a><div class="shell">
<nav aria-label="Main">{nav}</nav><main id="main" tabindex="-1">{content}</main>
<footer class="site-footer"><span class="meta">Independent portfolio concept by Mollie Sambrook</span><a href="#main">Back to top ↑</a></footer>
</div></body></html>
"""


def hero(label, title, content, prefix=""):
    return f"""<header class="masthead"><div><p class="kicker">{label}</p>
<h1>{title}</h1>{content}</div><img class="masthead-image" src="{prefix}moorland.webp" width="1536" height="1024" fetchpriority="high" decoding="async" alt="A stone wall crossing moorland at dusk beneath a blue and amber sky"></header>"""


def book_article(book, prefix):
    title = escape(book["title"])
    cover = book["cover"]
    return (f'<article class="book" id="{book["id"]}" data-reason="{escape(book["reason"])}">'
            f'<img class="book-cover" src="{prefix}covers/{book["id"]}.webp" width="{cover["width"]}" height="{cover["height"]}" loading="lazy" decoding="async" alt="UK hardback cover of {title} by Grace Curtis">'
            f'<div><p class="kicker">{escape(book["genre"])}</p><h3>{title}</h3>'
            f'<p class="meta">UK hardback · Published {book["date"]}</p>'
            f'<p><strong>{escape(book["hook"])}</strong></p><p>{escape(book["copy"])}</p>'
            f'<p class="meta">{escape(book["themes"])}</p>'
            f'<a href="{book["url"]}">Explore {title} at Hachette UK</a></div></article>')


def chapter(number, slug, title, content):
    return (f'<details class="chapter" id="{slug}" name="project-chapters">'
            f'<summary><span class="chapter-number">{number:02d}</span><span class="chapter-title">{title}</span></summary>'
            f'<div class="chapter-panel">{content}</div></details>')


def source(title, url, claims):
    return f'<li><a href="{url}">{title}</a> · 26 November 2026 · {claims}</li>'


def render_grace_curtis(root, route, site):
    books = json.loads((root / "_data/grace-curtis-books.json").read_text(encoding="utf-8"))
    case_assets = "../../assets/grace-curtis/"
    profile_assets = "../" + case_assets
    choices = "".join(f'<button type="button" data-book="{b["id"]}" aria-pressed="false">{escape(b["mood"])}</button>' for b in books)
    profile = hero("Independent author discovery concept", "Grace Curtis",
                   '<p class="lead">Worlds worth getting lost in.</p>'
                   '<p>Grace Curtis is a science fiction and fantasy writer from Newcastle upon Tyne. Her novels move from a climate-ravaged Earth to a hotel travelling between worlds and into landscapes marked by ruined civilisations. She has written about video games and enjoys hiking and climbing.</p>'
                   '<p><a class="action" href="#reading-guide">Find your first Grace Curtis book</a></p>', profile_assets)
    profile += f"""
    <section class="editorial" id="reading-guide"><h2>Where should I start?</h2>
    <p>Choose the kind of reading experience you’re after, or browse all four books.</p>
    <div class="moods" role="group" aria-label="Choose a reading mood" hidden>{choices}</div>
    <p class="recommendation" role="status" aria-live="polite" hidden></p>
    <div class="books">{''.join(book_article(book, profile_assets) for book in books)}</div></section>
    <section class="editorial" id="beyond"><h2>The worlds beyond the page.</h2>
    <p>In a Hodderscape Q&amp;A, Curtis describes how imagining people encountering the remains of Roman Britain helped shape <cite>Idolfire</cite>. She also recalls pitching its journey as a shift from the exploratory feel of <cite>Breath of the Wild</cite> towards the atmosphere of <cite>Dark Souls</cite>. That account offers a way into her approach to invented places.</p>
    <p>Her games writing offers another point of entry. A Eurogamer piece about Blackwater Dam considers a real landscape as the setting for a game.</p>
    <ul><li><a href="{interview}">Read the Hodderscape Q&amp;A</a></li>
    <li><a href="{journalism}">Read the Blackwater Dam piece at Eurogamer</a></li>
    <li><a href="{author}">Grace Curtis at Hachette UK</a></li><li><a href="{imprint}">Browse her books at Hodderscape</a></li></ul>
    </section>"""
    profile_html = page(
        "Grace Curtis | Sci-Fi and Fantasy Author Profile · Independent Concept",
        "Explore Grace Curtis’s science fiction and fantasy novels and choose a first book with this independent mood-based reading guide.",
        profile_assets, '<a href="../">Project case study</a><a href="#reading-guide">Reading guide</a>', profile, "reading.js",
        '<meta name="robots" content="noindex,follow">')

    sources = [
        source("Grace Curtis · Hachette UK contributor profile", author, "Newcastle upon Tyne and four-novel bibliography."),
        source("Hodderscape · Grace Curtis Q&A", interview, "Hiking and climbing, gaming journalism bio, and Curtis’s account of post-Roman Britain, Breath of the Wild and Dark Souls as Idolfire influences."),
        source("Hodderscape · Grace Curtis", imprint, "UK imprint’s author collection."),
        *(source(f'{b["title"]} · Hachette UK', b["url"], f'UK hardback on-sale date ({b["date"]}), genre and synopsis.') for b in books),
        source("Eurogamer · Someone should make a game about: Blackwater Dam", journalism, "Original games feature and Grace Curtis byline."),
    ]


    def strategy_feature(name):
        fragment = root / "_content/cases/grace-curtis" / f"{name}.html"
        return fragment.read_text(encoding="utf-8").replace("{{CASE_ASSETS}}", case_assets)

    mind_map = strategy_feature("mind-map")
    readers = strategy_feature("personas")
    direction = strategy_feature("design")
    evidence = strategy_feature("evidence")

    previews = ""
    desktop = root / "assets/grace-curtis/profile-desktop.jpg"
    mobile = root / "assets/grace-curtis/profile-mobile.jpg"
    if desktop.is_file() and mobile.is_file():
        previews = (f'<div class="preview-pair"><figure><a href="{case_assets}profile-desktop.jpg">'
                    f'<img src="{case_assets}profile-desktop.jpg" width="1440" height="1000" loading="lazy" alt="Desktop author introduction with editorial typography and a moorland scene"></a>'
                    f'<figcaption>Desktop prototype</figcaption></figure><figure><a href="{case_assets}profile-mobile.jpg">'
                    f'<img src="{case_assets}profile-mobile.jpg" width="390" height="844" loading="lazy" alt="Mobile reading guide and its recommendation controls"></a>'
                    '<figcaption>Mobile prototype</figcaption></figure></div>')
    slides = [
        ("Which Grace Curtis book should you read first?", "Choose by the kind of world you want to spend time in.", ""),
        *((b["title"], b["hook"],
           f'<img src="{case_assets}covers/{b["id"]}.webp" width="{b["cover"]["width"]}" height="{b["cover"]["height"]}" loading="lazy" alt="UK hardback cover of {escape(b["title"])}">')
          for b in books),
        ("Find your first book.", "Explore all four reading routes in the author profile.", ""),
    ]
    storyboard = "".join(
        f'<article class="slide"><p class="kicker">Slide {i:02d} / 06</p><h3>{escape(title)}</h3><p>{escape(copy)}</p>{art}</article>'
        for i, (title, copy, art) in enumerate(slides, 1)
    )
    metadata = (f'<link rel="canonical" href="{site}{route}">'
                f'<meta property="og:url" content="{site}{route}">'
                f'<meta property="og:image" content="{site}assets/grace-curtis/moorland.webp">')
    case = hero("Project 02 / Author marketing / Independent concept", "Worlds worth getting lost in.",
                '<p class="lead">An author discovery experience for Grace Curtis.</p>'
                '<p>An independent concept by Mollie Sambrook. An unofficial reader discovery prototype.</p>'
                '<a class="action" href="profile/">Open the reader-facing preview</a>', case_assets)
    case += '<section class="editorial" id="chapters"><h2>Case study</h2>'
    case += chapter(1, "finding-the-story", "Finding the story", f"""
    <p>Grace Curtis writes across overlapping speculative genres. A reader may be drawn to her work before knowing whether to begin with a western, a cosy mystery, a pilgrimage or an archaeological fantasy.</p>
    <p><strong>Objective</strong> · Help new readers choose a first book and reach its UK publisher page with confidence.</p>
    <p><strong>Audience</strong> · New and genre-adjacent readers encountering Curtis through bookselling, editorial or social discovery.</p>
    <p><strong>Role and scope</strong> · Independent research, positioning, copy, creative direction and a static web prototype. The profile and reading guide are built for review. Interviews, audience validation, analytics and campaign distribution are planned.</p>{mind_map}""")
    case += chapter(2, "understanding-the-author", "Understanding the author", f"""
    <h3>Intimate stories in expansive worlds.</h3>
    <p>My proposed positioning connects speculative places with human relationships. The books offer different kinds of travel and discovery, with romance, found family or memory giving readers a reason to care about where the journey leads.</p>
    <ul><li><strong>Literary identity and genre</strong> · The publisher describes Curtis as a writer from Newcastle upon Tyne. Her work spans queer science fiction and sapphic fantasy.</li>
    <li><strong>Influences</strong> · Curtis connects Idolfire with post-Roman Britain and open-world games in her publisher Q&amp;A.</li>
    <li><strong>Recurring themes</strong> · A preliminary editorial reading identifies exploration, relationships and the histories places carry.</li>
    <li><strong>Journalism and interests</strong> · Games writing, hiking and climbing provide subjects for further editorial exploration.</li>
    <li><strong>Tone</strong> · The proposed editorial voice is observant, warm and specific, with room for mystery.</li></ul>
    <details id="research-sources"><summary>Research source register</summary><ul class="sources">{''.join(sources)}</ul></details>""")
    case += chapter(3, "finding-the-readers", "Finding the readers", f"""
    {readers}
    <details id="search-intent"><summary>Preliminary search intent framework</summary>
    <ul><li><strong>Author discovery</strong> · Grace Curtis, Grace Curtis books, Grace Curtis author. Lead to the profile and bibliography.</li>
    <li><strong>Title-led</strong> · Frontier, Floating Hotel, Idolfire and Heaven’s Graveyard, qualified with the author’s name where needed. Lead to title sections and verified publisher links.</li>
    <li><strong>Choice-led</strong> · Which Grace Curtis book to read first. Lead to the mood guide.</li>
    <li><strong>Genre-led</strong> · Queer science fiction books, sapphic fantasy books, cosy science fiction and character-driven science fiction. Test fit before building discovery content.</li></ul>
    <p>Priority and search volumes await verification. For a future Semrush import, retain query, market, date, intent, volume, difficulty, source and proposed destination.</p></details>""")
    case += chapter(4, "creating-the-experience", "Creating the experience", f"""
    <p>Start with the kind of story the reader wants. Each mood points to a title with a brief reason, while the full bibliography stays available for comparison. A direct publisher link is the next step when a reader is ready.</p>
    {direction}
    <a class="action" href="profile/">Try the reader-facing profile</a>{previews}""")
    case += chapter(5, "beyond-the-profile", "Beyond the profile", f"""
    <div class="features"><details id="seo-plan"><summary>Search-led discovery</summary>
    <p><strong>Proposed title</strong> · Grace Curtis | Sci-Fi and Fantasy Author Profile</p>
    <p><strong>Proposed description</strong> · Explore Grace Curtis’s science fiction and fantasy novels and choose where to start with a mood-based reading guide.</p>
    <p>Use descriptive section headings, book-title anchors, cleared cover descriptions and verified publisher links. Connect author intent to the introduction, comparison intent to the guide and title intent to the individual books. The portfolio case study has a canonical URL and a moorland sharing image. The unofficial preview is noindex. The portfolio case study can be indexed if approved and published.</p></details>
    <details id="carousel"><summary>Social carousel storyboard</summary><p>Six designed concept slides for a potential author-discovery campaign.</p><div class="slides">{storyboard}</div></details>
    <details id="measurement"><summary>Measurement and usability plan</summary>
    <ul><li><strong>Profile visits and referrals</strong> · Compare entrances and tagged referrals by source.</li><li><strong>Guide interaction</strong> · Record mood selections, individual book selections and outbound publisher link clicks. Treat those clicks as intent signals.</li><li><strong>Mobile usability</strong> · Ask readers to pick a book, explain how two options differ and find publisher information using the guide. Record completion, first click, hesitation and qualitative notes.</li><li><strong>Carousel engagement</strong> · Compare saves, shares and profile referrals if the campaign is published.</li><li><strong>Organic visibility</strong> · Track impressions and relevant queries only if indexing is approved.</li></ul>
    <p>Record version, date, source, device, task or event, denominator and result for future findings. Use observation first, then test copy or ordering changes.</p></details></div>""")
    case += '</section>' + evidence
    case_html = page(
        "Worlds worth getting lost in. | Grace Curtis · The Art of Being Noticed",
        "An independent author-marketing case study and interactive reader discovery prototype.", case_assets,
        '<a href="../../#work">Back to portfolio work</a><a href="#chapters">Case study chapters</a><a href="profile/">Reader-facing preview</a>', case, "chapters.js", metadata)
    return {name: "\n".join(line.rstrip() for line in html.split("\n"))
            for name, html in (("index.html", case_html), ("profile/index.html", profile_html))}

"""Render the Cold Feet Editions research from the workbook export."""

import json
from html import escape
from math import ceil, floor, log10
from statistics import mean

INTENTS = {"I": "Informational", "C": "Commercial", "T": "Transactional", "N": "Navigational"}
CURATED = (
    "gifts for book lovers", "gifts for writers", "bookish gifts", "literary gifts",
    "bookish christmas gifts", "poetry gifts", "large desk mat", "notebook for writing poetry",
    "poetry wall art",
)


def intent(value):
    return " / ".join(INTENTS[code] for code in value.split("/")) if value else "Unavailable"


def metric(value, difficulty=False):
    if value is None:
        return "Unavailable"
    return f"{value:.0%}" if difficulty else f"{value:,}"


def details(label, content):
    return f"<details><summary>{label}</summary>{content}</details>"


def definition(items, css=""):
    return f'<dl class="{css}">' + "".join(f"<div><dt>{label}</dt><dd>{value}</dd></div>" for label, value in items) + "</dl>"


def render_explorer(terms):
    max_volume = max(term["volume"] or 0 for term in terms)

    def row(term):
        volume, kd = term["volume"], term["difficulty"]
        width = 100 * volume / max_volume if volume is not None else 0
        label = (
            f'<span class="kw-term">{escape(term["term"])}</span>'
            f'<span class="kw-value">{metric(volume)}<span class="kw-unit"> UK/mo</span></span>'
            f'<span aria-hidden="true" class="kw-track"><span style="--bar:{width:.4f}%"></span></span>'
        )
        info = definition([
            ("Estimated UK monthly volume", metric(volume)),
            ("Keyword difficulty", metric(kd, True)),
            ("Search intent", intent(term["intent"])),
            ("Cluster", escape(term["cluster"])),
            ("Suggested use", escape(f'{term["role"]} keyword for {term["page"]}')),
            ("Proposed priority", escape(term["priority"])),
        ], "kw-facts")
        return (
            f'<li data-volume="{volume if volume is not None else ""}" data-difficulty="{kd if kd is not None else ""}"'
            f' data-cluster="{escape(term["cluster"])}" data-intent="{term["intent"] or ""}">{details(label, info)}</li>'
        )

    clusters = "".join(f'<option>{escape(value)}</option>' for value in sorted({term["cluster"] for term in terms}))
    intents = "".join(f'<option value="{code}">{name}</option>' for code, name in INTENTS.items())
    return f'''<div class="kw-explorer">
<div class="kw-controls" hidden>
<label>Cluster<select name="cluster"><option value="">All clusters</option>{clusters}</select></label>
<label>Intent<select name="intent"><option value="">All intents</option>{intents}<option value="unknown">Unavailable</option></select></label>
<label>Display<select name="metric"><option value="volume">UK monthly volume</option><option value="difficulty">Keyword difficulty</option></select></label>
<label>Sort<select name="sort"><option value="featured">Research order</option><option value="volume">Volume: high to low</option><option value="difficulty">Difficulty: low to high</option></select></label>
</div>
<p class="kw-note kw-scale">Volume bars show each term relative to the largest recovered estimate. Difficulty bars use the full percentage scale.</p>
<p class="kw-note kw-count" role="status" hidden></p>
<ul class="kw-bars">{"".join(row(term) for term in terms)}</ul>
</div>'''


def render_architecture(mapping, by_term):
    def keyword_detail(term):
        row = by_term.get(term)
        if row is None:
            return f"{escape(term)} <span class='kw-note'>(metrics unavailable in the recovered database)</span>"
        return f'{escape(term)} <span class="kw-note">({metric(row["volume"])} UK/mo · KD {metric(row["difficulty"], True)} · {intent(row["intent"])})</span>'

    def node(rows):
        first = rows[0]
        supporting = list(dict.fromkeys(term.strip() for row in rows for term in row["supporting"].split(";")))
        links = first["destination"]
        link_note = ""
        if first["page"] == "Desk mat product":
            # The workbook URL now returns 404. Use the current listing from the site's sitemap.
            links = "https://coldfeeteditions.store/products/anatomy-of-a-creative-mind-literary-crafts-desk-mat"
            link_note = ' <span class="kw-note">(current listing)</span>'
        destination = (
            f'<a href="{escape(links)}">Visit existing page</a>{link_note}'
            if links.startswith("https://") else
            "Existing URL to confirm" if first["status"] == "Existing" else "Proposed destination"
        )
        recommendation = " ".join(escape(row["rationale"]) for row in rows)
        purposes = {
            "Homepage": "Introduce the brand to people exploring literary gifts.",
            "Gift collection": "Help readers browse relevant products after discovering the brand.",
            "Art print collection": "Group relevant prints for people exploring poetry wall art.",
            "Desk mat product": "Answer product-specific questions for shoppers considering a desk mat.",
            "Journal product": "Show how the journal suits people writing poetry.",
        }
        purpose = purposes.get(first["page"], "Answer an editorial query and give readers a relevant next step.")
        items = [
            ("Target page", destination),
            ("Primary keyword", keyword_detail(first["primary"])),
            ("Supporting keywords", "<ul>" + "".join(f"<li>{keyword_detail(term)}</li>" for term in supporting) + "</ul>"),
            ("Strategic purpose", purpose),
            ("Recommended SEO action", recommendation),
        ]
        status = first["status"]
        label = f'{escape(first["page"])} <span class="kw-status">{escape(status)}</span>'
        return details(label + f'<span class="kw-mapping-term">{escape(first["primary"])}</span>', definition(items, "kw-facts"))

    pages = {}
    for row in mapping:
        pages.setdefault(row["page"], []).append(row)
    columns = [
        ("Editorial content", "Discovery and engagement", ["Book lover gift guide", "Writer gift guide", "Poetry gift guide", "Seasonal gift guide", "Journal prompts article"]),
        ("Collections", "Product exploration", ["Gift collection", "Art print collection"]),
        ("Product pages", "Potential purchase", ["Desk mat product", "Journal product"]),
    ]
    assigned = {"Homepage", *(page for _, _, names in columns for page in names)}
    if assigned != set(pages):
        raise ValueError("Assign each target page in the workbook to an architecture pathway.")
    featured = {"Book lover gift guide", "Poetry gift guide", "Gift collection", "Desk mat product", "Journal product"}
    lanes = "".join(
        f'<section class="kw-lane"><h6 data-view-heading="5">{name}</h6><p class="kw-note">{purpose}</p>'
        + "".join(node(pages[page]) for page in names if page in featured) + "</section>" for name, purpose, names in columns
    )
    remaining = "".join(node(rows) for page, rows in pages.items() if page not in featured)
    return f'<div class="kw-pathways">{lanes}</div>' + details("More keyword destinations", f'<div class="kw-gateway">{remaining}</div>')


def render_opportunities(by_term):
    def example(term):
        row = by_term[term]
        return f'“{escape(term)}” ({metric(row["volume"])} UK searches/month, {metric(row["difficulty"], True)} KD)'

    themes = [
        ("Capture niche demand", f'{example("notebook for writing poetry")} closely matches the journal, while {example("large desk mat")} gives the desk mat page a concrete use case. For a small brand, a precise query can justify clearer product copy even if fewer people search for it.'),
        ("Build editorial reach", f'{example("gifts for writers")} and {example("gifts for book lovers")} suggest distinct evergreen guides. Each guide can answer the gifting question first and link naturally to relevant products.'),
        ("Leverage seasonality", f'{example("bookish christmas gifts")} supports a seasonal guide or a seasonal section in an existing guide. Confirm the search results and shipping dates before creating a separate page.'),
        ("Develop brand visibility", f'{example("literary gifts")} is a longer-term homepage theme. The proposed collection for {example("bookish gifts")} has a stronger competition estimate than {example("poetry gifts")}. Refresh the existing poetry guide first and build a distinct collection only if it serves a different need.'),
    ]
    return '<ol class="kw-themes">' + "".join(f'<li><strong>{title}</strong><p>{copy}</p></li>' for title, copy in themes) + "</ol>"


def render_roadmap(data, by_term):
    stages = [
        ("Immediate priorities", {"1", "2", "3"}, {"Poetry gift guide"}),
        ("Short-term content development", {"4", "5"}, {"Book lover gift guide", "Writer gift guide", "Seasonal gift guide"}),
        ("Longer-term organic growth", {"6"}, {"Journal prompts article"}),
    ]
    output = []
    for stage, orders, pages in stages:
        actions = "".join(
            f'<li><strong>{escape(row["action"])}</strong> {escape(row["implementation"])}'
            f' <span class="kw-note">Measure after implementation: {escape(row["measure"])}.</span></li>'
            for row in data["actions"] if str(row["order"]) in orders
        )
        briefs = "".join(
            f'<li><strong>{escape(row["title"])}</strong><br><span class="kw-note">{escape(row["keyword"])}'
            f' · {intent(by_term[row["keyword"]]["intent"])} · {escape(row["format"])}'
            f' · Link to {escape(row["links"])}.</span></li>'
            for row in data["opportunities"] if row["page"] in pages
        )
        output.append(f'<section><h6 data-view-heading="5">{stage}</h6><ul>{actions}{briefs}</ul></section>')
    return '<div class="kw-roadmap">' + "".join(output) + "</div>"


def render_keyword_strategy(root):
    data = json.loads((root / "_data/keyword-research.json").read_text(encoding="utf-8"))
    terms = data["keywords"]
    by_term = {row["term"]: row for row in terms}
    known = [row["difficulty"] for row in terms if row["difficulty"] is not None]
    metrics = definition([
        ("Recovered keywords", str(len(by_term))),
        ("Combined estimated UK searches/month", metric(sum(row["volume"] for row in terms if row["volume"] is not None))),
        (f"Mean known difficulty ({len(known)} terms)", f"{mean(known):.1%}"),
        ("Keyword clusters", str(len({row["cluster"] for row in terms}))),
    ], "kw-metrics")
    template = (root / "_content/cases/keyword-strategy.html").read_text(encoding="utf-8")
    parts = {
        "METRICS": metrics,
        "EXPLORER": render_explorer(terms),
        "SCATTER": scatter(terms, data["mapping"]),
        "PRIORITIES": priority_chart(by_term, data["mapping"]),
        "ARCHITECTURE": render_architecture(data["mapping"], by_term),
        "OPPORTUNITIES": render_opportunities(by_term),
        "ROADMAP": render_roadmap(data, by_term),
    }
    for name, html in parts.items():
        template = template.replace("{{" + name + "}}", html)
    return template


PRIORITIES = (
    "gifts for writers", "large desk mat", "bookish christmas gifts",
    "poetry gifts", "notebook for writing poetry",
)


def priority_chart(by_term, mapping):
    pages = {row["primary"]: row for row in reversed(mapping)}
    peak = max(by_term[key]["volume"] for key in PRIORITIES)
    rows = []
    for key in PRIORITIES:
        term, page = by_term[key], pages[key]
        width = 100 * term["volume"] / peak
        rows.append(
            f'<li><div class="kw-priority-line"><strong>{escape(key.capitalize())}</strong>'
            f'<span class="kw-note">{metric(term["volume"])} UK/mo · {metric(term["difficulty"], True)} KD</span></div>'
            f'<div class="kw-track" aria-hidden="true"><span style="--bar:{width:.4f}%"></span></div>'
            f'<p><b>{escape(page["page"])}</b> <span class="kw-status">{escape(page["status"])}</span>'
            f' · {escape(page["rationale"])}</p></li>'
        )
    return '<ol class="kw-priorities">' + "".join(rows) + "</ol>"


def scatter(terms, mapping):
    eligible = [row for row in terms if row["difficulty"] is not None
                and row["volume"] is not None and row["volume"] >= 0]
    positive = [row["volume"] for row in eligible if row["volume"] > 0]
    log_min, log_max = floor(log10(min(positive))), ceil(log10(max(positive)))
    log_max = max(log_min + 1, log_max)
    peak = max(positive)
    step = 10 ** floor(log10(peak))
    linear_max = ceil(peak / step) * step
    kd_max = max(.2, ceil(max(row["difficulty"] for row in eligible) * 10) / 10)
    left, right, top, bottom = 61, 546, 16, 196

    def x(value):
        return left + (right - left) * value / kd_max

    def y(value, logarithmic):
        ratio = ((log10(value) - log_min) / (log_max - log_min) if logarithmic
                 else value / linear_max)
        return bottom - (bottom - top) * ratio

    def horizontal(ticks, logarithmic):
        return "".join(
            f'<path class="kw-gridline" d="M{left} {y(tick, logarithmic):.3f}H{right}"/>'
            f'<text x="{left - 7}" y="{y(tick, logarithmic):.3f}" dy=".35em" text-anchor="end">{metric(tick)}</text>'
            for tick in ticks
        )

    difficulty_ticks = [i / 10 for i in range(round(kd_max * 10) + 1)]
    axes = "".join(
        f'<text x="{x(tick):.3f}" y="{bottom + 22}" text-anchor="middle">{tick:.0%}</text>'
        for tick in difficulty_ticks
    )
    pages = {row["page"]: row["status"] for row in mapping}
    points = []
    options = []
    for row in eligible:
        key, volume, kd = row["term"], row["volume"], row["difficulty"]
        featured = key in CURATED
        attrs = {
            "term": key, "cluster": row["cluster"], "volume": metric(volume),
            "kd": metric(kd, True), "intent": intent(row["intent"]),
            "page": f'{row["page"]} ({pages[row["page"]].lower()})' if row["page"] in pages else row["page"],
            "featured": str(featured).lower(),
            "log-y": f'{y(volume, True):.3f}' if volume > 0 else "",
            "linear-y": f'{y(volume, False):.3f}',
        }
        metadata = " ".join(f'data-{name}="{escape(value)}"' for name, value in attrs.items())
        points.append(
            f'<circle cx="{x(kd):.3f}" cy="{attrs["log-y"] or bottom}" r="6" {metadata}'
            f'{" hidden" if not featured or not volume else ""}{" class=\"is-selected\"" if key == CURATED[0] else ""}/>'
        )
        if featured and volume:
            options.append(f'<option>{escape(key)}</option>')
    initial = next(row for row in eligible if row["term"] == CURATED[0])
    initial_page = initial["page"]
    clusters = "".join(f'<option>{escape(key)}</option>' for key in sorted({row["cluster"] for row in terms}))
    return f'''<div class="kw-scatter">
<div class="kw-controls" hidden>
<label>Search volume scale<select name="scale"><option value="log">Logarithmic</option><option value="linear">Linear</option></select></label>
<label>Keywords shown<select name="scope"><option value="featured">Featured selection</option><option value="all">All plottable keywords</option></select></label>
<label>Cluster<select name="chart-cluster"><option value="">All clusters</option>{clusters}</select></label>
</div>
<p class="kw-note kw-axis-label">Estimated UK searches per month</p>
<svg viewBox="0 0 560 233" aria-hidden="true">
<rect class="kw-low-zone" x="{left}" y="{top}" width="{x(.2)-left:.3f}" height="{bottom-top}"/>
<g class="kw-log-axis">{horizontal([10**i for i in range(log_min, log_max+1)], True)}</g>
<g class="kw-linear-axis" hidden>{horizontal([round(linear_max*i/4) for i in range(5)], False)}</g>
<path class="kw-axis-line" d="M{left} {top}V{bottom}H{right}"/>{axes}
{"".join(points)}
</svg>
<p class="kw-note kw-axis-caption">Keyword difficulty (KD) · shaded area: 20% or lower</p>
<label class="kw-picker" hidden>Select a keyword<select name="point">{"".join(options)}</select></label>
<div class="kw-point-info" role="status" aria-atomic="true">
<strong>{escape(initial["term"])}</strong><p>{metric(initial["volume"])} UK searches/month · {metric(initial["difficulty"], True)} KD · {intent(initial["intent"])}<br>{escape(initial_page)} ({pages[initial_page].lower()})</p>
</div>
<p class="kw-note">Missing difficulty or volume stays in the full research. Zero volume can appear on the linear scale only.</p>
</div>'''

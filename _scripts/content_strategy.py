"""Render the workbook's content strategy as progressively enhanced HTML."""

import json
from collections import defaultdict
from datetime import date
from html import escape

from keyword_strategy import definition

RELEVANCE = ("No direct relevance", "Low relevance", "Medium relevance", "High relevance")
CAMPAIGN_THEMES = {
    "Thoughtful giving": "The art of thoughtful giving.",
    "The page you almost wrote": "The page you almost wrote.",
    "The things we carry": "The things we carry.",
    "Words we take with us": "The words we take with us.",
}
CAMPAIGNS = {
    "Lessons in Anatomy": (
        "Lessons in Anatomy", "Lessons in Anatomy film",
        "products/anatomy-lessons-framed-print.webp", 700, 948,
        "Framed Cold Feet Editions Anatomy Lessons poetry print",
    ),
    "Almost, Always": (
        "Almost, Always", "Almost, Always film",
        "products/almost-always-hardback-and-open-pages.webp", 1000, 417,
        "Cold Feet Editions Almost, Always hardback and open pages",
    ),
    "Revolution essay": (
        "We Were Never Asking for a Revolution", "Revolution essay",
        "strategy/cold-feet-editions-tiktok-covers.webp", 349, 122,
        "Cold Feet Editions TikTok covers including the Revolution essay adaptation",
    ),
    "Poetry gift guide": (
        "The poetry gift guide", "Poetry gift guide",
        "strategy/cold-feet-editions-pinterest-pins.webp", 362, 166,
        "Cold Feet Editions Pinterest pins showing poetry gift ideas",
    ),
}


def disclosure(label, content, group=None, opened=False):
    name = f' name="{group}"' if group else ""
    return f'<details{name}{" open" if opened else ""}><summary>{label}</summary>{content}</details>'


def facts(pairs):
    return definition([(label, escape(value)) for label, value in pairs if value], "kw-facts")


def personas(rows):
    cards = []
    for index, row in enumerate(rows):
        fields = facts([
            ("Motivation", row["motivation"]), ("Barrier", row["barrier"]),
            ("Preferred channels", row["channels"]), ("Content and relevant products", row["content"]),
            ("Search opportunity", row["search"]),
        ])
        cards.append(disclosure("The " + escape(row["name"]), fields, "cs-personas", index == 0))
    return '<div class="cs-disclosures">' + "".join(cards) + "</div>"


def pillars(rows):
    if abs(sum(row["share"] for row in rows) - 1) > 1e-9:
        raise ValueError("Content pillar shares must total 100%.")
    bar = "".join(f'<span style="--share:{row["share"]:.0%}"></span>' for row in rows)
    cards = "".join(
        disclosure(
            f'{escape(row["name"])} <span class="cs-score">{row["share"]:.0%}</span>',
            facts([("Objective", row["objective"]), ("Formats", row["formats"]), ("Example", row["example"])]),
            "cs-pillars",
        )
        for row in rows
    )
    return f'<div class="cs-mix" aria-hidden="true">{bar}</div><div class="cs-disclosures">{cards}</div>'


def audience_matrix(data):
    columns = []
    for persona, key in zip(data["personas"], ("romantic", "writer", "reader", "gifter")):
        name = persona["name"]
        cells = []
        for row in data["matrix"]:
            pillar, score = row["pillar"], row[key]
            concepts = [item for item in data["concepts"] if item["audience"] == name and item["pillar"] == pillar]
            content = "".join(
                f'<div><strong>{escape(item["name"])}</strong>'
                + facts([("Channel", item["channel"]), ("Objective", item["objective"]),
                         ("Call to action", item["cta"]), ("Keyword candidate", item["keyword"])])
                + '</div>' for item in concepts
            ) or '<p>No concept is mapped to this combination in the workbook.</p>'
            label = f'{escape(pillar)}<span class="cs-relevance cs-score-{score}">{score} · {RELEVANCE[score]}</span>'
            cells.append(disclosure(label, content, "cs-matrix"))
        columns.append(
            f'<section><h6 data-view-heading="5">The {escape(name)}</h6>{"".join(cells)}</section>'
        )
    return '<div class="cs-matrix cs-disclosures">' + "".join(columns) + "</div>"


def journey(rows):
    items = "".join(
        f'<li><strong>{escape(row["stage"])}</strong>'
        + facts([("Touchpoint", row["touchpoint"]), ("Intended action", row["action"]), ("Indicator", row["kpi"])])
        + '</li>' for row in rows
    )
    return f'<ol class="cs-journey">{items}</ol>'


def campaigns(data):
    assets = {row["name"]: row for row in data["assets"]}
    cards = []
    for index, row in enumerate(data["repurposing"]):
        title, key, path, width, height, alt = CAMPAIGNS[row["asset"]]
        asset = assets[key]
        flow = [
            ("Illustrated poetry film", "Draft exists; review the final export and captions."),
            ("TikTok", "Short excerpts from the illustrated film."),
        ] if index == 0 else [("TikTok", row["tiktok"])]
        flow += [("Pinterest", row["pinterest"]), ("Journal", row["journal"]),
                 ("Email", row["email"]), ("Product connection", row["product"])]
        content = (
            f'<div class="cs-campaign"><figure><img src="assets/images/{path}" width="{width}" height="{height}"'
            f' loading="lazy" decoding="async" alt="{escape(alt)}"><figcaption>Existing creative reference</figcaption></figure>'
            f'<div>{facts([("Known state", asset["state"]), ("Next action", asset["action"])])}'
            '<ol class="cs-adaptations">'
            + "".join(f'<li><strong>{escape(channel)}</strong><span>{escape(idea)}</span></li>' for channel, idea in flow)
            + '</ol></div></div>'
        )
        cards.append(disclosure(escape(title), content, "cs-campaigns", index == 0))
    return '<div class="cs-disclosures">' + "".join(cards) + "</div>"


def calendar(data):
    concepts = {row["name"]: row for row in data["concepts"]}
    weeks = defaultdict(lambda: defaultdict(list))
    for row in data["calendar"]:
        weeks[row["theme"]][row["date"]].append(row)
    channels = dict.fromkeys(row["channel"] for row in data["calendar"])

    def options(values):
        return '<option value="">All</option>' + "".join(f'<option>{escape(value)}</option>' for value in values)

    def entry(row):
        internal = row["channel"] == "Internal"
        activity = "Production / review" if internal else "Planned publishing"
        concept = concepts.get(row["concept"])
        entries = [
            ("Channel", "Internal" if internal else row["channel"]),
            ("Pillar", row["pillar"]), ("Audience", row["audience"]),
            ("Objective", concept["objective"] if concept else None),
            ("Task" if internal else "Call to action", row["cta"]), ("Keyword candidate", row["keyword"]),
        ]
        return (
            f'<li data-channel="{escape(row["channel"])}" data-pillar="{escape(row["pillar"] or "")}">'
            f'<span class="kw-note">{activity}</span><br><strong>{escape(row["concept"])}</strong>'
            f'{facts(entries)}</li>'
        )

    sections = []
    for theme, days in weeks.items():
        dates = [date.fromisoformat(value) for value in days]
        contents = "".join(
            disclosure(
                f'<time datetime="{day}">{date.fromisoformat(day).day} December</time>'
                + (' <span class="kw-note">Production / review</span>' if all(row["channel"] == "Internal" for row in rows) else ""),
                '<ul class="cs-agenda">' + "".join(entry(row) for row in rows) + '</ul>',
                "cs-calendar-day",
            )
            for day, rows in days.items()
        )
        sections.append(
            f'<section class="cs-week"><p class="kw-note">{min(dates).day}–{max(dates).day} December</p>'
            f'<h6 data-view-heading="5">{CAMPAIGN_THEMES[theme]}</h6>{contents}</section>'
        )
    return (
        '<div class="cs-calendar"><div class="kw-controls" hidden>'
        f'<label>Channel<select name="channel">{options(channels)}</select></label>'
        f'<label>Pillar<select name="pillar">{options(row["name"] for row in data["pillars"])}</select></label>'
        '</div><p class="kw-note cs-calendar-status" role="status" hidden></p>'
        '<div class="cs-weeks cs-disclosures">' + "".join(sections) + '</div></div>'
    )


def measurement(rows):
    objectives = {
        "Brand awareness": ("Views", "Impressions"),
        "Engagement": ("Shares", "Saves"),
        "Website acquisition": ("Outbound clicks", "Clicks"),
        "Subscriber growth": ("New subscribers",),
        "Commercial performance": ("Orders", "Conversion rate"),
    }
    metrics = {row["metric"]: row for row in rows}
    return '<dl class="cs-measurement">' + "".join(
        f'<div><dt>{label}</dt><dd><ul>'
        + "".join(f'<li>{escape(metric)} <span class="kw-note">· {escape(metrics[metric]["source"])}</span></li>'
                  for metric in names)
        + '</ul></dd></div>' for label, names in objectives.items()
    ) + '</dl>'


def render_content_strategy(root):
    data = json.loads((root / "_data/content-strategy.json").read_text(encoding="utf-8"))
    parts = {
        "METRICS": definition([
            ("Proposed audience personas", str(len(data["personas"]))),
            ("Content pillars", str(len(data["pillars"]))),
            ("Days of editorial planning", str(len({row["date"] for row in data["calendar"]}))),
        ], "kw-metrics"),
        "PERSONAS": personas(data["personas"]),
        "PILLARS": pillars(data["pillars"]),
        "MATRIX": audience_matrix(data),
        "JOURNEY": journey(data["journey"]),
        "CAMPAIGNS": campaigns(data),
        "CALENDAR": calendar(data),
        "KPIS": measurement(data["kpis"]),
    }
    template = (root / "_content/cases/content-strategy.html").read_text(encoding="utf-8")
    for key, value in parts.items():
        template = template.replace("{{" + key + "}}", value)
    return template

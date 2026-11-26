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


def disclosure(label, content, group=None, opened=False, anchor=None):
    name = f' name="{group}"' if group else ""
    target = f' id="{escape(anchor)}" data-open-disclosure' if anchor else ""
    return f'<details{name}{" open" if opened else ""}><summary{target}>{label}</summary>{content}</details>'


def facts(pairs):
    return definition([(label, escape(value)) for label, value in pairs if value], "kw-facts")


PERSONA_DETAILS = {
    "Literary Romantic": ("Literary work that resonates with how they feel", "Prints and journal", "Poetry and illustrated films"),
    "Aspiring Writer": ("Ideas and routines that make it easier to start writing", "Journal and desk mat", "Prompts and writing rituals"),
    "Cultural Reader": ("Writing that offers connection and representation", "No product assigned in the workbook", "Essays and literary commentary"),
    "Thoughtful Gifter": ("A gift with personal meaning and clear buying information", "Prints, journal and desk mat in the proposed reader gift guide", "Gift guides and product demonstrations"),
}

PILLAR_DESCRIPTIONS = {
    "Words worth keeping": "Give readers a line or image they want to keep or share.",
    "Behind the words": "Show how the writing and design take shape.",
    "Between the lines": "Make space for longer ideas about identity and literary culture.",
    "Objects with meaning": "Show how the writing carries through to a gift or an object.",
    "Notes from the margins": "Give readers a reason to stay in touch with the studio.",
}


PERSONA_PRESENTATION = {
    "Literary Romantic": (
        "I want to find words that feel like something I’ve lived.",
        "Build recognition through original poetry and illustrated storytelling, then introduce the prints and journal.",
        "literary gifts",
        "An open poetry book with handwritten annotations and pressed flowers",
    ),
    "Aspiring Writer": (
        "I’d like a small ritual that helps me start writing again.",
        "Present the journal and desk mat as part of a writing ritual. Use prompts and process-led content to give readers a reason to return.",
        "gifts for writers",
        "An open journal, fountain pen and manuscript pages on a writing desk",
    ),
    "Cultural Reader": (
        "I want to read work that gives me another way to see things.",
        "Build editorial trust through thoughtful essays, literary discussion and independent creative voices.",
        None,
        "A stack of books beside reading glasses and annotated essays",
    ),
    "Thoughtful Gifter": (
        "I want to give them something that feels chosen for them.",
        "Use search-led gift guides to help readers choose a meaningful gift. Show what makes each product relevant and make buying information easy to find.",
        "gifts for book lovers",
        "A literary gift wrapped with a burgundy ribbon and gift tag",
    ),
}


def personas(rows, keywords, root):
    by_term = {row["term"]: row for row in keywords}
    cards = []
    for index, row in enumerate(rows):
        name = row["name"]
        slug = name.lower().replace(" ", "-")
        label = "The " + escape(name)
        needs, products, preferences = PERSONA_DETAILS[name]
        quote, response, term, alt = PERSONA_PRESENTATION[name]
        keyword = by_term.get(term)
        if keyword:
            search = (
                f'<strong>{escape(term.capitalize())}</strong><br>'
                f'{keyword["volume"]:,} estimated UK searches/month · {keyword["difficulty"]:.0%} keyword difficulty'
            )
        else:
            search = "Editorial-led discovery. The research did not establish a direct target keyword."
        channels = "".join(f'<li>{escape(channel.strip())}</li>' for channel in row["channels"].split(";"))
        image = f"assets/images/personas/{slug}.webp"
        artwork = (
            f'<figure class="persona-art"><img src="{image}" width="640" height="480" '
            f'loading="lazy" decoding="async" alt="{escape(alt)}"></figure>'
            if (root / image).is_file() else ""
        )
        fields = (
            '<dl class="persona-facts">'
            f'<div><dt>Core motivation</dt><dd>{escape(row["motivation"])}</dd></div>'
            f'<div><dt>Audience needs</dt><dd><ul><li>{escape(needs)}</li></ul></dd></div>'
            f'<div><dt>Purchase barrier</dt><dd>{escape(row["barrier"])}</dd></div>'
            f'<div><dt>Preferred channels</dt><dd><ul class="persona-channels">{channels}</ul></dd></div>'
            f'<div><dt>Relevant products</dt><dd>{escape(products)}</dd></div>'
            f'<div><dt>Content preferences</dt><dd>{escape(preferences)}</dd></div>'
            '</dl>'
        )
        content = f'''<div class="persona-profile" id="persona-{slug}">
<div class="persona-profile-lead">
<div><p class="persona-label">Proposed content effort · {row["share"]:.0%}</p>
<h5 data-view-heading="4">{label}</h5>
<blockquote><p>“{escape(quote)}”</p><footer>Illustrative persona statement</footer></blockquote></div>
{artwork}
</div>
{fields}
<div class="persona-decisions"><div><p class="persona-label">Search opportunity</p><p>{search}</p></div>
<div><p class="persona-label">Strategic response</p><p>{escape(response)}</p></div></div>
</div>'''
        cards.append(disclosure(label, content, "cs-personas", index == 0))
    return (
        '<div class="persona-experience"><div class="persona-tabs" role="tablist" aria-label="Audience personas" hidden></div>'
        '<div class="persona-profiles">' + "".join(cards) + "</div></div>"
    )


def pillars(rows):
    if abs(sum(row["share"] for row in rows) - 1) > 1e-9:
        raise ValueError("Content pillar shares must total 100%.")
    segments, offset = [], 0
    for index, row in enumerate(rows):
        share = row["share"] * 100
        segments.append(
            f'<circle cx="110" cy="110" r="83" pathLength="100" data-pillar-index="{index}" '
            f'stroke-dasharray="{share - 0.65:g} {100 - share + 0.65:g}" stroke-dashoffset="{-offset:g}"/>'
        )
        offset += share
    cards = "".join(
        disclosure(
            f'{escape(row["name"])} <span class="cs-score">{row["share"]:.0%}</span>',
            facts([("What it does", PILLAR_DESCRIPTIONS[row["name"]]), ("Objective", row["objective"]), ("Formats", row["formats"]), ("Example", row["example"])]),
            "cs-pillars",
            opened=index == 0,
            anchor="pillar-" + row["name"].lower().replace(" ", "-"),
        )
        for index, row in enumerate(rows)
    )
    return (
        '<div class="cs-pillars"><div class="cs-mix-layout">'
        '<div class="cs-donut" hidden><svg viewBox="0 0 220 220" aria-hidden="true">'
        f'<g transform="rotate(-90 110 110)">{"".join(segments)}</g></svg>'
        '<div class="cs-donut-center" aria-hidden="true"><strong></strong><span>Content mix</span></div></div>'
        f'<div class="cs-disclosures cs-pillar-legend">{cards}</div></div>'
        '<div class="cs-pillar-selection" role="region" aria-label="Selected content pillar" hidden></div></div>'
    )


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
    channels = {
        "Discovery": "TikTok and Pinterest", "Connection": "Social and the Journal",
        "Exploration": "Website Journal and shop", "Consideration": "Shop and email",
        "Conversion": "Online shop", "Retention": "Email and the Journal",
    }
    items = "".join(
        '<li>' + disclosure(
            f'<span class="journey-number">{i:02}</span> {escape(row["stage"])}',
            facts([("Channels", channels[row["stage"]]), ("Touchpoint", row["touchpoint"]),
                   ("Intended action", row["action"]), ("Indicator", row["kpi"])]),
            "cs-journey-stage",
        ) + '</li>' for i, row in enumerate(rows, 1)
    )
    return f'<ol class="cs-journey cs-disclosures">{items}</ol>'


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
            f'<div>{facts([("Existing work", asset["state"]), ("Next action", asset["action"])])}'
            '<p class="kw-note">Channel adaptations and product links</p><ol class="cs-adaptations">'
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
        '<div class="cs-weeks cs-disclosures">' + "".join(sections) + '</div>'
        '<section class="cs-day-panel" aria-label="Selected calendar date" hidden><p class="cs-day-title"></p><ul class="cs-agenda"></ul></section></div>'
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
    keywords = json.loads((root / "_data/keyword-research.json").read_text(encoding="utf-8"))["keywords"]
    sections = {
        "CONTENT_STRATEGY": ("content-strategy", {
            "PILLARS": pillars(data["pillars"]),
            "MATRIX": audience_matrix(data),
            "JOURNEY": journey(data["journey"]),
            "CAMPAIGNS": campaigns(data),
            "CALENDAR": calendar(data),
        }),
        "AUDIENCE_STRATEGY": ("audience-strategy", {"PERSONAS": personas(data["personas"], keywords, root)}),
        "MEASUREMENT_STRATEGY": ("measurement-strategy", {"KPIS": measurement(data["kpis"])}),
    }
    output = {}
    for marker, (name, parts) in sections.items():
        template = (root / f"_content/cases/{name}.html").read_text(encoding="utf-8")
        for key, value in parts.items():
            template = template.replace("{{" + key + "}}", value)
        output[marker] = template
    return output

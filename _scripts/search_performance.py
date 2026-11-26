"""Render a dated Search Console snapshot without a client-side dependency."""
import json
from datetime import date
from html import escape


def date_label(value, include_year=False):
    day = date.fromisoformat(value)
    return f"{day.day} {day:%b}" + (f" {day.year}" if include_year else "")


def table(caption, headers, rows):
    head = "".join(f'<th scope="col">{escape(label)}</th>' for label in headers)
    body = "".join(
        f'<tr><th scope="row">{escape(str(first))}</th>'
        + "".join(f"<td>{escape(str(value))}</td>" for value in rest) + "</tr>"
        for first, *rest in rows
    )
    return (f'<table class="search-table"><caption>{escape(caption)}</caption>'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')


def bars(caption, rows):
    peak = max(1, *(value for _, value in rows))
    items = "".join(
        f'<li><span>{escape(label)}</span><strong>{value}</strong>'
        f'<span class="search-bar" style="--fill:{100 * value / peak:.4f}%" aria-hidden="true"></span></li>'
        for label, value in rows
    )
    return f'<figure class="search-bars"><figcaption>{escape(caption)}</figcaption><ul role="list">{items}</ul></figure>'


def donut(value, remainder, labels, percentage):
    left, right = labels
    return (
        '<figure class="search-donut">'
        f'<div class="search-ring" style="--share:{percentage}%" aria-hidden="true"><strong>{percentage:g}%</strong></div>'
        f'<figcaption><strong>{percentage:g}% {escape(left)}</strong><br>'
        f'{value} {escape(left)} · {remainder} {escape(right)}</figcaption></figure>'
    )


def line_chart(rows):
    peak = max(1, *(max(row["impressions"], row["clicks"]) for row in rows))
    x = lambda index: 37 + 476 * index / max(1, len(rows) - 1)
    y = lambda count: 186 - 150 * count / peak
    grid = "".join(
        f'<path class="search-gridline" d="M37 {y(tick)}H513"/><text x="29" y="{y(tick)+4}" text-anchor="end">{tick}</text>'
        for tick in range(0, peak + 1, 2)
    )
    ticks = sorted({round((len(rows) - 1) * fraction / 4) for fraction in range(5)})
    guides = "".join(f'<text x="{x(i)}" y="211" text-anchor="middle">{date_label(rows[i]["date"])}</text>'
                     for i in ticks)
    series = "".join(
        f'<polyline class="search-series search-series-{key}" points="'
        + " ".join(f'{x(i)},{y(row[key])}' for i, row in enumerate(rows)) + '"/>'
        for key in ("impressions", "clicks")
    )
    points = []
    for i, row in enumerate(rows):
        when = date_label(row["date"])
        impression_label = "impression" if row["impressions"] == 1 else "impressions"
        click_label = "click" if row["clicks"] == 1 else "clicks"
        label = f'{when}: {row["impressions"]} {impression_label}, {row["clicks"]} {click_label}'
        horizontal = min(max(x(i) - 65, 36), 334)
        points.append(
            f'<g class="search-point" tabindex="0" role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
            f'<rect class="search-hit" x="{x(i)-16}" y="35" width="32" height="153"/>'
            f'<circle class="search-dot" cx="{x(i)}" cy="{y(row["impressions"])}" r="4"/>'
            f'<g class="search-tip" transform="translate({horizontal} 2)" aria-hidden="true">'
            f'<rect width="205" height="26" rx="2"/><text x="8" y="17">{when} · {row["impressions"]} impr. · {row["clicks"]} {click_label}</text></g></g>'
        )
    period = f'{date_label(rows[0]["date"])}–{date_label(rows[-1]["date"], True)}'
    return (
        '<figure class="search-chart"><figcaption>Daily Web search counts</figcaption>'
        f'<svg viewBox="0 0 550 223" aria-label="Daily impressions and clicks, {period}">'
        + grid + guides + series + "".join(points) + '</svg>'
        '<p class="kw-note"><span class="search-impressions-key">Solid line: impressions</span> · '
        '<span class="search-clicks-key">Dashed line: clicks</span></p></figure>'
    )


def bullets(items):
    return '<ul>' + ''.join(f'<li>{escape(item)}</li>' for item in items) + '</ul>'


def evidence_gallery(root, items):
    figures = []
    for item in items:
        path = item["path"]
        if not path.startswith("assets/images/") or not (root / path).is_file():
            raise ValueError(f"Missing reviewed evidence image: {path}")
        path = escape(path)
        caption = escape(item["caption"])
        figures.append(
            f'<figure><a href="{path}"><img src="{path}" width="{int(item["width"])}" height="{int(item["height"])}" '
            f'loading="lazy" decoding="async" alt="View full-size evidence: {caption}"></a><figcaption>{caption}</figcaption></figure>'
        )
    if not figures:
        return ""
    return (
        '<details class="case-evidence"><summary id="search-source-evidence" data-open-disclosure>Original Search Console evidence</summary>'
        '<div class="search-evidence-grid">' + "".join(figures) + '</div></details>'
    )


def render_search_performance(root):
    data = json.loads((root / "_data/cold-feet-search-performance.json").read_text())
    snapshot = max(data["snapshots"], key=lambda item: item["captured"])
    overview, daily = snapshot["overview"], snapshot["daily"]
    countries, pages = snapshot["countries"], snapshot["pages"]
    indexing = snapshot["indexing"]
    uk = next(row for row in countries if row["country"] == "United Kingdom")
    rest = overview["impressions"] - uk["impressions"]
    country_remainder = overview["impressions"] - sum(row["impressions"] for row in countries)
    canonical, discovered = (indexing["reasons"][i]["urls"] for i in (0, 1))
    for key in ("clicks", "impressions"):
        if sum(row[key] for row in daily) != overview[key]:
            raise ValueError(f"Daily {key} do not reconcile with Search Console overview")
    if (indexing["known"] != indexing["indexed"] + indexing["excluded"]
            or sum(row["urls"] for row in indexing["reasons"]) != indexing["excluded"]
            or overview["average_ctr"] != 100 * overview["clicks"] / overview["impressions"]):
        raise ValueError("Search Console overview or indexing totals do not reconcile")

    metrics = [
        ("Impressions", overview["impressions"]), ("Organic click", overview["clicks"]),
        ("CTR", f'{overview["average_ctr"]:g}%'), ("Average position", overview["average_position"]),
    ]
    query = snapshot["queries"][0]
    start, end = snapshot["visible_dates"]
    values = {
        "SOURCE": escape(data["source"]), "PROPERTY": escape(data["property"]),
        "PERIOD": f'{date_label(start)}–{date_label(end, True)}',
        "FILTER": escape(snapshot["reporting_filter"]), "SEARCH_TYPE": escape(snapshot["search_type"]),
        "CAPTURED": date_label(snapshot["captured"], True), "INDEX_UPDATED": date_label(snapshot["indexing_updated"], True),
        "METRICS": '<dl class="search-metrics">' + "".join(f'<div><dt>{label}</dt><dd>{value}</dd></div>' for label,value in metrics) + '</dl>',
        "LINE_CHART": line_chart(daily),
        "DAILY_TABLE": table("Daily counts reconstructed from the screenshot", ("Date", "Impressions", "Clicks"),
                             [(date_label(row["date"]), row["impressions"], row["clicks"]) for row in daily]),
        "UK_DONUT": donut(uk["impressions"], rest, ("UK", "rest of world"), 100 * uk["impressions"] / overview["impressions"]),
        "UK_IMPRESSIONS": str(uk["impressions"]), "UK_SHARE": f'{100 * uk["impressions"] / overview["impressions"]:g}%',
        "UK_CTR": f'{100 * uk["clicks"] / uk["impressions"]:g}%',
        "COUNTRIES": table("Visible countries plus the calculated remainder", ("Country","Impressions","Clicks"),
                           [(row["country"],row["impressions"],row["clicks"]) for row in countries]
                           + [("Remaining impressions not shown",country_remainder,overview["clicks"] - sum(row["clicks"] for row in countries))]),
        "PAGE_BARS": bars("Impressions by page, ten visible rows", [(row["label"],row["impressions"]) for row in pages]),
        "PAGES": table("Visible page-level search performance", ("URL path","Impressions","Clicks"),
                       [(row["path"],row["impressions"],row["clicks"]) for row in pages]),
        "QUERY": escape(query["query"]), "QUERY_IMPRESSIONS": str(query["impressions"]), "QUERY_CLICKS": str(query["clicks"]),
        "INDEX_DONUT": donut(indexing["indexed"], indexing["excluded"], ("indexed", "excluded"),
                             round(100 * indexing["indexed"] / indexing["known"], 1)),
        "KNOWN": str(indexing["known"]),
        "INDEX_BARS": bars("Reasons URLs were excluded", [(row["reason"],row["urls"]) for row in indexing["reasons"]]),
        "CANONICAL_COUNT": str(canonical), "CANONICAL_EXCLUDED": f'{100 * canonical / indexing["excluded"]:.2f}%',
        "CANONICAL_KNOWN": f'{100 * canonical / indexing["known"]:.1f}%',
        "DISCOVERED_SHARE": f'{100 * discovered / indexing["excluded"]:.1f}%',
        "CANONICAL_EXAMPLES": table("Ten visible examples with reported last crawl dates", ("URL path","Last crawled"),
                                    [(row["path"],date_label(row["last_crawled"], True)) for row in snapshot["canonicals"]]),
        "ACTIONS": bullets(snapshot["actions"]),
        "METHODOLOGY": bullets(snapshot["methodology"] + snapshot["limitations"]),
        "EVIDENCE": evidence_gallery(root, snapshot["evidence"]),
    }
    template = (root / "_content/cases/search-performance.html").read_text()
    for name, value in values.items():
        template = template.replace("{{" + name + "}}", value)
    return template

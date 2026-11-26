"""Render the verified V5 scene sequence and V2/V5 comparisons."""

import json
from html import escape
from pathlib import Path

IMAGES = "assets/images/campaigns/lessons-in-anatomy"
MEDIA = "assets/video/lessons-in-anatomy-v5.mp4"


def clock(seconds):
    return f"{int(seconds) // 60}:{int(seconds) % 60:02}"


def scene_card(scene):
    number = int(scene["number"])
    title = escape(scene["title"])
    image = f'{IMAGES}/{Path(scene["image"]).name}'
    start, end = (clock(scene[key]) for key in ("start_seconds", "end_seconds"))
    still = float(scene["still_seconds"])
    composition = escape(scene["composition"])
    motion = escape(scene["movement_and_transition"])
    intent = escape(scene["intention"])
    return f'''<li class="anatomy-scene">
<details name="anatomy-scene">
<summary aria-label="Scene {number:02}: {title}, {start} to {end}"><img src="{image}" width="450" height="800" loading="lazy" decoding="async" alt="{composition}">
<span class="anatomy-scene-time">{number:02} · {start}–{end}</span><span class="anatomy-scene-title">{title}</span></summary>
<div class="anatomy-scene-detail">
<p><strong>{title}</strong></p>
<dl><div><dt>Composition</dt><dd>{composition}</dd></div>
<div><dt>Movement and transition</dt><dd>{motion}</dd></div>
<div><dt>Creative intention</dt><dd>{intent}</dd></div></dl>
<a href="{MEDIA}#t={still:g}" data-anatomy-seek="{still:g}">View this moment in the film</a>
</div>
</details></li>'''


def comparison_card(item):
    title = escape(item["title"])
    name = item["title"].lower()
    src = f"{IMAGES}/v2-v5-{name}.webp"
    return f'''<figure><a href="{src}"><img src="{src}" width="760" height="692" loading="lazy" decoding="async" alt="{title}, V2 on the left and V5 on the right"></a>
<figcaption><strong>{title}.</strong> {escape(item["description"])}</figcaption></figure>'''


def render_anatomy_feature(root):
    data = json.loads((root / "_data/lessons-in-anatomy-scenes.json").read_text(encoding="utf-8"))
    strip = '<div class="anatomy-sequence"><ol class="anatomy-storyboard">' + "".join(
        scene_card(scene) for scene in data["scenes"]
    ) + '</ol><div id="anatomy-selection" class="anatomy-selection" role="region" aria-label="Selected scene" hidden></div></div>'
    comparisons = '<div class="anatomy-comparisons">' + "".join(
        comparison_card(item) for item in data["comparisons"]
    ) + "</div>"
    template = (root / "_content/cases/anatomy-feature.html").read_text(encoding="utf-8")
    return template.replace("{{ANATOMY_SCENES}}", strip).replace("{{ANATOMY_COMPARISONS}}", comparisons)

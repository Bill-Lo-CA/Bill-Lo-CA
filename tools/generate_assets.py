"""Generate the terminal-styled SVG assets for the Bill-Lo-CA GitHub profile README.

Colours, radii and component shapes follow bill-lo-ca.github.io/style.css.
Every element that holds text carries data-max (the right edge it must not cross),
so check.py can measure the rendered text and catch overflow under fallback fonts.
"""
from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

W = 900
MONO = "'Cascadia Code','JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif"
ACCENT, ACCENT2, TEXT, MUTED, BODY = "#39ff88", "#00d9ff", "#e9fff2", "#8baa95", "#c9e6d3"
MONO_W = 0.62  # generous per-character width estimate for monospace fallbacks
SANS_W = 0.5


def e(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def mono_w(text: str, size: float, spacing: float = 0.0) -> float:
    return len(text) * (size * MONO_W + spacing)


def wrap(text: str, size: float, width: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        cand = f"{cur} {word}".strip()
        if len(cand) * size * SANS_W > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def defs(uid: str, h: int) -> str:
    return f"""<defs>
    <linearGradient id="bg-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#03110a"/><stop offset="1" stop-color="#010604"/>
    </linearGradient>
    <radialGradient id="glow-g-{uid}" cx="0.12" cy="0" r="0.55">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0.14"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-c-{uid}" cx="0.92" cy="0.05" r="0.45">
      <stop offset="0" stop-color="{ACCENT2}" stop-opacity="0.10"/><stop offset="1" stop-color="{ACCENT2}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid-{uid}" width="42" height="42" patternUnits="userSpaceOnUse">
      <path d="M42 0H0V42" fill="none" stroke="{ACCENT}" stroke-opacity="0.045" stroke-width="1"/>
    </pattern>
    <pattern id="scan-{uid}" width="5" height="5" patternUnits="userSpaceOnUse">
      <rect width="5" height="1" fill="#ffffff" fill-opacity="0.012"/>
    </pattern>
    <clipPath id="clip-{uid}"><rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="18"/></clipPath>
  </defs>"""


def panel(uid: str, h: int) -> str:
    return f"""<g clip-path="url(#clip-{uid})">
    <rect width="{W}" height="{h}" fill="url(#bg-{uid})"/>
    <rect width="{W}" height="{h}" fill="url(#glow-g-{uid})"/>
    <rect width="{W}" height="{h}" fill="url(#glow-c-{uid})"/>
    <rect width="{W}" height="{h}" fill="url(#grid-{uid})"/>
    <rect width="{W}" height="{h}" fill="url(#scan-{uid})"/>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="18" fill="none" stroke="{ACCENT}" stroke-opacity="0.3"/>"""


def svg(h: int, title: str, body: str, style: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{e(title)}">
  <title>{e(title)}</title>
  <style>
    .mono {{ font-family: {MONO}; }}
    .sans {{ font-family: {SANS}; }}{style}
  </style>
{body}
</svg>
"""


def chip(x: float, y: float, text: str, *, size=12.5, fill="#39ff88", fill_op=0.075, stroke_op=0.17,
         color="#b9ffd2", pad=10, h=28, radius=9, brackets=False, max_x=W - 32) -> tuple[str, float]:
    """A rounded label; returns (svg, width). y is the top edge."""
    label = f"<{text}/>" if brackets else text
    w = mono_w(label, size) + 2 * pad
    base = y + h / 2 + size * 0.36
    if brackets:
        inner = (f'<tspan fill="{ACCENT2}">&lt;</tspan><tspan fill="{color}">{e(text)}</tspan>'
                 f'<tspan fill="{ACCENT2}">/&gt;</tspan>')
    else:
        inner = e(text)
    out = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{radius}" fill="#020a06"/>'
           f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{radius}" fill="{fill}" fill-opacity="{fill_op}" '
           f'stroke="{fill}" stroke-opacity="{stroke_op}"/>'
           f'<text class="mono" x="{x + pad:.1f}" y="{base:.1f}" font-size="{size}" fill="{color}" '
           f'data-max="{min(x + w, max_x):.1f}">{inner}</text>')
    return out, w


def flow_box(y: float, steps: list[str], label: str) -> tuple[str, float]:
    """Dashed cyan box with step chips and green arrows, wrapping as needed. Returns (svg, height)."""
    x0, x1, pad, gap, ch = 32, W - 32, 14, 8, 26
    items, x, row = [], x0 + pad, 0
    arrow_w = mono_w("→", 12.5)
    for i, step in enumerate(steps):
        w = mono_w(step, 12.5) + 16
        need = w + (arrow_w + 2 * gap if i < len(steps) - 1 else 0)
        if x + w > x1 - pad and x > x0 + pad:
            row += 1
            x = x0 + pad
        yy = y + pad + row * (ch + 10)
        c, cw = chip(x, yy, step, size=12.5, fill=ACCENT, fill_op=0.06, stroke_op=0.12, color=MUTED, pad=8, h=ch, radius=8,
                     max_x=x1 - pad)
        items.append(c)
        x += cw + gap
        if i < len(steps) - 1:
            items.append(f'<text class="mono" x="{x:.1f}" y="{yy + ch / 2 + 4.5:.1f}" font-size="12.5" fill="{ACCENT}">→</text>')
            x += arrow_w + gap
    h = 2 * pad + (row + 1) * ch + row * 10
    box = (f'<g aria-label="{e(label)}"><rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="12" fill="{ACCENT2}" '
           f'fill-opacity="0.045" stroke="{ACCENT2}" stroke-opacity="0.3" stroke-dasharray="5 4"/>' + "".join(items) + "</g>")
    return box, h


def tag_row(y: float, tags: list[str]) -> tuple[str, float]:
    x, row, out = 32.0, 0, []
    for t in tags:
        w = mono_w(f"<{t}/>", 12.5) + 20
        if x + w > W - 32 and x > 32:
            row += 1
            x = 32
        c, cw = chip(x, y + row * 38, t, brackets=True)
        out.append(c)
        x += cw + 8
    return "".join(out), (row + 1) * 28 + row * 10


# ---------------------------------------------------------------- header

def header() -> str:
    uid, h = "hdr", 372
    eyebrow = "SOFTWARE ENGINEERING · APPLIED AI · SECURITY OPERATIONS"
    ew = mono_w(eyebrow, 12, 0.5) + 28
    para = [
        "I’m Bill Lo, a software engineer with 4+ years of experience building enterprise",
        "applications and APIs. My current work combines production engineering, local AI",
        "systems, browser tooling, and hands-on security investigation.",
    ]
    body = [defs(uid, h), panel(uid, h)]
    body.append(f"""<g clip-path="url(#clip-{uid})">
    <rect x="0" y="0" width="{W}" height="36" fill="{ACCENT}" fill-opacity="0.08"/>
    <line x1="0" y1="36" x2="{W}" y2="36" stroke="{ACCENT}" stroke-opacity="0.18"/>
  </g>
  <text class="mono" x="18" y="23" font-size="12.5"><tspan fill="{MUTED}">● ● ● </tspan><tspan fill="{ACCENT}">terminal://bill-lo-ca/github</tspan></text>
  <rect x="36" y="58" width="{ew:.1f}" height="30" rx="15" fill="{ACCENT}" fill-opacity="0.09" stroke="{ACCENT}" stroke-opacity="0.22"/>
  <text class="mono" x="50" y="77.5" font-size="12" letter-spacing="0.5" fill="{ACCENT}" data-max="{36 + ew:.1f}">{e(eyebrow)}</text>
  <g filter="url(#h1glow)">
    <text class="mono" x="36" y="136" font-size="30" font-weight="700" letter-spacing="-1" fill="{TEXT}" data-max="{W - 36}">Building defensible software,</text>
    <text class="mono" x="36" y="176" font-size="30" font-weight="700" letter-spacing="-1" fill="{TEXT}" data-max="{W - 36}">local AI tools, and security workflows.</text>
  </g>""")
    for i, line in enumerate(para):
        body.append(f'  <text class="sans" x="36" y="{216 + i * 24}" font-size="15.5" fill="{BODY}" data-max="{W - 36}">{e(line)}</text>')
    body.append(f"""  <line x1="36" y1="290" x2="{W - 36}" y2="290" stroke="{ACCENT}" stroke-opacity="0.14"/>
  <text class="mono" x="36" y="316" font-size="13" data-max="{W - 36}"><tspan fill="{ACCENT2}">status: </tspan><tspan fill="{ACCENT}">open to SOC Analyst, Software Engineer, and AI / Automation roles</tspan></text>
  <text class="mono" x="36" y="342" font-size="13" data-max="{W - 36}"><tspan fill="{ACCENT2}">location: </tspan><tspan fill="{BODY}">Kanata, Ontario · open to relocation across Canada</tspan><tspan class="cursor" fill="{ACCENT}"> █</tspan></text>""")
    style = """
    .cursor { animation: blink 1.1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) { .cursor { animation: none; } }"""
    glow = """<defs><filter id="h1glow" x="-5%" y="-30%" width="110%" height="160%">
    <feGaussianBlur stdDeviation="7" result="b"/>
    <feColorMatrix in="b" type="matrix" values="0 0 0 0 0.22  0 0 0 0 1  0 0 0 0 0.53  0 0 0 0.35 0" result="g"/>
    <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter></defs>"""
    title = ("Bill Lo — Software Engineering, Applied AI, Security Operations. Building defensible software, local AI tools, "
             "and security workflows. Open to SOC Analyst, Software Engineer, and AI / Automation roles; Kanata, Ontario, "
             "open to relocation across Canada.")
    return svg(h, title, glow + "\n" + "\n".join(body), style)


# ---------------------------------------------------------------- buttons

def button(kind: str, label: str) -> str:
    size, pad, h = 14, 18, 44
    prefix = "$ " if kind == "primary" else "./"
    w = mono_w(prefix + label, size) + 2 * pad
    if kind == "primary":
        bg = f'<rect x="1" y="1" width="{w - 2:.1f}" height="{h - 2}" rx="12" fill="{ACCENT}"/>'
        txt = f'<tspan fill="#001b0a">{e(prefix + label)}</tspan>'
    else:
        bg = (f'<rect x="1" y="1" width="{w - 2:.1f}" height="{h - 2}" rx="12" fill="#03110a"/>'
              f'<rect x="1" y="1" width="{w - 2:.1f}" height="{h - 2}" rx="12" fill="{ACCENT2}" fill-opacity="0.08" '
              f'stroke="{ACCENT2}" stroke-opacity="0.35"/>')
        txt = f'<tspan fill="{ACCENT2}">./</tspan><tspan fill="#c8fbff">{e(label)}</tspan>'
    body = (bg + f'<text class="mono" x="{pad}" y="{h / 2 + 5:.1f}" font-size="{size}" font-weight="700" '
            f'data-max="{w - 4:.1f}">{txt}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.1f} {h}" role="img" '
            f'aria-label="{e(label)}"><title>{e(label)}</title><style>.mono {{ font-family: {MONO}; }}</style>{body}</svg>\n')


# ---------------------------------------------------------------- project / writeup cards

def card(uid: str, meta: str, name: str, status: str, summary: str, steps: list[str], flow_label: str,
         tags: list[str], title: str) -> str:
    parts = []
    y = 46
    sw = mono_w("● " + status, 12) + 22
    parts.append(f'<text class="mono" x="32" y="{y}" font-size="12" letter-spacing="0.6" fill="{ACCENT2}" '
                 f'data-max="{W - 32 - sw - 12:.1f}">{e(meta.upper())}</text>')
    parts.append(f'<rect x="{W - 32 - sw:.1f}" y="26" width="{sw:.1f}" height="30" rx="15" fill="{ACCENT}" fill-opacity="0.08" '
                 f'stroke="{ACCENT}" stroke-opacity="0.25"/>'
                 f'<text class="mono" x="{W - 32 - sw + 11:.1f}" y="45.5" font-size="12" font-weight="700" fill="{ACCENT}" '
                 f'data-max="{W - 32:.1f}">● {e(status)}</text>')
    prompt = "root@portfolio:~# "
    px = 32 + mono_w(prompt, 12)
    parts.append(f'<text class="mono" x="32" y="88" font-size="12" fill="{ACCENT2}">{prompt}</text>'
                 f'<text class="mono" x="{px:.1f}" y="88" font-size="26" font-weight="700" fill="{ACCENT}" '
                 f'data-max="{W - 32}">{e(name)}</text>')
    y = 124
    for line in wrap(summary, 15.5, W - 64 - 16):
        parts.append(f'<text class="sans" x="32" y="{y}" font-size="15.5" fill="{BODY}" data-max="{W - 32}">{e(line)}</text>')
        y += 25
    y += 4
    fb, fh = flow_box(y, steps, flow_label)
    parts.append(fb)
    y += fh + 16
    tr, th = tag_row(y, tags)
    parts.append(tr)
    h = int(y + th + 30)
    return svg(h, title, defs(uid, h) + "\n" + panel(uid, h) + "\n" + "\n".join(parts))


CARDS = {
    "project-2much2read": dict(
        meta="Featured · Local LLM Pipeline · Hardened Automation", name="2Much2Read", status="In daily personal use",
        summary=("A local-first pipeline that reads selected Gmail newsletters, extracts and ranks stories with three local "
                 "models, folds duplicate coverage together, and posts one daily digest to a private Discord channel. "
                 "Sandboxed systemd runtime, SSRF-safe link following, and weekly mutation testing."),
        steps=["Gmail / Hacker News", "Ollama Extract", "Reranker", "Review & Merge", "Discord Digest"],
        flow_label="2Much2Read digest pipeline",
        tags=["Python", "Ollama", "sentence-transformers", "Gmail API", "SQLite", "systemd", "Mutation Testing"]),
    "project-contextbubble": dict(
        meta="Featured · Chromium Extension · Local AI Backend", name="ContextBubble", status="Functional prototype",
        summary=("A Chromium extension that prepares timestamped learning notes for YouTube videos and displays reviewed "
                 "concept bubbles near the relevant playback moment, with caption-first ingestion and a local ASR fallback."),
        steps=["YouTube", "Captions / ASR", "Concept Agent", "Reviewer", "Bubble Overlay"],
        flow_label="ContextBubble data flow",
        tags=["Chromium Extension", "Python", "whisper.cpp", "Gemini", "Ollama", "Local Auth"]),
    "project-summerday": dict(
        meta="Featured · SvelteKit · FastAPI · Local LLM", name="SummerDay", status="Vertical slice implemented",
        summary=("A local-first French learning application that creates one short reading lesson and a focused vocabulary "
                 "set each day, with NLP suitability checks, structured generation, and TTS review gates."),
        steps=["Vikidia", "Stanza NLP", "Ollama", "TTS Review", "Published Lesson"],
        flow_label="SummerDay lesson pipeline",
        tags=["SvelteKit", "FastAPI", "Stanza NLP", "Ollama", "TTS", "pytest"]),
    "writeup-szechuan-sauce": dict(
        meta="Writeup · Digital Forensics · Incident Response", name="Stolen Szechuan Sauce", status="Published",
        summary=("A solo DFIR investigation of DFIR Madness Case 001: an RDP intrusion, malware persistence, lateral "
                 "movement, and data theft rebuilt across a Windows domain controller and desktop from disk images, "
                 "event logs, registry hives, and a packet capture."),
        steps=["RDP Brute Force", "Metasploit Service", "C2 over 443", "Secret.zip Exfiltration", "Pivot to Desktop"],
        flow_label="Reconstructed attack chain",
        tags=["FTK Imager", "Autopsy", "Wireshark", "Registry Explorer", "EvtxECmd", "MFTECmd", "Timeline Explorer"]),
}


# ---------------------------------------------------------------- skills matrix

SKILLS = [
    ("Software Engineering", "C#, ASP.NET/.NET, React, JavaScript, Python, FastAPI, REST APIs, JSON/XML integration, SQL, "
                             "production debugging, automated testing."),
    ("Applied AI", "Ollama, Gemini, structured generation, provider abstraction, local LLM workflows, whisper.cpp, ASR "
                   "fallback design, NLP pipelines, validation gates."),
    ("Security Operations", "Alert triage, Windows/Linux log analysis, timeline reconstruction, detection validation, "
                            "incident documentation, SIEM investigation workflows."),
    ("Systems & Delivery", "Linux, Windows Server, Git/GitHub, uv, pnpm, deployment configuration, environment management, "
                           "local services, API integration, technical documentation."),
]


def skills() -> str:
    gap, cw = 16, (W - 16) / 2
    wrapped = [wrap(t, 14, cw - 44 - 8) for _, t in SKILLS]
    rows = [max(len(wrapped[0]), len(wrapped[1])), max(len(wrapped[2]), len(wrapped[3]))]
    ch = [int(58 + n * 22 + 20) for n in rows]
    h = ch[0] + gap + ch[1]
    parts = []
    for i, (name, _) in enumerate(SKILLS):
        col, row = i % 2, i // 2
        x = col * (cw + gap)
        y = 0 if row == 0 else ch[0] + gap
        uid = f"sk{i}"
        hh = ch[row]
        parts.append(f"""<g transform="translate({x:.1f},{y})">
  <defs>
    <linearGradient id="bg-{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#03110a"/><stop offset="1" stop-color="#010604"/></linearGradient>
    <pattern id="grid-{uid}" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="{ACCENT}" stroke-opacity="0.045"/></pattern>
  </defs>
  <rect x="1" y="1" width="{cw - 2:.1f}" height="{hh - 2}" rx="18" fill="url(#bg-{uid})"/>
  <rect x="1" y="1" width="{cw - 2:.1f}" height="{hh - 2}" rx="18" fill="url(#grid-{uid})"/>
  <rect x="1" y="1" width="{cw - 2:.1f}" height="{hh - 2}" rx="18" fill="none" stroke="{ACCENT}" stroke-opacity="0.3"/>
  <text class="mono" x="22" y="40" font-size="15.5" font-weight="700" data-max="{x + cw - 20:.1f}"><tspan fill="{ACCENT}"># </tspan><tspan fill="{TEXT}">{e(name)}</tspan></text>""")
        for j, line in enumerate(wrapped[i]):
            parts.append(f'  <text class="sans" x="22" y="{70 + j * 22}" font-size="14" fill="{BODY}" data-max="{x + cw - 20:.1f}">{e(line)}</text>')
        parts.append("</g>")
    title = "Skills matrix. " + " ".join(f"{n}: {t}" for n, t in SKILLS)
    return svg(h, title, "\n".join(parts))


def main() -> None:
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    for name, label, kind in [("btn-portfolio", "bill-lo-ca.github.io", "primary"), ("btn-linkedin", "LinkedIn", "secondary"),
                              ("btn-medium", "Medium", "secondary"), ("btn-htb", "HackTheBox", "secondary")]:
        (OUT / f"{name}.svg").write_text(button(kind, label), encoding="utf-8")
    for name, spec in CARDS.items():
        title = f"{spec['name']}: {spec['summary']} Flow: {' → '.join(spec['steps'])}. Tags: {', '.join(spec['tags'])}."
        (OUT / f"{name}.svg").write_text(card(name, title=title, **spec), encoding="utf-8")
    (OUT / "skills.svg").write_text(skills(), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.iterdir()))


main()

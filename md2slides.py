#!/usr/bin/env python3
"""Build a self-contained HTML slide deck from Markdown.

Usage:
    python md2slides.py slides.md
    python md2slides.py slides.md -o presentation.html

The input Markdown is intentionally small and presentation-oriented.
No external libraries are required.
"""

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
from pathlib import Path

BREAK = "<!-- slide -->"


def fence_info(line: str) -> tuple[int, str] | None:
    """Return (fence_length, language) for a fenced code delimiter."""
    match = re.match(r"^\s*(`{3,})(?:\s*(.*))?$", line)
    if not match:
        return None

    fence_length = len(match.group(1))
    language = (match.group(2) or "").strip()

    return fence_length, language


def embed_image(path: Path) -> str:
    """Return an image as a self-contained data URL."""
    if not path.exists():
        raise ValueError(f"Image not found: {path}")

    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported image type: {path}")

    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{data}"


def inline(text: str, asset_root: Path | None = None) -> str:
    """Render a small subset of inline Markdown."""

    image_html: list[str] = []

    def replace_image(match: re.Match[str]) -> str:
        alt = html.escape(match.group(1), quote=True)
        src = match.group(2)
        title = match.group(3)
        attrs = match.group(4) or ""

        if asset_root is not None:
            image_path = (asset_root / src).resolve()
            src = embed_image(image_path)

        src = html.escape(src, quote=True)

        title_attr = (
            f' title="{html.escape(title, quote=True)}"'
            if title
            else ""
        )

        class_name = ""
        class_match = re.fullmatch(
            r"\s*\{\.([A-Za-z0-9_-]+)\}\s*",
            attrs,
        )

        if class_match:
            class_name = f' class="{class_match.group(1)}"'

        image_html.append(
            f'<img src="{src}" alt="{alt}"'
            f'{class_name}{title_attr}>'
        )

        return f"\x00IMG{len(image_html) - 1}\x00"

    # Extract images before escaping the rest of the text.
    text = re.sub(
        r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)(\s*\{[^}]+\})?',
        replace_image,
        text,
    )

    # Escape normal text.
    text = html.escape(text, quote=False)

    # Code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Links
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )

    # Restore image HTML after escaping.
    for i, image in enumerate(image_html):
        text = text.replace(f"\x00IMG{i}\x00", image)

    return text


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|[\s:\-|]+\|", line.strip()))


def render(lines: list[str], asset_root: Path | None = None) -> str:
    """Render a small, safe subset of Markdown as HTML."""
    out: list[str] = []
    i = 0

    while i < len(lines):
        text = lines[i].strip()

        if not text or text == "---":
            i += 1
            continue

        # Fenced code block
        fence = fence_info(text)
        if fence:
            fence_length, language = fence
            i += 1
            code_lines: list[str] = []

            while i < len(lines):
                closing_fence = fence_info(lines[i])

                if closing_fence and closing_fence[0] >= fence_length:
                    i += 1
                    break

                code_lines.append(lines[i])
                i += 1

            lang_class = (
                f' class="language-{html.escape(language.split()[0], quote=True)}"'
                if language
                else ""
            )

            code = html.escape("\n".join(code_lines), quote=False)
            out.append(f"<pre><code{lang_class}>{code}</code></pre>")
            continue

        # Table
        if text.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            head = [inline(c, asset_root) for c in split_row(lines[i])]
            i += 2
            body: list[list[str]] = []

            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([inline(c, asset_root) for c in split_row(lines[i])])
                i += 1

            out.append("<table><thead><tr>")
            out.extend(f"<th>{c}</th>" for c in head)
            out.append("</tr></thead><tbody>")

            for row in body:
                out.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")

            out.append("</tbody></table>")
            continue

        # Headings
        if text.startswith("### "):
            out.append(f"<h3>{inline(text[4:], asset_root)}</h3>")
        elif text.startswith("## "):
            out.append(f"<h2>{inline(text[3:], asset_root)}</h2>")
        elif text.startswith("# "):
            out.append(f"<h1>{inline(text[2:], asset_root)}</h1>")

        # Blockquote
        elif text.startswith("> "):
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + "<br>".join(inline(q, asset_root) for q in quote) + "</blockquote>")
            continue

        # Ordered list
        elif re.match(r"^\d+\.\s", text):
            items: list[str] = []
            while i < len(lines):
                match = re.match(r"^\d+\.\s+(.+)", lines[i].strip())
                if not match:
                    break
                items.append(inline(match.group(1), asset_root))
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue

        # Unordered list
        elif text.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(inline(lines[i].strip()[2:], asset_root))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue

        # Paragraph
        else:
            out.append(f"<p>{inline(text, asset_root)}</p>")

        i += 1

    return "\n".join(out)


def split_slides(text: str) -> list[list[str]]:
    """Split Markdown into slides while respecting fenced code blocks."""
    slides: list[list[str]] = []
    current: list[str] | None = None
    fence_length: int | None = None

    for line in text.lstrip("\ufeff").splitlines():
        stripped = line.strip()
        fence = fence_info(line)

        # Inside a fenced code block.
        if fence_length is not None:
            if fence and fence[0] >= fence_length:
                fence_length = None

            if current is None:
                current = []

            current.append(line)
            continue

        # Opening fenced code block.
        if fence:
            fence_length = fence[0]

            if current is None:
                current = []

            current.append(line)
            continue

        # Explicit slide break.
        if stripped == BREAK:
            if current and any(item.strip() for item in current):
                slides.append(current)
            current = []
            continue

        # Heading starts a new slide.
        if line.startswith(("# ", "## ")):
            if current and any(item.strip() for item in current):
                slides.append(current)
            current = [line]
            continue

        if current is None:
            current = [line]
        else:
            current.append(line)

    if current and any(item.strip() for item in current):
        slides.append(current)

    return slides


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Markdown Slides</title>
<style>
  :root {
    --bg: #14161a;
    --fg: #e8eaed;
    --muted: #9aa0a6;
    --accent: #6ea8fe;
    --line: #2b2f36;
    --card: #1c1f25;
  }

  body.light {
    --bg: #fbfbfd;
    --fg: #1a1c20;
    --muted: #5f6672;
    --accent: #1a56db;
    --line: #e2e5ea;
    --card: #ffffff;
  }

  * { box-sizing: border-box; }

  html, body {
    height: 100%;
    margin: 0;
  }

  body {
    background: var(--bg);
    color: var(--fg);
    font: 17px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI",
      Roboto, Helvetica, Arial, sans-serif;
    overflow: hidden;
  }

  #deck { height: 100vh; }

  .slide {
    display: none;
    position: absolute;
    inset: 0;
    padding: 56px 64px 72px;
    overflow-y: auto;
  }

  .slide.on { display: block; }

  .slide > div {
    max-width: 1080px;
    margin: 0 auto;
  }
  
  .slide img {
    display: block;
    max-width: 100%;
    max-height: 60vh;
    object-fit: contain;
  }
    
  .slide img.qr {
    width: 220px;
    height: 220px;
    padding: 14px;
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, .25);
  }
  
  .slide table img.qr {
    width: 180px;
    height: 180px;
    margin: 12px auto 0;
  }
    
  .slide table th,
  .slide table td {
    text-align: center;
    vertical-align: middle;
  }

  h1 {
    font-size: 42px;
    line-height: 1.15;
    margin: 0 0 28px;
    letter-spacing: -0.5px;
  }

  h2 {
    font-size: 32px;
    margin: 0 0 26px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--line);
  }

  h3 {
    font-size: 21px;
    margin: 30px 0 10px;
    color: var(--accent);
  }

  h3:first-child { margin-top: 0; }

  p {
    margin: 0 0 14px;
    color: var(--muted);
  }

  h1 + p, .slide p strong { color: var(--fg); }

  ul, ol {
    margin: 0 0 16px;
    padding-left: 24px;
  }

  li { margin: 0 0 9px; }

  li strong { color: var(--fg); }

  code {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.9em;
    font-family: "Cascadia Mono", Consolas, monospace;
  }

  pre {
    margin: 0 0 20px;
    padding: 16px 18px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow-x: auto;
    white-space: pre;
    tab-size: 2;
    box-shadow: 0 2px 12px rgba(0, 0, 0, .12);
  }

  pre code {
    display: block;
    padding: 0;
    border: 0;
    background: transparent;
    border-radius: 0;
    color: var(--fg);
    font-size: 14px;
    line-height: 1.55;
    white-space: pre;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 0 18px;
    font-size: 15.5px;
  }

  th, td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--line);
    vertical-align: top;
  }

  th {
    color: var(--muted);
    font-weight: 600;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }

  blockquote {
    border-left: 3px solid var(--accent);
    padding-left: 16px;
    color: var(--muted);
    margin: 0 0 16px;
  }

  a { color: var(--accent); }

  #bar {
    position: fixed;
    left: 0;
    top: 0;
    height: 3px;
    background: var(--accent);
    transition: width .18s;
  }

  #foot {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 22px;
    color: var(--muted);
    font-size: 13.5px;
    background: linear-gradient(to top, var(--bg) 60%, transparent);
  }

  #foot kbd, #ov kbd {
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 1px 6px;
    font: inherit;
    font-size: 12.5px;
    color: var(--fg);
  }

  #ov {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 20;
    overflow-y: auto;
    background: var(--bg);
    padding: 40px;
    cursor: default;
  }

  #ov.on { display: block; }

  #ov h4 {
    margin: 0 0 22px;
    font-size: 15px;
    color: var(--muted);
    font-weight: 600;
  }

  #grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    gap: 14px;
  }

  .thumb {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 15px;
    min-height: 74px;
    color: var(--fg);
    cursor: pointer;
  }

  .thumb:hover { border-color: var(--accent); }

  .thumb small {
    display: block;
    color: var(--muted);
    font-size: 12.5px;
    margin-bottom: 6px;
  }

  @media print {
    body { overflow: visible; }

    .slide {
      display: block !important;
      position: static;
      page-break-after: always;
      padding: 24px;
    }

    #foot, #bar, #ov { display: none; }
  }

  @media (max-width: 700px) {
    .slide { padding: 36px 24px 68px; }
    h1 { font-size: 34px; }
    h2 { font-size: 27px; }
    #foot span:first-child { display: none; }
  }
</style>
</head>
<body>
<div id="bar"></div>

<main id="deck">
__SLIDES__
</main>

<div id="foot">
  <span>
    <kbd>←</kbd> <kbd>→</kbd> navigate
    &nbsp;·&nbsp; <kbd>O</kbd> overview
    &nbsp;·&nbsp; <kbd>F</kbd> fullscreen
    &nbsp;·&nbsp; <kbd>D</kbd> theme
  </span>
  <span id="counter"></span>
</div>

<div id="ov">
  <h4>Slide overview — click a slide, <kbd>Esc</kbd> to close</h4>
  <div id="grid"></div>
</div>

<script>
  const slides = [...document.querySelectorAll('.slide')];
  const bar = document.getElementById('bar');
  const counter = document.getElementById('counter');
  const grid = document.getElementById('grid');
  const ov = document.getElementById('ov');
  let cur = 0;

  slides.forEach((s, i) => {
    const h = s.querySelector('h1, h2, h3');
    const t = document.createElement('div');
    t.className = 'thumb';
    t.innerHTML =
      '<small>Slide ' + (i + 1) + '</small>' +
      (h ? h.textContent : 'Untitled slide');

    t.onclick = () => {
      show(i);
      toggle(false);
    };

    grid.appendChild(t);
  });

  function show(n) {
    cur = Math.max(0, Math.min(slides.length - 1, n));

    slides.forEach((s, i) => s.classList.toggle('on', i === cur));

    slides[cur].scrollTop = 0;
    bar.style.width = ((cur + 1) / slides.length * 100) + '%';
    counter.textContent = (cur + 1) + ' / ' + slides.length;
  }

  function toggle(on) {
    ov.classList.toggle(
      'on',
      on === undefined ? !ov.classList.contains('on') : on
    );
  }

  document.addEventListener('keydown', (e) => {
    const k = e.key;

    if (k === 'Escape') return toggle(false);

    if (['o', 'O', 'щ', 'Щ'].includes(k)) return toggle();

    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'n'].includes(k)) {
      show(cur + 1);
      e.preventDefault();
    } else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'p'].includes(k)) {
      show(cur - 1);
      e.preventDefault();
    } else if (k === 'Home') {
      show(0);
    } else if (k === 'End') {
      show(slides.length - 1);
    } else if (['f', 'F', 'а', 'А'].includes(k)) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        document.documentElement.requestFullscreen();
      }
    } else if (['d', 'D', 'в', 'В'].includes(k)) {
      document.body.classList.toggle('light');
    }
  });

  show(0);
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a self-contained HTML slide deck from Markdown."
    )
    parser.add_argument("source", type=Path, help="input Markdown file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output HTML file; defaults to <source>.html",
    )
    args = parser.parse_args()

    source = args.source.resolve()

    if not source.exists():
        raise SystemExit(f"Input file not found: {source}")

    output = args.output.resolve() if args.output else source.with_suffix(".html")

    slides = split_slides(source.read_text(encoding="utf-8"))

    if not slides:
        raise SystemExit("No slides found.")

    body = "\n".join(
        f'<section class="slide"><div>{render(block, source.parent)}</div></section>'
        for block in slides
    )

    output.write_text(
        TEMPLATE.replace("__SLIDES__", body),
        encoding="utf-8",
    )

    print(f"Slides: {len(slides)}")
    print(f"Written: {output}")


if __name__ == "__main__":
    main()

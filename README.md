# md2slides

A tiny, dependency-free Markdown → HTML presentation generator.

Write slides in Markdown, run one Python command, and get a self-contained HTML presentation.

## Why?

Sometimes a presentation is already mostly text.

Instead of maintaining a presentation file in a GUI editor, this project lets you keep the source as plain Markdown:

```text
slides.md
    ↓
md2slides.py
    ↓
slides.html
```

The generated HTML contains its own CSS and JavaScript, so it does not need a server or external libraries to run.

## Requirements

- Python 3.9+
- a web browser

No third-party Python packages are required.

## Usage

```bash
python md2slides.py slides.md
```

This creates:

```text
slides.html
```

Or choose the output path explicitly:

```bash
python md2slides.py slides.md -o presentation.html
```

Then open the generated HTML file in a browser.

## Markdown format

A heading starts a new slide:

```markdown
## The idea

This is the content of the slide.
```

You can also explicitly start a slide:

```markdown
<!-- slide -->
```

Supported Markdown features:

- `#`, `##`, `###` headings
- unordered lists
- ordered lists
- tables
- fenced code blocks
- blockquotes
- **bold text**
- `inline code`
- links

The parser is intentionally small. It is designed for presentation-oriented Markdown, not as a complete CommonMark implementation.

## Controls

| Key | Action |
|---|---|
| `←` / `→` | Previous / next slide |
| `O` | Slide overview |
| `Esc` | Close overview |
| `F` | Fullscreen |
| `D` | Toggle light/dark theme |
| `Home` | First slide |
| `End` | Last slide |

Mouse clicks also navigate between slides.

## Project structure

```text
md2slides/
├── md2slides.py
├── video-slides.md
├── README.md
├── LICENSE
└── .gitignore
```

`video-slides.md` is also an example deck and can be used as a starting point.

## Design goals

The project intentionally prefers:

1. **Plain text** — the source is easy to read and edit.
2. **No dependencies** — only Python's standard library.
3. **One output file** — the HTML is self-contained.
4. **Small codebase** — easy to understand and modify.
5. **Git-friendly source** — presentation changes are ordinary text diffs.

## Limitations

This is a deliberately small renderer, not a full Markdown engine.

For complex documents, use a proper Markdown parser or a dedicated presentation framework.

## License

MIT. See `LICENSE`.

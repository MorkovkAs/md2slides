# Markdown → HTML slides

**A tiny presentation tool made from one Python file.**

<!-- slide -->

## The problem

Presentation software is great.

But sometimes I just want to write:

- a Markdown file
- a few headings
- some bullets
- maybe a table

…and get a presentation.

No PowerPoint.
No framework.
No build system.

Just a file I can edit with a text editor.

<!-- slide -->

## The idea

**Markdown is already a structured document.**

So let's use that structure as our presentation format.

````text
slides.md
    ↓
md2slides.py
    ↓
slides.html
````

The result is a completely self-contained HTML file.

<!-- slide -->

## And this presentation is the demo

There is no separate slide editor behind this.

These slides came from the Markdown file you're looking at in the repository.

The source is just text.

The presentation is generated from it.

> Edit the Markdown. Run the script. Open the HTML.

<!-- slide -->

## The whole interface

The generated presentation has only a few things:

- `←` / `→` to navigate
- `O` for a slide overview
- `F` for fullscreen
- `D` to switch theme
- mouse clicks to move between slides

And because the output is HTML, there is nothing to install to view it.

<!-- slide -->

## The command

````text
python md2slides.py video-slides.md
````

That's the entire build step.

It creates:

````text
video-slides.html
````

You can open that file directly in a browser.

<!-- slide -->

## The Markdown is the source of truth

A slide can be as simple as:

````markdown
## The idea

Markdown is already structured.

- headings
- lists
- tables
- quotes
- inline code
````

The script turns these blocks into HTML.

The important part is not the syntax.

**The important part is that the source stays human-readable.**

<!-- slide -->

# Looking for a Senior Systems Analyst

**To join my team.**

Someone strong who enjoys digging into complex systems,
asking the right questions, and turning chaos into clear solutions.

### Want to talk?

| **My Telegram** | **My Telegram channel** |
| --- | --- |
| **[@MorkovkA_57](https://t.me/MorkovkA_57)** | **[@oko_arch](https://t.me/oko_arch)** |
| ![QR code](assets/qr.png){.qr} | ![QR code](assets/qr_channel.png){.qr} |

## How slides are separated

There are two simple rules.

### A heading starts a slide

````markdown
## A new slide

Content goes here.
````

### Or use an explicit marker

````markdown
<!-- slide -->
````

This lets you split a slide without adding a heading.

That's it.

<!-- slide -->

## What the Python actually does

The script has three main jobs:

| Step | What happens |
|---|---|
| 1 | Read the Markdown |
| 2 | Split it into slide-sized blocks |
| 3 | Render those blocks into one HTML file |

The browser handles the rest.

Navigation, fullscreen, theme and overview are all JavaScript in the generated file.

<!-- slide -->

## No dependencies

The generator uses only Python's standard library:

````python
import argparse
import html
import re
from pathlib import Path
````

No package manager.

No virtual environment.

No JavaScript build chain.

No server.

That is intentional.

<!-- slide -->

## Why HTML?

Because HTML is a surprisingly good presentation format.

The browser already gives us:

- typography
- scrolling
- fullscreen
- printing
- links
- JavaScript
- cross-platform rendering

So instead of building a presentation engine…

**we can build a tiny layer on top of the browser.**

<!-- slide -->

## The output is self-contained

The generated HTML contains:

- the slide content
- the CSS
- the JavaScript

There are no external assets required.

You can copy the HTML file somewhere else and it still works.

<!-- slide -->

## A tiny parser is enough

This is not trying to implement all of Markdown.

It supports the things that are useful for slides:

- `#`, `##`, `###` headings
- unordered lists
- ordered lists
- tables
- blockquotes
- bold text
- inline code
- links

Keeping the scope small makes the project easy to understand.

<!-- slide -->

## Where this becomes useful

I originally made this kind of presentation for a practical conversation.

And that's where I think the format gets interesting.

A slide deck can be:

- a meeting brief
- a project proposal
- a technical demo
- a decision document
- a workshop outline
- a talk
- a README-like presentation

The source remains editable text.

<!-- slide -->

## Text first, presentation second

Traditional workflow:

````text
open presentation software
→ create slides
→ format things
→ rearrange objects
→ export
````

This workflow:

````text
write Markdown
→ run one command
→ open HTML
````

The second one is especially nice when the content matters more than visual editing.

<!-- slide -->

## And Git likes this

Markdown is plain text.

That means it works naturally with Git:

````text
git diff
git log
git blame
git merge
````

You can review changes to a presentation like changes to code or documentation.

That's a pretty useful property.

<!-- slide -->

## The project

The repository is deliberately small:

````text
md2slides/
├── md2slides.py
├── video-slides.md
├── README.md
├── LICENSE
└── .gitignore
````

Clone it.

Create a Markdown file.

Run the script.

Open the HTML.

<!-- slide -->

## The point

This is not a replacement for PowerPoint.

It's a different trade-off.

**If your presentation is already text, why not keep it as text?**

One Markdown file.

One Python script.

One self-contained HTML presentation.

<!-- slide -->

# Try it

Get the project from GitHub.

Create your own `slides.md`.

Run:

````text
python md2slides.py slides.md
````

Then open:

````text
slides.html
````

And if you improve the idea, send a pull request.

**Let's see how far a tiny script can go.**

# One More Thing

### I'm looking for a Senior Systems Analyst to join my team.

| **My Telegram** | **My Telegram channel** |
| --- | --- |
| **[@MorkovkA_57](https://t.me/MorkovkA_57)** | **[@oko_arch](https://t.me/oko_arch)** |
| ![QR code](assets/qr.png){.qr} | ![QR code](assets/qr_channel.png){.qr} |
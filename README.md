# kindle-wallp → `kwallp`

Resize images to perfect-fitting e-reader screensavers and wallpapers. Supports **25 devices** across Kindle, Kobo, reMarkable, Boox, Nook and PocketBook.

Powered by `Pillow` (`ImageOps.fit` + `LANCZOS`) and `uv`. Single terminal command `kwallp` handles a single image or a folder with nested subfolders, preserves original filenames, and keeps color or converts to grayscale on demand.

## Features

- **25 models** with exact panel resolutions (from [E-Reader Screensaver](https://e-reader-screensaver.com) data):
  - `1072×1448` — Kindle 11th Gen, Paperwhite 10th Gen, Kobo Clara series, Nook GlowLight 4
  - `1264×1680` — Kindle Paperwhite 12th Gen / Colorsoft / Oasis 3rd Gen, Kobo Libra, Boox Page, PocketBook Era
  - `1236×1648` — Kindle Paperwhite 11th Gen
  - `1404×1872` — Kobo Elipsa 2E, reMarkable 2, Boox Note Air/Tab Ultra, PocketBook InkPad 4
  - `758×1024` — Kobo Nia, Nook GlowLight 4e
  - `1440×1920` — Kobo Sage
  - `1860×2480` — Kindle Scribe
  - `824×1648` — Boox Palma
  - `1620×2160` — reMarkable Paper Pro
- Recursive folder support (`rglob`) — `input/a/b.jpg` → `output/a/b.png`
- Preserves original name (`photo.jpg` → `photo.png`, not `0.png`)
- Grayscale or color output (prompted if not flagged)
- Clean output mode, explicit file targets, pure `argparse` (no extra deps)

## Installation

Requires Python `>=3.13` and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone <repo> && cd kindle-wallp
uv sync              # creates .venv and installs kwallp entry point
# or install globally
uv tool install .
```

After `uv sync`, `kwallp` is available via:

```bash
uv run kwallp --help
# after uv tool install:
kwallp --help
```

## Usage

```
usage: kwallp [-h] [-m MODEL] [-o OUTPUT] [--grayscale | --no-grayscale] [--clean] [--list-models] [path]

Resize images for e-reader screensavers (Kindle, Kobo, Boox, etc.)

positional arguments:
  path                  image file or folder of images (recursive)

options:
  -h, --help            show this help message and exit
  -m, --model MODEL     e-reader model slug (see --list-models)
  -o, --output OUTPUT   output file or directory (default: ./output)
  --grayscale           convert to grayscale
  --no-grayscale        keep color
  --clean               clean output directory before processing
  --list-models         list all supported models and exit
```

### Examples

```bash
# List all 25 models
kwallp --list-models
uv run kwallp --list-models

# Single image → Kindle Scribe (1860×2480), grayscale
kwallp input/photo.jpg -m kindle-scribe --grayscale -o output/

# Folder (nested) → Kobo Nia (758×1024), keep color, clean output
kwallp input/ -m kobo-nia --no-grayscale -o output/ --clean

# Interactive: prompts for model + grayscale if -m / --grayscale not given
kwallp input/photo.jpg -o output/
kwallp input/ -o output/

# Explicit output file
kwallp input/photo.jpg -m boox-palma --grayscale -o /tmp/out.png

# Nested folders preserve structure and original names
# input/a/b.jpg → output/a/b.png
# input/sub/deep/c.jpg → output/sub/deep/c.png
kwallp input/ -m remarkable-paper-pro --grayscale -o output/
```

If `-m` is omitted, `kwallp` prints a numbered table and accepts either a number `1-25` or a slug:

```
Available e-reader models:
  1. boox-note-air                  1404x1872       Boox Note Air Series (Boox)
  5. kindle-11th-gen                1072x1448       Kindle (11th Gen) (Amazon)
  ...
Select model [1-25 or slug]: 11
Selected: Kindle Scribe (Amazon) - 1860x2480 [kindle-scribe]
Convert to grayscale for e-ink? [Y/n]: y
```

If neither `--grayscale` nor `--no-grayscale` is given, `kwallp` prompts `Convert to grayscale for e-ink? [Y/n]`.

## Supported Models

| Slug | Size | Device | Brand |
|------|------|--------|-------|
| `boox-note-air` | 1404×1872 | Boox Note Air Series | Boox |
| `boox-page` | 1264×1680 | Boox Page | Boox |
| `boox-palma` | 824×1648 | Boox Palma | Boox |
| `boox-tab-ultra` | 1404×1872 | Boox Tab Ultra Series | Boox |
| `kindle-11th-gen` | 1072×1448 | Kindle (11th Gen) | Amazon |
| `kindle-colorsoft` | 1264×1680 | Kindle Colorsoft | Amazon |
| `kindle-oasis-3rd-gen` | 1264×1680 | Kindle Oasis (3rd Gen) | Amazon |
| `kindle-paperwhite-10th-gen` | 1072×1448 | Kindle Paperwhite (10th Gen) | Amazon |
| `kindle-paperwhite-11th-gen` | 1236×1648 | Kindle Paperwhite (11th Gen) | Amazon |
| `kindle-paperwhite-12th-gen` | 1264×1680 | Kindle Paperwhite (12th Gen) | Amazon |
| `kindle-scribe` | 1860×2480 | Kindle Scribe | Amazon |
| `kobo-clara-2e` | 1072×1448 | Kobo Clara 2E / Clara HD | Kobo |
| `kobo-clara-bw` | 1072×1448 | Kobo Clara BW | Kobo |
| `kobo-clara-colour` | 1072×1448 | Kobo Clara Colour | Kobo |
| `kobo-elipsa-2e` | 1404×1872 | Kobo Elipsa 2E | Kobo |
| `kobo-libra-2` | 1264×1680 | Kobo Libra 2 / Libra H2O | Kobo |
| `kobo-libra-colour` | 1264×1680 | Kobo Libra Colour | Kobo |
| `kobo-nia` | 758×1024 | Kobo Nia | Kobo |
| `kobo-sage` | 1440×1920 | Kobo Sage | Kobo |
| `nook-glowlight-4` | 1072×1448 | Nook GlowLight 4 | B&N |
| `nook-glowlight-4e` | 758×1024 | Nook GlowLight 4e | B&N |
| `pocketbook-era` | 1264×1680 | PocketBook Era | PocketBook |
| `pocketbook-inkpad-4` | 1404×1872 | PocketBook InkPad 4 / Color 3 | PocketBook |
| `remarkable-2` | 1404×1872 | reMarkable 2 | reMarkable |
| `remarkable-paper-pro` | 1620×2160 | reMarkable Paper Pro | reMarkable |

Run `kwallp --list-models` for the current table.

## Development

```bash
uv sync --group dev
uv run ruff check --fix
uv run ruff format
uv run kwallp --help
```

- Lint/format: `ruff` (`dev` dependency-group in `pyproject.toml:22`)
- Image handling: `Pillow==12.3.0` (`main.py:6` uses `ImageOps.fit(..., LANCZOS)`)
- Entry point: `[project.scripts] kwallp = "main:main"` (`pyproject.toml:12`)

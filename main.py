import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}

# All 25 e-readers from output.md:29-54
E_READERS: dict[str, tuple[tuple[int, int], str, str]] = {
    # Kindle (7)
    "kindle-11th-gen": ((1072, 1448), "Kindle (11th Gen)", "Amazon"),
    "kindle-paperwhite-12th-gen": (
        (1264, 1680),
        "Kindle Paperwhite (12th Gen)",
        "Amazon",
    ),
    "kindle-paperwhite-11th-gen": (
        (1236, 1648),
        "Kindle Paperwhite (11th Gen)",
        "Amazon",
    ),
    "kindle-paperwhite-10th-gen": (
        (1072, 1448),
        "Kindle Paperwhite (10th Gen)",
        "Amazon",
    ),
    "kindle-oasis-3rd-gen": ((1264, 1680), "Kindle Oasis (3rd Gen)", "Amazon"),
    "kindle-scribe": ((1860, 2480), "Kindle Scribe", "Amazon"),
    "kindle-colorsoft": ((1264, 1680), "Kindle Colorsoft", "Amazon"),
    # Kobo (8)
    "kobo-nia": ((758, 1024), "Kobo Nia", "Kobo"),
    "kobo-clara-bw": ((1072, 1448), "Kobo Clara BW", "Kobo"),
    "kobo-clara-2e": ((1072, 1448), "Kobo Clara 2E / Clara HD", "Kobo"),
    "kobo-clara-colour": ((1072, 1448), "Kobo Clara Colour", "Kobo"),
    "kobo-libra-2": ((1264, 1680), "Kobo Libra 2 / Libra H2O", "Kobo"),
    "kobo-libra-colour": ((1264, 1680), "Kobo Libra Colour", "Kobo"),
    "kobo-sage": ((1440, 1920), "Kobo Sage", "Kobo"),
    "kobo-elipsa-2e": ((1404, 1872), "Kobo Elipsa 2E", "Kobo"),
    # reMarkable (2)
    "remarkable-2": ((1404, 1872), "reMarkable 2", "reMarkable"),
    "remarkable-paper-pro": ((1620, 2160), "reMarkable Paper Pro", "reMarkable"),
    # Boox (4)
    "boox-palma": ((824, 1648), "Boox Palma", "Boox"),
    "boox-page": ((1264, 1680), "Boox Page", "Boox"),
    "boox-note-air": ((1404, 1872), "Boox Note Air Series", "Boox"),
    "boox-tab-ultra": ((1404, 1872), "Boox Tab Ultra Series", "Boox"),
    # Others
    "nook-glowlight-4": ((1072, 1448), "Nook GlowLight 4", "B&N"),
    "nook-glowlight-4e": ((758, 1024), "Nook GlowLight 4e", "B&N"),
    "pocketbook-era": ((1264, 1680), "PocketBook Era", "PocketBook"),
    "pocketbook-inkpad-4": (
        (1404, 1872),
        "PocketBook InkPad 4 / Color 3",
        "PocketBook",
    ),
}


def clean_output(output: Path) -> None:
    if not output.exists():
        return
    for item in output.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def convert_image(src: Path, dst: Path, size: tuple[int, int], grayscale: bool) -> None:
    with Image.open(src) as img:
        img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
        if grayscale:
            img = img.convert("L")
        else:
            # preserve color; ensure RGB for PNG consistency
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(dst, format="PNG")


def prompt_model() -> str:
    sorted_models = sorted(E_READERS.items(), key=lambda x: x[0])
    print("Available e-reader models:")
    print(f"{'#':>3}  {'Slug':30s} {'Size':14s} {'Device'}")
    print("-" * 80)
    for i, (slug, ((w, h), name, brand)) in enumerate(sorted_models, 1):
        print(f"{i:3d}. {slug:30s} {w}x{h:<10d} {name} ({brand})")
    print()
    while True:
        raw = input("Select model [1-25 or slug]: ").strip()
        if not raw:
            continue
        # numeric selection
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(sorted_models):
                return sorted_models[idx - 1][0]
            print(f"Please enter 1-{len(sorted_models)}")
            continue
        # slug selection
        slug = raw.lower()
        if slug in E_READERS:
            return slug
        print(f"Unknown model '{raw}'. Try number or slug from list.")


def prompt_grayscale() -> bool:
    while True:
        raw = input("Convert to grayscale for e-ink? [Y/n]: ").strip().lower()
        if raw in ("", "y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer y or n.")


def list_models() -> None:
    print(f"{'Slug':30s} {'Size':14s} {'Device':30s} Brand")
    print("-" * 90)
    for slug, ((w, h), name, brand) in sorted(E_READERS.items()):
        print(f"{slug:30s} {w}x{h:<10d} {name:30s} {brand}")


def process_path(
    input_path: Path, output_root: Path, size: tuple[int, int], grayscale: bool
) -> int:
    count = 0
    if input_path.is_file():
        if input_path.suffix.lower() not in IMAGE_EXTS:
            print(
                f"Error: {input_path} is not a supported image {sorted(IMAGE_EXTS)}",
                file=sys.stderr,
            )
            sys.exit(1)
        dst = output_root / f"{input_path.stem}.png"
        convert_image(input_path, dst, size, grayscale)
        print(
            f"  {input_path} -> {dst} [{size[0]}x{size[1]}]{' grayscale' if grayscale else ''}"
        )
        count = 1
    else:
        # recursive rglob, preserve relative structure and original name
        found = False
        for src in input_path.rglob("*"):
            if src.is_file() and src.suffix.lower() in IMAGE_EXTS:
                found = True
                rel = src.relative_to(input_path)
                dst = output_root / rel.with_suffix(".png")
                convert_image(src, dst, size, grayscale)
                print(f"  {src} -> {dst}")
                count += 1
        if not found:
            print(
                f"No images found in {input_path} (recursive search, exts: {sorted(IMAGE_EXTS)})",
                file=sys.stderr,
            )
            sys.exit(1)
    return count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kwallp",
        description="Resize images for e-reader screensavers (Kindle, Kobo, Boox, etc.)",
        epilog="Example: kwallp input/ -m kindle-scribe -o output/ --grayscale",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="image file or folder of images (recursive)",
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=sorted(E_READERS.keys()),
        help="e-reader model slug (see --list-models)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output"),
        help="output file or directory (default: ./output)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--grayscale", action="store_true", default=None, help="convert to grayscale"
    )
    group.add_argument("--no-grayscale", action="store_true", help="keep color")
    parser.add_argument(
        "--clean", action="store_true", help="clean output directory before processing"
    )
    parser.add_argument(
        "--list-models", action="store_true", help="list all supported models and exit"
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_models:
        list_models()
        return

    if args.path is None:
        parser.print_usage(sys.stderr)
        print(
            "error: the following arguments are required: path (or use --list-models)",
            file=sys.stderr,
        )
        sys.exit(2)

    input_path: Path = args.path
    if not input_path.exists():
        print(f"Error: path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    # resolve model
    model_slug = args.model
    if model_slug is None:
        model_slug = prompt_model()
    size, display_name, brand = E_READERS[model_slug]
    print(f"Selected: {display_name} ({brand}) - {size[0]}x{size[1]} [{model_slug}]")

    # resolve grayscale (argparse trick: --grayscale True, --no-grayscale True, none -> None)
    grayscale: bool | None
    if args.grayscale is True:
        grayscale = True
    elif args.no_grayscale:
        grayscale = False
    else:
        grayscale = None
    if grayscale is None:
        grayscale = prompt_grayscale()
    print(f"Grayscale: {'yes' if grayscale else 'no'}")

    output_root: Path = args.output
    # if input is single file and output looks like a file path with suffix, honor it
    # otherwise treat output as directory
    if input_path.is_file() and output_root.suffix.lower() in IMAGE_EXTS | {".png"}:
        # user gave explicit output file
        output_root.parent.mkdir(parents=True, exist_ok=True)
        if output_root.exists() and output_root.is_dir():
            output_root = output_root / f"{input_path.stem}.png"
        # else keep as file path, handle in single-file branch below
        is_explicit_file = True
    else:
        is_explicit_file = False
        output_root.mkdir(parents=True, exist_ok=True)
        if args.clean:
            print(f"Cleaning {output_root} ...")
            clean_output(output_root)

    if is_explicit_file:
        # direct file output
        convert_image(input_path, output_root, size, grayscale)
        print(f"Done: {input_path} -> {output_root} ({size[0]}x{size[1]})")
        return

    count = process_path(input_path, output_root, size, grayscale)
    print(
        f"Done: {count} image(s) -> {output_root} [{display_name} {size[0]}x{size[1]}]"
    )


if __name__ == "__main__":
    main()

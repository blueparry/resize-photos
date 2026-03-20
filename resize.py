#!/usr/bin/env python3
"""
Core resize and optimize logic for photos.

Can be used as CLI:
    python resize.py [--directory DIR] [--width 1024] [--height 768]
                     [--quality 85] [--no-backup]
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install it with:")
    print("  pip install Pillow")
    sys.exit(1)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}

DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 768
DEFAULT_QUALITY = 85


def find_images(directory):
    """Return sorted list of image files in the given directory."""
    return sorted(
        p
        for p in Path(directory).iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def resize_image(image_path, target_width, target_height, quality, backup_dir):
    """Resize a single image to fit within target_width x target_height.

    Returns a dict with status info, or raises on error.
    """
    img = Image.open(image_path)
    original_width, original_height = img.size

    if original_width <= target_width and original_height <= target_height:
        img.close()
        return {
            "status": "skipped",
            "name": image_path.name,
            "original_size": (original_width, original_height),
            "new_size": (original_width, original_height),
        }

    # Back up original
    if backup_dir is not None:
        backup_path = Path(backup_dir) / image_path.name
        if not backup_path.exists():
            shutil.copy2(image_path, backup_path)

    # Scale to fit within target dimensions, preserving aspect ratio
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = round(original_width * ratio)
    new_height = round(original_height * ratio)

    resized = img.resize((new_width, new_height), Image.LANCZOS)

    exif_data = img.info.get("exif")

    save_kwargs = {"optimize": True}
    suffix = image_path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        save_kwargs["quality"] = quality
        save_kwargs["subsampling"] = 0
        if exif_data:
            save_kwargs["exif"] = exif_data
        resized.save(image_path, "JPEG", **save_kwargs)
    elif suffix == ".png":
        if exif_data:
            save_kwargs["exif"] = exif_data
        resized.save(image_path, "PNG", **save_kwargs)
    elif suffix == ".webp":
        save_kwargs["quality"] = quality
        if exif_data:
            save_kwargs["exif"] = exif_data
        resized.save(image_path, "WEBP", **save_kwargs)
    else:
        resized.save(image_path, **save_kwargs)

    img.close()
    resized.close()

    return {
        "status": "resized",
        "name": image_path.name,
        "original_size": (original_width, original_height),
        "new_size": (new_width, new_height),
    }


def resize_all(directory, target_width, target_height, quality, no_backup=False,
               on_progress=None):
    """Resize all images in directory. Returns summary dict.

    on_progress(result_dict) is called after each image if provided.
    """
    directory = Path(directory)
    images = find_images(directory)

    backup_dir = None
    if not no_backup:
        backup_dir = directory / "originals"
        backup_dir.mkdir(exist_ok=True)

    resized_count = 0
    skipped_count = 0
    error_count = 0
    results = []

    for image_path in images:
        try:
            result = resize_image(
                image_path, target_width, target_height, quality, backup_dir
            )
            if result["status"] == "resized":
                resized_count += 1
            else:
                skipped_count += 1
            results.append(result)
        except Exception as e:
            error_count += 1
            result = {"status": "error", "name": image_path.name, "error": str(e)}
            results.append(result)

        if on_progress:
            on_progress(result)

    return {
        "total": len(images),
        "resized": resized_count,
        "skipped": skipped_count,
        "errors": error_count,
        "results": results,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Resize and optimize photos.")
    parser.add_argument(
        "--directory",
        type=str,
        default=str(Path(__file__).resolve().parent),
        help="Directory containing images (default: script directory)",
    )
    parser.add_argument(
        "--width", type=int, default=DEFAULT_WIDTH,
        help=f"Target max width in pixels (default: {DEFAULT_WIDTH})",
    )
    parser.add_argument(
        "--height", type=int, default=DEFAULT_HEIGHT,
        help=f"Target max height in pixels (default: {DEFAULT_HEIGHT})",
    )
    parser.add_argument(
        "--quality", type=int, default=DEFAULT_QUALITY,
        help=f"JPEG/WebP quality 1-100 (default: {DEFAULT_QUALITY})",
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip backing up originals to 'originals/' folder",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    directory = Path(args.directory)

    if not directory.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    images = find_images(directory)
    if not images:
        print("No images found in the directory.")
        print(f"Place images ({', '.join(SUPPORTED_EXTENSIONS)}) in: {directory}")
        sys.exit(0)

    print(f"Found {len(images)} image(s). Target: {args.width}x{args.height}, "
          f"quality: {args.quality}")
    print(f"Directory: {directory}")
    print()

    def on_progress(result):
        if result["status"] == "resized":
            orig = result["original_size"]
            new = result["new_size"]
            print(f"  DONE {orig[0]}x{orig[1]} -> {new[0]}x{new[1]}: {result['name']}")
        elif result["status"] == "skipped":
            orig = result["original_size"]
            print(f"  SKIP (already {orig[0]}x{orig[1]}): {result['name']}")
        else:
            print(f"  ERROR: {result['name']}: {result.get('error', 'unknown')}")

    summary = resize_all(
        directory, args.width, args.height, args.quality,
        no_backup=args.no_backup, on_progress=on_progress,
    )

    print()
    print(f"Done! Resized: {summary['resized']}, Skipped: {summary['skipped']}, "
          f"Errors: {summary['errors']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Resize and optimize photos for web use.

Usage:
    python resize.py [--max-size 1024] [--quality 85] [--no-backup]

- Resizes images so the longest side is at most --max-size pixels (default 1024)
- Uses Lanczos resampling for best quality downscaling
- Saves JPEGs at --quality (default 85, visually near-lossless)
- Backs up originals to an 'originals/' subfolder (unless --no-backup)
- Skips images already smaller than --max-size
- Preserves filenames
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
SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Resize and optimize photos for web.")
    parser.add_argument(
        "--max-size",
        type=int,
        default=1024,
        help="Maximum dimension (longest side) in pixels (default: 1024)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG/WebP quality 1-100 (default: 85)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backing up originals to 'originals/' folder",
    )
    return parser.parse_args()


def find_images(directory):
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def resize_image(image_path, max_size, quality, backup_dir):
    img = Image.open(image_path)
    original_width, original_height = img.size
    longest_side = max(original_width, original_height)

    if longest_side <= max_size:
        print(f"  SKIP (already {original_width}x{original_height}): {image_path.name}")
        return False

    # Back up original
    if backup_dir is not None:
        backup_path = backup_dir / image_path.name
        if not backup_path.exists():
            shutil.copy2(image_path, backup_path)

    # Calculate new dimensions preserving aspect ratio
    ratio = max_size / longest_side
    new_width = round(original_width * ratio)
    new_height = round(original_height * ratio)

    resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Preserve EXIF data if available
    exif_data = img.info.get("exif")

    # Save with optimization
    save_kwargs = {"optimize": True}
    suffix = image_path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        save_kwargs["quality"] = quality
        save_kwargs["subsampling"] = 0  # 4:4:4 chroma for better quality
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

    print(
        f"  DONE {original_width}x{original_height} -> {new_width}x{new_height}: "
        f"{image_path.name}"
    )
    return True


def main():
    args = parse_args()
    images = find_images(SCRIPT_DIR)

    if not images:
        print("No images found in the script directory.")
        print(f"Place images ({', '.join(SUPPORTED_EXTENSIONS)}) next to this script.")
        sys.exit(0)

    print(f"Found {len(images)} image(s). Max size: {args.max_size}px, quality: {args.quality}")
    print()

    backup_dir = None
    if not args.no_backup:
        backup_dir = SCRIPT_DIR / "originals"
        backup_dir.mkdir(exist_ok=True)
        print(f"Originals backed up to: {backup_dir}")
        print()

    resized_count = 0
    skipped_count = 0
    error_count = 0

    for image_path in images:
        try:
            was_resized = resize_image(image_path, args.max_size, args.quality, backup_dir)
            if was_resized:
                resized_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ERROR: {image_path.name}: {e}")
            error_count += 1

    print()
    print(f"Done! Resized: {resized_count}, Skipped: {skipped_count}, Errors: {error_count}")


if __name__ == "__main__":
    main()

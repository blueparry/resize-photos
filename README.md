# resize-photos

Simple cross-platform script to resize and optimize photos for web use.

Drop your high-resolution photos (4000–8000px) into the folder, run the script, and get web-ready images (800–1024px) with minimal quality loss.

## Features

- Resizes images so the longest side fits a configurable max (default **1024px**)
- **Lanczos** resampling for highest quality downscaling
- JPEG quality **85** (visually near-lossless)
- Preserves filenames and EXIF data
- Backs up originals to `originals/` subfolder
- Supports: JPG, JPEG, PNG, WebP, TIFF, BMP
- Works on **Windows**, **Linux**, and **macOS**

## Quick Start

1. Place your photos in this folder
2. Run the script:

```bash
# macOS / Linux
./resize.sh

# Windows
resize.bat
```

The wrapper scripts automatically create a Python virtual environment and install [Pillow](https://python-pillow.org/) on first run.

## Options

```
--max-size N    Max dimension in pixels (default: 1024)
--quality N     JPEG/WebP quality 1-100 (default: 85)
--no-backup     Skip backing up originals
```

### Examples

```bash
./resize.sh --max-size 800           # smaller for faster loading
./resize.sh --quality 90             # higher quality, larger files
./resize.sh --no-backup              # don't keep originals
```

## Requirements

- Python 3.8+
- [Pillow](https://python-pillow.org/) (installed automatically by the wrapper scripts)

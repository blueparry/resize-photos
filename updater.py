"""
Auto-updater that checks GitHub for new versions and downloads updates.

Uses the GitHub API (no dependencies beyond stdlib).
"""

import json
import os
import shutil
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

REPO_OWNER = "blueparry"
REPO_NAME = "resize-photos"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

SCRIPT_DIR = Path(__file__).resolve().parent
VERSION_FILE = SCRIPT_DIR / ".version"

# Files to update (all distributable files in the repo root)
UPDATABLE_FILES = [
    "version.py",
    "resize.py",
    "resize_gui.py",
    "icon.py",
    "updater.py",
    "resize.sh",
    "resize.bat",
]


def _read_local_version():
    """Read the locally stored commit SHA, or return None."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return None


def _write_local_version(sha):
    """Persist the current commit SHA."""
    VERSION_FILE.write_text(sha + "\n")


def _api_get(path):
    """Make a GET request to the GitHub API and return parsed JSON."""
    url = f"{API_BASE}/{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", f"{REPO_NAME}-updater")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download_raw(file_path, sha):
    """Download a single raw file from the repo at the given commit."""
    url = (
        f"https://raw.githubusercontent.com/"
        f"{REPO_OWNER}/{REPO_NAME}/{sha}/{file_path}"
    )
    req = urllib.request.Request(url)
    req.add_header("User-Agent", f"{REPO_NAME}-updater")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def check_for_update():
    """Check GitHub for a newer version.

    Returns:
        dict with keys:
            - "available" (bool): True if an update is available
            - "current_sha" (str | None): local SHA
            - "latest_sha" (str): remote SHA
            - "message" (str): latest commit message (first line)
    Raises on network errors.
    """
    data = _api_get(f"commits/{BRANCH}")
    latest_sha = data["sha"]
    message = data["commit"]["message"].split("\n")[0]
    current_sha = _read_local_version()

    # First run: no .version file yet — save current SHA as baseline
    if current_sha is None:
        _write_local_version(latest_sha)
        current_sha = latest_sha

    return {
        "available": current_sha != latest_sha,
        "current_sha": current_sha,
        "latest_sha": latest_sha,
        "message": message,
    }


def apply_update(latest_sha, on_progress=None):
    """Download updated files from GitHub and replace local copies.

    Args:
        latest_sha: the commit SHA to download from.
        on_progress: optional callback(filename, index, total).

    Returns:
        list of filenames that were updated.
    """
    # First, get the file list from the repo tree to know which files exist
    tree_data = _api_get(f"git/trees/{latest_sha}")
    repo_files = {item["path"] for item in tree_data["tree"] if item["type"] == "blob"}

    files_to_update = [f for f in UPDATABLE_FILES if f in repo_files]
    updated = []

    # Download to a temp dir first, then move into place (atomic-ish)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        for i, filename in enumerate(files_to_update):
            if on_progress:
                on_progress(filename, i, len(files_to_update))

            content = _download_raw(filename, latest_sha)
            tmp_file = tmp_path / filename
            tmp_file.write_bytes(content)
            updated.append(filename)

        # All downloads succeeded — now replace local files
        for filename in updated:
            src = tmp_path / filename
            dst = SCRIPT_DIR / filename
            # Preserve file permissions
            old_mode = dst.stat().st_mode if dst.exists() else None
            shutil.copy2(src, dst)
            if old_mode is not None:
                os.chmod(dst, old_mode)

    _write_local_version(latest_sha)

    if on_progress:
        on_progress(None, len(files_to_update), len(files_to_update))

    return updated


def initialize_version():
    """If no .version file exists, write the current commit SHA.

    Call this once on first run so future checks have a baseline.
    """
    if not VERSION_FILE.exists():
        try:
            data = _api_get(f"commits/{BRANCH}")
            _write_local_version(data["sha"])
        except Exception:
            pass

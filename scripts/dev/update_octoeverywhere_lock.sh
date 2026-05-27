#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PKG_SCRIPT="$REPO_ROOT/overlays/firmware-extended/65-app-cloud/root/usr/local/bin/octoeverywhere-pkg"
LOCK_FILE="$REPO_ROOT/overlays/firmware-extended/65-app-cloud/root/usr/local/share/octoeverywhere/requirements.lock"

usage() {
  cat <<'EOF'
Usage: update_octoeverywhere_lock.sh --commit <sha> [--version <label>]

Refreshes OctoEverywhere's pinned source archive SHA256 and regenerates
requirements.lock with pip-compile --generate-hashes.
EOF
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

read_pkg_value() {
  local key="$1"
  python3 - "$PKG_SCRIPT" "$key" <<'PY'
import pathlib
import re
import sys

content = pathlib.Path(sys.argv[1]).read_text()
match = re.search(rf'^{re.escape(sys.argv[2])}="([^"]+)"', content, re.MULTILINE)
if not match:
    raise SystemExit(1)
print(match.group(1))
PY
}

find_requirements_input() {
  local source_dir="$1"
  local candidate
  local -a candidates=(
    "requirements.txt"
    "requirements.in"
    "requirements/requirements.txt"
    "requirements/requirements.in"
  )

  for candidate in "${candidates[@]}"; do
    if [[ -f "$source_dir/$candidate" ]]; then
      printf '%s\n' "$source_dir/$candidate"
      return 0
    fi
  done

  fail "Could not find a supported requirements input file in $source_dir"
}

COMMIT=""
VERSION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit)
      [[ $# -ge 2 ]] || fail "--commit requires a value"
      COMMIT="$2"
      shift 2
      ;;
    --version)
      [[ $# -ge 2 ]] || fail "--version requires a value"
      VERSION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

[[ -n "$COMMIT" ]] || {
  usage >&2
  fail "Missing required --commit input"
}

require_cmd curl
require_cmd unzip
require_cmd sha256sum
require_cmd python3

if [[ -z "$VERSION" ]]; then
  VERSION="$(read_pkg_value VERSION)" || fail "Could not read VERSION from octoeverywhere-pkg"
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

ARCHIVE_PATH="$TMP_DIR/octoeverywhere.zip"
EXTRACT_DIR="$TMP_DIR/source"
VENV_DIR="$TMP_DIR/venv"
LOCK_TMP="$TMP_DIR/requirements.lock"
PKG_TMP="$TMP_DIR/octoeverywhere-pkg"
URL="https://github.com/QuinnDamerell/OctoPrint-OctoEverywhere/archive/${COMMIT}.zip"

mkdir -p "$EXTRACT_DIR"

echo "Downloading OctoEverywhere archive for commit $COMMIT"
curl -fsSL "$URL" -o "$ARCHIVE_PATH"

ARCHIVE_SHA256="$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"

echo "Extracting archive"
unzip -q "$ARCHIVE_PATH" -d "$EXTRACT_DIR"
SOURCE_DIR="$(find "$EXTRACT_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
[[ -n "$SOURCE_DIR" ]] || fail "Could not find extracted source directory"

REQUIREMENTS_INPUT="$(find_requirements_input "$SOURCE_DIR")"
echo "Using dependency input: ${REQUIREMENTS_INPUT#$SOURCE_DIR/}"

echo "Creating isolated tool environment"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --disable-pip-version-check --quiet --upgrade pip pip-tools

echo "Generating requirements.lock"
"$VENV_DIR/bin/python" -m piptools compile \
  --generate-hashes \
  --output-file "$LOCK_TMP" \
  "$REQUIREMENTS_INPUT"

python3 - "$PKG_SCRIPT" "$PKG_TMP" "$VERSION" "$COMMIT" "$URL" "$ARCHIVE_SHA256" <<'PY'
import pathlib
import re
import sys

pkg_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
updates = {
    "VERSION": sys.argv[3],
    "COMMIT": sys.argv[4],
    "URL": sys.argv[5],
    "SHA256": sys.argv[6],
}

content = pkg_path.read_text()
for key, value in updates.items():
    content, count = re.subn(
        rf'^{re.escape(key)}="[^"]*"$',
        f'{key}="{value}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise SystemExit(f"Failed to update {key} in {pkg_path}")

out_path.write_text(content)
PY

mv "$LOCK_TMP" "$LOCK_FILE"
mv "$PKG_TMP" "$PKG_SCRIPT"

echo "Updated:"
echo "  - $LOCK_FILE"
echo "  - $PKG_SCRIPT"
echo "Review with:"
echo "  git diff -- $LOCK_FILE $PKG_SCRIPT"

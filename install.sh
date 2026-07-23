#!/usr/bin/env bash
#
# install.sh — restore this skills collection into a fresh Claude Code setup.
#
# Copies every skill under ./skills/ into ~/.claude/skills/ so Claude Code
# picks them up. Existing skills of the same name are skipped unless you pass
# --force. Run it again any time to sync new skills.
#
# Usage:
#   ./install.sh            # copy skills, skip ones that already exist
#   ./install.sh --force    # overwrite existing skills of the same name
#   ./install.sh --link     # symlink instead of copy (edits stay in this repo)
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/skills"
DEST="${CLAUDE_HOME:-$HOME/.claude}/skills"

MODE="copy"
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --link)  MODE="link" ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 1 ;;
  esac
done

if [ ! -d "$SRC" ]; then
  echo "error: $SRC not found — run this from inside the repo." >&2
  exit 1
fi

mkdir -p "$DEST"
echo "Installing skills into: $DEST"
echo "Mode: $MODE   Force: $FORCE"
echo

installed=0 skipped=0
for skill in "$SRC"/*/; do
  name="$(basename "$skill")"
  target="$DEST/$name"

  if [ -e "$target" ] && [ "$FORCE" -eq 0 ]; then
    echo "  skip    $name (already exists — use --force to overwrite)"
    skipped=$((skipped + 1))
    continue
  fi

  rm -rf "$target"
  if [ "$MODE" = "link" ]; then
    ln -s "${skill%/}" "$target"
    echo "  link    $name"
  else
    cp -R "$skill" "$target"
    echo "  copy    $name"
  fi
  installed=$((installed + 1))
done

echo
echo "Done. $installed installed, $skipped skipped."
echo
echo "Next steps to fully restore the environment:"
echo "  1. Copy config/settings.template.json to ~/.claude/settings.json and fill in your own token."
echo "  2. Re-add the plugins/marketplaces listed in docs/PLUGINS.md."
echo "  3. Re-connect the MCP servers listed in docs/CONNECTIONS.md."

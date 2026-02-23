#!/usr/bin/env bash
# make_compat_links.sh
# Create compatibility symlinks so legacy names keep working during migration.
# Run this inside your project root (agastya_app). Safe to run multiple times.

set -e
shopt -s nullglob

echo "[*] Creating compatibility links (agastia_* -> agastya_*)"
for path in agastia_*; do
  [ -e "$path" ] || continue
  new="${path/agastia_/agastya_}"
  if [ ! -e "$new" ]; then
    ln -s "$path" "$new"
    echo "  [link] $new -> $path"
  fi
done

echo "[*] Creating compatibility links (files with 'agastia' in name)"
# handle files in root only to keep it simple/safe
for path in *agastia*; do
  [ -f "$path" ] || continue
  new="${path//agastia/agastya}"
  if [ ! -e "$new" ]; then
    ln -s "$path" "$new"
    echo "  [link] $new -> $path"
  fi
done

echo "[OK] Compatibility links ready."

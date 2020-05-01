#!/bin/bash
set -euo pipefail

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")
repo_path="$script_dir/.."

cd "$repo_path" || { echo "Could not cd into $repo_path" >&2; exit 1; }

SUDO=""
[ "$USER" != "root" ] && SUDO='sudo'

$SUDO yum --setopt=skip_missing_names_on_install=False install -y \
  redhat-rpm-config \
  rpm-build \
  rpmdevtools \
  rpmlint \
  ShellCheck

rpmdev-setuptree


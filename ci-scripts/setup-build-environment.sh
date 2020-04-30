#!/bin/bash
set -euo pipefail

dir=$(realpath "$(dirname $(realpath $0))/..")
cd "$dir" || { echo "Could not cd into $dir" >&2; exit 1; }

SUDO=""
[ "$USER" != "root" ] && SUDO='sudo'

$SUDO yum --setopt=skip_missing_names_on_install=False install -y \
  redhat-rpm-config \
  rpm-build \
  rpmdevtools \
  rpmlint \
  ShellCheck

rpmdev-setuptree


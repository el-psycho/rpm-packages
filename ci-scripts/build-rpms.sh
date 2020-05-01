#!/bin/bash
set -euo pipefail

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")
repo_path="$script_dir/.."

cd "$repo_path" || { echo "Could not cd into $repo_path" >&2; exit 1; }

SUDO=""
[ "$(id -un)" != "root" ] && SUDO='sudo'

DIFF_COMPARE='master..HEAD'

if [ "${BRANCH_NAME-empty}" == 'empty' ]; then
  BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
fi

echo "======================================================================="
echo "  Building RPMS"
echo "======================================================================="
echo
echo -n "INFO: Current branch is $BRANCH_NAME. "

if [ "$BRANCH_NAME" == 'master' ]; then
  DIFF_COMPARE='HEAD~1 HEAD'
  echo -e "Only building RPM specs from the last commit.\n"
else
  echo -e "Building new RPM specs compared to master.\n"
fi

changed_spec_files=$(
  git diff --name-status $DIFF_COMPARE |
  grep "\.spec$" |
  grep -v D |
  awk '{print $2}' || :
)

if [ ! "$changed_spec_files" ]; then
  echo "WARNING: No committed changes found for any spec files."
fi

for spec_file in $changed_spec_files; do
  echo -e "=============== Building $spec_file ===============\n"

  if grep -qi 'BuildRequires:' "$spec_file"; then
    echo "Downloading build requirements:"
    echo "-------------------------------"

    pkgs=$(
      grep '^BuildRequires:' "$spec_file" |\
      tr -s '\t' ' ' |\
      cut -d ' ' -f 2 |\
      grep -v '^/' |\
      xargs -n 1 rpm --eval |\
      tr '\n' ' '
    )

    [ "$pkgs" ] && $SUDO yum install -y $pkgs
  fi

  rpmbuild -bb --clean "$spec_file"
  echo
done


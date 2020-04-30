#!/bin/bash
set -euo pipefail

dir=$(realpath "$(dirname $(realpath $0))/..")
cd "$dir" || { echo "Could not cd into $dir" >&2; exit 1; }

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
  echo "WARNING: No changes found for any spec files. Have you commited your changes?"
fi

for specfile in $changed_spec_files; do
  echo -e "=============== Building $specfile ===============\n"

  if grep -qi 'BuildRequires:' "$specfile"; then
    echo "Downloading build requirements:"
    echo "-------------------------------"

    pkgs=$(
      grep '^BuildRequires:' "$specfile" |\
      tr -s ' ' |\
      cut -d ' ' -f 2 |\
      grep -v '^/' |\
      xargs -n 1 rpm --eval |\
      tr '\n' ' '
    )

    [ "$pkgs" ] && $SUDO yum install -y $pkgs
  fi

  rpmbuild -bb --clean "$specfile"
  echo
done


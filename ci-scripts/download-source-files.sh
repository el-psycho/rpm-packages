#!/bin/bash
set -euo pipefail

dir=$(realpath "$(dirname $(realpath $0))/..")
cd "$dir" || { echo "Could not cd into $dir" >&2; exit 1; }

DIFF_COMPARE='master..HEAD'

if [ "${BRANCH_NAME-empty}" == 'empty' ]; then
  BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
fi

echo "====================================================================="
echo "  Downloading RPM SOURCE files"
echo "====================================================================="
echo
echo -n "INFO: Current branch is $BRANCH_NAME. "

if [ "$BRANCH_NAME" == 'master' ]; then
  DIFF_COMPARE='HEAD~1 HEAD'
  echo -e "Only downloading sources for RPM specs from the last commit.\n"
else
  echo -e "Downloading sources for new RPM specs compared to master.\n"
fi

changed_spec_files=$(
  git diff --name-status $DIFF_COMPARE |
  grep "\.spec" |
  grep -v D |
  awk '{print $2}' || :
)

if [ ! "$changed_spec_files" ]; then
  echo "WARNING: No changes found for any spec files. Have you commited your changes?"
fi

for specfile in $changed_spec_files; do
  specFileDirname=$(dirname "$specfile")
  rsync "$specFileDirname"/ --exclude '*.spec' "$HOME/rpmbuild/SOURCES/"

  if grep -qi 'source[0-9]\?:' "$specfile"; then
    echo "==========  Downloading sources for $specfile =========="
  fi

  spectool --get-files --all --sourcedir "$specfile"
  echo
done


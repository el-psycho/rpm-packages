#!/bin/bash
set -euo pipefail

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")
repo_path="$script_dir/.."

cd "$repo_path" || { echo "Could not cd into $repo_path" >&2; exit 1; }

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

for spec_file in $changed_spec_files; do
  spec_dirname=$(dirname "$spec_file")
  rsync -r "$spec_dirname"/ --exclude '*.spec' "$HOME/rpmbuild/SOURCES/"

  if grep -qi 'source[0-9]\?:' "$spec_file"; then
    echo "==========  Downloading sources for $spec_file =========="
  fi

  spectool --get-files --all --sourcedir "$spec_file"
  echo
done


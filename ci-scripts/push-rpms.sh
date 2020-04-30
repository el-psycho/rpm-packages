#!/bin/bash
# This script uploads RPM files to the "bardel-apps" Katello
set -euo pipefail

dir=$(realpath "$(dirname $(realpath $0))/..")
cd "$dir" || { echo "Could not cd into $dir" >&2; exit 1; }

oIFS="$IFS"
IFS=$'\n'

for rpmfile in $(find "$HOME"/rpmbuild/RPMS/ -type f -iname '*.rpm'); do
  # Only upload packages that are new
  hammer \
    --no-headers \
    --server "$KATELLO_URL" \
    --username "$KATELLO_CREDS_USR" \
    --password "$KATELLO_CREDS_PSW" \
    package list \
    --product "Apps" \
    --repository "bardel-apps" \
    --organization "Bardel" \
    --search "$(basename $rpmfile)" |\
  grep -q "$(basename $rpmfile)" && continue

  echo "Pushing $(basename $rpmfile) to Katello"
  hammer \
    --server "$KATELLO_URL" \
    --username "$KATELLO_CREDS_USR" \
    --password "$KATELLO_CREDS_PSW" \
    repository upload-content \
    --product "Apps" \
    --name "bardel-apps" \
    --organization "Bardel" \
    --path "$rpmfile"
done

IFS="$oIFS"


#!/bin/bash
dir=$(realpath "$(dirname $(realpath $0))/..")
cd "$dir" || { echo "Could not cd into $dir" >&2; exit 1; }

scripts=$(find . -type f -iname '*\.sh')
[ ! "$scripts" ] && { echo 'No shell scripts found'; exit 0; }

SHELLCHECK="$(
  echo shellcheck \
    --exclude=SC1004 \
    --exclude=SC1117 \
    --exclude=SC2012 \
    --exclude=SC2016 \
    --exclude=SC2039 \
    --exclude=SC2046 \
    --exclude=SC2086 \
    --exclude=SC2116 \
    --exclude=SC2162 \
    --exclude=SC2044 \
)"

echo "========================================================================"
echo " Checking bash scripts with shellcheck and using the following options:"
echo "$SHELLCHECK" | tr ' ' '\n' | grep -v shellcheck
echo "========================================================================"
echo

oldIFS="$IFS"
IFS=$'\n'
errors=0

for script in $scripts; do
  mark="\e[1;32m✔\e[0m"
  output=""

  output=$( eval $SHELLCHECK '"$script"' )
  [ "$output" ] && mark="\e[1;91m✘\e[0m" errors=$(( errors + 1 ))

  echo -e "$mark $script"

  if [ "$output" ]; then
    echo -e '\e[31m---------------------------------------------------------------------\e[0m'
    echo -e "\e[31m${output}\e[0m"
    echo -e '\e[31m---------------------------------------------------------------------\e[0m'
  fi
done

IFS="$oldIFS"
exit $errors


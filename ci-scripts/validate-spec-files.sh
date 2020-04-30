#!/bin/bash

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")
repo_path="$script_dir/.."

cd "$repo_path" || { echo "Could not cd into $repo_path" >&2; exit 1; }

spec_files=$(find . -type f -iname '*\.spec')
[ ! "$spec_files" ] && { echo 'No RPM spec files found'; exit 0; }

echo "============================================="
echo "   Validating RPM SPEC files using rpmlint"
echo "============================================="
echo

old_IFS="$IFS"
IFS=$'\n'
errors=0

for spec_file in $spec_files; do
  mark="\e[1;32m✔\e[0m"
  output=""

  spec_dirname=$(dirname "$spec_file")
  output=$(rpmlint -i -f "$spec_dirname/rpmlint.conf" "$spec_file")
  errnum=$?

  [ $errnum -ne 0 ] && mark="\e[1;91m✘\e[0m" errors=$(( errors + 1 ))

  echo -e "$mark $spec_file"

  if [ $errnum -ne 0 ]; then
    echo -e '\e[31m---------------------------------------------------------------------\e[0m'
    echo -e "\e[31m${output}\e[0m"
    echo -e '\e[31m---------------------------------------------------------------------\e[0m'
  elif echo "$output" | grep -q ' [^0][0-9]\+\? warnings'; then
    echo -e '\e[33m---------------------------------------------------------------------\e[0m'
    echo -e "\e[33m${output}\e[0m"
    echo -e '\e[33m---------------------------------------------------------------------\e[0m'
  fi
done

IFS="$old_IFS"
exit $errors


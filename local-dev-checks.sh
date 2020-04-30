#!/bin/bash
set -euo pipefail

projectDir="$(dirname "$(realpath "$0")")"

# Change the range in the selinux security context so the project directory
# can be accessed from a container
chcon -R -t container_file_t -l s0 "$projectDir"

mkdir -p "$HOME/rpmbuild"
chcon -R -t container_file_t -l s0 "$HOME/rpmbuild"

cd "$projectDir"

podman build -t rpm-packages:fedora32 -f Dockerfile.fedora32 .

podman run -it --rm -v "$PWD:/work" -v "$HOME/rpmbuild:/root/rpmbuild" \
  rpm-packages:fedora32 bash -c '
    cd /work
    ci-scripts/validate-shell-scripts.sh || :
    echo
    ci-scripts/validate-spec-files.sh || :
    echo
    ci-scripts/download-source-files.sh || :
    echo
    ci-scripts/build-rpms.sh || :
    echo
  '


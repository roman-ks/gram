k8s_repo := "/home/roman/projects/home-projects-parent-k8s"
registry := "oci-registry.pi.home/gram"
tag := `git rev-parse --short HEAD`

bootstrap:
    sudo apt update && sudo apt install -y buildah qemu-user-binfmt

build:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -n "$(git status --porcelain)" ]; then
        echo "warning: uncommitted changes — image tag {{tag}} won't match a pushed commit" >&2
    fi
    buildah bud --layers \
        --arch arm64 \
        -t {{registry}}:{{tag}} .

push: build
    buildah push --tls-verify=false \
        {{registry}}:{{tag}}

# Build, push, and roll out to the cluster in one step.
deploy: push
    #!/usr/bin/env bash
    set -euo pipefail
    sed -i -E 's/^(\s*tag: ").*(")$/\1{{tag}}\2/' {{k8s_repo}}/values/gram.yaml
    cd {{k8s_repo}} && just gram
    echo "Deployed {{registry}}:{{tag}}"
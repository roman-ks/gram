bootstrap:
    sudo apt update && sudo apt install -y buildah qemu-user-binfmt

build:
    buildah bud --layers \
        --arch arm64 \
        -t oci-registry.pi.home/gram:0.1.1 .
push:
    buildah push --tls-verify=false \
        oci-registry.pi.home/gram:0.1.1
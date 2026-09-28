#!/usr/bin/env bash
set -euo pipefail

# Optional recovery path for the repository-wide GitHub-hosted Actions gate.
# This script never stores a GitHub token in the repository.
#
# Required:
#   GITHUB_RUNNER_TOKEN=<short-lived registration token>
#
# Optional:
#   RUNNER_DIR=$HOME/actions-runner-siftalpha-research
#   RUNNER_NAME=$(hostname)-siftalpha-research
#   INSTALL_SERVICE=0|1
#
# Registration token must be obtained by an authorized repository owner from:
# Settings -> Actions -> Runners -> New self-hosted runner

REPO_URL="https://github.com/kuashan/siftalpha-research"
RUNNER_VERSION="2.337.0"
RUNNER_DIR="${RUNNER_DIR:-$HOME/actions-runner-siftalpha-research}"
RUNNER_NAME="${RUNNER_NAME:-$(hostname)-siftalpha-research}"
INSTALL_SERVICE="${INSTALL_SERVICE:-0}"

: "${GITHUB_RUNNER_TOKEN:?GITHUB_RUNNER_TOKEN is required}"

case "$(uname -m)" in
  x86_64|amd64)
    ARCH="x64"
    SHA256="70920811a4f8ad4328818682bca5c6469c1c942fab52448868071d0063816613"
    ;;
  aarch64|arm64)
    ARCH="arm64"
    SHA256="9b1dc70626422526e3c94767cf024896beb15da5342a3f4819bf2feac13e0393"
    ;;
  *)
    echo "Unsupported architecture: $(uname -m)" >&2
    exit 2
    ;;
esac

mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

PKG="actions-runner-linux-${ARCH}-${RUNNER_VERSION}.tar.gz"
URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${PKG}"

if [[ ! -f "$PKG" ]]; then
  curl -fL --retry 5 --retry-delay 3 "$URL" -o "$PKG"
fi

echo "${SHA256}  ${PKG}" | sha256sum -c -

if [[ ! -x ./config.sh ]]; then
  tar xzf "$PKG"
fi

# Install OS dependencies if the runner bundle exposes GitHub's helper.
if [[ -x ./bin/installdependencies.sh ]]; then
  if command -v sudo >/dev/null 2>&1; then
    sudo ./bin/installdependencies.sh || true
  else
    ./bin/installdependencies.sh || true
  fi
fi

./config.sh \
  --url "$REPO_URL" \
  --token "$GITHUB_RUNNER_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "siftalpha-research,v2" \
  --work "_work" \
  --unattended \
  --replace

if [[ "$INSTALL_SERVICE" == "1" ]]; then
  if ! command -v sudo >/dev/null 2>&1; then
    echo "INSTALL_SERVICE=1 requires sudo" >&2
    exit 3
  fi
  sudo ./svc.sh install
  sudo ./svc.sh start
  sudo ./svc.sh status
else
  cat <<'EOF'
Runner registration complete.

To run interactively:
  ./run.sh

Or rerun this setup with:
  INSTALL_SERVICE=1 GITHUB_RUNNER_TOKEN=<new-token> ./setup_self_hosted_runner.sh

Then trigger the manual workflow:
  V2 Research Infra (Self Hosted)
EOF
fi

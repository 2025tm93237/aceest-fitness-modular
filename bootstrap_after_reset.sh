#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# bootstrap_after_reset.sh
# Rebuilds everything that a lab VM reset wipes: registry, images (Docker +
# Podman), SonarQube container, Minikube/kubectl, and the base k8s deploy.
# Safe to re-run — every step checks "is this already there?" first.
# Run from inside the repo: cd aceest-fitness-modular && bash ../bootstrap_after_reset.sh
# ---------------------------------------------------------------------------
set -uo pipefail
IMAGE="aceest-fitness-modular"
REG="localhost:5050"

log() { echo -e "\n=== $1 ==="; }

# 0. Make sure we're in the repo and have the latest committed pipeline assets
log "0. Sync repo"
if [ ! -f "Dockerfile" ]; then
  echo "Run this from inside the aceest-fitness-modular repo directory. Aborting."
  exit 1
fi
git pull

# 1. Container registry
log "1. Local registry on :5050"
if [ "$(docker ps -q -f name=^registry$)" ]; then
  echo "registry already running"
elif [ "$(docker ps -aq -f name=^registry$)" ]; then
  docker start registry
else
  docker run -d -p 5050:5000 --restart=always --name registry registry:2
fi
sleep 2
curl -s -o /dev/null -w "registry catalog HTTP %{http_code}\n" http://localhost:5050/v2/_catalog

# 2. Docker build + push (current version)
log "2. Docker build & push v1.2"
docker build -t ${REG}/${IMAGE}:v1.2 -t ${REG}/${IMAGE}:latest .
docker push ${REG}/${IMAGE}:v1.2
docker push ${REG}/${IMAGE}:latest

# 2b. Rebuild earlier version too, so the registry shows real history
log "2b. Rebuild v1.1 from its tag (for registry version history)"
if git rev-parse aceest-modular-v1.1 >/dev/null 2>&1; then
  git worktree add /tmp/aceest-v1.1 aceest-modular-v1.1 >/dev/null 2>&1 || true
  if [ -d /tmp/aceest-v1.1 ]; then
    (cd /tmp/aceest-v1.1 && docker build -t ${REG}/${IMAGE}:v1.1 . && docker push ${REG}/${IMAGE}:v1.1)
    git worktree remove /tmp/aceest-v1.1 --force
  fi
else
  echo "tag aceest-modular-v1.1 not found locally — skipping (not fatal)"
fi

# 3. Podman — install if missing, build with sudo (works around the
#    rootless UID/GID namespace error seen on this lab's accounts)
log "3. Podman"
if ! command -v podman >/dev/null; then
  echo "podman not found — installing"
  sudo dnf install -y podman
fi
sudo podman build -t ${REG}/${IMAGE}:v1.2-podman .
sudo podman push --tls-verify=false ${REG}/${IMAGE}:v1.2-podman

# 4. SonarQube
log "4. SonarQube container"
if [ "$(docker ps -q -f name=^sonarqube$)" ]; then
  echo "sonarqube already running"
elif [ "$(docker ps -aq -f name=^sonarqube$)" ]; then
  docker start sonarqube
else
  docker run -d --name sonarqube -p 9000:9000 sonarqube:community
fi
echo "waiting for SonarQube to become operational (can take 1-2 min)..."
for i in $(seq 1 40); do
  if curl -s http://localhost:9000/api/system/status 2>/dev/null | grep -q '"status":"UP"'; then
    echo "SonarQube is UP"
    break
  fi
  sleep 5
done
curl -s -o /dev/null -w "sonarqube HTTP %{http_code}\n" http://localhost:9000

# 5. Minikube + kubectl — install if missing
log "5. kubectl + Minikube"
if ! command -v kubectl >/dev/null; then
  echo "kubectl not found — installing"
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl && sudo mv kubectl /usr/local/bin/
fi
if ! command -v minikube >/dev/null; then
  echo "minikube not found — installing"
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  chmod +x minikube-linux-amd64 && sudo mv minikube-linux-amd64 /usr/local/bin/minikube
fi
if minikube status >/dev/null 2>&1; then
  echo "minikube already running"
else
  minikube start --driver=docker
fi

# 6. Load the image straight into Minikube's node (sidesteps the
#    "localhost:5050 means the minikube node itself" problem) and deploy
log "6. Load image into Minikube + deploy base manifests"
minikube image load ${REG}/${IMAGE}:v1.2
kubectl apply -f k8s/base/
kubectl rollout restart deployment/aceest-fitness 2>/dev/null || true
kubectl get pods,svc

# 7. Summary + what's still manual
log "7. Done — summary"
echo "Registry tags:"
curl -s http://localhost:5050/v2/${IMAGE}/tags/list
echo
echo "Minikube endpoint:"
minikube service aceest-fitness --url 2>/dev/null || echo "(pods may still be starting — re-run: minikube service aceest-fitness --url)"
echo
echo "Docker gateway IP for SonarQube webhook (if you use one instead of API polling):"
docker inspect sonarqube --format '{{.NetworkSettings.Gateway}}' 2>/dev/null

cat <<'EOF'

----------------------------------------------------------------------
STILL MANUAL (can't be scripted — these live in Jenkins/SonarQube's UI
and the token/project are regenerated fresh every time the SonarQube
container is recreated):

  1. Open http://localhost:9000 -> log in -> if project
     "aceest-fitness-modular" doesn't exist, create it.
  2. My Account -> Security -> Generate Token -> copy it.
  3. Jenkins -> Manage Jenkins -> System -> "SonarQube servers" ->
     edit "My SonarQube Server" -> paste the NEW token as its
     Secret text credential (the old one died with the old container).
     Confirm Server URL is exactly: http://localhost:9000
  4. Jenkins -> your job -> Configure -> Pipeline -> Script Path:
     Jenkinsfile.v2   (confirm it's still set this way — should be,
     since it's a job setting, not VM state, but worth a glance)
  5. Trigger a build:
       git commit --allow-empty -m "trigger: rebuild after reset" && git push
----------------------------------------------------------------------
EOF

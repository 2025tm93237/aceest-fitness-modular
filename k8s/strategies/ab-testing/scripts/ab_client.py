"""
Tiny A/B demo client. Reads an X-Variant header value and calls the matching
Service's NodePort directly, so you can prove both variants are live and
distinguishable without needing a full Ingress-based header router.
Usage: python3 ab_client.py A   (or B)
"""
import sys
import requests

MINIKUBE_IP = "192.168.49.2"   # replace with: minikube ip
VARIANT_PORTS = {"A": 30081, "B": 30082}

variant = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
port = VARIANT_PORTS[variant]
resp = requests.get(f"http://{MINIKUBE_IP}:{port}/version")
print(f"Variant {variant} -> {resp.status_code} {resp.text}")

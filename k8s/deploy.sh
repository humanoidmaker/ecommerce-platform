#!/bin/bash
set -e
echo "=== E-Commerce Platform K8s Deployment ==="
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml
kubectl apply -f postgres/
kubectl apply -f redis/
echo "Waiting for infra..."
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=60s
kubectl apply -f backend/
kubectl apply -f celery-worker/
kubectl apply -f celery-beat/
kubectl apply -f frontend-buyer/
kubectl apply -f frontend-seller/
kubectl apply -f frontend-admin/
kubectl apply -f ingress.yaml
echo "=== Done ==="

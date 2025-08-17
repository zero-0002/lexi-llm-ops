#!/bin/bash

# Create analytics-config secret for frontend configuration
kubectl create secret generic analytics-config \
  --namespace=secrets-store \
  --from-literal=ga_tracking_id="" \
  --from-literal=enable_analytics="false" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Analytics config secret created in secrets-store namespace"

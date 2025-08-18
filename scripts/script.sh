
# Remove application
helmfile destroy

# check secret
kubectl get secret legal-backend-secret -n application -o yaml
kubectl get secret legal-backend-secret -n application -o jsonpath="{.data.ENCRYPTION_KEY}" | base64 -d
kubectl get clustersecretstore legal-secret-store -o yaml

helmfile destroy --selector name=setup-secrets
helmfile apply --selector name=setup-secrets
kubectl get applications -n argocd --no-headers | grep -v root-app-of-apps | awk '{print $1}' | xargs kubectl delete application -n argocd
#
kubectl delete namespace argocd --grace-period=0 --force

kubectl get namespace argocd -o json > ns.json
"spec": {
  "finalizers": [
    "kubernetes"
  ]
}

# tắt sync
kubectl patch application setup-secrets -n argocd --type merge -p '{"spec":{"syncPolicy":{"automated":null}}}'
kubectl delete namespace secrets-management --force --grace-period=0
#
kubectl proxy
curl -k -H "Content-Type: application/json" -X PUT --data-binary @ns.json \
http://127.0.0.1:8002/api/v1/namespaces/argocd/finalize

# remove application with helm
for ns in $(kubectl get ns -o jsonpath='{.items[*].metadata.name}'); do
  helm list -n $ns -q | xargs -r -n1 helm uninstall -n $ns
done

# check owner resources
kubectl get pod curl-test -o yaml | grep -A5 ownerReferences

# down docker-compose
docker compose -f docker-compose.yml down

### argocd


kubectl apply -f helm/charts/argocd/cmp-helmfile-plugin.yaml
kubectl delete -f helm/charts/argocd/cmp-helmfile-plugin.yaml

kubectl apply -f helm/charts/argocd/root-app.yaml
kubectl delete pod -n argocd -l app.kubernetes.io/name=argocd-repo-server

kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d && echo
kubectl port-forward svc/argocd-server -n argocd 8888:443


### Create namespace secrets
kubectl create ns secrets-ns
kubectl -n secrets-ns create secret generic db-credentials \
  --from-env-file=.env

# Remove application
helmfile destroy

#
kubectl delete namespace argocd --grace-period=0 --force

kubectl get namespace argocd -o json > ns.json
"spec": {
  "finalizers": [
    "kubernetes"
  ]
}
kubectl proxy
curl -k -H "Content-Type: application/json" -X PUT --data-binary @ns.json \
http://127.0.0.1:8001/api/v1/namespaces/argocd/finalize

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


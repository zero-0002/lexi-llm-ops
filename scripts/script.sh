### Create namespace secrets
kubectl create ns secrets-ns
kubectl -n secrets-ns create secret generic db-credentials \
  --from-env-file=.env

# Remove application
helmfile destroy

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


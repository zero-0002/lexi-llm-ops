### Create namespace secrets
kubectl create ns secrets-ns
kubectl -n secrets-ns create secret generic db-credentials \
  --from-env-file=.env


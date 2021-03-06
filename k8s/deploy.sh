NS=pyhook
SERVICES="pyhook echo"

kubectl -n ${NS} apply -f pyhook-deploy.yaml
kubectl -n ${NS} apply -f ingress.yaml
kubectl -n ${NS} create configmap pyhook --from-file=../app/conf/config.yaml --dry-run=client -o yaml | kubectl -n ${NS} apply -f -

for SERVICE in $SERVICES
do
  envsubst < roles-bindings.yaml | kubectl apply -f -
done

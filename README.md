# pyhook
pyhook - a simple Docker Hub webhook handler to update kubernetes deployments when you push a new image. This scratches an itch for my development cluster and I wanted to play with Flask, the Kubernetes python client, and some unit testing.

## Running pyhook via compose

- copy `app/conf/config.yaml.example` to `app/conf/config.yaml`
- Edit `config.yaml` to define the parameters of your deployment(s):
  - image, namespace, deployment name, and a tag regex to honor for updates
  - add a key
- run `docker-compose up`

The compose file will attempt to mount a `~/.kube/config` into the container for use; change as necessary.

Browsing to http://localhost:5000/appname?key=yourkey will now report the deployment's current image and tag.
`POST`ing to that URL with a JSON payload with the following format `{'push_data': 'tag': 'newtag'}` will attempt to update the deployment with the new tag if it matches your `valid_tag` regex.

## Running pyhook in k8s

- Set up your `app/conf/config.yaml` as above.
- Examine the `k8s/deploy.sh` script and edit as necessary:
  - Set the namespace and the `SERVICES` to allow RBAC rights for pyhook.
  - `SERVICES` are the namespaces where the deployments you want pyhook to update reside.
- Create an `ingress.yaml` to expose the service if desired
- run `deploy.sh`
- configure your docker hub repo with a webhook pointing to pyhook URL!

from flask import Flask, request, Response
from kubernetes import client, config
import os
import re
import yaml

app = Flask(__name__)

# Load settings from yaml conf
conf_file = "conf/config.yaml"
if os.path.exists(conf_file):
    with open(conf_file) as f:
        app_config = yaml.load(f, Loader=yaml.SafeLoader)
    app.config.update(app_config)
else:
    print("Error: pyhook config file not found!")
    app.config["deployments"] = ""


def load_kube_conf():
    if os.path.exists("/run/secrets/kubernetes.io/"):
        config.load_incluster_config()
    else:
        try:
            config.load_kube_config()
        except config.config_exception.ConfigException as e:
            print(f"Error: Unable to load kube conf: {e}")


def update_deployment_image(apiclient, deployment, ns, deployname, image):
    # Modify our deploy object's image tag
    deployment.spec.template.spec.containers[0].image = image
    #  Submit the deployment
    api_response = apiclient.patch_namespaced_deployment(
        name=deployname, namespace=ns, body=deployment
    )
    return api_response


def get_or_update_deploy(request, my_deploy):
    apps_v1 = client.AppsV1Api()

    # deployment attributes from conf_file
    ns = my_deploy["ns"]
    deploy_name = my_deploy["deploy"]
    image = my_deploy["image"]

    try:
        # Fetch deployment object from k8s
        deployment = apps_v1.read_namespaced_deployment(deploy_name, ns)
    except Exception as e:
        print(f"Error fetching deployment from k8s: {e}")
        return f"Exception: {e}", 500

    if request.method == "GET":
        result = deployment

    if request.method == "POST":
        try:
            tag = request.json["push_data"]["tag"]
            if re.match(my_deploy["valid_tag"], tag):
                print(f"Info: Updating {deploy_name} to {image}:{tag}")
                result = update_deployment_image(
                    apps_v1, deployment, ns, deploy_name, f"{image}:{tag}"
                )
            else:
                print(f"Info: Invalid - not updating {deploy_name} to {image}:{tag}")
                return "Invalid tag.", 400
        except Exception as e:
            print(f"Error: malformed json or error updating tag - {e}")
            return "Malformed json", 400
    return result, 200


load_kube_conf()


@app.route("/")
def index():
    return "", 403


@app.route("/<path>", methods=["GET", "POST"])
def service_update(path):
    result = "No op."
    args = request.args

    if path in app.config["deployments"]:
        service = app.config["deployments"][path]
    else:
        return "Service not configured.", 404

    if "key" in args and args["key"] == service["key"]:
        result = get_or_update_deploy(request, service)
    else:
        return "No key or key incorrect.", 403

    return Response(response=str(result[0]), status=result[1], mimetype="text/plain")

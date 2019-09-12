from indico_install.utils import run_cmd


APP_MAP = {
    "review": "moonbow",
    "teach": "crowdlabel",
    "auth": "noct",
    "datasets": "sharknado",
    "discover": "elmosfire",
    "default": "default",
    "kit": "indiKit",
}


def get_app_hashes():
    output = run_cmd(
        r"""echo -e $(kubectl get configmap app-edge-nginx-conf -o json | jq '.data["nginx.conf"]') | grep -A 10 'map \$appname \$clientloc'""",
        silent=True,
    )
    output = output[output.find("{") + 1: output.find("}")].strip()
    output = output.split()

    app_hashes = {}
    for idx in range(0, len(output), 2):
        app_hash = output[idx + 1]
        app_hashes[APP_MAP[output[idx]]] = app_hash[app_hash.rfind("/") + 1: -1]
    return app_hashes


def get_non_matching_images(configs, only_first=False):
    output = run_cmd(
        "kubectl get deploy -o wide  | grep indico | awk '{print $1\"=\"$7s}'",
        silent=True,
    )
    images = {
        x[0]: ("deployment", x[1])
        for x in [y.split("=") for y in output.split("\n") if y.strip()]
    }

    output = run_cmd(
        "kubectl get statefulset -o wide  | grep indico | awk '{print $1\"=\"$5}'",
        silent=True,
    )

    images.update(
        {
            x[0]: ("statefulset", x[1])
            for x in [y.split("=") for y in output.split("\n") if y.strip()]
        }
    )
    for (deployment, (resource, image)) in images.items():
        if image.startswith("gcr.io/new-indico"):
            image = image[len("gcr.io/new-indico") + 1:]
        elif image.startswith("indicoio"):
            image = image[len("indicoio") + 1:]

        images[deployment] = (resource, image)

    for app, saved_image in configs["images"].items():
        for (deployment, (resource, cluster_image)) in images.items():
            formatted_deployment = deployment.replace("-", "").replace("_", "").lower()

            if app.lower() == formatted_deployment or app.lower() in cluster_image.replace(
                ".", ""
            ).replace(
                "-", ""
            ).replace(
                "_", ""
            ):
                if saved_image != cluster_image:
                    yield (app, resource, deployment, saved_image, cluster_image)
                if only_first:
                    break

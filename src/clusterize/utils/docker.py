from clusterize import structures


def get_container_name(cluster: structures.cluster.Cluster,
                       session: str) -> str:

    # The name of the containers is specified in the yaml, falling back to the
    # session name.
    # Using the session name allows having multiple clusters active in the
    # same time (operating on a subset of the available resources).
    return session if cluster.docker.container_name == "" else cluster.docker.container_name


def wrap_in_docker(cmd: str, container_name: str) -> str:

    return f"docker exec -t {container_name} /bin/sh -c '{cmd}'"


from copy import deepcopy
def dockerize_cluster(cluster: structures.cluster.Cluster) -> structures.cluster.Cluster:

    dockerized_cluster = deepcopy(cluster)

    if cluster.docker is None:
        raise RuntimeError("Docker not enabled in the cluster config")

    # Get the docker images to use
    docker = cluster.docker
    head_img = docker.image if docker.head_image == "" else docker.head_image
    worker_img = docker.image if docker.worker_image == "" else docker.worker_image

    # Name of the docker containers
    cname = cluster.docker.container_name if cluster.docker.container_name != "" \
        else cluster.cluster_name

    # Initialize the deployed cluster configuration and ssh key file names
    cluster_ssh_key = "cluster_ssh_key.pem"
    cluster_bootstrap = "cluster_bootstrap.yaml"

    # We don't touch the following initial phases:
    # - initialization_commands
    # - setup_commands

    # Post-process head_setup_commands
    # --------------------------------

    head_setup_commands = []

    # Pull the image if asked
    if cluster.docker.pull_before_run:
        head_setup_commands.append(f"docker pull {docker.head_image}")

    # Start building the "docker run" command line
    head_extra_run_options = " ".join(docker.run_options + docker.head_run_options)

    # Note that the cluster and project names are forced to match
    labels = f"-l clusterize " \
             f"-l clusterize.project={cluster.cluster_name}"

    docker_run = f"docker run -t --rm -d --name {cname} {labels} --net host " \
                 f"-v ~/.clusterize/{cluster_bootstrap}:/{cluster_bootstrap}:ro " \
                 f"-v ~/.clusterize/{cluster_ssh_key}:/{cluster_ssh_key}:ro " \
                 f"-e LC_ALL=C.UTF-8 -e LANG=C.UTF-8 " \
                 f"{head_extra_run_options} " \
                 f"{head_img} bash"

    # Start the container (it will fail during runtime if there's a name collision)
    head_setup_commands.append(docker_run)

    # Wrap in docker all the original commands
    for head_cmd in cluster.head_setup_commands:
        head_setup_commands.append(wrap_in_docker(cmd=head_cmd, container_name=cname))

    # Store the new commands
    dockerized_cluster.head_setup_commands = head_setup_commands

    # Post-process worker_setup_commands
    # ----------------------------------

    worker_setup_commands = []

    # Pull the image if asked
    if dockerized_cluster.docker.pull_before_run:
        worker_setup_commands.append(f"docker pull {docker.worker_image}")

    # Start building the "docker run" command line
    worker_extra_run_options = " ".join(docker.run_options + docker.worker_run_options)

    # Note that the cluster and project names are forced to match
    labels = f"-l clusterize " \
             f"-l clusterize.project={cluster.cluster_name}"

    docker_run = f"docker run -t --rm -d --name {cname} {labels} --net host " \
                 f"-v ~/.clusterize/{cluster_bootstrap}:/{cluster_bootstrap}:ro " \
                 f"-v ~/.clusterize/{cluster_ssh_key}:/{cluster_ssh_key}:ro " \
                 f"-e LC_ALL=C.UTF-8 -e LANG=C.UTF-8 " \
                 f"-e RAY_HEAD_IP={cluster.provider.head_ip} " \
                 f"{worker_extra_run_options} " \
                 f"{worker_img} bash"

    # Start the container (it will fail during runtime if there's a name collision)
    worker_setup_commands.append(docker_run)

    # Wrap in docker all the original commands
    for worker_cmd in cluster.worker_setup_commands:
        worker_setup_commands.append(wrap_in_docker(cmd=worker_cmd, container_name=cname))

    # Store the new commands
    dockerized_cluster.worker_setup_commands = worker_setup_commands

    # Post-process head_start_ray_commands
    # ------------------------------------

    head_start_ray_commands = []

    # Wrap in docker all the original commands
    for head_cmd in cluster.head_start_ray_commands:
        head_start_ray_commands.append(wrap_in_docker(cmd=head_cmd,
                                                      container_name=cname))

    # Store the new commands
    dockerized_cluster.head_start_ray_commands = head_start_ray_commands

    # Post-process worker_start_ray_commands
    # --------------------------------------

    worker_start_ray_commands = []

    # Wrap in docker all the original commands
    for worker_cmd in cluster.worker_start_ray_commands:
        worker_start_ray_commands.append(wrap_in_docker(cmd=worker_cmd,
                                                        container_name=cname))

    # Store the new commands
    dockerized_cluster.worker_start_ray_commands = worker_start_ray_commands

    # Return the new cluster config
    return dockerized_cluster

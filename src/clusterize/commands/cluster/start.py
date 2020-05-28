import fabric
import tempfile
from pathlib import Path
from fabric import transfer
from argparse import Namespace
from clusterize.executors import ssh
from clusterize import utils, structures


def check_clean_docker_cluster(cluster: structures.cluster.Cluster) -> None:

    # Name of the docker containers
    cname = cluster.docker.container_name if cluster.docker.container_name != "" \
        else cluster.cluster_name

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_cluster() as run:

        ps = f"docker ps -f 'name={cname}' --format '{{.Names}}'"
        results = run(cmd=ps)

        hosts_with_existing_cname = []

        for _, result in results.items():

            result: fabric.Result
            connection: fabric.Connection = result.connection

            if result.stdout.strip() != "":
                hosts_with_existing_cname.append(connection.host)

        if len(hosts_with_existing_cname) != 0:
            raise RuntimeError(
                f"Container '{cname}' found already running in the following hosts: "
                f"[{', '.join(hosts_with_existing_cname)}]. Clean the cluster before "
                f"continuing.")


def deploy_cluster_resources(cluster: structures.cluster.Cluster) -> None:

    handle, tmpfile = tempfile.mkstemp(prefix="cluster_bootstrap")

    # Write the bootstrap cluster yaml
    with open(handle, 'w') as f:
        yaml = cluster.to_yaml()
        f.write(yaml)

    # Deploy the bootstrap yaml to all cluster nodes
    ssh_key = Path(cluster.auth.ssh_private_key).expanduser().absolute()
    hosts = [cluster.provider.head_ip] + cluster.provider.worker_ips

    for host in tuple(hosts):

        connection = fabric.Connection(
            host=host,
            user=cluster.auth.ssh_user,
            connect_kwargs={'key_filename': str(ssh_key)})

        _ = connection.run(command="mkdir -p $HOME/.clusterize")

        result: transfer.Result = connection.put(
            local=tmpfile, remote=".clusterize/cluster_bootstrap.yaml")

        result: transfer.Result = connection.put(
            local=str(ssh_key), remote=".clusterize/cluster_ssh_key.pem")


def initialize(cluster: structures.cluster.Cluster) -> None:

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_cluster() as run:

        for init_cmd in cluster.initialization_commands:
            _ = run(cmd=init_cmd, print_output=True)


def setup(cluster: structures.cluster.Cluster) -> None:

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_cluster() as run:

        for init_cmd in cluster.setup_commands:
            _ = run(cmd=init_cmd, print_output=True)


def head_setup(cluster: structures.cluster.Cluster) -> None:

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_head() as run:

        for init_cmd in cluster.head_setup_commands:
            _ = run(cmd=init_cmd, print_output=True)


def worker_setup(cluster: structures.cluster.Cluster) -> None:

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_workers() as run:

        for init_cmd in cluster.worker_setup_commands:
            _ = run(cmd=init_cmd, print_output=True)


def head_start_ray(cluster: structures.cluster.Cluster) -> None:

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_head() as run:

        for init_cmd in cluster.head_start_ray_commands:
            _ = run(cmd=init_cmd, print_output=True)


def worker_start_ray(cluster: structures.cluster.Cluster) -> None:

    with ssh.SSHClusterCommandRunner(cluster=cluster, parallel=True).in_workers() as run:

        for init_cmd in cluster.worker_start_ray_commands:
            _ = run(cmd=init_cmd, print_output=True)


def start(args: Namespace) -> None:

    project_data = utils.project.get_project_data(project_folder=args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{project_data.directory}'")

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    if args.session is None:
        args.session = project_data.name

    if cls.docker is not None:
        cls = utils.docker.dockerize_cluster(cluster=cls)
        check_clean_docker_cluster(cluster=cls)
    else:
        raise NotImplementedError

    # Deploy the bootstrapped cluster yaml and the ssh key
    deploy_cluster_resources(cluster=cls)

    # Execute initialization and setup commands in the cluster
    initialize(cluster=cls)
    setup(cluster=cls)
    head_setup(cluster=cls)
    worker_setup(cluster=cls)

    # Start Ray
    head_start_ray(cluster=cls)
    worker_start_ray(cluster=cls)

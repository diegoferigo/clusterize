from argparse import Namespace
from clusterize.executors import ssh
from clusterize import structures, utils


def stop_cluster_with_docker(cluster: structures.cluster.Cluster,
                             session: str) -> None:

    if session is None:
        filter = "docker ps -q -f label=clusterize"
    else:
        filter = f"docker ps -q -f label=clusterize.session={session}"

    with ssh.SSHClusterCommandRunner(cluster=cluster).in_cluster() as run:

        cmd = f'[ -n "$({filter})" ] && docker stop $({filter}) || true'
        _ = run(cmd=cmd)


def stop_cluster() -> None:
    raise NotImplementedError


def stop(args: Namespace) -> None:

    project_data = utils.project.get_project_data(project_folder=args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{project_data.directory}'")

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    if cls.docker is not None:
        stop_cluster_with_docker(cluster=cls, session=args.session)
    else:
        stop_cluster()

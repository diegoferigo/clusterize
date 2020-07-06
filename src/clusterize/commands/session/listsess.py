from argparse import Namespace
from clusterize import structures
from clusterize.utils import project
from clusterize.executors import ssh


def listsess(args: Namespace):

    print(args)

    project_data = project.get_project_data(args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{args.project_dir}'")

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    with ssh.SSHClusterCommandRunner(cluster=cls).in_cluster() as run:

        cmd = ""

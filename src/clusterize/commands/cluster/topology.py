from typing import List
from argparse import Namespace
from operator import itemgetter
from tree_format import format_tree
from clusterize.executors import ssh
from clusterize import structures, utils
from dataclasses import dataclass, field, astuple


@dataclass()
class ExtraNodeInfo:

    gpus: int = None
    processing_units: int = None


@dataclass
class TreeNode:

    name: str
    children: List["TreeNode"] = field(default_factory=list)


def get_extra_node_info(username: str, ip: str, ssh_key: str) -> ExtraNodeInfo:

    info = ssh.NodeConnectionInfo(ip=ip, username=username, ssh_private_key=ssh_key)

    with ssh.SSHCommandRunner(node_info=info) as runner:

        nproc_result = runner.run(cmd="nproc")
        which_result = runner.run(cmd="which nvidia-settings", allow_failures=True)

        if not which_result.failed:
            cmd = "nvidia-smi --query-gpu=name --format=csv,noheader | wc -l"
            nvidia_smi_result = runner.run(cmd=cmd)

        extra_node_info = ExtraNodeInfo()

        if not nproc_result.failed:
            extra_node_info.processing_units = int(nproc_result.stdout)

        if not which_result.failed and not nvidia_smi_result.failed:
            extra_node_info.gpus = int(nvidia_smi_result.stdout)
        else:
            extra_node_info.gpus = 0

        return extra_node_info


def node_description(ip: str, username: str, extra_info: ExtraNodeInfo = None) -> str:

    description = f"{username}@{ip}"

    if extra_info is not None \
        and extra_info.gpus is not None and extra_info.processing_units is not None:
        description += f" (CPU={extra_info.processing_units}, GPU={extra_info.gpus})"

    return description


def topology(args: Namespace) -> None:

    project_data = utils.project.get_project_data(args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{args.project_dir}'")

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    head_extra_info = None
    workers_extra_info = [None] * len(cls.provider.worker_ips)

    if args.full:

        head_extra_info = get_extra_node_info(ip=cls.provider.head_ip,
                                              username=cls.auth.ssh_user,
                                              ssh_key=cls.auth.ssh_private_key)

        workers_extra_info = []

        for ip in cls.provider.worker_ips:
            extra_info = get_extra_node_info(ip=ip,
                                             username=cls.auth.ssh_user,
                                             ssh_key=cls.auth.ssh_private_key)
            workers_extra_info.append(extra_info)

    root = TreeNode(name=project_data.name)

    head = TreeNode(name="Head")
    workers = TreeNode(name="Workers")

    root.children.append(head)
    root.children.append(workers)

    # Add the head description
    head_node = TreeNode(name=node_description(ip=cls.provider.head_ip,
                                               username=cls.auth.ssh_user,
                                               extra_info=head_extra_info))
    head.children.append(head_node)

    # Add the workers descriptions
    for ip, extra_info in zip(cls.provider.worker_ips, workers_extra_info):
        worker_node = TreeNode(name=node_description(ip=ip,
                                                     username=cls.auth.ssh_user,
                                                     extra_info=extra_info))
        workers.children.append(worker_node)

    print(format_tree(
        node=astuple(root), format_node=itemgetter(0), get_children=itemgetter(1)))

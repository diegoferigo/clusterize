import copy
import invoke
import fabric
from . import base
from pathlib import Path
from functools import partial
from clusterize import structures
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, ContextManager


RunCallableGroup = Callable[[str, float, bool, bool], fabric.GroupResult]
RunCallableConnection = Callable[[str, float, bool, bool], fabric.Result]


@dataclass
class NodeConnectionInfo:

    ip: str
    username: str
    ssh_private_key: str


@dataclass
class GroupConnectionInfo:

    ips: field(default_factory=list)
    username: str
    ssh_private_key: str


class SSHCommandRunner(base.CommandRunner):

    def __init__(self, node_info: NodeConnectionInfo):

        super().__init__()
        self._connection = None
        self._node_info = node_info

    def run(self,
            cmd: str,
            timeout: float = base.DEFAULT_TIMEOUT,
            print_output: bool = False,
            allow_failures: bool = False) -> fabric.Result:

        return SSHCommandRunner.run_connection(
            connection=self.connection,
            cmd=cmd,
            timeout=timeout,
            print_output=print_output,
            allow_failures=allow_failures)

    @staticmethod
    def run_connection(connection: fabric.Connection,
                       cmd: str,
                       timeout: float = base.DEFAULT_TIMEOUT,  # TODO
                       print_output: bool = False,
                       allow_failures: bool = True) -> fabric.Result:

        if allow_failures is False:
            result = connection.run(command=cmd, hide=not print_output)

        else:
            try:
                result = connection.run(command=cmd, hide=not print_output)
            except invoke.exceptions.UnexpectedExit as e:
                result = e.result

        return result

    @staticmethod
    def connection_from_node_info(node_info: NodeConnectionInfo) -> fabric.Connection:

        ssh_private_key = Path(node_info.ssh_private_key).expanduser().absolute()

        if not ssh_private_key.exists():
            ssh_private_key = None

        connection = fabric.Connection(
            host=node_info.ip,
            user=node_info.username,
            connect_kwargs={'key_filename': str(ssh_private_key)})

        return connection

    @property
    def connection(self) -> fabric.Connection:

        if self._connection is not None:
            return self._connection

        connection = SSHCommandRunner.connection_from_node_info(node_info=self._node_info)

        self._connection = connection
        return self._connection

    def __enter__(self) -> "SSHCommandRunner":

        _ = self.connection
        return self

    def __exit__(self, *exc):

        self._connection = None


class SSHGroupCommandRunner(base.CommandGroupRunner):

    def __init__(self,
                 group_info: GroupConnectionInfo,
                 parallel: bool = False):

        super().__init__()
        self._group = None
        self._parallel = parallel
        self._group_info = group_info

    def run(self,
            cmd: str,
            timeout: float = base.DEFAULT_TIMEOUT,
            print_output: bool = False,
            allow_failures: bool = False) -> fabric.GroupResult:

        return SSHGroupCommandRunner.run_group(
            group=self.group,
            cmd=cmd,
            timeout=timeout,
            print_output=print_output,
            allow_failures=allow_failures)

    @staticmethod
    def run_group(group: fabric.Group,
                  cmd: str,
                  timeout: float = base.DEFAULT_TIMEOUT,  # TODO
                  print_output: bool = False,
                  allow_failures: bool = False):

        if allow_failures is False:
            result = group.run(command=cmd, hide=not print_output)

        else:
            try:
                result = group.run(command=cmd, hide=not print_output)
            except invoke.exceptions.UnexpectedExit as e:
                result = e.result

        return result

    @staticmethod
    def group_from_group_info(group_info: GroupConnectionInfo,
                              parallel: bool = False) -> fabric.Group:
        ssh_private_key = Path(group_info.ssh_private_key).expanduser().absolute()

        if not ssh_private_key.exists():
            ssh_private_key = None

        if not parallel:
            fabric_group_cls = fabric.SerialGroup
        else:
            fabric_group_cls = fabric.ThreadingGroup

        group = fabric_group_cls(
            *group_info.ips,
            user=group_info.username,
            connect_kwargs={'key_filename': str(ssh_private_key)})

        return group

    @property
    def group(self) -> fabric.Group:

        if self._group is not None:
            return self._group

        group = SSHGroupCommandRunner.group_from_group_info(group_info=self._group_info,
                                                            parallel=self._parallel)

        self._group = group
        return self._group

    def __enter__(self) -> "SSHGroupCommandRunner":

        _ = self.group
        return self

    def __exit__(self, *exc):

        self._group = None


class SSHClusterCommandRunner(base.CommandClusterRunner,
                              base.CommandHeadRunner,
                              base.CommandWorkersRunner):

    def __init__(self,
                 cluster: structures.cluster.Cluster,
                 parallel: bool = False):

        super().__init__()

        self._cluster = cluster
        self._parallel = parallel

    def run_in_head(self,
                    cmd: str,
                    timeout: float = base.DEFAULT_TIMEOUT,
                    print_output: bool = False,
                    allow_failures: bool = False) -> fabric.Result:

        head_info = SSHClusterCommandRunner.head_connection_info(cluster=self._cluster)
        connection = SSHCommandRunner.connection_from_node_info(node_info=head_info)

        return SSHCommandRunner.run_connection(
            connection=connection,
            cmd=cmd,
            timeout=timeout,
            print_output=print_output,
            allow_failures=allow_failures)

    def run_in_workers(self,
                       cmd: str,
                       timeout: float = base.DEFAULT_TIMEOUT,
                       print_output: bool = False,
                       allow_failures: bool = False) -> fabric.GroupResult:

        workers_info = SSHClusterCommandRunner.workers_connection_info(
            cluster=self._cluster)
        group = SSHGroupCommandRunner.group_from_group_info(
            group_info=workers_info, parallel=self._parallel)

        return SSHGroupCommandRunner.run_group(
            group=group,
            cmd=cmd,
            timeout=timeout,
            print_output=print_output,
            allow_failures=allow_failures)

    def run_in_cluster(self,
                       cmd: str,
                       timeout: float = base.DEFAULT_TIMEOUT,
                       print_output: bool = False,
                       allow_failures: bool = False) -> fabric.GroupResult:

        cluster_info = SSHClusterCommandRunner.cluster_connection_info(
            cluster=self._cluster)
        group = SSHGroupCommandRunner.group_from_group_info(
            group_info=cluster_info, parallel=self._parallel)

        return SSHGroupCommandRunner.run_group(
            group=group,
            cmd=cmd,
            timeout=timeout,
            print_output=print_output,
            allow_failures=allow_failures)

    @contextmanager
    def in_head(self) -> ContextManager[RunCallableConnection]:

        head_info = SSHClusterCommandRunner.head_connection_info(cluster=self._cluster)
        connection = SSHCommandRunner.connection_from_node_info(node_info=head_info)

        in_head = partial(SSHCommandRunner.run_connection, connection=connection)

        yield in_head

    @contextmanager
    def in_workers(self) -> ContextManager[RunCallableGroup]:

        workers_info = SSHClusterCommandRunner.workers_connection_info(
            cluster=self._cluster)

        group = SSHGroupCommandRunner.group_from_group_info(
            group_info=workers_info, parallel=self._parallel)

        in_workers = partial(SSHGroupCommandRunner.run_group, group=group)

        yield in_workers

    @contextmanager
    def in_cluster(self) -> ContextManager[RunCallableGroup]:

        cluster_info = SSHClusterCommandRunner.cluster_connection_info(
            cluster=self._cluster)

        group = SSHGroupCommandRunner.group_from_group_info(
            group_info=cluster_info, parallel=self._parallel)

        in_cluster = partial(SSHGroupCommandRunner.run_group, group=group)

        yield in_cluster

    @staticmethod
    def head_connection_info(cluster: structures.cluster.Cluster) -> NodeConnectionInfo:

        ssh_private_key = Path(cluster.auth.ssh_private_key).expanduser().absolute()

        if not ssh_private_key.exists():
            ssh_private_key = None

        info = NodeConnectionInfo(ip=cluster.provider.head_ip,
                                  username=cluster.auth.ssh_user,
                                  ssh_private_key=str(ssh_private_key))

        return info

    @staticmethod
    def workers_connection_info(cluster: structures.cluster.Cluster) \
            -> GroupConnectionInfo:

        ssh_private_key = Path(cluster.auth.ssh_private_key).expanduser().absolute()

        if not ssh_private_key.exists():
            ssh_private_key = None

        info = GroupConnectionInfo(ips=cluster.provider.worker_ips,
                                   username=cluster.auth.ssh_user,
                                   ssh_private_key=str(ssh_private_key))

        return info

    @staticmethod
    def cluster_connection_info(cluster: structures.cluster.Cluster) \
            -> GroupConnectionInfo:

        head_info = SSHClusterCommandRunner.head_connection_info(cluster=cluster)
        workers_info = SSHClusterCommandRunner.workers_connection_info(cluster=cluster)

        if head_info.username != workers_info.username:
            raise RuntimeError("Head and workers user names do not match")

        if head_info.ssh_private_key != workers_info.ssh_private_key:
            raise RuntimeError("Head and workers ssh keys do not match")

        cluster_info = copy.deepcopy(workers_info)
        cluster_info.ips.append(head_info.ip)

        return cluster_info

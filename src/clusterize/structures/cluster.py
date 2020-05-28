from typing import Dict, List
from mashumaro import DataClassYAMLMixin
from dataclasses import dataclass, field


@dataclass
class Auth(DataClassYAMLMixin):

    ssh_user: str = ""
    ssh_private_key: str = "~/.ssh/id_rsa"


@dataclass
class Provider(DataClassYAMLMixin):

    type: str = "local"
    head_ip: str = ""
    worker_ips: List[str] = field(default_factory=list)


@dataclass
class ClusterMinimal(DataClassYAMLMixin):

    cluster_name: str = ""
    auth: Auth = Auth()
    max_workers: int = 0
    min_workers: int = 0
    head_node: Dict[str, str] = field(default_factory=dict)
    worker_nodes: Dict[str, str] = field(default_factory=dict)
    file_mounts: Dict[str, str] = field(default_factory=dict)
    provider: Provider = Provider()


@dataclass
class Docker(DataClassYAMLMixin):

    image: str = ""
    container_name: str = ""
    pull_before_run: bool = True
    run_options: List[str] = field(default_factory=list)

    head_image: str = None
    worker_image: str = None
    head_run_options: List[str] = None
    worker_run_options: List[str] = None


@dataclass
class Cluster(ClusterMinimal):

    docker: Docker = None

    initialization_commands: List[str] = field(default_factory=list)
    setup_commands: List[str] = field(default_factory=list)
    head_setup_commands: List[str] = field(default_factory=list)
    worker_setup_commands: List[str] = field(default_factory=list)

    head_start_ray_commands: List[str] = field(default_factory=list)
    worker_start_ray_commands: List[str] = field(default_factory=list)

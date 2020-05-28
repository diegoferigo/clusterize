from typing import List
from mashumaro import DataClassYAMLMixin
from dataclasses import dataclass, field


@dataclass
class Cluster(DataClassYAMLMixin):
    config: str = "cluster.yaml"


@dataclass
class Command(DataClassYAMLMixin):
    name: str
    command: str


@dataclass
class Environment(DataClassYAMLMixin):
    dockerimage: str = ""
    shell: List[str] = field(default_factory=list)


@dataclass
class ProjectMinimal(DataClassYAMLMixin):

    name: str = ""
    description: str = ""

    cluster: Cluster = Cluster()
    commands: List[Command] = field(default_factory=list)
    environment: Environment = Environment()

@dataclass
class Project(ProjectMinimal):

    pass

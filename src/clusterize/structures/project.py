from typing import Dict, List, Optional
from mashumaro import DataClassYAMLMixin
from dataclasses import dataclass, field


@dataclass
class Cluster(DataClassYAMLMixin):
    config: str = "cluster.yaml"


@dataclass
class Environment(DataClassYAMLMixin):
    dockerimage: str = ""
    shell: List[str] = field(default_factory=list)


@dataclass
class Resource(DataClassYAMLMixin):

    source: str
    destination: str


@dataclass
class Command(DataClassYAMLMixin):

    run: str
    name: str = None
    shell: Optional[str] = None
    # writing_directory: str = None
    env: Dict[str,str] = field(default_factory=dict)

    # TODO:
    deploy: List[Resource] = field(default_factory=list)

    def expand(self, default_shell: str = "/bin/bash -c {}") -> str:

        import shlex
        cmd = default_shell if self.shell is None else self.shell
        print("expand", cmd.format(shlex.quote(self.run.strip())))
        print("cmd", shlex.quote(self.run.strip()))
        return cmd.format(shlex.quote(self.run.strip()))


@dataclass
class ProjectMinimal(DataClassYAMLMixin):

    name: str = ""
    description: str = ""

    cluster: Cluster = Cluster()
    commands: List[Command] = field(default_factory=list)

    setup: List[Command] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)


@dataclass
class Repository(DataClassYAMLMixin):

    url: str
    type: str = "git"
    branch: str = "master"


@dataclass
class Project(ProjectMinimal):

    repos: List[Repository] = field(default_factory=list)

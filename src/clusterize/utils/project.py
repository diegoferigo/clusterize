import os
from pathlib import Path
from clusterize import structures
from typing import List, NamedTuple, Optional


class ProjectData(NamedTuple):

    name: str
    cluster: str
    project: str
    directory: str


def find_projects(folder: str = str(Path.cwd())) -> List[ProjectData]:

    found_projects = []

    for f in os.listdir(folder):

        project_path = Path(f).expanduser().absolute()

        if (project_path / ".clusterize").exists():

            project_data = get_project_data(project_folder=str(project_path))

            if project_data is None:
                raise RuntimeError(f"Project folder {str(project_path)} is malformed")

            found_projects.append(project_data)

    return found_projects


def get_project_data(project_folder: str = str(Path.cwd())) -> Optional[ProjectData]:

    project_path = Path(project_folder).expanduser().absolute()

    if not project_path.exists():
        return None

    cluster_yaml = project_path / "cluster.yaml"
    project_yaml = project_path / "project.yaml"

    assert cluster_yaml.is_file()
    assert project_yaml.is_file()

    with open(file=cluster_yaml, mode='r') as f:
        cluster: structures.cluster.Cluster = \
            structures.cluster.Cluster.from_yaml(data=f)

    with open(file=project_yaml, mode='r') as f:
        project: structures.project.Project = \
            structures.project.Project.from_yaml(data=f)

    if project.name != cluster.cluster_name:
        raise RuntimeError(f"Project and cluster name do not match ('{project_path}')")

    project_data = ProjectData(name=project.name,
                               directory=str(project_path),
                               cluster=str(project_path / "cluster.yaml"),
                               project=str(project_path / "project.yaml"))

    return project_data

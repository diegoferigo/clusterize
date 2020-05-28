import yaml
import getpass
from pathlib import Path
from argparse import Namespace
from dataclasses import asdict
from clusterize import structures, utils


def create_cluster_yaml(project_dir: str, args: Namespace) -> None:

    cluster = structures.cluster.ClusterMinimal()

    cluster.cluster_name = args.project_name
    cluster.provider.head_ip = args.head_ip
    cluster.auth.ssh_user = getpass.getuser()

    with open(file=f"{project_dir}/cluster.yaml", mode='w') as f:
        yaml.dump(data=asdict(cluster), stream=f)


def create_project_yaml(project_dir: str, args: Namespace) -> None:

    project = structures.project.ProjectMinimal()

    project.name = args.project_name
    project.environment.dockerimage = "ubuntu:bionic"
    project.environment.shell = ['echo "Setting up the environment"']

    cmd = 'echo "Starting ray job" && wait 600'
    project.commands = [structures.project.Command(name="default", command=cmd)]

    with open(file=f"{project_dir}/project.yaml", mode='w') as f:
        yaml.dump(data=asdict(project), stream=f)


def create_dot_clusterize(project_dir: str):

    Path(f"{project_dir}/.clusterize").touch()


def create(args: Namespace) -> None:

    # Absolute path of the project
    project_dir = Path().cwd().expanduser().absolute() / args.project_name

    if project_dir.exists():
        raise RuntimeError(f"Project folder '{str(project_dir)}' already exists")

    # Create project folder
    project_dir.mkdir()

    # Populate the project directory
    create_cluster_yaml(project_dir=str(project_dir), args=args)
    create_project_yaml(project_dir=str(project_dir), args=args)
    create_dot_clusterize(project_dir=str(project_dir))

    assert utils.project.get_project_data(project_folder=str(project_dir)) \
           in utils.project.find_projects()

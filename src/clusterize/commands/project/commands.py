from argparse import Namespace
from clusterize import structures, utils


def commands(args: Namespace) -> None:

    project_data = utils.project.get_project_data(args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{project_data.directory}'")

    with open(file=project_data.project, mode='r') as f:
        prj: structures.project.Project = structures.project.Project.from_yaml(data=f)

    print(f"Active project: {prj.name}")
    print()

    if len(prj.commands) == 0:
        print("No commands found.")

    for cmd in prj.commands:
        print(f'Command "{cmd.name}":')
        print(f'  usage: {cmd.name}')

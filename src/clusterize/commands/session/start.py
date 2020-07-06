from argparse import Namespace
from clusterize.executors import ssh
from clusterize import structures, utils


# # TODO: check get_project_commands
# def get_session_env(project_name: str,
#                     session_name: str):
#
#     env = dict(
#         PROJECT_DIR=f"$CLUSTERIZE_DIR/{project_name}",
#         SESSION_DIR=f"$PROJECT_DIR/{session_name}",
#     )
#
#     return env


def start(args: Namespace) -> None:

    print(args)

    project_data = utils.project.get_project_data(args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{args.project_dir}'")

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    with open(file=project_data.project, mode='r') as f:
        prj: structures.project.Project = structures.project.Project.from_yaml(data=f)

    # Get the list of commands
    project_cmds = utils.project.get_project_commands(project=prj)

    # Get the session env
    session_env = utils.session.get_session_env(project_name=prj.name,
                                                session_name=prj.name)  # TODO

    # TODO: settare le env var nell'host in caso docker e poi forwardarle nel container?
    # tipo -e CLUSTERIZE_DIR -e PROJECT_DIR ...
    # Resolve the session env
    # utils.session.resolve_env(env=session_env)

    # Dockerize if needed
    if cls.docker is not None:
        project_cmds = utils.project.dockerize_commands(commands=project_cmds,
                                                        cluster=cls,
                                                        env=session_env)

    with ssh.SSHClusterCommandRunner(cluster=cls, parallel=True).in_cluster() as run:

        for cmd in project_cmds:
            _ = run(cmd=cmd.expand(), print_output=True, env=session_env)

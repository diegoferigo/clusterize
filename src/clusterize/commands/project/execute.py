import shlex
from pathlib import Path
from argparse import Namespace
from clusterize.utils import project
from clusterize.executors import ssh
from clusterize import commands, structures, utils


def resolve_resource(resource: structures.project.Resource,
                     project_dir: str,
                     project: structures.project.Project,
                     cluster: structures.cluster.Cluster) \
    -> structures.project.Resource:

    source = Path(resource.source).expanduser()

    if not source.is_absolute():
        source = (project_dir / source).expanduser().absolute()

    if not source.is_file():
        raise FileNotFoundError(resource.source)

    # Destination resources could use env variables that need to be resolved
    # (e.g. CLUSTERIZE_DIR or SESSION_DIR)
    with ssh.SSHClusterCommandRunner(cluster=cluster).in_head() as run:

        session_env = utils.session.get_session_env(project_name=project.name,
                                                    session_name=project.name)

        result = run(cmd=f"echo {resource.destination}", env=session_env)
        destination = Path(result.stdout.strip()).expanduser().absolute()

    if not destination.is_absolute():
        raise RuntimeError("The destination path of the resource must be absolute")

    resolved_resource = structures.project.Resource(source=str(source),
                                                    destination=str(destination))

    # print(resolved_resource)
    return resolved_resource


def deploy_resource(resource: structures.project.Resource,
                    node_info: ssh.NodeConnectionInfo) -> None:

    # print("res", resource)

    if not Path(resource.source).is_file():
        raise FileNotFoundError(resource.source)

    with ssh.SSHCommandRunner(node_info=node_info) as runner:

        # result = runner.run(cmd=f"echo {resource.destination}")
        # print(result.stdout)
        # raise

        _ = runner.run(cmd=f"mkdir -p {resource.destination}")
        _ = runner.connection.put(local=resource.source, remote=resource.destination)


def execute(args: Namespace) -> None:

    print(args)

    project_data = project.get_project_data(args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{args.project_dir}'")

    with open(file=project_data.project, mode='r') as f:
        prj: structures.project.Project = structures.project.Project.from_yaml(data=f)

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    cmds = [cmd for cmd in prj.commands if cmd.name == args.command]

    if len(cmds) != 1:
        raise RuntimeError(f"Failed to find command '{args.command}'")

    cmd: structures.project.Command = cmds[0]
    print(cmd)

    if len(cmd.deploy) != 0:
        for resource in cmd.deploy:

            resolved_res = resolve_resource(resource=resource,
                                            project_dir=project_data.directory,
                                            project=prj,
                                            cluster=cls)

            head_node_info = ssh.SSHClusterCommandRunner.head_connection_info(cluster=cls)
            deploy_resource(resource=resolved_res, node_info=head_node_info)

    if args.session is None:
        args.session = project_data.name

    # Get the session env
    session_env = utils.session.get_session_env(project_name=prj.name,
                                                session_name=prj.name)  # TODO

    if cls.docker is not None:
        cmd = utils.project.dockerize_commands(commands=[cmd],
                                               cluster=cls,
                                               env=session_env)[0]

    with ssh.SSHClusterCommandRunner(cluster=cls, parallel=True).in_head() as run:

        if args.tmux:
            byobu = utils.tmux.Byobu(runner=run, env=session_env)
            byobu.create_session(session_name=f"{project_data.name}_{cmd.name}")
            byobu.execute(session_name=f"{project_data.name}_{cmd.name}",
                          command=cmd.expand())
        else:
            _ = run(cmd=cmd.expand(), print_output=True, env=session_env)

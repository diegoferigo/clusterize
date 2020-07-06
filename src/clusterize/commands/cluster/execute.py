from argparse import Namespace
from clusterize.executors import ssh
from clusterize import structures, utils


def execute(args: Namespace) -> None:

    print(args)

    project_data = utils.project.get_project_data(args.project_dir)

    if project_data is None:
        raise RuntimeError(f"No project found in '{args.project_dir}'")

    with open(file=project_data.cluster, mode='r') as f:
        cls: structures.cluster.Cluster = structures.cluster.Cluster.from_yaml(data=f)

    if args.session is None:
        args.session = project_data.name

    command = args.command + " " + " ".join(args.args)

    if args.docker:
        cname = utils.docker.get_container_name(cluster=cls, session=args.session)
        command = utils.docker.wrap_in_docker(cmd=command, container_name=cname)

    if args.tmux and args.on != "HEAD":
        raise ValueError("Tmux can only run in the head node")

    if args.on == "HEAD":
        with ssh.SSHClusterCommandRunner(cluster=cls, parallel=True).in_head() as run:

            if args.tmux:
                byobu = utils.tmux.Byobu(runner=run)
                byobu.create_session(session_name=f"{project_data.name}_{args.command}",
                                     command=command)
            else:
                _ = run(cmd=command, disown=args.tmux)

    elif args.on == "WORKERS":
        with ssh.SSHClusterCommandRunner(cluster=cls, parallel=True).in_workers() as run:
            _ = run(cmd=command, print_output=True)

    elif args.on == "CLUSTER":
        with ssh.SSHClusterCommandRunner(cluster=cls, parallel=True).in_cluster() as run:
            _ = run(cmd=command, print_output=True)

    else:
        raise RuntimeError(f"'{args.on}' not recognized")

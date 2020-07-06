import os
import sys
import inspect
import argparse
import netifaces
from . import commands
from pathlib import Path
from typing import Tuple, NamedTuple, List


class ClusterCmdLine:

    @classmethod
    def cluster(cls):

        cluster_parser = argparse.ArgumentParser(
            description="Cluster manager.",
            prog=os.path.basename(sys.argv[0]) + " " + sys.argv[1])

        choices = ["start", "stop", "topology", "execute"]
        cluster_parser.add_argument("subcommand", type=str, choices=choices, help="")

        args, _ = cluster_parser.parse_known_args(sys.argv[2:3])

        if not hasattr(cls, "_cluster_" + args.subcommand):
            print(f"Unrecognized command '{args.command}'\n")
            cluster_parser.print_help()
            exit(1)

        return getattr(cls, "_cluster_" + args.subcommand)()

    @staticmethod
    def _cluster_start():

        start_parser = argparse.ArgumentParser(
            description="Start a session based on current project config.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        start_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        start_parser.add_argument(
            "--session", metavar="NAME",
            help="A name to tag the session with (default: the project name)")

        args, extra = start_parser.parse_known_args(sys.argv[3:])
        commands.cluster.start.start(args)

    @staticmethod
    def _cluster_stop():

        stop_parser = argparse.ArgumentParser(
            description="Stop a session based on current project config.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        stop_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        stop_parser.add_argument(
            "--session", metavar="NAME",
            help="The tag of the active session. If not passed all the project's "
                 "sessions are stopped.")

        args, extra = stop_parser.parse_known_args(sys.argv[3:])
        commands.cluster.stop.stop(args)

    @staticmethod
    def _cluster_topology():

        commands_parser = argparse.ArgumentParser(
            description="Print the cluster topology of the project.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        commands_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        commands_parser.add_argument(
            "--full", action="store_true", default=False,
            help="Gather extra information from the nodes "
                 "(by connecting to the nodes)")

        args, extra = commands_parser.parse_known_args(sys.argv[3:])
        commands.cluster.topology.topology(args)

    @staticmethod
    def _cluster_execute():

        command = os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3])
        example = inspect.cleandoc(f"""
                example:
                    {command} --session exp1 --project foo --shell ls -al 
                """)
        # TODO: docker?
        # TODO: required args?

        execute_parser = argparse.ArgumentParser(
            description="Execute a command in a session.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]),
            epilog=example,
            formatter_class=argparse.RawDescriptionHelpFormatter)

        execute_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        execute_parser.add_argument(
            "command", metavar="CMD", type=str,
            help="The command to execute")

        execute_parser.add_argument(
            "args", type=str, nargs=argparse.REMAINDER,
            help="The optional command arguments")

        choices = ["HEAD", "CLUSTER", "WORKERS"]
        execute_parser.add_argument(
            "--on", metavar="NODE", type=str, choices=choices, default="HEAD",
            help=f"The node(s) where to run the command: {{{', '.join(choices)}}} "
                 f"(default: %(default)s)")

        execute_parser.add_argument(
            "--session", metavar="NAME", type=str,
            help="The session name (default: the project name)")

        execute_parser.add_argument(
            "--docker", action="store_true", default=False,
            help="Execute the command in the docker containers if the cluster has docker "
                 "support")

        execute_parser.add_argument(
            "--tmux", action="store_true", default=False,
            help="Execute the command in a persistent tmux session")

        args, extra = execute_parser.parse_known_args(sys.argv[3:])
        commands.cluster.execute.execute(args)


class ProjectCmdLine:

    @classmethod
    def project(cls):
        project_parser = argparse.ArgumentParser(
            description="Project manager.",
            prog=os.path.basename(sys.argv[0]) + " " + sys.argv[1])

        choices = ["create", "list", "commands", "execute"]
        project_parser.add_argument("subcommand", type=str, choices=choices, help="")

        args, _ = project_parser.parse_known_args(sys.argv[2:3])

        if not hasattr(cls, "_project_" + args.subcommand):
            print(f"Unrecognized command '{args.command}'\n")
            project_parser.print_help()
            exit(1)

        return getattr(cls, "_project_" + args.subcommand)()

    @staticmethod
    def _project_create():

        create_parser = argparse.ArgumentParser(
            description="Create a new project in the current directory.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        create_parser.add_argument(
            "project_name", metavar="NAME", type=str,
            help='The name of the project')

        # From https://stackoverflow.com/a/55613158/12150968
        interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        default_ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        create_parser.add_argument(
            "--head-ip", metavar="IP", default=default_ip,
            help="The IP address of the head node (default: %(default)s)")

        args, extra = create_parser.parse_known_args(sys.argv[3:])
        commands.project.create.create(args)

    @staticmethod
    def _project_list():

        list_parser = argparse.ArgumentParser(
            description="List the projects found in a directory.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        list_parser.add_argument(
            "--dir", metavar="DIR", type=str,
            default=Path().cwd().expanduser().absolute(),
            help="The directory containing the projects to list (default: pwd)")

        args, extra = list_parser.parse_known_args(sys.argv[3:])
        commands.project.listprj.listprj(args)

    @staticmethod
    def _project_commands():

        commands_parser = argparse.ArgumentParser(
            description="Print available commands for sessions of this project.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        commands_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        args, extra = commands_parser.parse_known_args(sys.argv[3:])
        commands.project.commands.commands(args)

    @staticmethod
    def _project_execute():

        execute_parser = argparse.ArgumentParser(
            description="Execute a command in a session.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]),
            formatter_class=argparse.RawDescriptionHelpFormatter)

        execute_parser.add_argument(
            "command", metavar="CMD", type=str,
            help="The command to execute")

        execute_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        execute_parser.add_argument(
            "--tmux", action="store_true", default=False,
            help="Execute the command in a persistent tmux session")

        execute_parser.add_argument(
            "--session", metavar="NAME", type=str,
            help="The session name (default: the project name)")

        args, extra = execute_parser.parse_known_args(sys.argv[3:])
        commands.project.execute.execute(args)


class SessionCmdLine:

    @classmethod
    def session(cls):
        session_parser = argparse.ArgumentParser(
            description="Session manager.",
            prog=os.path.basename(sys.argv[0]) + " " + sys.argv[1])

        choices = ["list", "start"]
        session_parser.add_argument("subcommand", type=str, choices=choices, help="")

        args, _ = session_parser.parse_known_args(sys.argv[2:3])

        if not hasattr(cls, "_session_" + args.subcommand):
            print(f"Unrecognized command '{args.command}'\n")
            session_parser.print_help()
            exit(1)

        return getattr(cls, "_session_" + args.subcommand)()

    @staticmethod
    def _session_list():

        list_parser = argparse.ArgumentParser(
            description="List the sessions found in the cluster.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        list_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        args, extra = list_parser.parse_known_args(sys.argv[3:])
        commands.session.listsess.listsess(args)

    @staticmethod
    def _session_start():

        start_parser = argparse.ArgumentParser(
            description="Start a new project sessions.",
            prog=os.path.basename(sys.argv[0]) + " " + " ".join(sys.argv[1:3]))

        start_parser.add_argument(
            "project_dir", metavar="DIR", type=str,
            help="The directory of the project")

        args, extra = start_parser.parse_known_args(sys.argv[3:])
        commands.session.start.start(args)


class CmdLineParser(ClusterCmdLine, ProjectCmdLine, SessionCmdLine):

    def __init__(self):

        # Main parser
        self.parser = argparse.ArgumentParser(
            description="Manage Ray cluster experiments.")

        # Configure the accepted commands
        choices = ["cluster", "project", "session"]
        self.parser.add_argument("command", type=str, choices=choices, help="")

    def parse(self) -> Tuple[NamedTuple, List[str]]:

        args = self.parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print(f"Unrecognized command '{args.command}'\n")
            self.parser.print_help()
            exit(1)

        return getattr(self, args.command)()

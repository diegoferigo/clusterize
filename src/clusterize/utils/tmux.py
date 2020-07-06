import shlex
from typing import Callable, Dict, List


class Byobu:

    def __init__(self, runner: Callable, env: Dict[str, str] = None):

        self.env = env
        self.run = runner

    def get_sessions(self) -> List[str]:

        # Check if we need to address this on old byobu versions:
        # https://askubuntu.com/questions/927187/byobu-cache-or-restored-duplicate-sessions
        result = self.run(
            cmd='byobu-tmux ls | tr -s " " | cut -d " " -f 1 | rev | cut -c 2- | rev')

        sessions_str = result.stdout
        sessions_str = sessions_str.strip()

        return sessions_str.split("\n")

    def get_windows(self, session_name: str) -> Dict[int, str]:

        if session_name not in self.get_sessions():
            return {}

        cmd = f'byobu-tmux list-windows -t {session_name} | tr -s " " | cut -d " " -f 1,2'
        result = self.run(cmd=cmd)

        windows_str = result.stdout
        windows_list = windows_str.strip().split("\n")
        windows_dict = \
            {int(w.split(":")[0].strip()): w.split(":")[1].strip() for w in windows_list}

        return windows_dict

    def create_session(self,
                       session_name: str,
                       window_name: str = None,
                       command: str = "") -> None:

        if session_name in self.get_sessions():
            raise ValueError(f"Session {session_name} already exists")

        if window_name is None:
            w_name = ""
        else:
            w_name = f"-n {window_name}"

        # TODO: use shell utils to escape other '?
        if command != "":
            command = shlex.quote(command)
            # command = f"'{command}'"

        cmd = f"byobu-tmux new-session -d -s {session_name} {w_name} {command}"
        print("===", cmd)
        _ = self.run(cmd=cmd, env=self.env)

    def kill_session(self, session_name: str) -> None:

        if session_name not in self.get_sessions():
            return

        _ = self.run(cmd=f"byobu-tmux kill-session -t {session_name}")

    def kill_window(self, session_name: str, window_id: int) -> None:

        if session_name not in self.get_sessions():
            return

        if window_id not in self.get_windows(session_name=session_name).keys():
            return

        _ = self.run(cmd=f"byobu-tmux kill-window -t {window_id}")

    def create_window(self, session_name: str, window_name = None) -> None:  # TODO win_id

        if session_name not in self.get_sessions():
            self.create_session(session_name=session_name)

        if window_name is None:
            w_name = ""
        else:
            w_name = f"-n {window_name}"

        cmd = f'byobu-tmux new-window -t {session_name} {w_name}'
        _ = self.run(cmd=cmd, env=self.env)

    def execute(self, session_name: str, command: str, window_id: int = None) -> None:

        if session_name not in self.get_sessions():
            self.create_session(session_name=session_name)

        if window_id is None:
            window_id = ""
        else:
            if window_id in self.get_windows(session_name=session_name).keys():
                window_id = f":{window_id}"
            else:
                raise ValueError(
                    f"Window #{window_id} not found in session '{session_name}'")

        cmd = f"byobu-tmux send -t {session_name}{window_id} -- {shlex.quote(command)} ENTER"
        print("cmd", cmd)
        _ = self.run(cmd=cmd, env=self.env)

    # def attach(self, session_name: str) -> None:
    #
    #     if session_name not in self.get_sessions():
    #         self.create_session(session_name=session_name)
    #
    #     # _ = self.run(cmd=f"byobu-tmux attach -t {session_name}", pty=True, asynchronous=True)
    #     self.run(cmd="bash", pty=True, print_output=True)

        # aync?

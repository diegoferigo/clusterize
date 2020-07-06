import abc
import fabric
from typing import Dict

DEFAULT_TIMEOUT = 600.0


class CommandRunner(abc.ABC):

    @abc.abstractmethod
    def run(self,
            cmd: str,
            env: Dict[str, str] = None,
            print_output: bool = False,
            allow_failures: bool = False,
            timeout: float = DEFAULT_TIMEOUT,
            asynchronous: bool = False,
            disown: bool = False) -> fabric.Result:
        pass


class CommandGroupRunner(abc.ABC):

    @abc.abstractmethod
    def run(self,
            cmd: str,
            env: Dict[str, str] = None,
            print_output: bool = False,
            allow_failures: bool = True,
            timeout: float = DEFAULT_TIMEOUT,
            asynchronous: bool = False,
            disown: bool = False) -> fabric.GroupResult:
        pass


class CommandHeadRunner(abc.ABC):

    @abc.abstractmethod
    def run_in_head(self,
                    cmd: str,
                    env: Dict[str, str] = None,
                    print_output: bool = False,
                    allow_failures: bool = True,
                    timeout: float = DEFAULT_TIMEOUT,
                    asynchronous: bool = False,
                    disown: bool = False) -> fabric.Result:
        pass


class CommandWorkersRunner(abc.ABC):

    @abc.abstractmethod
    def run_in_workers(self,
                       cmd: str,
                       env: Dict[str, str] = None,
                       print_output: bool = False,
                       allow_failures: bool = True,
                       timeout: float = DEFAULT_TIMEOUT,
                       asynchronous: bool = False,
                       disown: bool = False) -> fabric.GroupResult:
        pass


class CommandClusterRunner(abc.ABC):

    @abc.abstractmethod
    def run_in_cluster(self,
                       cmd: str,
                       env: Dict[str, str] = None,
                       print_output: bool = False,
                       allow_failures: bool = True,
                       timeout: float = DEFAULT_TIMEOUT,
                       asynchronous: bool = False,
                       disown: bool = False) -> fabric.GroupResult:
        pass

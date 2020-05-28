import abc
import fabric

DEFAULT_TIMEOUT = 30.0


class CommandRunner(abc.ABC):

    @abc.abstractmethod
    def run(self,
            cmd: str,
            timeout: float = DEFAULT_TIMEOUT,
            print_output: bool = False,
            allow_failures: bool = True) -> fabric.Result:
        pass


class CommandGroupRunner(abc.ABC):

    @abc.abstractmethod
    def run(self,
            cmd: str,
            timeout: float = DEFAULT_TIMEOUT,
            print_output: bool = False,
            allow_failures: bool = True) -> fabric.GroupResult:
        pass


class CommandHeadRunner(abc.ABC):

    @abc.abstractmethod
    def run_in_head(self,
                    cmd: str,
                    timeout: float = DEFAULT_TIMEOUT,
                    print_output: bool = False,
                    allow_failures: bool = True) -> fabric.Result:
        pass


class CommandWorkersRunner(abc.ABC):

    @abc.abstractmethod
    def run_in_workers(self,
                       cmd: str,
                       timeout: float = DEFAULT_TIMEOUT,
                       print_output: bool = False,
                       allow_failures: bool = True) -> fabric.GroupResult:
        pass


class CommandClusterRunner(abc.ABC):

    @abc.abstractmethod
    def run_in_cluster(self,
                       cmd: str,
                       timeout: float = DEFAULT_TIMEOUT,
                       print_output: bool = False,
                       allow_failures: bool = True) -> fabric.GroupResult:
        pass

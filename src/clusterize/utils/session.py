import fabric
from typing import Union, Dict
from collections import OrderedDict


def get_session_env(project_name: str,
                    session_name: str) -> OrderedDict:
    # TODO: check get_project_commands
    env = OrderedDict(
        PROJECT_DIR=f"$CLUSTERIZE_DIR/{project_name}",
        SESSION_DIR=f"$PROJECT_DIR/{session_name}",
    )

    return env


def get_inline_env(env: Union[Dict, OrderedDict]) -> str:

    inline_env = []

    for var, value in env.items():
        inline_env.append(f"export {var}={value}")

    return " && ".join(inline_env)


# def resolve_env(env: Union[Dict, OrderedDict],
#                 connection: fabric.Connection) -> OrderedDict:
#
#     resolved_env = OrderedDict()
#     inlined_env = get_inline_env(env=env)
#
#     for var in env.keys():
#         result = connection.run(cmd=f"{inlined_env} && echo ${var}")
#         resolved_env[var] = result.stdout.strip()
#
#     print(resolved_env)
#     return resolved_env


# def resolve_env(env: Union[Dict, OrderedDict], connection: fabric.Connection) \
#         -> Union[Dict, OrderedDict]:
#
#     # TODO: aggiungere manualmente gli export VAR=VALUE in ordine e vonde
#
#     resolved_env = OrderedDict()
#
#     for var, value in env.items():
#     # for item in env.items():
#
#         # print(env)
#         # env
#         print("testing", var, value)
#         resolved_env.update([(var, value)])
#
#         _ = connection.run(command=f"env",
#                            env=resolved_env)
#
#         result = connection.run(command=f"echo ${var}",
#                                 env=resolved_env,
#                                 hide=True)
#
#         resolved_value = result.stdout
#         resolved_value = resolved_value.strip()
#
#         resolved_env.update([(var, resolved_value)])
#
#         # env[var] = result.stdout
#         # env[var] = env[var].strip()
#
#         print(resolved_env)
#     raise
#     return resolved_env

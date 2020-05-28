from setuptools import setup, find_packages


setup(
    name="clusterize",
    version="1.0",
    author="Diego Ferigo",
    author_email="diego.ferigo@iit.com",
    description="Tool to manage a cluster with docker support",
    url="https://github.com/diegoferigo/clusterize",
    license="LGPL",
    platforms='any',
    python_requires='>=3.6',
    keywords="cluster distributed ssh docker rl ml",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    ],
    use_scm_version={
        "local_scheme": "dirty-tag",
    },
    setup_requires=["setuptools_scm"],
    packages=find_packages("src"),
    package_dir={'': "src"},
    zip_safe=False,
    install_requires=[
        "pyyaml",
        "invoke",
        "fabric",
        "mashumaro",
        "netifaces",
        "tree-format",
        "dataclasses",
    ],
    entry_points={
        "console_scripts": [
            "clusterize=clusterize.__main__:main",
        ],
    },
)

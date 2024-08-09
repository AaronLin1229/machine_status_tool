from setuptools import setup, find_packages

setup(
    name="machine_status_tool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tabulate",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "mst=machine_status_tool.__main__:main",
        ],
    },
)
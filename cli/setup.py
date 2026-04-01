from setuptools import find_packages, setup


setup(
    name="polonium-cli",
    version="0.1.0",
    description="Polonium command line interface",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "polonium=polonium_cli.main:run",
        ]
    },
)


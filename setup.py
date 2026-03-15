from setuptools import setup, find_packages
from typing import List


def get_requirements() -> List[str]:
    """
    This function returns the list of requirements
    """
    requirement_list: List[str] = []

    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()

            for line in lines:
                requirement = line.strip()

                if requirement and requirement != "-e .":
                    requirement_list.append(requirement)

    except FileNotFoundError:
        pass

    return requirement_list
setup(
    name="network_security_ds_project",
    version="0.0.1",
    author="Ranjit Pawar",
    author_email="ranjitpawar@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)
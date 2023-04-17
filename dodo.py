"""Doit function."""
import glob
from sys import platform

DOIT_CONFIG = {'default_tasks': ['babel', 'style', 'docstyle', 'docs', 'test', 'wheel', 'sdist']}
project_dir = "netjudge"
domain = "netjudge"
podir = "netjudge/po"
python_exec = ''

if platform.startswith('win'):
    python_exec = 'python'
else:
    python_exec = 'python3'
    if not platform.startswith('linux'):
        print('Your platform may not be supported!')


def task_babel():
    """Update and compile translation"""
    return {
        "actions": [f"pybabel extract -o {podir}/{domain}.pot --input-dirs={project_dir}",
                    f"pybabel update -l ru -D {domain} -i {podir}/{domain}.pot -d {podir}",
                    f"pybabel compile -l ru -D {domain} -d {podir}"],
        'targets': [f'{podir}/{domain}.pot', f'{podir}/ru/LC_MESSAGES/{domain}.mo'],
        "clean": True,
    }


def task_test():
    """Run tests"""
    return {
        "actions": [f"{python_exec} -m unittest -v tests/test_appcmd.py"],
    }


def task_wheel():
    """Build a wheel"""
    return {
        "actions": [f"{python_exec} -m build -w"],
        "file_dep": [f"{podir}/ru/LC_MESSAGES/{domain}.mo"],
    }


def task_sdist():
    """Build a cdist"""
    return {
        "actions": [f"{python_exec} -m build -s"],
        "file_dep": [f"{podir}/ru/LC_MESSAGES/{domain}.mo"],
    }


def task_cleanup():
    """Remove all"""
    return {
        "actions": [f"rm {podir}/{domain}.pot",
                    f"rm {podir}/ru/LC_MESSAGES/{domain}.mo"]
    }


def task_style():
    """Check style against flake8."""
    return {
        "actions": ["flake8"]
    }


def task_docstyle():
    """Check docstrings against pydocstyle."""
    return {
        "actions": ["pydocstyle"]
    }


def task_docs():
    """Make HTML documentation."""
    return {
        "actions": ["sphinx-build -M html docs docs/_build"],
        "file_dep": glob.glob("*py") + glob.glob("*rst"),
        "targets": ["_build"],
        "clean": True,
    }

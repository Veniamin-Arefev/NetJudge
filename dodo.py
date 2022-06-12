DOIT_CONFIG = {'default_tasks': ['babel', 'test', 'wheel', 'sdist']}
domain = "netjudge"
version = "1.0.0"
podir = "po"

def task_babel():
    """Update and compile translation"""
    return {
        "actions": [f"pybabel extract -o {podir}/{domain}.pot --input-dirs=.",
                    f"pybabel update -l ru -D {domain} -i {podir}/{domain}.pot -d {podir}",
                    f"pybabel compile -l ru -D {domain} -d {podir}"],
        'targets': [f'{podir}/{domain}.pot', f'{podir}/ru/LC_MESSAGES/{domain}.mo'],
        "clean": True,
    }

def task_test():
    """Run tests"""
    return {
        "actions": ["python -m unittest -v"],
    }

def task_wheel():
    """Build a wheel"""
    return {
        "actions": ["python -m build -w"],
        "file_dep": [f"{podir}/ru/LC_MESSAGES/{domain}.mo"],
        "targets": [f"dist/{domain}-{version}-py3-none-any.whl"]
    }

def task_sdist():
    """Build a cdist"""
    return {
        "actions": ["python -m build -s"],
        "file_dep": [f"{podir}/ru/LC_MESSAGES/{domain}.mo"],
        "targets": [f"dist/{domain}-{version}.tar.gz"]
    }

def task_cleanup():
    """Remove all"""
    return {
        "actions": [f"rm {podir}/{domain}.pot",
                    f"rm {podir}/ru/LC_MESSAGES/{domain}.mo"]
    }
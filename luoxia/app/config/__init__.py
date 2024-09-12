from pathlib import Path

from luoxia.app.config.config import Configuration
from luoxia.app.config.log import LOG

CONF = Configuration()

ROOT_DIR = None


def get_project_root():
    global ROOT_DIR
    LOG.debug(f"first load config. ROOT_DIR: {ROOT_DIR}")
    if ROOT_DIR:
        LOG.debug("n load config")
        return
    ROOT_DIR = Path(__file__).resolve().parent
    for parent in ROOT_DIR.parents:
        if (
            (parent / ".git").exists()
            or (parent / "pyproject.toml").exists()
            or (parent / "setup.py").exists()
        ):
            ROOT_DIR = parent
            break
    LOG.debug(f"project base dir {ROOT_DIR}")


get_project_root()

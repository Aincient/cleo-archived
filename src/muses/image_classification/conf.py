import os

__all__ = (
    'gettext',
    'project_dir',
    'PROJECT_DIR',
)


def project_dir(base):
    """Absolute path to a file from current directory."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), base).replace('\\', '/')
    )


def gettext(val):
    """Dummy gettext."""
    return val


PROJECT_DIR = project_dir


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

IMAGE_CLASSIFICATION_DIR = BASE_DIR[:]

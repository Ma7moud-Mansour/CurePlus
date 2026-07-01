import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VENV_SITE_PACKAGES = BASE_DIR.parent / "venv" / "Lib" / "site-packages"

sys.path.insert(0, str(VENV_SITE_PACKAGES))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CurePlus.settings")

from django.core.management import execute_from_command_line


if __name__ == "__main__":
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000", "--noreload"])

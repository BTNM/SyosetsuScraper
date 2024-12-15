import os
from pathlib import Path

# ProjectDirectory = "/d/VisualStudioProjects/SyosetsuScraper"
PROJECT_ROOT_PATH = Path.cwd()
STORAGE_PATH = os.path.abspath(
    os.path.join(
        PROJECT_ROOT_PATH,
        "src",
        "storage",
    )
)

import sys
import pytest
from pathlib import Path
from utils.config import get_config

# Ensure root dir is in path for imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Register Plugins
pytest_plugins = [
    "tests.plugins.hooks",
    "tests.plugins.core",
    "tests.plugins.data",
    "tests.plugins.actors_api",
    "tests.plugins.actors_ui",
    "tests.plugins.pages",
    "tests.plugins.mongodb_fixtures",
    "tests.plugins.api_fixtures",
]

def pytest_addoption(parser):
    parser.addoption(
        "--env", 
        action="store", 
        default="staging", 
        help="Environment to run tests against: local, staging, production"
    )

@pytest.fixture(scope="session")
def env_config(request):
    """
    Returns the configuration object for the selected environment.
    """
    env_name = request.config.getoption("--env")
    return get_config(env_name)

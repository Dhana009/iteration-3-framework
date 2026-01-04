import sys
import pytest
from pathlib import Path
from utils.config import get_config
from playwright.sync_api import Browser
from dotenv import load_dotenv

# Load env vars
load_dotenv()

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
    "tests.plugins.seed_fixtures",
    "tests.plugins.api_fixtures",
    "pytest_playwright",
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

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Override browser launch args to run in headed mode (visible browser).
    """
    return {
        **browser_type_launch_args,
        "headless": False,  # Run browser in headed mode (visible)
        "slow_mo": 500,  # Slow down operations by 500ms for visibility
    }

"""Shared constants for config parsing and CLI selection."""

# Config file names
DEFAULT_CONFIG_FILENAME = "foga.yml"

# Top-level config sections
PROJECT_SECTION = "project"
BUILD_SECTION = "build"
TEST_SECTION = "test"
FORMAT_SECTION = "format"
LINT_SECTION = "lint"
DEPLOY_SECTION = "deploy"
CLEAN_SECTION = "clean"
PROFILES_SECTION = "profiles"

# Nested config keys
RUNNERS_KEY = "runners"
TARGETS_KEY = "targets"

# Workflow selections
CPP_WORKFLOW_KIND = "cpp"
PYTHON_WORKFLOW_KIND = "python"
ALL_WORKFLOW_SELECTION = "all"

WORKFLOW_KINDS = (CPP_WORKFLOW_KIND, PYTHON_WORKFLOW_KIND)
WORKFLOW_SELECTIONS = (*WORKFLOW_KINDS, ALL_WORKFLOW_SELECTION)

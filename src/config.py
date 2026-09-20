from pathlib import Path
import yaml


def load_config(path):
    """Load and minimally validate the frozen analysis configuration."""
    path = Path(path)
    with path.open() as stream:
        config = yaml.safe_load(stream) or {}
    required = {"seed", "primary_tasks", "context_tasks", "data"}
    missing = required - set(config)
    if missing:
        raise ValueError(f"config missing required keys: {sorted(missing)}")
    tasks = set(config["primary_tasks"]) | set(config["context_tasks"])
    if len(tasks) != len(config["primary_tasks"]) + len(config["context_tasks"]):
        raise ValueError("primary_tasks and context_tasks must not overlap")
    return config

import git
import sys
import importlib
from pathlib import Path


def clone_repo(repo_url, commit_hash, run_dir):
    repo_path = run_dir / repo_url.split("/")[-1]
    git.Repo.clone_from(repo_url, repo_path)
    repo = git.Repo(repo_path)
    repo.git.checkout(commit_hash)
    return repo_path


def import_function_from_repo(repo_path: Path, module_name: str, function_name: str):
    """
    Import a specific function from a module within the cloned repo.

    Args:
    - repo_path: Path to the cloned repository.
    - module_path: Relative path to the module (e.g., "evaluate.py").
    - function_name: Name of the function to import.

    Returns:
    - The imported function.
    """
    # Construct the full module path
    full_module_path = repo_path / module_name

    # Load the module
    spec = importlib.util.spec_from_file_location(
        "loaded_module", str(full_module_path)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the function from the module
    func = getattr(module, function_name)
    return func

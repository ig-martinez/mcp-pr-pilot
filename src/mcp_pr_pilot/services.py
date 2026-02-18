import os
import subprocess
from pathlib import Path

from .diff_types import DiffType


def get_pr_template_path() -> str | None:
    """Get the PR template path from environment variable."""
    return os.environ.get('PR_TEMPLATE_PATH')


def read_pr_template(repo_path: str = '.') -> str | None:
    """Read the PR template file if configured.
    
    Args:
        repo_path: The repository path to resolve relative template paths against.
    """
    template_path = get_pr_template_path()
    if not template_path:
        return None
    
    try:
        path = Path(template_path).expanduser()
        
        # If path is not absolute, resolve it relative to repo_path
        if not path.is_absolute():
            path = (Path(repo_path) / path).resolve()
        else:
            path = path.resolve()
        
        if path.exists() and path.is_file():
            return path.read_text(encoding='utf-8')
        else:
            return None
    except Exception:
        return None


def get_git_diff(diff_type: DiffType = DiffType.WORKING, branch: str = 'main', repo_path: str = '.') -> str:
    try:
        if diff_type == DiffType.WORKING:
            cmd = ['git', 'diff']
        elif diff_type == DiffType.BRANCH_COMPARE:
            cmd = ['git', 'diff', f'{branch}...']
        elif diff_type == DiffType.STAGED:
            cmd = ['git', 'diff', '--cached']
        elif diff_type == DiffType.COMMITTED:
            cmd = ['git', 'diff', f'{branch}..HEAD']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f'Error running git diff: {e.stderr.strip()}'

import click
import os
from pathlib import Path
import subprocess
from typing import Optional


def env_validate(api_type: str):
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set")

    if api_type == "azure":
        if not os.environ.get("AZURE_API_VERSION"):
            raise ValueError("AZURE_API_VERSION is not set")

        if not os.environ.get("AZURE_RESOURCE_NAME"):
            raise ValueError("AZURE_RESOURCE_NAME is not set")


def get_git_diff(
    repo_root: str,
    old_hash: str = None,
    new_hash: str = None,
) -> str:
    cmd = ["git", "diff"]
    if old_hash:
        cmd.append(old_hash)
    if new_hash:
        cmd.append(new_hash)

    diff_output = subprocess.check_output(cmd, cwd=repo_root)
    diff_str = diff_output.decode("utf-8")

    return diff_str


def get_current_docs(docs_dir: str) -> dict[str, str]:
    docs = os.listdir(docs_dir)
    current_docs = {}

    for doc in docs:
        with open(f"{docs_dir}/{doc}", "r") as f:
            current_docs[doc] = f.read()

    return current_docs


@click.command()
@click.option("--repo", default=None, help="The path to the repository.")
@click.option(
    "--docs-dir", default="docs", help="The path to documents in the repository."
)
@click.option(
    "--api-type", default="openai", help="The API type to use. Defaults to OpenAI."
)
def main(repo: Optional[str], docs_dir: str, api_type: str) -> None:
    env_validate(api_type)

    if not repo:
        repo = os.getcwd()

    repo = Path(repo)
    docs_dir = Path(docs_dir)

    diff = get_git_diff(repo)
    docs_dict = get_current_docs(repo / docs_dir)

    click.echo(f"Ditected documents: {list(docs_dict.keys())}")


if __name__ == "__main__":
    main()

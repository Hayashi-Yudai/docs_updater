import difflib
import json
import os
from pathlib import Path
import re
import subprocess

import click
from colored import fg, attr
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.schema import HumanMessage
from loguru import logger

from docs_updater.prompts import (
    create_context_prompt,
    create_filelist_prompt,
    create_update_prompt,
)

load_dotenv()


def env_validate(api_type: str):
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set")

    if api_type == "azure":
        if not os.environ.get("OPENAI_API_VERSION"):
            raise ValueError("OPENAI_API_VERSION is not set")

        if not os.environ.get("AZURE_RESOURCE_NAME"):
            raise ValueError("AZURE_RESOURCE_NAME is not set")
    if api_type not in ["openai", "azure"]:
        raise ValueError(
            f"API type '{api_type}' is not supported. "
            + "Select from 'openai' or 'azure'."
        )


def get_git_diff(
    repo_root: str,
    old_hash: str = None,
    new_hash: str = None,
) -> str:
    cmd = ["git", "diff", "--", ".", "':(exclude)*.md' ':(exclude)*.rst'"]
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


def choose_updatable_docs(
    model, docs_dict: dict[str, str], diff: str, debug: bool
) -> dict[str, str]:
    # Create the context and filelist prompts
    context = create_context_prompt(docs_dict)
    filelist_prompt = create_filelist_prompt(diff)

    file_list_json_str = model(
        [HumanMessage(content=context), HumanMessage(content=filelist_prompt)]
    ).content

    if debug:
        click.echo(f"context: {context}")
        click.echo(f"filelist_prompt: {filelist_prompt}")
        click.echo(f"file_list_json_str: {file_list_json_str}")
    # FIXME
    file_list_json_str = re.findall(r"\{.*\}", file_list_json_str)[0]

    return json.loads(file_list_json_str)


def print_colored_diff(current_doc: str, updated_doc: str):
    diff = difflib.unified_diff(
        current_doc.splitlines(),
        updated_doc.splitlines(),
        fromfile="Current Document",
        tofile="Updated Document",
        lineterm="",
    )

    for line in diff:
        if line.startswith("+"):
            print(f"{fg(2)}{line}{attr(0)}")
        elif line.startswith("-"):
            print(f"{fg(1)}{line}{attr(0)}")
        else:
            print(line)


@click.command()
@click.option("--repo", default=None, help="The path to the repository.")
@click.option(
    "--docs-dir",
    default="docs",
    help="The path to documents in the repository.",
)
@click.option(
    "--api-type",
    default="openai",
    help="The API type to use. Defaults to OpenAI.",
)
@click.option(
    "--model-name",
    default="gpt-3.5-turbo",
    help="The GPT model to use.",
)
@click.option(
    "--debug",
    default=False,
    help="Whether to print debug information.",
)
def main(
    repo: str | None,
    docs_dir: str,
    api_type: str,
    model_name: str,
    debug: bool,
) -> None:
    env_validate(api_type)
    if not repo:
        repo = os.getcwd()

    repo = Path(repo)
    docs_dir = Path(docs_dir)

    diff = get_git_diff(repo)
    docs_dict = get_current_docs(repo / docs_dir)

    logger.info(f"Ditected documents: {list(docs_dict.keys())}")

    if api_type == "azure":
        model = AzureChatOpenAI(deployment_name=model_name, temperature=0)
    else:
        model = ChatOpenAI(temperature=0)

    files = choose_updatable_docs(model, docs_dict, diff, debug=debug)
    logger.info(f"Files to update: {files}")

    # Update each file in the list
    for file in files["files"]:
        with open(repo / docs_dir / file, "r") as f:
            current_doc = f.read()

        update_prompt = create_update_prompt(diff, current_doc)

        updated_doc = model(
            [
                HumanMessage(content=update_prompt),
            ]
        ).content

        click.echo(f"{file} (diff)")
        click.echo("===")
        print_colored_diff(current_doc, updated_doc)
        click.echo()

        if click.confirm("Do you want to apply this update?"):
            with open(repo / docs_dir / file, "w") as f:
                current_doc = f.write(updated_doc)
        else:
            click.echo("Skipping this file.")


if __name__ == "__main__":
    main()

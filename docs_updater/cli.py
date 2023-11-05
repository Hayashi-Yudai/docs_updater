import difflib
import json
import os
from pathlib import Path

import click
from colored import fg, attr
from dotenv import load_dotenv
import git
from loguru import logger
import openai

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")


def get_current_docs(docs_dir: str) -> list[Document]:
    docs = os.listdir(docs_dir)
    docs_contents = []

    for doc in docs:
        with open(f"{docs_dir}/{doc}", "r") as f:
            docs_contents.append(
                Document(page_content=f.read(), metadata={"title": doc})
            )

    return docs_contents


def create_vector_store(docs: list[Document]) -> Chroma:
    embedding = OpenAIEmbeddings()
    db = Chroma.from_documents(docs, embedding=embedding)

    return db


def get_updated_doc_json(
    git_diff: str, doc: Document, model_name: str
) -> dict[str, str]:
    functions = [
        {
            "name": "extract_json_from_updated_doc",
            "description": "変更後のドキュメントをJSON形式で返します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_filename": {
                        "type": "string",
                        "description": "変更を行ったドキュメントのファイル名",
                    },
                    "doc_content": {
                        "type": "string",
                        "description": "変更後のドキュメントの内容",
                    },
                },
            },
        }
    ]
    query = (
        "以下に示すgit diffの結果をもとに、ドキュメントで更新が必要な部分を全て探し出し更新し、その結果を返してください。"
        + "\n\n===git diff\n"
        + git_diff
        + f"\n\n===古いドキュメント: {doc.metadata['title']}\n"
        + doc.page_content
    )

    response = openai.ChatCompletion.create(
        model=model_name,
        temperature=0,
        messages=[{"role": "user", "content": query}],
        functions=functions,
        function_call={"name": "extract_json_from_updated_doc"},
    )
    message = response["choices"][0]["message"]

    return json.loads(message["function_call"]["arguments"])


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
    "--docs_path", default="docs", help="The path to documents in the repository."
)
@click.option("--model_name", default="gpt-3.5-turbo", help="The model name to use.")
@click.option("--debug", default=False, help="Whether to print debug information.")
def main(repo: str, debug: bool, docs_path: str, model_name: str):
    repo = Path(repo)

    r = git.Repo(repo)
    tree = r.head.commit.tree
    git_diff = r.git.diff(tree)
    if debug:
        logger.debug(git_diff)

    logger.info(f"Using mode: {model_name}")
    db = create_vector_store(get_current_docs(repo / docs_path))
    logger.info(f"Created DB")
    retriever = db.as_retriever(search_kwargs={"k": 1})

    context_docs = retriever.get_relevant_documents(git_diff)
    logger.info(f"Update the following document: {context_docs[0].metadata['title']}")
    logger.info("Asking for ChatGPT...")
    updated_doc = get_updated_doc_json(git_diff, context_docs[0], model_name)

    print_colored_diff(context_docs[0].page_content, updated_doc["doc_content"])

    if click.confirm("Do you want to apply this update?"):
        with open(repo / docs_path / context_docs[0].metadata["title"], "w") as f:
            f.write(updated_doc["doc_content"])
    else:
        click.echo("Skipping this file.")


if __name__ == "__main__":
    main()

# Docs updator

`git diff` からリポジトリのドキュメントを更新するCLIツール. 2023/05/03現在では日本語で書かれたドキュメントのみに対応.

## Requirements

- Python >=3.9, <3.12
- OpenAI API Key / Azure OpenAI API Key

## How to use

### Install

```bash
pip install --user dist/docs_updater-0.1.0-py3-none-any.whl
```

### Update documents

```bash
dupdate [OPTIONS]
```

Options

- `--repo`: リポジトリへのパス. 指定しない場合はカレントディレクトリになる　.
- `--docs-dir`: リポジトリ内でのドキュメントディレクトリのパス. デフォルトは `docs`.
- `--api-type`: 使うAPIのタイプ. `openai` (default) と `azure` を指定可能.
- `--model-name`: 使うGPTのバージョン. デフォルトは `gpt-3.5-turbo`

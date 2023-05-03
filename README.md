# Docs updator

`git diff` からリポジトリのドキュメントを更新するCLIツール. 2023/05/03現在では日本語で書かれたドキュメントのみに対応.

## Requirements

- Python >=3.9, <3.12
- OpenAI API Key / Azure OpenAI API Key

## How to use

### Install

Download whl from https://github.com/Hayashi-Yudai/docs_updater/releases.

```bash
pip install --user dist/docs_updater-$VERSION-py3-none-any.whl
```

必要な環境変数

- `OPENAI_API_KEY`: APIキー
- `OPENAI_API_BASE`: APIのURL (e.g. https://$RESOURCE_NAME.openai.azure.com (azure), https://api.openai.com/v1 (openai))
- `OPENAI_API_VERSION`: APIのバージョン (e.g. 2023-03-15-preview). GPT-4を使う場合のみ必要.

### Update documents

```bash
dupdate [OPTIONS]
```

Options

- `--repo`: リポジトリへのパス. 指定しない場合はカレントディレクトリになる.
- `--docs-dir`: リポジトリ内でのドキュメントディレクトリのパス. デフォルトは `docs`.
- `--api-type`: 使うAPIのタイプ. `openai` (default) と `azure` を指定可能.
- `--model-name`: 使うGPTのバージョン. デフォルトは `gpt-3.5-turbo`.

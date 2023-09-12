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

### Build

```
poetry build
```

buildされたものが `dist/` 以下に格納される。

### Update documents

```bash
dupdate [OPTIONS]
```

Options

- `--repo`: リポジトリへのパス. 指定しない場合はカレントディレクトリになる.
- `--docs-dir`: リポジトリ内でのドキュメントディレクトリのパス. デフォルトは `docs`.
- `--api-type`: 使うAPIのタイプ. `openai` (default) と `azure` を指定可能.
- `--model-name`: 使うGPTのバージョン. デフォルトは `gpt-3.5-turbo`.

### Example

Flaskで書かれた簡単なAPIを例にとって実行例を示す。このAPIは `/hello` にGETリクエストを送ると "hello" と返すだけの機能を持つとする。ここに新たにエンドポイントを追加して `/hello/<name>` にGETリクエストを送ると "hello <name>" と返すように変更した場合を考える。このとき `git diff` は次のようになっている。
  
```diff
diff --git a/src/main.py b/src/main.py
index 218a963..2ed528d 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,9 +1,16 @@
 from flask import Flask
+
 app = Flask(__name__)

-@app.route('/hello', methods=['GET'])
-def hello():
-    return "hello"
+
+@app.route("/hello", methods=["GET"])
+@app.route("/hello/<name>", methods=["GET"])
+def hello(name=None):
+    if name is None:
+        return "hello"
+    else:
+        return f"hello {name}"
+

 if __name__ == "__main__":
     app.run(debug=True)
```
  
このシンプルなリポジトリには2つのドキュメントが用意されているとする。
  
```
.
└── docs
   ├── hello.md
   └── manual.md
```
  
次のコマンドでドキュメント更新をしてみる。

```bash
dupdate --repo path/to/the/repository --docs-dir docs --api-type azure --model-name gpt-4-32k
```
  
Output:
  
```diff
Ditected documents: ['hello.md', 'manual.md']
Files to update: {'files': ['hello.md']}
hello.md (diff)
===
--- Current Document
+++ Updated Document
@@ -3,3 +3,4 @@
 ${YOUR_SERVER_URL}/hello にアクセスすることで利用できます。

 - `/`: helloという文字列を返します。
+- `/<name>`: hello {name}という文字列を返します。

Do you want to apply this update? [y/N]:
```
  
ちゃんと新しいエンドポイントが正しい説明で記載されている。 "y" を選択すれば上記の変更が実際にドキュメントに反映される。

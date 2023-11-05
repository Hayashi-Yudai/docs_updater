# Docs updator

`git diff` からリポジトリのドキュメントを更新するCLIツール. 2023/11/05現在では日本語で書かれたドキュメントのみに対応.

## Requirements

- Python >=3.11, <3.12
- OpenAI API Key

## How to use

### Install

Download whl from https://github.com/Hayashi-Yudai/docs_updater/releases.

```bash
pip install --user dist/docs_updater-$VERSION-py3-none-any.whl
```

必要な環境変数

- `OPENAI_API_KEY`: APIキー

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

- `--repo`: リポジトリへのパス.
- `--docs_path`: リポジトリ内でのドキュメントディレクトリのパス. デフォルトは `docs`.
- `--model_name`: 使うGPTのバージョン. デフォルトは `gpt-3.5-turbo`.
- `--k`: 差分との類似度が高い順にいくつのドキュメントの更新必要性をチェックするか.デフォルトは1.
- `--debug`: デバッグ情報を表示するかどうか.デフォルトはfalse

### Example

標準入力から2つの整数a, bを受取り、指定した四則演算をするだけの簡単なCLIツールを考える。これまでは加算と減算だけに対応していたのを乗算への対応を新たに追加したという状況を考える。このとき `git diff` は下のようになる。
  
```diff 
diff --git a/dummy_project/main.py b/dummy_project/main.py
index 13b538b..a018c1b 100644
--- a/dummy_project/main.py
+++ b/dummy_project/main.py
@@ -1,7 +1,7 @@
 import click
 
 @click.command()
-@click.option("--calc_type", type=click.Choice(["add", "sub"]))
+@click.option("--calc_type", type=click.Choice(["add", "sub", "mul"]))
 @click.option("--a", type=int)
 @click.option("--b", type=int)
 def simple_calc(calc_type: str, a: int, b: int):
@@ -10,6 +10,8 @@ def simple_calc(calc_type: str, a: int, b: int):
             print(a + b)
         case "sub":
             print(a - b)
+        case "mul":
+            print(a * b)
         case _:
             raise ValueError("Unknown calculation type")
```
  
このシンプルなリポジトリには2つのドキュメントが用意されているとする。`simple_calc.md` は上の差分と関係のあるドキュメントで、`complicated_calc.md` は関係のないドキュメントである。
  
```
.
└── docs
   ├── simple_calc.md
   └── complicated_calc.md
```
  
次のコマンドでドキュメント更新をしてみる。

```bash
dupdate --repo path/to/the/repository --docs_path docs --model_name gpt-4
```
  
Output:
  
```diff
2023-11-05 15:22:42.471 | INFO     | __main__:main:123 - Using mode: gpt-4
2023-11-05 15:22:43.440 | INFO     | __main__:main:125 - Created DB
2023-11-05 15:22:43.672 | INFO     | __main__:main:130 - Update the following document: simple_calc.md
2023-11-05 15:22:43.672 | INFO     | __main__:main:133 - Asking to ChatGPT...
--- Current Document
+++ Updated Document
@@ -2,8 +2,9 @@
 
 `calc_type`, `a`, `b` を標準入力として受取り、指定の計算を行った結果を標準出力に返す。
 
-- `calc_type` str: "add"、もしくは "sub" を指定可能。
+- `calc_type` str: "add"、"sub"、もしくは "mul" を指定可能。
     - "add": 加算を行う
     - "sub": 減算を行う
+    - "mul": 乗算を行う
 - `a` int
 - `b` int
Do you want to apply this update? [y/N]: y
2023-11-05 15:23:16.010 | INFO     | __main__:main:130 - Update the following document: complicated_calc.md
2023-11-05 15:23:16.011 | INFO     | __main__:main:133 - Asking to ChatGPT...
No changes found in complicated_calc.md.
```

コードの差分から `simple_calc.md` に対してのみ更新が必要であると判断して更新を提案している。
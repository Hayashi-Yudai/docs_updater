import json


def create_context_prompt(docs: dict) -> str:
    prompt = f"""
    今からあなたにはドキュメントの更新を行ってもらいます。そのためにまず、現在あるドキュメントの内容について教えます。形式はドキュメントファイル名をキー、内容をバリューに持つJSONとなっています。

    {json.dumps(docs)}
    """
    return prompt


def create_update_prompt(diff: str, doc: str) -> str:
    prompt = f"""
    開発しているリポジトリで次のような差分が生じました。

    ```git diff
    {diff}
    ```

    この部分に関係するドキュメントは次のような内容です。このコード差分に対してこのドキュメントを必要に応じて修正し、出力をそのままドキュメントファイルに貼り付けたいので、ドキュメントの文章だけ出力してください。
    ただし説明の粒度は現状のものを踏襲し、具体的にどのように実装されているかまでは書かないこと。

    ```md
    {doc}
    ```
    """
    return prompt


def create_filelist_prompt(diff: str) -> str:
    prompt = f"""
    開発しているリポジトリで次のような差分が生じました。

    ```git diff
    {diff}
    ```

    この変更に対して、更新の必要のあるドキュメントファイル名を次の形式のJSONで返してください。
    なお、返答に入れるドキュメントは先程与えたドキュメントのリストに含まれているものに限定してください。

    {{"files": ['file1.md', ...]}}
    """
    return prompt
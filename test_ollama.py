"""Ollama接続テスト"""
import asyncio
from openai import AsyncOpenAI

async def test_ollama():
    client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
    
    # シンプルなテスト
    print("=== テスト1: シンプルなテキスト生成 ===")
    response = await client.chat.completions.create(
        model="qwen2.5:7b",
        messages=[
            {"role": "user", "content": "こんにちは。一言で答えてください。"}
        ],
        max_tokens=100
    )
    print(f"応答: {response.choices[0].message.content}")
    
    # JSON形式のテスト
    print("\n=== テスト2: JSON形式 ===")
    response = await client.chat.completions.create(
        model="qwen2.5:7b",
        messages=[
            {"role": "system", "content": "JSON形式のみで回答してください。"},
            {"role": "user", "content": '以下のJSON形式で回答してください: {"name": "名前", "age": 数字}'}
        ],
        max_tokens=200
    )
    print(f"応答: {response.choices[0].message.content}")
    
    # 構成テスト
    print("\n=== テスト3: 見出し構成 ===")
    response = await client.chat.completions.create(
        model="qwen2.5:7b",
        messages=[
            {"role": "system", "content": "あなたはSEOを十分に理解しているプロのWebライターです。"},
            {"role": "user", "content": """「AI副業」というキーワードで記事の見出し構成を3つだけ作成してください。

以下の形式で出力してください：
h2：見出し1
h3：サブ見出し1
h2：見出し2
"""}
        ],
        max_tokens=500
    )
    print(f"応答:\n{response.choices[0].message.content}")

if __name__ == "__main__":
    asyncio.run(test_ollama())

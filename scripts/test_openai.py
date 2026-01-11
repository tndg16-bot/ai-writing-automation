#!/usr/bin/env python
"""OpenAI API 接続テストスクリプト"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# .envを読み込み
load_dotenv(project_root / ".env")


async def main():
    print("OpenAI API 接続テスト")
    print("=" * 40)

    # APIキー確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY が設定されていません")
        print("  .env ファイルに OPENAI_API_KEY=sk-xxx を設定してください")
        return False

    print(f"[OK] APIキーを検出: {api_key[:8]}...{api_key[-4:]}")

    # 接続テスト
    print("\n接続テスト中...")
    try:
        from ai_writing.services.llm.openai import OpenAILLM

        llm = OpenAILLM(model="gpt-4o-mini")
        response = await llm.generate("Say 'Hello' in Japanese in one word.")
        print(f"[OK] 応答: {response}")
        return True
    except Exception as e:
        print(f"[ERROR] 接続失敗: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

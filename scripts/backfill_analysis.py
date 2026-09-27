#!/usr/bin/env python
"""並發回填 LLM 分析：把 analyzed_at IS NULL 的 text 訊息批次送 LLM，寫回結果。

與按鈕／每月排程共用 travel.llm_analyzer.analyze_pending（不寫 sentiment，情緒由
scripts/backfill_sentiment.py 的視窗式分析負責）。可隨時中斷續跑（只挑未分析的）。

用法：
    DB_PATH=data/chat.db python scripts/backfill_analysis.py
    DB_PATH=data/chat.db python scripts/backfill_analysis.py --concurrency 8 --limit 500
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from travel.llm_analyzer import analyze_pending  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None, help="只處理前 N 則（測試用）")
    ap.add_argument("--since", type=int, default=None, help="只撈此 timestamp (ms) 之後的訊息")
    args = ap.parse_args()
    asyncio.run(analyze_pending(since_ms=args.since, limit=args.limit, concurrency=args.concurrency))


if __name__ == "__main__":
    main()

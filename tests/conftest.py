"""全域測試設定。"""
import pytest


@pytest.fixture(autouse=True)
def _no_liff_token_enforcement(monkeypatch):
    # corpus_config 一 import 就會載入 .env；正式環境的 LIFF_CHANNEL_ID 會讓 LIFF API 強制驗 token，
    # 測試預設關掉，要測驗證的測試自己 setenv。
    monkeypatch.delenv("LIFF_CHANNEL_ID", raising=False)

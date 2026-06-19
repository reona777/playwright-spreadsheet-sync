# playwright-spreadsheet-sync

> PlaywrightでWebページから商品情報を収集し、Google Sheetsへ差分同期するスクレイピングパイプライン

毎回全件上書きではなく「既存行は更新・新規行のみ追記」の差分同期を実装。定期実行に適した設計で、`--dummy` フラグでスクレイピングなしの動作確認にも対応しています。

## 処理フロー

```
Playwright（Chromium）
  ↓  ページネーションを辿りながら商品情報を収集
scraper.py（Product データクラスで型安全に管理）
  ↓
sheets_sync.py（商品IDをキーに差分検出）
  ↓  既存行は上書き更新・新規行は追記
Google スプレッドシート
```

## 背景・導入経緯

Web からデータを定期収集してスプレッドシートに記録するユースケースで、毎回全件書き直しを行うスクリプトを使っていた。件数が増えると書き込みに時間がかかるうえ、変更のない行まで上書きされるため更新履歴が追いづらくなっていた。

差分同期（既存行は更新・新規行のみ追記）を汎用パターンとして整備することで、定期実行に耐えるスクレイピングパイプラインを実現した。商品 ID をキーにした設計になっているため、対象サイトに合わせて `scraper.py` を差し替えるだけで流用できる。

## 技術スタック

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=flat&logo=google-sheets&logoColor=white)

- **Python 3.x**
- **Playwright** — Chromiumを使ったヘッドレスブラウザスクレイピング
- **Google Sheets API** — 差分同期・データ蓄積
- **pytest** — ユニットテスト

## 実装上の工夫

- スクレイピング結果を `dataclass` で型定義し、同期処理との責務を明確に分離
- 商品IDをキーにした差分検出で、定期実行のたびに全件書き直しを防止
- `--dummy` フラグでダミーデータを使用でき、認証情報なしで動作確認が可能
- `--no-headless` でブラウザを表示しながらデバッグできるオプション設計

## セットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Google Cloudのサービスアカウントキー（JSON）を `credentials.json` として配置してください（`.gitignore` 対象）。

## 使い方

```bash
# ダミーデータで動作確認（スクレイピング不要）
python main.py --dummy --spreadsheet-id YOUR_SPREADSHEET_ID

# 実際のスクレイピングと同期
python main.py --spreadsheet-id YOUR_SPREADSHEET_ID
```

```bash
# テスト実行
pytest tests/ -v
```

### オプション一覧

| オプション | 説明 | デフォルト |
|---|---|---|
| `--dummy` | ダミーデータを使用 | off |
| `--spreadsheet-id` | 同期先スプレッドシートID | 環境変数 `SPREADSHEET_ID` |
| `--sheet-name` | 書き込み先シート名 | `商品一覧` |
| `--credentials` | サービスアカウントJSONのパス | `credentials.json` |
| `--no-headless` | ブラウザを表示して実行 | off |

## ファイル構成

```
playwright-spreadsheet-sync/
├── main.py              # CLI引数処理・エントリポイント
├── scraper.py           # Playwright スクレイピング・ダミーデータ定義
├── sheets_sync.py       # Google Sheets API 差分同期処理
├── requirements.txt
└── tests/
    └── test_scraper.py
```

## ライセンス

MIT License

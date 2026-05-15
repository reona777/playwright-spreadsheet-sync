# Playwright × Python スプレッドシート自動同期

Playwright でWebページから商品情報を収集し、Google Sheets API でスプレッドシートへ自動同期するサンプルです。
`--dummy` フラグで実際のスクレイピングなしに動作確認できます。

---

## 処理フロー

```
Playwright（Chromium）
  ↓  ページネーションを辿りながら商品情報を収集
scraper.py
  ↓  Product データクラスのリストとして返す
sheets_sync.py
  ↓  既存行は上書き更新・新規行は追記（差分同期）
Google スプレッドシート
```

---

## ファイル構成

```
playwright-spreadsheet-sync/
├── main.py              # エントリポイント・CLI引数処理
├── scraper.py           # Playwright スクレイピング・ダミーデータ定義
├── sheets_sync.py       # Google Sheets API 差分同期処理
├── requirements.txt     # 依存パッケージ
└── tests/
    └── test_scraper.py  # pytest ユニットテスト
```

---

## セットアップ

### 1. 仮想環境と依存パッケージ

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Google Cloud でサービスアカウントを作成

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. 「APIとサービス」→「ライブラリ」で **Google Sheets API** を有効化
3. 「認証情報」→「サービスアカウント」を作成し、JSONキーをダウンロード
4. ダウンロードしたJSONを `credentials.json` として配置
   （`.gitignore` で除外済み — Gitにコミットしないこと）

### 3. スプレッドシートの共有設定

サービスアカウントのメールアドレス（`xxxxx@your-project.iam.gserviceaccount.com`）を
対象スプレッドシートに **編集者** として共有する。

---

## 実行方法

### ダミーデータで動作確認（スクレイピング不要）

```bash
python main.py --dummy --spreadsheet-id YOUR_SPREADSHEET_ID
```

### 実サイトをスクレイピングして同期

```bash
python main.py --spreadsheet-id YOUR_SPREADSHEET_ID
```

スプレッドシートIDは環境変数でも渡せます。

```bash
export SPREADSHEET_ID=your_spreadsheet_id
python main.py --dummy
```

### オプション一覧

| オプション | 説明 | デフォルト |
|---|---|---|
| `--dummy` | ダミーデータを使用（スクレイピングをスキップ） | off |
| `--spreadsheet-id` | 同期先スプレッドシートID | 環境変数 `SPREADSHEET_ID` |
| `--sheet-name` | 書き込み先のシート名 | `商品一覧` |
| `--credentials` | サービスアカウントJSONのパス | `credentials.json` |
| `--no-headless` | ブラウザを表示して実行（デバッグ用） | off |

---

## テスト実行

```bash
pytest tests/ -v
```

---

## 同期後のスプレッドシート構成

| 商品ID | 商品名 | カテゴリ | 価格（円） | 在庫数 | 在庫状態 | URL | 最終更新日時 |
|---|---|---|---|---|---|---|---|
| P001 | ビジネスバッグ A4対応 | バッグ | 12800 | 15 | 在庫あり | https://... | 2026/05/15 09:00:00 |
| P005 | 保温タンブラー 500ml | キッチン | 2800 | 0 | 在庫切れ | https://... | 2026/05/15 09:00:00 |

差分同期のため、2回目以降の実行では既存行が上書き更新され、新規商品のみ追記されます。

---

## スクレイピング対象のカスタマイズ

`scraper.py` の `_parse_product()` 内のCSSセレクタを実際のサイト構造に合わせて変更してください。

```python
# 変更例
name = await item.locator(".your-site__product-title").inner_text()
price_text = await item.locator(".your-site__price").inner_text()
```

`BASE_URL` と `_scrape_pages()` のページネーション処理も合わせて調整してください。

---

## GitHub Actions での定期実行

`.github/workflows/` にワークフローを配置すれば、毎日自動実行できます。
詳細は [github-actions-scheduler](https://github.com/reona777/github-actions-scheduler) を参照してください。

---

## ライセンス

MIT License

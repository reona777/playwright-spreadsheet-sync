"""Google Sheets API へのデータ差分同期モジュール"""
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from scraper import Product

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADER = [
    "商品ID", "商品名", "カテゴリ", "価格（円）", "在庫数", "在庫状態", "URL", "最終更新日時",
]


class SheetsSync:
    """スプレッドシートへの差分同期クラス（追記・上書き更新対応）"""

    def __init__(
        self,
        spreadsheet_id: str,
        sheet_name: str = "商品一覧",
        credentials_path: str = "credentials.json",
    ):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.service = self._build_service(credentials_path)

    def _build_service(self, credentials_path: str):
        creds = Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        return build("sheets", "v4", credentials=creds)

    def ensure_header(self) -> None:
        """ヘッダー行が無ければA1に挿入する"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!A1:H1",
        ).execute()
        existing = result.get("values", [])
        if not existing or existing[0] != HEADER:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A1",
                valueInputOption="RAW",
                body={"values": [HEADER]},
            ).execute()

    def sync(self, products: list[Product]) -> dict:
        """
        商品リストをスプレッドシートへ差分同期する。
        既存行（商品IDが一致）は上書き更新、新規は追記。
        """
        existing = self._fetch_existing_ids()
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        rows_to_append = []
        rows_to_update = []

        for p in products:
            row = self._to_row(p, now)
            if p.product_id in existing:
                rows_to_update.append((existing[p.product_id], row))
            else:
                rows_to_append.append(row)

        if rows_to_append:
            self._append_rows(rows_to_append)

        for row_index, row in rows_to_update:
            self._update_row(row_index, row)

        return {
            "appended": len(rows_to_append),
            "updated": len(rows_to_update),
            "total": len(products),
        }

    def _fetch_existing_ids(self) -> dict[str, int]:
        """既存データの 商品ID → シート行番号（1始まり）マップを返す"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!A:A",
        ).execute()
        values = result.get("values", [])
        return {
            row[0]: i + 1
            for i, row in enumerate(values)
            if row and i > 0  # ヘッダー行はスキップ
        }

    def _to_row(self, product: Product, updated_at: str) -> list:
        stock_status = "在庫あり" if product.stock > 0 else "在庫切れ"
        return [
            product.product_id,
            product.name,
            product.category,
            product.price,
            product.stock,
            stock_status,
            product.url,
            updated_at,
        ]

    def _append_rows(self, rows: list[list]) -> None:
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": rows},
        ).execute()

    def _update_row(self, row_index: int, row: list) -> None:
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!A{row_index}:H{row_index}",
            valueInputOption="USER_ENTERED",
            body={"values": [row]},
        ).execute()

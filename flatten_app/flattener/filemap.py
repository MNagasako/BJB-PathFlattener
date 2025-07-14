# filemap管理ロジック（雛形）
import csv
import json
from typing import List, Dict

class FileMap:
    @staticmethod
    def save_csv(filemap: List[Dict], path: str):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["original_path", "flattened_name"])
            writer.writeheader()
            for row in filemap:
                writer.writerow(row)

    @staticmethod
    def save_json(filemap: List[Dict], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(filemap, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_csv(path: str) -> List[Dict]:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    @staticmethod
    def load_json(path: str) -> List[Dict]:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

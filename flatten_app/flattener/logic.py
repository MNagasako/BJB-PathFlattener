import os
import urllib.parse
from pathlib import Path
from typing import List, Dict, Optional

EXCLUDE_PATTERNS = [
    'Thumbs.db', '.DS_Store', '.tmp', '.swp', '~$', 'desktop.ini'
]

class DirectoryScanner:
    """
    ディレクトリを再帰的にスキャンし、ファイル・フォルダ構成を取得する
    除外ファイルもフィルタリング
    """
    def __init__(self, root: Path, exclude_patterns: Optional[List[str]] = None):
        self.root = Path(root)
        self.exclude_patterns = exclude_patterns or EXCLUDE_PATTERNS

    def is_excluded(self, name: str) -> bool:
        for pat in self.exclude_patterns:
            if pat in name:
                return True
        return False

    def scan(self) -> List[Dict]:
        """
        ディレクトリ配下の全ファイル・フォルダ情報をリストで返す
        各要素: {'relpath': str, 'is_dir': bool, 'name': str}
        """
        result = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            rel_dir = os.path.relpath(dirpath, self.root)
            # フォルダ
            if rel_dir != '.':
                result.append({'relpath': rel_dir, 'is_dir': True, 'name': os.path.basename(dirpath)})
            # ファイル
            for fname in filenames:
                if self.is_excluded(fname):
                    continue
                rel_file = os.path.normpath(os.path.join(rel_dir, fname)) if rel_dir != '.' else fname
                result.append({'relpath': rel_file, 'is_dir': False, 'name': fname})
        return result

def flatten_filename(relpath: str) -> str:
    """
    相対パスをフラットなファイル名に変換
    ・区切り文字は _ に
    ・空白や記号はURLエンコード
    """
    # パス区切りを _ に
    flat = relpath.replace('\\', '_').replace('/', '_')
    # URLエンコード（_はそのまま）
    parts = flat.split('_')
    encoded = [urllib.parse.quote(part, safe='') for part in parts]
    return '_'.join(encoded)

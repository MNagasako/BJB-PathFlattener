# --- フラット名→元パスへの復元関数 ---
def restore_flattened_filename(flatname: str, *,
                               pathsep: str = None,
                               pathsep_esc: str = None,
                               esc_seq: str = None) -> str:
    """
    フラット化ファイル名から元の相対パスを復元
    - flatten_filename() の逆変換
    """
    # デフォルト値をグローバル定数から取得
    if pathsep is None:
        pathsep = FLAT_PATHSEP
    if pathsep_esc is None:
        pathsep_esc = FLAT_PATHSEP_ESC
    if esc_seq is None:
        esc_seq = FLAT_ESCAPE_SEQ
    # 区切りを一時的にユニークなトークンに
    tmp = flatname.replace(pathsep, '\0')
    # エスケープを戻す
    tmp = tmp.replace(esc_seq + '_ESC', esc_seq)  # エスケープ文字列自体
    tmp = tmp.replace(esc_seq, pathsep_esc)
    tmp = tmp.replace(pathsep_esc, pathsep)
    # 区切りをパス区切りに戻す
    restored = tmp.replace('\0', os.sep)
    return restored
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
        各要素: {'relpath': str, 'is_dir': bool, 'name': str, 'ext': str, 'size': int}
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
                ext = os.path.splitext(fname)[1].lower()
                try:
                    size = os.path.getsize(os.path.join(dirpath, fname))
                except Exception:
                    size = -1
                result.append({'relpath': rel_file, 'is_dir': False, 'name': fname, 'ext': ext, 'size': size})
        return result


# --- フラット化・復元用エスケープ設定 ---
FLAT_ESCAPE_SEQ = '___UNDERSCORE___'  # エスケープ用文字列（デフォルト）
FLAT_PATHSEP = '__'                   # パス区切り（デフォルト: ダブルアンダースコア）
FLAT_PATHSEP_ESC = '___'              # 区切りのエスケープ（デフォルト: トリプルアンダースコア）

def flatten_filename(relpath: str, *,
                     pathsep: str = FLAT_PATHSEP,
                     pathsep_esc: str = FLAT_PATHSEP_ESC,
                     esc_seq: str = FLAT_ESCAPE_SEQ) -> str:
    """
    相対パスをフラットなファイル名に変換（可読性重視・復元性配慮）
    - パス区切りは pathsep（例: '__'）
    - 元の pathsep は pathsep_esc（例: '___'）にエスケープ
    - 元の pathsep_esc は esc_seq（例: '___UNDERSCORE___'）に一時エスケープ
    - 日本語や記号はエンコードしない
    """
    relpath = relpath.replace(esc_seq, esc_seq + '_ESC')  # エスケープ文字列自体の衝突回避
    relpath = relpath.replace(pathsep_esc, esc_seq)       # まず pathsep_esc をエスケープ
    relpath = relpath.replace(pathsep, pathsep_esc)       # 次に pathsep をエスケープ
    relpath = relpath.replace('\\', pathsep).replace('/', pathsep)  # パス区切りを pathsep に
    return relpath

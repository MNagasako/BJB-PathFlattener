import os
from pathlib import Path
from flattener.logic import DirectoryScanner, flatten_filename

def test_flatten_filename():
    assert flatten_filename('dir1/dir2/ファイル 1.txt') == 'dir1_dir2_%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%201.txt'
    assert flatten_filename('a b/c d.txt') == 'a%20b_c%20d.txt'
    assert flatten_filename('日本語/テスト.txt') == '%E6%97%A5%E6%9C%AC%E8%AA%9E_%E3%83%86%E3%82%B9%E3%83%88.txt'

def test_directory_scanner(tmp_path):
    # ディレクトリ構成作成
    (tmp_path / 'a').mkdir()
    (tmp_path / 'a' / 'b').mkdir()
    (tmp_path / 'a' / 'b' / 'file1.txt').write_text('test')
    (tmp_path / 'a' / 'file2.txt').write_text('test')
    (tmp_path / 'Thumbs.db').write_text('x')
    scanner = DirectoryScanner(tmp_path)
    result = scanner.scan()
    relpaths = [r['relpath'] for r in result if not r['is_dir']]
    assert 'a/b/file1.txt'.replace('/', os.sep) in relpaths
    assert 'a/file2.txt'.replace('/', os.sep) in relpaths
    assert not any('Thumbs.db' in r['relpath'] for r in result)

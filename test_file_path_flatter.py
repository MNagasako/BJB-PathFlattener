import unittest
import tempfile
import shutil
from pathlib import Path
import os
from file_path_flatter import FilePathFlatter


class TestFilePathFlatter(unittest.TestCase):
    """FilePathFlatterのテストクラス"""
    
    def setUp(self):
        """テスト用のディレクトリ構造を作成"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.target_dir = Path(self.temp_dir) / "target"
        
        # テスト用のディレクトリ構造を作成
        self.source_dir.mkdir(parents=True, exist_ok=True)
        
        # テストファイルを作成
        (self.source_dir / "file1.txt").write_text("test content 1")
        (self.source_dir / "subdir1").mkdir()
        (self.source_dir / "subdir1" / "file2.txt").write_text("test content 2")
        (self.source_dir / "subdir1" / "subdir2").mkdir()
        (self.source_dir / "subdir1" / "subdir2" / "file3.txt").write_text("test content 3")
        (self.source_dir / "subdir1" / "subdir2" / "file1.txt").write_text("duplicate name")
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_directories_success(self):
        """ディレクトリ検証の成功テスト"""
        flatter = FilePathFlatter(str(self.source_dir), str(self.target_dir))
        self.assertTrue(flatter.validate_directories())
        self.assertTrue(self.target_dir.exists())
    
    def test_validate_directories_missing_source(self):
        """存在しないソースディレクトリのテスト"""
        non_existent = Path(self.temp_dir) / "non_existent"
        flatter = FilePathFlatter(str(non_existent), str(self.target_dir))
        self.assertFalse(flatter.validate_directories())
    
    def test_get_all_files(self):
        """全ファイル取得のテスト"""
        flatter = FilePathFlatter(str(self.source_dir), str(self.target_dir))
        files = flatter.get_all_files()
        self.assertEqual(len(files), 4)  # 4つのファイルが存在
    
    def test_generate_unique_filename(self):
        """一意ファイル名生成のテスト"""
        flatter = FilePathFlatter(str(self.source_dir), str(self.target_dir))
        existing = {"file1.txt", "file2.txt"}
        
        # 重複しない場合
        unique_name = flatter.generate_unique_filename("file3.txt", existing)
        self.assertEqual(unique_name, "file3.txt")
        
        # 重複する場合
        unique_name = flatter.generate_unique_filename("file1.txt", existing)
        self.assertEqual(unique_name, "file1_001.txt")
    
    def test_flatten_files_copy(self):
        """ファイル平坦化（コピーモード）のテスト"""
        flatter = FilePathFlatter(str(self.source_dir), str(self.target_dir))
        result = flatter.flatten_files(copy_mode=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["processed"], 4)
        self.assertEqual(result["errors"], 0)
        
        # ターゲットディレクトリにファイルが存在することを確認
        target_files = list(self.target_dir.glob("*"))
        self.assertEqual(len(target_files), 4)
        
        # 元ファイルが残っていることを確認（コピーモード）
        source_files = []
        for root, dirs, files in os.walk(self.source_dir):
            source_files.extend(files)
        self.assertEqual(len(source_files), 4)
    
    def test_flatten_files_move(self):
        """ファイル平坦化（移動モード）のテスト"""
        flatter = FilePathFlatter(str(self.source_dir), str(self.target_dir))
        result = flatter.flatten_files(copy_mode=False)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["processed"], 4)
        
        # ターゲットディレクトリにファイルが存在することを確認
        target_files = list(self.target_dir.glob("*"))
        self.assertEqual(len(target_files), 4)


if __name__ == "__main__":
    unittest.main()

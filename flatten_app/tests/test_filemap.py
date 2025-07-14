import os
import tempfile
from flattener.filemap import FileMap

def test_filemap_csv_json():
    filemap = [
        {"original_path": "a/b/c.txt", "flattened_name": "a_b_c.txt"},
        {"original_path": "日本語/テスト.txt", "flattened_name": "%E6%97%A5%E6%9C%AC%E8%AA%9E_%E3%83%86%E3%82%B9%E3%83%88.txt"}
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "filemap.csv")
        json_path = os.path.join(tmpdir, "filemap.json")
        FileMap.save_csv(filemap, csv_path)
        FileMap.save_json(filemap, json_path)
        loaded_csv = FileMap.load_csv(csv_path)
        loaded_json = FileMap.load_json(json_path)
        assert loaded_csv == filemap
        assert loaded_json == filemap

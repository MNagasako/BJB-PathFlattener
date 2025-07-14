# 階層フォルダのファイルフラット化・復元ツール

> **大量ファイルをデータベースに一括登録したいけど、階層構造は受け入れてくれない…？**
> そんな時は「ファイル名にパス情報を埋め込んでフラット化」！
> サブフォルダも含めて、すべてのファイルを1つのフォルダにまとめてアップロードできます。
> 
> **入れ子フォルダも一発変換！**

![Python](https://img.shields.io/badge/python-3.9%2B-blue)

## 概要
階層構造を持つフォルダ内のファイルをフラット化し、元の構造情報を保持したまま別ディレクトリにコピー・保存します。filemapやファイル名から元の構造を復元でき、GUI（Tkinter）とCLIの両方に対応しています。

---

## 動作環境
- **OS:** Windows 10 以降 (64bit)
- **Python:** 3.9 以降
- **GUI:** Tkinter
- **配布:** PyInstallerによるスタンドアロンバイナリ（オプション）

---

## 主な機能
- ディレクトリ指定とスキャン（GUI: フォルダ選択ダイアログ／CLI: 引数または対話式）
- ZIP化対象の指定（GUI上のツリービュー＋チェックボックス）
- ファイルのフラット化コピー（パス区切り→`_`、記号→URLエンコード）
- 長いファイルパス対応（パス長260文字超は短縮エイリアス化、filemapに記録）
- 除外ファイル・拡張子フィルタリング（例: Thumbs.db, .DS_Store, .tmp, .swp, ~$*, desktop.ini）
- filemap出力（CSV/JSON, original_path, flattened_name）
- 復元機能（filemap優先／ファイル名推測、ZIPは解凍して復元、元ディレクトリは変更せず別フォルダに展開）

---

## 使い方

### GUIモード
1. `python main.py` またはダブルクリックで起動
2. 入力・出力フォルダを選択
3. ZIP化対象をチェック
4. 「フラット化実行」ボタンで処理開始
5. プログレスバー・完了通知あり

### CLIモード
```sh
python main.py --cli --src <input_dir> --dst <output_dir> [--interactive]
```

---

## 出力例
- フラット化ファイル群
- ZIPファイル（任意）
- filemap.csv または .json

---

## ユースケース例
- 電子顕微鏡の観察データとEDS分析データを安全かつ分離して保存

---

## 入出力サンプル
```text
[入力]
EM_data/SampleA_低倍率/img1.tif
EM_data/SampleA_高倍率/img2.tif
EM_data/SampleA_EDS/eds1.dat

[出力]
EM_data_flat_20250714/SampleA_低倍率%2Fimg1.tif
EM_data_flat_20250714/SampleA_高倍率%2Fimg2.tif
EM_data_flat_20250714/SampleA_EDS.zip
EM_data_flat_20250714/filemap.csv
```

---

## フォルダ構成
```
flatten_app/
  main.py
  gui.py
  cli.py
  flattener/
    logic.py
    filemap.py
  resources/
    icon.ico
```

---

## 開発・テスト方針
- モジュール分割・クラスベース設計
- 自動テスト・リファクタリング・ログ記録
- テストログ例:
  ```
  [YYYY-MM-DD HH:MM:SS] TEST MODULE: test_module_name
  RESULT: PASS | FAIL
  SUMMARY: 概要説明
  DETAIL:
    - テスト内容:
    - 入力:
    - 出力:
    - エラー内容（あれば）:
  ```
- リファクタログ例:
  ```
  [YYYY-MM-DD HH:MM:SS] REFACTOR MODULE: module_name
  SUMMARY: リファクタの目的と変更点
  BEFORE: （変更前の処理概要）
  AFTER: （変更後の処理概要）
  IMPACT: テスト結果や影響範囲（あれば）
  ```

---

## 今後の拡張予定
- 除外ファイルカスタマイズUI
- 処理ログ保存・フィルタUI
- 多言語対応（日本語／英語）

---

## テスト・リファクタ履歴
```
[2025-07-14 00:00:00] TEST MODULE: test_filemap.py
RESULT: PASS
SUMMARY: filemapのCSV/JSON保存・読込の自動テスト
DETAIL:
  - テスト内容: filemapの保存・読込
  - 入力: filemapリスト
  - 出力: CSV/JSONファイル、読込結果
  - エラー内容: なし

[2025-07-14 00:00:00] TEST MODULE: test_logic.py
RESULT: PASS
SUMMARY: ディレクトリスキャン・ファイル名変換の自動テスト
DETAIL:
  - テスト内容: DirectoryScanner, flatten_filename
  - 入力: テスト用ディレクトリ・ファイル名
  - 出力: スキャン結果・変換結果
  - エラー内容: なし

[2025-07-14 00:00:00] REFACTOR MODULE: gui.py
SUMMARY: ツリービューによるZIP化対象指定・filemap出力機能の追加
BEFORE: 単純なディレクトリ選択・コピーのみ
AFTER: ツリービューでZIP化対象をチェック、filemap.csv出力
IMPACT: GUIの利便性・仕様準拠性向上
```

# app_name: "階層フォルダのファイルフラット化・復元ツール"
# version: "1.0"
# description:
#   階層構造を持つフォルダ内のファイルをフラット化し、
#   元の構造情報を保持したまま別ディレクトリにコピー・保存。
#   また、filemapやファイル名から元の構造を復元できる。
#   GUI（Tkinter）とCUIの両方に対応。

# environment:
#   os: "Windows 10 以降 (64bit)"
#   python: "3.9 以降"
#   gui: "Tkinter"
#   distribution: "PyInstaller によるスタンドアロンバイナリ（オプション）"

# features:
#   - name: "ディレクトリ指定とスキャン"
#     gui: "フォルダ選択ダイアログ"
#     cli: "引数または対話式"
#     behavior: "サブフォルダとファイル構造を再帰的に取得"
#
#   - name: "ZIP化対象の指定"
#     method: "GUI上のツリービュー＋チェックボックスで指定"
#     effect: "チェックされたフォルダはZIP化して保存"
#
#   - name: "ファイルのフラット化コピー"
#     transformation:
#       - "パス区切り → `_`"
#       - "記号 → URLエンコード"
#     output: "指定出力先にフラット化ファイルをコピー"
#     auto_naming: "例: sample_flat_YYYYMMDDHHMMSS"
#
#   - name: "長いファイルパスへの対応"
#     trigger: "パス長260文字超"
#     solution: "長いフォルダ名を短縮エイリアスに変換（重複防止）"
#     log: "変換内容を filemap に記録"
#
#   - name: "除外ファイルのフィルタリング"
#     default_exclude:
#       - "Thumbs.db"
#       - ".DS_Store"
#       - ".tmp"
#       - ".swp"
#       - "~$*"
#       - "desktop.ini"
#
#   - name: "filemap出力"
#     format: ["CSV", "JSON"]
#     fields: ["original_path", "flattened_name"]
#
#   - name: "復元機能"
#     methods:
#       - "filemap に基づく復元（推奨）"
#       - "ファイル名に含まれる区切り文字（例: '__DIR__'）から復元"
#     options:
#       delimiter:
#         configurable: true
#         default: "__DIR__"
#     zip_handling: "ZIPは解凍して復元"
#     safety: "元ディレクトリは変更せず、別フォルダに展開"

# execution_modes:
#   gui:
#     launch: "python main.py またはダブルクリック"
#     flow:
#       - "フォルダ選択"
#       - "ZIP化対象チェック"
#       - "処理実行"
#     feedback: ["プログレスバー", "完了通知"]
#   cli:
#     launch: "python main.py --cli"
#     options:
#       - "--src <input_dir>"
#       - "--dst <output_dir>"
#       - "--interactive"

# output:
#   safe: true
#   structure:
#     - "フラット化ファイル群"
#     - "ZIPファイル（任意）"
#     - "filemap.csv または .json"

# example_use_case:
#   - "電子顕微鏡の観察データとEDS分析データを安全かつ分離して保存"

# example_structure:
#   input:
#     - "EM_data/SampleA_低倍率/img1.tif"
#     - "EM_data/SampleA_高倍率/img2.tif"
#     - "EM_data/SampleA_EDS/eds1.dat"
#   output:
#     - "EM_data_flat_20250714/SampleA_低倍率%2Fimg1.tif"
#     - "EM_data_flat_20250714/SampleA_高倍率%2Fimg2.tif"
#     - "EM_data_flat_20250714/SampleA_EDS.zip"
#     - "EM_data_flat_20250714/filemap.csv"

# folder_structure:
#   base: "flatten_app/"
#   files:
#     - "main.py"
#     - "gui.py"
#     - "cli.py"
#     - "flattener/logic.py"
#     - "flattener/filemap.py"
#     - "resources/icon.ico"

# development:
#   architecture: "モジュール分割・クラスベース"
#   test_policy: "自動テスト、リファクタリング、ログ記録"
#   test_log_format: |
#     [YYYY-MM-DD HH:MM:SS] TEST MODULE: test_module_name
#     RESULT: PASS | FAIL
#     SUMMARY: 概要説明
#     DETAIL:
#       - テスト内容:
#       - 入力:
#       - 出力:
#       - エラー内容（あれば）:
#   refactor_log_format: |
#     [YYYY-MM-DD HH:MM:SS] REFACTOR MODULE: module_name
#     SUMMARY: リファクタの目的と変更点
#     BEFORE: （変更前の処理概要）
#     AFTER: （変更後の処理概要）
#     IMPACT: テスト結果や影響範囲（あれば）

# future_extensions:
#   - "除外ファイルカスタマイズUI"
#   - "処理ログ保存・フィルタUI"
#   - "多言語対応（日本語／英語）"

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

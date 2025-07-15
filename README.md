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
- 階層フォルダのファイルを「パス埋め込みファイル名」またはZIP化でフラット化
- filemap（CSV/JSON）による元構造の完全復元
- 除外/ZIP推奨拡張子のGUI指定・親子連動チェック
- ZIP化/除外指定のツリービュー操作（カラムクリックでON/OFF）
- プログレス・統計・色分け・進捗ラベルのリアルタイム表示
- 設定自動保存（入出力フォルダ）
- ヘルプボタン（❓）による使い方ガイド表示
- 復元時のfilemap優先/ファイル名推測・ZIP展開ON/OFF切替
- テスト・リファクタ・バージョン管理・.gitignore整備
- PyInstallerバイナリ化対応

---

## 使い方

### GUIモード
1. `python main.py` または `python -m flatten_app.gui` で起動（またはバイナリ実行）
2. 入力・出力フォルダを選択
3. [スキャン]でツリー表示、ZIP化/除外指定はカラムクリックでON/OFF
4. 除外/ZIP推奨拡張子は右側テキスト欄で編集
5. 「フラット化実行」で平坦化コピー＋filemap.csv出力
6. [復元]モードでfilemap/推測復元・ZIP展開ON/OFF選択→「復元実行」
7. 進捗・統計・ログ・ヘルプ（❓）は画面上部/下部に常時表示

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
    image/
      nanote_01.png
      nanote_02.png
      nanote_03.png
      nanote_04.png
      CNTS.png
      nanote_sab_01.png
      nanote_sab_02.png
      nanote_sab_03.png
      spinner.gif
      icon/
        icon1.ico
        icon1.png
        icon2.ico
        icon2.png
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
- CLIモード・多言語対応・filemap強化
- 変換前後のツリー可視化ファイル出力
- 除外ファイルカスタマイズUI
- 処理ログ保存・フィルタUI
- 高速化・大規模データ対応

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
SUMMARY: ツリービューによるZIP化/除外指定・filemap出力・進捗/統計/色分け・ヘルプボタン追加・UI/UX改善
BEFORE: 単純なディレクトリ選択・コピーのみ
AFTER: ツリービューでZIP化/除外指定・filemap.csv出力・進捗/統計/色分け・ヘルプボタン追加
IMPACT: GUIの利便性・仕様準拠性・ユーザビリティ大幅向上
```

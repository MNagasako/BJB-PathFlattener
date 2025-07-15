


import sys
import os
import pathlib
# --- import時点でファイル書き出し（importされたことを確実に検知） ---
try:
    # バイナリ実行時はsys._MEIPASS、通常は__file__の親
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    debug_marker_path = os.path.join(base_dir, "debug_import_marker.txt")
    import datetime
    os.makedirs(os.path.dirname(debug_marker_path), exist_ok=True)
    with open(debug_marker_path, "w", encoding="utf-8") as f:
        f.write(f"[import] __file__ = {__file__}\n")
        f.write(f"datetime = {datetime.datetime.now()}\n")
except Exception as e:
    pass

# --- import時に必ずファイル書き出し（import経路デバッグ） ---
try:
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    debug_marker_path = os.path.join(base_dir, "debug_import_marker.txt")
    import datetime
    os.makedirs(os.path.dirname(debug_marker_path), exist_ok=True)
    with open(debug_marker_path, "w", encoding="utf-8") as f:
        f.write(f"imported: {__file__}\n{datetime.datetime.now()}\n")
except Exception:
    pass

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import shutil
import json
import urllib.parse
# Pillowで画像表示
from PIL import Image, ImageTk
import random

# --- どの実行形態でも動作するimport構文に統一 ---
import sys
import pathlib
_here = pathlib.Path(__file__).resolve().parent
_root = _here.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))
# --- import fallback: flatten_app.flattener → flattener ---
try:
    from flatten_app.flattener.logic import DirectoryScanner, flatten_filename
    from flatten_app.flattener.filemap import FileMap
except ImportError:
    from flattener.logic import DirectoryScanner, flatten_filename
    from flattener.filemap import FileMap

class FlattenApp(tk.Tk):
    def show_help(self):
        help_text = (
            "【ファイルフラット化・復元ツール ヘルプ】\n\n"
            "■ 基本操作\n"
            "1. 入力フォルダ・出力フォルダを指定してください。\n"
            "2. [スキャン]ボタンでフォルダ内を解析し、ツリー表示します。\n"
            "3. ZIP化/除外したいフォルダ・ファイルはツリーの該当列をクリックで指定できます。\n"
            "4. 除外/ZIP推奨拡張子は右側のテキスト欄で編集できます。\n"
            "5. [フラット化実行]で平坦化コピー＋filemap.csv出力。\n"
            "6. [復元]モードに切り替えると復元リストが表示され、[復元実行]で元の構造に戻せます。\n\n"
            "■ 各UIの説明\n"
            "- ZIP化: フォルダ単位でZIP化する場合にチェック\n"
            "- 除外: コピー/ZIP化から除外したいファイル・フォルダにチェック\n"
            "- 除外拡張子: 指定した拡張子・ファイル名は全て除外\n"
            "- ZIP推奨拡張子: 指定拡張子を含むフォルダは自動でZIP化ON\n\n"
            "■ 進捗・統計\n"
            "- 対象ファイル数・合計サイズ、処理中の進捗が画面下部に表示されます。\n\n"
            "■ 設定\n"
            "- 入出力フォルダは自動保存されます。\n\n"
            "■ その他\n"
            "- 詳細仕様・CLI・多言語対応などはREADME.md参照\n"
        )
        messagebox.showinfo("ヘルプ", help_text)

    def __init__(self):
        # --- 実際に使われているファイルパスをファイルに書き出す ---
        try:
            if hasattr(sys, '_MEIPASS'):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            debug_gui_path = os.path.join(base_dir, "debug_gui_path.txt")
            os.makedirs(os.path.dirname(debug_gui_path), exist_ok=True)
            with open(debug_gui_path, "w", encoding="utf-8") as f:
                f.write(f"__file__ = {__file__}\n")
        except Exception as e:
            pass
        super().__init__()
        self.title("ファイルフラット化・復元ツール")
        self.geometry("800x600")
        self.resizable(True, True)
        self.create_widgets()
        self.dir_tree_items = {}
        self.zip_targets = set()
        self.dir_nodes = {}  # relpath: node_id
        self.load_settings()
        # 初期表示で必ずフラット化ツリーが表示されるようにする
        self.on_mode_change()

    def human_readable_size(self, size):
        # バイト数を見やすい単位（B, KB, MB, GB, TB）で返す
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:,.0f} {unit}"
            size /= 1024.0
        return f"{size:,.0f} PB"

    def show_random_image(self):
        import tkinter.messagebox as mb
        if not self._image_files:
            self._image_label.config(image="", text="画像なし")
            mb.showerror("画像エラー", "画像ファイルリストが空です。imageフォルダに画像が存在するか確認してください。")
            return
        img_path = random.choice(self._image_files)
        print(f"[DEBUG] show_random_image: 選択画像: {img_path}")
        try:
            img = Image.open(img_path)
            max_w, max_h = 120, 120
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            self._image_tk = ImageTk.PhotoImage(img)
            # ファイル名もtextで表示
            self._image_label.config(image=self._image_tk, text="")
            self._image_label.image = self._image_tk  # 明示的に参照保持
            print(f"[DEBUG] show_random_image: 画像ラベルにセット完了")
        except Exception as e:
            self._image_label.config(image="", text=f"画像読込失敗\n{os.path.basename(img_path)}")
            mb.showerror("画像読込失敗", f"画像読込失敗: {img_path}\n{e}")
    def show_restore_ui(self, frm):
        # メイン表示領域を復元リストに切り替え
        for widget in self.main_area.winfo_children():
            widget.pack_forget()
        # 復元方式選択ボタン
        self.restore_btn_frame = ttk.Frame(frm)
        self.restore_btn_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky=tk.W)
        ttk.Label(self.restore_btn_frame, text="復元方式:", font=('Meiryo UI', 10, 'bold')).pack(side=tk.LEFT)
        self.restore_method = tk.StringVar(value='filemap')
        ttk.Radiobutton(self.restore_btn_frame, text='filemap優先', variable=self.restore_method, value='filemap').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.restore_btn_frame, text='ファイル名推測', variable=self.restore_method, value='filename').pack(side=tk.LEFT, padx=5)
        self.unzip_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.restore_btn_frame, text='ZIPファイルは展開する', variable=self.unzip_var).pack(side=tk.LEFT, padx=10)
        self.restore_exec_btn = ttk.Button(self.restore_btn_frame, text='復元実行', command=self.run_restore)
        self.restore_exec_btn.pack(side=tk.LEFT, padx=10)
        # プログレスバー
        self.restore_progress = ttk.Progressbar(self.restore_btn_frame, mode='indeterminate', length=120)
        self.restore_progress.pack(side=tk.LEFT, padx=10)
        # 復元ツリー（main_area内に表示、スクロールバー付き）
        restore_frame = ttk.Frame(self.main_area)
        restore_frame.pack(fill=tk.BOTH, expand=True)
        self.restore_tree_scrollbar = ttk.Scrollbar(restore_frame, orient="vertical")
        self.restore_tree = ttk.Treeview(restore_frame, columns=("flatname", "restore_path_filemap", "restore_path_guess"), height=15, yscrollcommand=self.restore_tree_scrollbar.set)
        self.restore_tree_scrollbar.config(command=self.restore_tree.yview)
        self.restore_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.restore_tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.restore_tree.heading("#0", text="ファイル名")
        self.restore_tree.heading("flatname", text="フラット名")
        self.restore_tree.heading("restore_path_filemap", text="filemap復元パス")
        self.restore_tree.heading("restore_path_guess", text="推測復元パス")
        self.restore_tree.column("flatname", width=180)
        self.restore_tree.column("restore_path_filemap", width=220)
        self.restore_tree.column("restore_path_guess", width=220)
        self.restore_tree.column("#0", width=120)
        frm.rowconfigure(6, weight=1)

    def hide_restore_ui(self):
        if hasattr(self, 'restore_btn_frame'):
            self.restore_btn_frame.destroy()
        # メイン表示領域をツリーに戻す
        for widget in self.main_area.winfo_children():
            widget.pack_forget()
        # tree_frameはself.treeの親
        self.tree.master.pack(fill=tk.BOTH, expand=True)
        # packのみで表示制御（pack/grid混在禁止）

    def run_restore(self):
        import shutil
        import zipfile
        from flattener.filemap import FileMap
        method = self.restore_method.get()
        src = self.src_var.get()
        dst = self.dst_var.get()
        unzip = self.unzip_var.get()
        if not os.path.isdir(src):
            messagebox.showerror("エラー", "入力フォルダを正しく指定してください")
            return
        if not os.path.isdir(dst):
            messagebox.showerror("エラー", "出力フォルダを正しく指定してください")
            return
        self.restore_exec_btn.config(state=tk.DISABLED)
        if hasattr(self, 'restore_progress'):
            self.restore_progress.start(10)
        self.log(f"復元実行: {method} (ZIP展開: {'ON' if unzip else 'OFF'})")
        filemap_path = os.path.join(src, "filemap.csv")
        filemap = []
        if os.path.exists(filemap_path):
            try:
                filemap = FileMap.load_csv(filemap_path)
            except Exception as e:
                self.log(f"filemap.csv読込エラー: {e}")
        files = []
        for root, dirs, fs in os.walk(src):
            for f in fs:
                if f == "filemap.csv":
                    continue
                rel = os.path.relpath(os.path.join(root, f), src)
                files.append(rel)
        count = 0
        for f in files:
            src_path = os.path.join(src, f)
            # 復元パス決定
            if method == 'filemap' and filemap:
                rec = next((row for row in filemap if row['flattened_name'] == f), None)
                if rec:
                    out_path = os.path.join(dst, rec['original_path'])
                else:
                    self.log(f"filemap未登録: {f}")
                    continue
            else:
                try:
                    parts = f.split('_')
                    decoded = [urllib.parse.unquote(p) for p in parts]
                    out_path = os.path.join(dst, *decoded)
                except Exception as e:
                    self.log(f"復元名変換エラー: {f}: {e}")
                    continue
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            # ZIPファイルなら展開 or コピー
            if f.lower().endswith('.zip'):
                if unzip:
                    # ZIP展開: ZIPファイル名(拡張子なし)のフォルダ内に展開
                    zip_folder = os.path.splitext(os.path.basename(out_path))[0]
                    extract_dir = os.path.join(os.path.dirname(out_path), zip_folder)
                    os.makedirs(extract_dir, exist_ok=True)
                    try:
                        with zipfile.ZipFile(src_path, 'r') as zf:
                            zf.extractall(extract_dir)
                        self.log(f"展開: {src_path} → {extract_dir}")
                        count += 1
                    except Exception as e:
                        self.log(f"ZIP展開エラー: {src_path}: {e}")
                else:
                    # ZIPコピー: ファイル名に.zip拡張子を必ず付与してコピー
                    zip_copy_path = out_path
                    if not zip_copy_path.lower().endswith('.zip'):
                        zip_copy_path += '.zip'
                    try:
                        shutil.copy2(src_path, zip_copy_path)
                        self.log(f"ZIPコピー: {src_path} → {zip_copy_path}")
                        count += 1
                    except Exception as e:
                        self.log(f"ZIPコピーエラー: {src_path} → {zip_copy_path}: {e}")
            else:
                try:
                    shutil.copy2(src_path, out_path)
                    self.log(f"復元: {src_path} → {out_path}")
                    count += 1
                except Exception as e:
                    self.log(f"復元エラー: {src_path} → {out_path}: {e}")
        self.log(f"\n復元完了: {count} ファイル/ZIP")
        self.restore_exec_btn.config(state=tk.NORMAL)
        if hasattr(self, 'restore_progress'):
            self.restore_progress.stop()
    SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

    def __init__(self):
        super().__init__()
        self.title("ファイルフラット化・復元ツール")
        self.geometry("800x600")
        self.resizable(True, True)
        self.create_widgets()
        self.dir_tree_items = {}
        self.zip_targets = set()
        self.dir_nodes = {}  # relpath: node_id
        self.load_settings()
        # 初期表示で必ずフラット化ツリーが表示されるようにする
        self.on_mode_change()

    def create_widgets(self):
        import tkinter.messagebox as mb
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Meiryo UI', 10), padding=6)
        style.configure('TLabel', font=('Meiryo UI', 10))
        style.configure('Treeview.Heading', font=('Meiryo UI', 10, 'bold'))
        style.configure('TEntry', font=('Meiryo UI', 10))

        # モード切替＋ヘルプボタン（強調・右上配置）
        self.mode_var = tk.StringVar(value='flatten')
        topbar = ttk.Frame(self)
        topbar.pack(fill=tk.X, padx=10, pady=(10, 0))
        mode_frame = ttk.Frame(topbar)
        mode_frame.pack(side=tk.LEFT)
        ttk.Label(mode_frame, text='動作モード:').pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text='フラット化', variable=self.mode_var, value='flatten', command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text='復元', variable=self.mode_var, value='restore', command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        # ヘルプボタンを右上に大きく強調
        help_btn = ttk.Button(topbar, text='❓ ヘルプ', command=self.show_help, style='Accent.TButton')
        help_btn.pack(side=tk.RIGHT, padx=5)
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Meiryo UI', 11, 'bold'), foreground='#005580', background='#e6f7ff', padding=8)

        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 入力ディレクトリ
        self.src_var = tk.StringVar()
        ttk.Label(frm, text="入力フォルダ:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.src_var, width=50).grid(row=0, column=1)
        ttk.Button(frm, text="参照", command=self.select_src).grid(row=0, column=2)
        ttk.Button(frm, text="スキャン", command=self.scan_dir).grid(row=0, column=3)

        # 出力ディレクトリ
        self.dst_var = tk.StringVar()
        ttk.Label(frm, text="出力フォルダ:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.dst_var, width=50).grid(row=1, column=1)
        ttk.Button(frm, text="参照", command=self.select_dst).grid(row=1, column=2)

        # --- 画像表示エリア（実行ボタン左側） ---
        # PyInstallerバイナリ対応: _MEIPASSがあればそこを参照
        if hasattr(sys, '_MEIPASS'):
            image_dir = os.path.join(sys._MEIPASS, "flatten_app", "resources", "image")
        else:
            image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "image")
        self._image_files = []
        for i in range(1, 5):
            p = os.path.join(image_dir, f"nanote_0{i}.png")
            if os.path.isfile(p):
                self._image_files.append(p)
        self._image_label = tk.Label(frm, bg="white", borderwidth=0, highlightthickness=0, width=120, height=120, anchor="center", text="") 
        self._image_label.grid(row=3, column=0, rowspan=2, sticky=tk.N, padx=(0, 10), pady=5)
        self._image_tk = None  # 参照保持
        print(f"[DEBUG] image_dir: {image_dir}")
        print(f"[DEBUG] _image_files: {self._image_files}")
        if not self._image_files:
            self._image_label.config(text="画像なし")
            mb.showerror("画像エラー", f"画像ファイルが見つかりませんでした\n{image_dir}\nに nanote_01.png〜nanote_04.png を配置してください。")
        else:
            try:
                self.show_random_image()
            except Exception as e:
                self._image_label.config(text="画像表示エラー")
                mb.showerror("画像表示エラー", f"画像表示処理で例外発生:\n{e}")

        # メイン表示領域（ツリー/復元リスト切替用）
        self.main_area = ttk.Frame(frm)
        self.main_area.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=10)
        frm.rowconfigure(2, weight=1)
        frm.columnconfigure(1, weight=1)

        # ツリービュー（ZIP化・除外指定）＋スクロールバー
        tree_frame = ttk.Frame(self.main_area)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree = ttk.Treeview(tree_frame, columns=("type", "relpath", "ext", "size", "count", "exclude"), selectmode="none", height=15, yscrollcommand=self.tree_scrollbar.set)
        self.tree_scrollbar.config(command=self.tree.yview)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.heading("#0", text="名前")
        self.tree.heading("type", text="種別")
        self.tree.heading("relpath", text="相対パス")
        self.tree.heading("ext", text="拡張子")
        self.tree.heading("size", text="サイズ")
        self.tree.heading("count", text="ZIP化")
        self.tree.heading("exclude", text="除外")
        self.tree.column("type", width=60, anchor="center")
        self.tree.column("relpath", width=200)
        self.tree.column("ext", width=60, anchor="center")
        self.tree.column("size", width=80, anchor="e")
        self.tree.column("count", width=60, anchor="center")
        self.tree.column("exclude", width=60, anchor="center")
        self.tree.tag_configure('dir_total', background='#e6f7ff', foreground='#005580', font=('Meiryo UI', 10, 'bold'))
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.restore_tree = None  # 復元リストはshow_restore_uiで生成

        # 統計表示＋進捗表示
        stat_frame = ttk.Frame(frm)
        stat_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W)
        self.stat_label = ttk.Label(stat_frame, text="対象ファイル数: 0    合計サイズ: 0 B")
        self.stat_label.pack(side=tk.LEFT, anchor=tk.W)
        self.progress_label = ttk.Label(stat_frame, text="")
        self.progress_label.pack(side=tk.LEFT, padx=(20,0))

        # 実行ボタン
        self.run_btn = ttk.Button(frm, text="フラット化実行", command=self.run_flatten)
        self.run_btn.grid(row=3, column=1, pady=10)

        # 除外・ZIP推奨拡張子指定を横並びに
        self.exclude_ext_var = tk.StringVar()
        default_ex = "Thumbs.db\n.DS_Store\n.tmp\n.swp\n~$\ndesktop.ini"
        self.exclude_ext_var.set(default_ex)
        self.target_ext_var = tk.StringVar()
        default_target_ex = ".ico\n.pdf\n.ASW"
        self.target_ext_var.set(default_target_ex)
        ex_zip_frame = ttk.Frame(frm)
        ex_zip_frame.grid(row=3, column=2, columnspan=2, sticky=tk.W+tk.E)
        # 除外
        exclude_frame = ttk.Frame(ex_zip_frame)
        exclude_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        ttk.Label(exclude_frame, text="除外拡張子・ファイル名(1行1つ):").pack(anchor=tk.W)
        self.exclude_ext_text = tk.Text(exclude_frame, height=4, width=22, font=('Meiryo UI', 10))
        self.exclude_ext_text.pack(fill=tk.X)
        self.exclude_ext_text.insert('1.0', default_ex)
        # ZIP推奨
        zip_frame = ttk.Frame(ex_zip_frame)
        zip_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(zip_frame, text="ZIP推奨拡張子(1行1つ):").pack(anchor=tk.W)
        self.target_ext_text = tk.Text(zip_frame, height=4, width=22, font=('Meiryo UI', 10))
        self.target_ext_text.pack(fill=tk.X)
        self.target_ext_text.insert('1.0', default_target_ex)

        # ログ表示
        self.log_text = tk.Text(self, height=8, width=90, state=tk.DISABLED)
        self.log_text.pack(fill=tk.X, padx=10, pady=(0,10), side=tk.BOTTOM)

    def select_src(self):
        path = filedialog.askdirectory(title="入力フォルダ選択")
        if path:
            self.src_var.set(path)
            self.save_settings()

    def select_dst(self):
        path = filedialog.askdirectory(title="出力フォルダ選択")
        if path:
            self.dst_var.set(path)
            self.save_settings()

    def scan_dir(self):
        self.save_settings()
        src = self.src_var.get()
        if not os.path.isdir(src):
            messagebox.showerror("エラー", "入力フォルダを正しく指定してください")
            return
        self.tree.delete(*self.tree.get_children())
        self.zip_targets = set()
        self.exclude_targets = set()
        self.dir_nodes = {"": ""}
        scanner = DirectoryScanner(src)
        items = scanner.scan()
        file_count = {}
        dir_size = {}
        # ZIP推奨拡張子リスト取得
        target_exts = [e.strip().lower() for e in self.target_ext_text.get('1.0', tk.END).splitlines() if e.strip()]
        # 除外拡張子リスト取得
        exclude_exts = [e.strip().lower() for e in self.exclude_ext_text.get('1.0', tk.END).splitlines() if e.strip()]
        # フォルダごとに対象拡張子ファイルが含まれるかチェック
        folder_ext_hit = {}
        # ディレクトリ合計サイズ計算用
        for item in items:
            relpath = item['relpath']
            parent = os.path.dirname(relpath) if os.path.dirname(relpath) != '.' else ""
            if item.get('is_dir'):
                node_id = self.tree.insert(self.dir_nodes.get(parent, ""), "end", text=item['name'],
                                           values=("DIR", relpath, "", "", "[ ]", "[ ]"))
                self.dir_nodes[relpath] = node_id
                dir_size[relpath] = 0
            else:
                ext = item.get('ext', '').lower()
                size = item.get('size', '')
                size_str = f"{size:,}" if isinstance(size, int) and size >= 0 else "-"
                node_id = self.tree.insert(self.dir_nodes.get(parent, ""), "end", text=item['name'],
                                           values=("FILE", relpath, ext, size_str, "", "[ ]"))
                file_count[parent] = file_count.get(parent, 0) + 1
                # 親フォルダに対象拡張子が含まれるか記録
                if ext in target_exts:
                    folder_ext_hit[parent] = True
                # ディレクトリ合計サイズ加算
                p = parent
                while p != "":
                    dir_size[p] = dir_size.get(p, 0) + (size if isinstance(size, int) and size >= 0 else 0)
                    p = os.path.dirname(p) if os.path.dirname(p) != '.' else ""
        # ファイル数を表示＋対象拡張子が含まれるフォルダはZIP化ON
        for rel, node_id in self.dir_nodes.items():
            if rel in file_count and node_id:
                if rel in folder_ext_hit:
                    self.tree.set(node_id, column="count", value="[✔]")
                    self.zip_targets.add(rel)
                else:
                    self.tree.set(node_id, column="count", value="[ ]")
        # ディレクトリ未展開時は合計サイズを色付きで表示
        for rel, node_id in self.dir_nodes.items():
            if node_id and rel in dir_size and dir_size[rel] > 0:
                self.tree.set(node_id, column="size", value=f"{dir_size[rel]:,}")
                self.tree.item(node_id, tags=('dir_total',))
        # 統計表示（除外ファイル以外のファイル数・合計サイズ）
        total_count = 0
        total_size = 0
        for item in items:
            if not item.get('is_dir'):
                ext = item.get('ext', '').lower()
                relpath = item['relpath']
                if ext and any(ext == ('.' + e.lstrip('.').lower()) for e in exclude_exts):
                    continue
                total_count += 1
                size = item.get('size', 0)
                if isinstance(size, int) and size >= 0:
                    total_size += size
        self.stat_label.config(
            text=f"対象ファイル数: {total_count:,}    合計サイズ: {self.human_readable_size(total_size)}"
        )
        # 進捗ラベルも初期化
        self.progress_label.config(text="")

    def load_settings(self):
        try:
            with open(self.SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if os.path.isdir(data.get("last_src", "")):
                self.src_var.set(data["last_src"])
            if os.path.isdir(data.get("last_dst", "")):
                self.dst_var.set(data["last_dst"])
        except Exception:
            pass

    def save_settings(self):
        data = {
            "last_src": self.src_var.get(),
            "last_dst": self.dst_var.get()
        }
        try:
            with open(self.SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        print(f"[DEBUG] region={region}, col={col}, row={row}, x={event.x}, y={event.y}")
        if region != "cell" or not row:
            print("[DEBUG] セル以外または空白クリック。処理しません。")
            return
        values = self.tree.item(row, "values")
        print(f"[DEBUG] values={values}")
        relpath = values[1] if values else None
        if col == "#5":  # ZIP化列
            if not values or values[0] != "DIR":
                print("[DEBUG] DIR行以外。処理しません。")
                return
            # チェック状態トグル
            if relpath in self.zip_targets:
                self.zip_targets.remove(relpath)
                self.tree.set(row, column="count", value="[ ]")
                print(f"[DEBUG] ZIP化OFF: {relpath}")
                self.log(f"ZIP化対象OFF: {relpath}")
            else:
                self.zip_targets.add(relpath)
                self.tree.set(row, column="count", value="[✔]")
                print(f"[DEBUG] ZIP化ON: {relpath}")
                self.log(f"ZIP化対象ON: {relpath}")
            self.log(f"ZIP化対象リスト: {sorted(self.zip_targets)}")
        elif col == "#6":  # 除外列
            # ファイル・ディレクトリ両方OK
            if not hasattr(self, 'exclude_targets'):
                self.exclude_targets = set()

            def set_exclude_recursive(node_id, check):
                values = self.tree.item(node_id, "values")
                relpath = values[1] if values else None
                if relpath:
                    if check:
                        self.exclude_targets.add(relpath)
                        self.tree.set(node_id, column="exclude", value="[✔]")
                    else:
                        self.exclude_targets.discard(relpath)
                        self.tree.set(node_id, column="exclude", value="[ ]")
                # 子ノードも再帰的に処理
                for child in self.tree.get_children(node_id):
                    set_exclude_recursive(child, check)

            if relpath in self.exclude_targets:
                # OFF: 自分と子孫すべて除外OFF
                set_exclude_recursive(row, False)
                print(f"[DEBUG] 除外OFF: {relpath}（子孫もOFF）")
                self.log(f"除外OFF: {relpath}（子孫もOFF）")
            else:
                # ON: 自分と子孫すべて除外ON
                set_exclude_recursive(row, True)
                print(f"[DEBUG] 除外ON: {relpath}（子孫もON）")
                self.log(f"除外ON: {relpath}（子孫もON）")
            self.log(f"除外リスト: {sorted(self.exclude_targets)}")
        else:
            print("[DEBUG] ZIP化/除外列以外。処理しません。")
            return

    def run_flatten(self):
        src = self.src_var.get()
        dst = self.dst_var.get()
        if not os.path.isdir(src):
            messagebox.showerror("エラー", "入力フォルダを正しく指定してください")
            return
        if not os.path.isdir(dst):
            messagebox.showerror("エラー", "出力フォルダを正しく指定してください")
            return
        self.run_btn.config(state=tk.DISABLED)
        self.log("フラット化処理を開始します...")
        zip_targets = set(self.zip_targets)
        exclude_targets = set(getattr(self, 'exclude_targets', set()))
        # 除外拡張子・ファイル名を複数行テキストから取得
        exclude_exts = [e.strip() for e in self.exclude_ext_text.get('1.0', tk.END).splitlines() if e.strip()]
        # 統計情報取得
        scanner = DirectoryScanner(src)
        items = scanner.scan()
        total_count = 0
        total_size = 0
        for item in items:
            if not item.get('is_dir'):
                ext = item.get('ext', '').lower()
                relpath = item['relpath']
                if ext and any(ext == ('.' + e.lstrip('.').lower()) for e in exclude_exts):
                    continue
                total_count += 1
                size = item.get('size', 0)
                if isinstance(size, int) and size >= 0:
                    total_size += size
        self._flatten_progress = {
            'total_count': total_count,
            'total_size': total_size,
            'done_count': 0,
            'done_size': 0
        }
        # 進捗表示用ラベル（stat_labelの右側に表示するため、ここでは値のみ更新）
        self.progress_label.config(
            text=f" | 残り{total_count:,}件, 処理済0件, 残り{self.human_readable_size(total_size)}"
        )
        threading.Thread(target=self._flatten_thread, args=(src, dst, zip_targets, exclude_targets, exclude_exts), daemon=True).start()

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == 'flatten':
            self.run_btn.config(text='フラット化実行')
            self.run_btn.grid(row=3, column=1, pady=10)
            self.hide_restore_ui()
            # packのみで表示制御（pack/grid混在禁止）
        else:
            self.run_btn.grid_forget()
            # pack/grid混在禁止: grid_remove()は呼ばない
            self.show_restore_ui(self.run_btn.master)
            # 入力フォルダをスキャンして復元ツリーを作成（ダミー表示）
            self.populate_restore_tree()

    def populate_restore_tree(self):
        # 入力フォルダ内のファイルをスキャンし、filemap/推測復元パスを本ロジックで表示
        if not hasattr(self, 'restore_tree'):
            return
        self.restore_tree.delete(*self.restore_tree.get_children())
        src = self.src_var.get()
        if not os.path.isdir(src):
            return
        filemap_path = os.path.join(src, "filemap.csv")
        filemap = []
        if os.path.exists(filemap_path):
            try:
                filemap = FileMap.load_csv(filemap_path)
            except Exception:
                pass
        files = []
        for root, dirs, fs in os.walk(src):
            for f in fs:
                if f == "filemap.csv":
                    continue
                rel = os.path.relpath(os.path.join(root, f), src)
                files.append(rel)
        for f in files:
            # filemap方式
            filemap_path_val = ""
            if filemap:
                rec = next((row for row in filemap if row['flattened_name'] == f), None)
                if rec:
                    filemap_path_val = rec['original_path']
            # ファイル名推測方式
            try:
                parts = f.split('_')
                decoded = [urllib.parse.unquote(p) for p in parts]
                guess_path_val = os.path.join(*decoded)
            except Exception:
                guess_path_val = ""
            self.restore_tree.insert('', 'end', text=f, values=(f, filemap_path_val, guess_path_val))

    def _flatten_thread(self, src, dst, zip_targets, exclude_targets, exclude_exts):
        try:
            scanner = DirectoryScanner(src)
            items = scanner.scan()
            count = 0
            filemap = []
            # --- ZIP化対象のディレクトリを先にZIP化 ---
            zip_count = 0
            zip_total = len(zip_targets)
            zip_spinner_seq = ['|', '/', '-', '\\']
            zip_spinner_idx = 0
            def spin_update(zc, zt, idx):
                spin = zip_spinner_seq[idx % len(zip_spinner_seq)]
                remain_count = self._flatten_progress['total_count'] - self._flatten_progress['done_count']
                remain_size = self._flatten_progress['total_size'] - self._flatten_progress['done_size']
                self.progress_label.config(
                    text=f" | 残り{remain_count:,}件, 処理済{self._flatten_progress['done_count']:,}件, 残り{self.human_readable_size(remain_size)} / {self.human_readable_size(self._flatten_progress['total_size'])}  (ZIP圧縮中 {zc}/{zt} {spin})"
                )
            for relpath in sorted(zip_targets):
                if relpath in exclude_targets:
                    self.log(f"スキップ（除外指定）: {relpath}")
                    continue
                abs_dir = os.path.join(src, relpath)
                zip_name = flatten_filename(relpath) + ".zip"
                zip_path = os.path.join(dst, zip_name)
                zip_count += 1
                # スピナーを一定時間ごとに回す
                spinning = True
                def spinner_loop(zc=zip_count, zt=zip_total):
                    nonlocal zip_spinner_idx, spinning
                    if not spinning:
                        return
                    zip_spinner_idx = (zip_spinner_idx + 1) % len(zip_spinner_seq)
                    spin_update(zc, zt, zip_spinner_idx)
                    self.progress_label.after(120, spinner_loop, zc, zt)
                spinning = True
                self.progress_label.after(0, spinner_loop, zip_count, zip_total)
                try:
                    shutil.make_archive(zip_path[:-4], 'zip', abs_dir)
                    if not zip_path.endswith('.zip'):
                        zip_path += '.zip'
                    self.log(f"ZIP化: {abs_dir} → {zip_path}")
                    filemap.append({
                        "original_path": relpath,
                        "flattened_name": os.path.basename(zip_path)
                    })
                except Exception as e:
                    self.log(f"ZIP化エラー: {abs_dir} : {e}")
                spinning = False
                # 最終状態を明示的に表示
                spin_update(zip_count, zip_total, zip_spinner_idx)
            # --- 通常ファイルのフラット化 ---
            for item in items:
                if not item['is_dir']:
                    skip = False
                    for z in zip_targets:
                        if item['relpath'].startswith(z + os.sep) or item['relpath'] == z:
                            skip = True
                            break
                    if skip:
                        continue
                    if item['relpath'] in exclude_targets:
                        self.log(f"スキップ（除外指定）: {item['relpath']}")
                        continue
                    ext = os.path.splitext(item['name'])[1].lower()
                    if ext and any(ext == ('.' + e.lstrip('.').lower()) for e in exclude_exts):
                        self.log(f"スキップ（除外拡張子）: {item['relpath']}")
                        continue
                    src_path = os.path.join(src, item['relpath'])
                    # flatten_filename高速化: 既存のままでは遅い場合はキャッシュ利用
                    if not hasattr(self, '_flatten_name_cache'):
                        self._flatten_name_cache = {}
                    relpath_key = item['relpath']
                    if relpath_key in self._flatten_name_cache:
                        flat_name = self._flatten_name_cache[relpath_key]
                    else:
                        flat_name = flatten_filename(relpath_key)
                        self._flatten_name_cache[relpath_key] = flat_name
                    dst_path = os.path.join(dst, flat_name)
                    try:
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        count += 1
                        filemap.append({
                            "original_path": item['relpath'],
                            "flattened_name": flat_name
                        })
                        self.log(f"コピー: {src_path} → {dst_path}")
                        # 進捗更新
                        self._flatten_progress['done_count'] += 1
                        size = item.get('size', 0)
                        if isinstance(size, int) and size >= 0:
                            self._flatten_progress['done_size'] += size
                        remain_count = self._flatten_progress['total_count'] - self._flatten_progress['done_count']
                        remain_size = self._flatten_progress['total_size'] - self._flatten_progress['done_size']
                        total = self._flatten_progress['total_count']
                        done = self._flatten_progress['done_count']
                        total_size = self._flatten_progress['total_size']
                        done_size = self._flatten_progress['done_size']
                        self.progress_label.after(0, lambda c=done, rc=remain_count, ds=done_size, rs=remain_size, t=total, ts=total_size: self.progress_label.config(
                            text=f" | 残り{rc:,}件, 処理済{c:,}件, 残り{self.human_readable_size(rs)} / {self.human_readable_size(ts)}"
                        ))
                    except Exception as e:
                        self.log(f"エラー: {src_path} → {dst_path} : {e}")
            out_csv = os.path.join(dst, "filemap.csv")
            FileMap.save_csv(filemap, out_csv)
            self.log(f"filemap.csv を出力: {out_csv}")
            self.log(f"\n完了: {count} ファイルをフラット化・{len(zip_targets)}フォルダをZIP化しました")
        finally:
            self.run_btn.config(state=tk.NORMAL)
            if hasattr(self, 'progress_label'):
                self.progress_label.after(0, lambda: self.progress_label.config(text=""))
            # 完了ポップアップ＋エクスプローラーで出力先を開く
            try:
                import subprocess
                messagebox.showinfo(
                    "完了",
                    "フラット化・ZIP化が完了しました！\n\n出力フォルダを開きます。\n\n※エクスプローラーでファイルが表示されない場合は、右クリック→最新の情報に更新 でリフレッシュしてください。"
                )
                if os.name == 'nt':
                    # Windows
                    os.startfile(dst)
                else:
                    # Mac/Linux
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', dst])
            except Exception as e:
                self.log(f"エクスプローラー起動エラー: {e}")

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

def main():
    app = FlattenApp()
    app.mainloop()

# 直接実行時は警告のみ（正しい起動経路は main.py 経由）
if __name__ == "__main__":
    import sys
    import tkinter.messagebox as mb
    mb.showerror("起動エラー", "このファイルを直接実行しないでください。\n必ず main.py から起動してください。\n(例: python -m flatten_app.main)")
    sys.exit(1)

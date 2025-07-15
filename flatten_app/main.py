
import sys
import os
# flatten_appディレクトリの親をsys.pathに追加（どこから実行してもOKにする）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    # --- デバッグ: どのFlattenApp/どのgui.pyが使われているかを記録 ---
    import os
    import sys
    import datetime
    try:
        from flatten_app import gui as gui_mod
        # バイナリ実行時はデバッグファイルを出力しない
        if hasattr(sys, '_MEIPASS'):
            pass
        else:
            debug_dir = os.path.dirname(os.path.abspath(__file__))
            debug_main_entry_path = os.path.join(debug_dir, "debug_main_entry.txt")
            with open(debug_main_entry_path, "w", encoding="utf-8") as f:
                f.write(f"main.py __file__ = {__file__}\n")
                f.write(f"gui_mod.__file__ = {getattr(gui_mod, '__file__', 'N/A')}\n")
                f.write(f"FlattenApp = {getattr(gui_mod, 'FlattenApp', 'N/A')}\n")
                f.write(f"datetime = {datetime.datetime.now()}\n")
    except Exception as e:
        try:
            if hasattr(sys, '_MEIPASS'):
                pass
            else:
                debug_dir = os.path.dirname(os.path.abspath(__file__))
                debug_main_entry_path = os.path.join(debug_dir, "debug_main_entry.txt")
                with open(debug_main_entry_path, "a", encoding="utf-8") as f:
                    f.write(f"[ERROR] {e}\n")
        except Exception:
            pass
    if '--cli' in sys.argv:
        print("CLIモード（未実装）")
    else:
        from flatten_app.gui import main as gui_main
        gui_main()

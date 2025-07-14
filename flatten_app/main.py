import sys

if __name__ == "__main__":
    if '--cli' in sys.argv:
        print("CLIモード（未実装）")
    else:
        from gui import main as gui_main
        gui_main()

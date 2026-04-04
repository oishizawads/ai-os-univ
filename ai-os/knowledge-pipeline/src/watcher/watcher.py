"""ファイル監視デーモン

raw/ を監視して新規 .md が来たら自動 ingest。
vault/ 全体を監視して変更があれば debounce 後に auto compile（オプション）。

起動:
  python main.py --watch              # ingest のみ自動
  python main.py --watch --auto-compile  # ingest + compile も自動
"""
import logging
import time
from pathlib import Path
from threading import Timer

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

# 最後のイベントからこの秒数後に処理を実行（連続保存をまとめる）
INGEST_DEBOUNCE = 5
COMPILE_DEBOUNCE = 60  # compile は重いので長めに待つ


class RawDirHandler(FileSystemEventHandler):
    """raw/ への新規ファイルを検出して auto-ingest"""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self._timer: Timer | None = None

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix == ".md" and not path.name.startswith("_"):
            logger.info("[watcher] 新規ファイル検出: %s", path.name)
            self._schedule()

    def on_moved(self, event):
        """Obsidian は一時ファイル経由で保存するので moved も監視"""
        if event.is_directory:
            return
        dest = Path(event.dest_path)
        if dest.suffix == ".md" and not dest.name.startswith("_"):
            logger.info("[watcher] ファイル移動検出: %s", dest.name)
            self._schedule()

    def _schedule(self):
        if self._timer:
            self._timer.cancel()
        self._timer = Timer(INGEST_DEBOUNCE, self._run_ingest)
        self._timer.daemon = True
        self._timer.start()

    def _run_ingest(self):
        try:
            from src.ingest.processor import process_new_files
            logger.info("[watcher] auto-ingest 開始")
            count = process_new_files(self.cfg)
            if count > 0:
                print(f"\n[auto-ingest] {count} 件を処理しました")
            else:
                logger.debug("[watcher] 新規ファイルなし（スキップ）")
        except Exception as e:
            logger.error("[watcher] ingest 失敗: %s", e)


class VaultChangeHandler(FileSystemEventHandler):
    """vault 全体の変更を検出して auto-compile（--auto-compile 時のみ）"""

    def __init__(self, cfg: dict, raw_dir: Path):
        self.cfg = cfg
        self.raw_dir = raw_dir
        self._timer: Timer | None = None

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        # raw/ の変更は RawDirHandler が担当するのでスキップ
        if self.raw_dir in path.parents:
            return
        if path.suffix == ".md" and not path.name.startswith("_"):
            self._schedule()

    def on_created(self, event):
        self.on_modified(event)

    def _schedule(self):
        if self._timer:
            self._timer.cancel()
        self._timer = Timer(COMPILE_DEBOUNCE, self._run_compile)
        self._timer.daemon = True
        self._timer.start()

    def _run_compile(self):
        try:
            from src.compiler.wiki import compile_wiki
            logger.info("[watcher] auto-compile 開始")
            compile_wiki(self.cfg, force=False)
            print("\n[auto-compile] wiki ページを更新しました")
        except Exception as e:
            logger.error("[watcher] compile 失敗: %s", e)


def start_watcher(cfg: dict, auto_compile: bool = False):
    vault_cfg = cfg["vault"]
    vault_root = Path(vault_cfg["path"])
    raw_dir = vault_root / vault_cfg.get("raw_dir", "raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    observer = Observer()

    # raw/ 監視（ingest）
    observer.schedule(RawDirHandler(cfg), str(raw_dir), recursive=False)

    # vault 全体監視（compile）— オプション
    if auto_compile:
        observer.schedule(VaultChangeHandler(cfg, raw_dir), str(vault_root), recursive=True)

    observer.start()

    mode_str = "ingest + compile" if auto_compile else "ingest"
    print(f"監視開始 [{mode_str}]")
    print(f"  raw/ : {raw_dir}")
    if auto_compile:
        print(f"  vault: {vault_root}")
    print("Web Clipper でクリップすると自動で ingest されます")
    if auto_compile:
        print(f"vault ファイル変更後 {COMPILE_DEBOUNCE}秒で auto-compile されます")
    print("停止: Ctrl+C\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n監視停止")
    finally:
        observer.stop()
        observer.join()

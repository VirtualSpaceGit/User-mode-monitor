import os, sys, time, threading, queue
from datetime import datetime
from collections import defaultdict
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32gui, win32con
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSize
from PySide6.QtGui import QPalette, QColor, QFont

COLOR_RESTORED = "#2ecc71"
COLOR_FILE     = "#00c8ff"
COLOR_INFO     = "#dcdcdc"

def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fmt(prefix, msg):
    return f"[{ts()}] {prefix} {msg}"

class WindowWatcher(QThread):
    s = Signal(str)
    def __init__(self):
        super().__init__()
        self.run_flag = True
        self.states = {}
    def stop(self):
        self.run_flag = False
    def run(self):
        while self.run_flag:
            cur = {}
            win32gui.EnumWindows(
                lambda h, _: cur.update({h: win32gui.GetWindowText(h)}) if win32gui.IsWindowVisible(h) else None,
                None
            )
            for h, title in cur.items():
                st = win32gui.GetWindowPlacement(h)[1]
                prev = self.states.get(h)
                if prev is None:
                    self.states[h] = st
                elif st != prev:
                    if st == win32con.SW_SHOWMINIMIZED:
                        self.s.emit(fmt("[-]", f"Window Minimized: {title}"))
                    elif prev == win32con.SW_SHOWMINIMIZED and st in (win32con.SW_SHOWNORMAL, win32con.SW_SHOWMAXIMIZED):
                        self.s.emit(fmt("[+]", f"Window Restored: {title}"))
                    self.states[h] = st
            for h in set(self.states) - set(cur):
                self.states.pop(h, None)
            time.sleep(0.5)

class ProcessWatcher(QThread):
    s = Signal(str)
    def __init__(self):
        super().__init__()
        self.run_flag = True
        self.procs = {p.pid for p in psutil.process_iter()}
    def stop(self):
        self.run_flag = False
    def run(self):
        while self.run_flag:
            cur = {p.pid for p in psutil.process_iter()}
            new  = cur - self.procs
            dead = self.procs - cur
            for pid in new:
                try:
                    self.s.emit(fmt("[+]", f"Process Started: {psutil.Process(pid).name()} (PID {pid})"))
                except psutil.NoSuchProcess:
                    pass
            for pid in dead:
                self.s.emit(fmt("[-]", f"Process Ended: PID {pid}"))
            self.procs = cur
            time.sleep(1)

class DirHandler(FileSystemEventHandler):
    def __init__(self, sig):
        super().__init__()
        self.sig = sig
    def _is_target(self, path):
        return path.lower().endswith(".exe")
    def on_created(self, e):
        if not e.is_directory and self._is_target(e.src_path):
            self.sig.emit(fmt("[+]", f"File Created: {e.src_path}"))
    def on_deleted(self, e):
        if not e.is_directory and self._is_target(e.src_path):
            self.sig.emit(fmt("[-]", f"File Deleted: {e.src_path}"))
    def on_moved(self, e):
        if e.is_directory:
            return
        if self._is_target(e.src_path):
            self.sig.emit(fmt("[-]", f"File Deleted: {e.src_path}"))
        if self._is_target(e.dest_path):
            self.sig.emit(fmt("[+]", f"File Created: {e.dest_path}"))

class FileWatcher(QThread):
    s = Signal(str)
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.observer = Observer()
        self.run_flag = True
    def stop(self):
        self.run_flag = False
        self.observer.stop()
        self.observer.join()
    def run(self):
        self.observer.schedule(DirHandler(self.s), self.path, recursive=True)
        self.observer.start()
        while self.run_flag:
            time.sleep(1)

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VirtualSpace Monitor")
        self.resize(1000, 650)
        self._set_palette()
        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(15, 15, 15, 15)
        v.setSpacing(10)
        header = QLabel("VirtualSpace Monitor", alignment=Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        v.addWidget(header)
        self.stats = QLabel(alignment=Qt.AlignCenter)
        self.stats.setFont(QFont("Segoe UI", 10))
        v.addWidget(self.stats)
        self.log = QTextEdit(readOnly=True)
        self.log.setFont(QFont("Consolas", 10))
        self.log.setStyleSheet("background:#1e1e1e;color:#dcdcdc;border-radius:6px;padding:6px;")
        v.addWidget(self.log, 1)
        h = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_stop  = QPushButton("Stop")
        for b in (self.btn_start, self.btn_stop):
            b.setFixedSize(QSize(110, 44))
            b.setFont(QFont("Segoe UI", 10, QFont.Bold))
            b.setCursor(Qt.PointingHandCursor)
        self.btn_start.setStyleSheet(
            "QPushButton{background:#007acc;color:#fff;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#409eff;}"
        )
        self.btn_stop.setStyleSheet(
            "QPushButton{background:#555;color:#fff;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#777;}"
        )
        self.btn_stop.setEnabled(False)
        h.addStretch(1)
        h.addWidget(self.btn_start)
        h.addWidget(self.btn_stop)
        h.addStretch(1)
        v.addLayout(h)
        self.btn_start.clicked.connect(self._start)
        self.btn_stop.clicked.connect(self._stop)
        self.threads = []
        self.msg_q   = queue.Queue()
        self.counts  = defaultdict(int)
        self._refresh_counts()
        self.timerId = self.startTimer(100)
    def _set_palette(self):
        pal = QPalette()
        pal.setColor(QPalette.Window,          QColor("#252526"))
        pal.setColor(QPalette.WindowText,      QColor("#d4d4d4"))
        pal.setColor(QPalette.Base,            QColor("#1e1e1e"))
        pal.setColor(QPalette.Text,            QColor("#d4d4d4"))
        pal.setColor(QPalette.Button,          QColor("#3c3c3c"))
        pal.setColor(QPalette.ButtonText,      QColor("#ffffff"))
        pal.setColor(QPalette.Highlight,       QColor("#007acc"))
        pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(pal)
    def _launch(self, thread):
        thread.s.connect(self._enqueue)
        thread.start()
        self.threads.append(thread)
    @Slot()
    def _start(self):
        self._enqueue(fmt("[i]", "Monitor started"))
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        sys_drive = os.getenv("SystemDrive", "C:") + "\\"
        self._launch(WindowWatcher())
        self._launch(ProcessWatcher())
        self._launch(FileWatcher(sys_drive))
    @Slot()
    def _stop(self):
        self._enqueue(fmt("[i]", "Stopping monitor…"))
        for th in self.threads:
            th.stop()
        for th in self.threads:
            th.wait()
        self.threads.clear()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self._enqueue(fmt("[i]", "Monitor stopped"))
    @Slot(str)
    def _enqueue(self, msg):
        self.msg_q.put(msg)
    def _color_for(self, msg):
        if "Restored" in msg:
            return COLOR_RESTORED
        if "File Created" in msg or "File Deleted" in msg:
            return COLOR_FILE
        return COLOR_INFO
    def _update_counts(self, msg):
        if "File Created" in msg:
            self.counts['files_created'] += 1
        elif "File Deleted" in msg:
            self.counts['files_deleted'] += 1
        elif "Process Started" in msg:
            self.counts['procs_started'] += 1
        elif "Process Ended" in msg:
            self.counts['procs_ended'] += 1
        elif "Window Minimized" in msg:
            self.counts['win_min'] += 1
        elif "Window Restored" in msg:
            self.counts['win_restored'] += 1
        self._refresh_counts()
    def _refresh_counts(self):
        c = self.counts
        self.stats.setText(
            f"Files +{c['files_created']} / -{c['files_deleted']}    |    "
            f"Procs +{c['procs_started']} / -{c['procs_ended']}    |    "
            f"Windows min {c['win_min']} / restored {c['win_restored']}"
        )
    def timerEvent(self, _):
        try:
            while True:
                msg = self.msg_q.get_nowait()
                self._update_counts(msg)
                color = self._color_for(msg)
                self.log.append(f"<span style='color:{color};'>{msg}</span>")
                self.log.moveCursor(self.log.textCursor().End)
        except queue.Empty:
            pass
    def closeEvent(self, e):
        if self.threads:
            self._stop()
        e.accept()

def main():
    app = QApplication(sys.argv)
    ui  = UI()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

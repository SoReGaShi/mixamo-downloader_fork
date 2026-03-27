# Stdlib modules
import json
import os

# Third-party modules - PySide6に書き換え
from PySide6 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets, QtWebEngineCore

# Local modules
from downloader import HEADERS
from downloader import MixamoDownloader
from webpage import CustomWebPage


class MixamoDownloaderUI(QtWidgets.QMainWindow):
    """Main UI that allows users to bulk download animations from Mixamo."""

    def __init__(self):        
        """Initialize the Mixamo Downloader UI."""
        super().__init__()
        
        # Set the window title and size.
        self.setWindowTitle('Mixamo Bulk Downloader (PySide6 Mac)')
        self.setGeometry(100, 100, 1200, 800)
        # アイコンファイルがない場合はエラーにならないよう注意
        if os.path.exists("mixamo.ico"):
            self.setWindowIcon(QtGui.QIcon("mixamo.ico"))

        # Create a QWebEngineView instance
        self.browser = QtWebEngineWidgets.QWebEngineView()

        # Create an instance of our custom QWebEnginePage.
        self.page = CustomWebPage() # selfに保持させておくのが安全です
        # Set the Mixamo website as its URL.
        self.page.setUrl((QtCore.QUrl('https://www.mixamo.com')))
        # Apply this page to the web browser.
        self.browser.setPage(self.page)
        
        # Signal connection
        self.page.retrieved_token.connect(self.apply_token)

        # UI Layout setup
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        central_widget.setLayout(layout)

        layout.addWidget(self.browser)

        footer_lyt = QtWidgets.QVBoxLayout()
        layout.addLayout(footer_lyt)

        anim_opt_lyt = QtWidgets.QHBoxLayout()
        footer_lyt.addLayout(anim_opt_lyt)

        self.rb_all = QtWidgets.QRadioButton("All animations")
        self.rb_all.setChecked(True)

        self.rb_query = QtWidgets.QRadioButton("Animations containing the word:")
        self.le_query = QtWidgets.QLineEdit()
        self.le_query.setEnabled(False)

        self.rb_tpose = QtWidgets.QRadioButton("T-Pose (with skin)")

        # Connect radio buttons
        self.rb_query.toggled.connect(self.le_query.setEnabled)
        self.rb_all.toggled.connect(lambda checked: self.le_query.setEnabled(not checked))
        self.rb_tpose.toggled.connect(lambda checked: self.le_query.setEnabled(not checked))

        anim_opt_lyt.addWidget(self.rb_all)
        anim_opt_lyt.addWidget(self.rb_query)
        anim_opt_lyt.addWidget(self.le_query)
        anim_opt_lyt.addWidget(self.rb_tpose)

        output_dir_lyt = QtWidgets.QHBoxLayout()
        footer_lyt.addLayout(output_dir_lyt)

        gbox_output = QtWidgets.QGroupBox("Output Folder")
        gbox_output.setMaximumHeight(70)
        gbox_output_lyt = QtWidgets.QHBoxLayout()
        gbox_output.setLayout(gbox_output_lyt)

        self.le_path = QtWidgets.QLineEdit()
        tb_path = QtWidgets.QToolButton()
        icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon)
        tb_path.setIcon(icon)
        tb_path.clicked.connect(self.set_path)

        gbox_output_lyt.addWidget(self.le_path)
        gbox_output_lyt.addWidget(tb_path)
        output_dir_lyt.addWidget(gbox_output)

        self.get_btn = QtWidgets.QPushButton('Start download')
        self.get_btn.clicked.connect(self.get_access_token)
        footer_lyt.addWidget(self.get_btn)

        prog_lyt = QtWidgets.QHBoxLayout()
        footer_lyt.addLayout(prog_lyt)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFormat("Downloading %v/%m")
        # Qt6の配置指定フラグに修正
        self.progress_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        prog_lyt.addWidget(self.progress_bar)

        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_download)        
        prog_lyt.addWidget(self.stop_btn)        
        
        self.setCentralWidget(central_widget)

    def get_access_token(self):
        script = """
        var token = localStorage.getItem('access_token');
        console.log('ACCESS TOKEN:', token);
        """
        self.browser.page().runJavaScript(script)

    def apply_token(self, token):
        HEADERS["Authorization"] = f"Bearer {token}"
        self.run_downloader()

    def run_downloader(self):
        """Wrapper method that sets everything up for the download."""
        
        # 1. まずUIから必要な情報をすべて取得する
        mode = self.get_mode()
        query = self.le_query.text()
        path = self.le_path.text()

        # 2. スレッドとワーカーの準備
        self.thread = QtCore.QThread()
        self.worker = MixamoDownloader(path, mode, query)
        self.worker.moveToThread(self.thread)

        # 3. シグナルとスロットの接続（実行開始）
        self.thread.started.connect(self.worker.run)

        # 4. 終了時の後処理
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # 終了したらボタンの状態を元に戻す
        self.thread.finished.connect(lambda: self.stop_btn.setEnabled(False))
        self.thread.finished.connect(lambda: self.get_btn.setEnabled(True))

        # 5. 進捗状況の更新用シグナル
        self.worker.total_tasks.connect(self.set_progress_bar)
        self.worker.current_task.connect(self.update_progress_bar)

        # 6. スレッドを開始する直前にボタンの状態を切り替える（確実な方法）
        self.stop_btn.setEnabled(True)
        self.get_btn.setEnabled(False)

        # 7. スレッド開始
        self.thread.start()

    def set_progress_bar(self, total_tasks):
        self.progress_bar.reset()
        self.progress_bar.setRange(0, total_tasks)

    def update_progress_bar(self, step):
        self.progress_bar.setValue(step)

    def stop_download(self):
        if hasattr(self, 'worker'):
            self.worker.stop = True

    def set_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the output folder')
        if path:
            self.le_path.setText(path)

    def get_mode(self):
        if self.rb_all.isChecked():
            return "all"
        elif self.rb_query.isChecked():
            return "query"
        elif self.rb_tpose.isChecked():
            return "tpose"

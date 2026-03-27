# Third-party modules - PySide2からPySide6に変更
from PySide6 import QtWidgets
import sys

# Local modules
from ui import MixamoDownloaderUI

if __name__ == "__main__":
    # Macなどの環境で引数を正しく扱うために sys.argv を渡すのが推奨されます
    app = QtWidgets.QApplication(sys.argv)

    md = MixamoDownloaderUI()
    md.show()

    # PySide6 (Qt6) では app.exec_() ではなく app.exec() が標準ですが
    # 互換性のために exec_() も動くことが多いです。最新の書き方に合わせておきます。
    sys.exit(app.exec())

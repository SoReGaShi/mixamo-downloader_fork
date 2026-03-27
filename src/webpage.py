# Third-party modules - PySide6に書き換え
from PySide6 import QtCore, QtWebEngineCore, QtWebEngineWidgets

# クラス定義の継承元を QtWebEngineCore に変更します
class CustomWebPage(QtWebEngineCore.QWebEnginePage):
    """Custom QWebEnginePage that catches data from the JavaScript console."""    

    # PySide6でのシグナル定義
    retrieved_token = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """
        PySide6(Qt6)では、メソッドを直接 self.javaScriptConsoleMessage に
        代入するのではなく、このようにメソッド自体をオーバーライドします。
        """
        # コンソールメッセージに "ACCESS TOKEN" が含まれているかチェック
        if "ACCESS TOKEN" in message:
            # メッセージからトークン部分を抽出
            access_token = message.split(":")[-1].strip()
            # シグナルを飛ばしてUI側に伝える
            self.retrieved_token.emit(access_token)
        
        # デバッグ用に通常のコンソール出力も維持したい場合は継承元を呼ぶ（任意）
        # super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

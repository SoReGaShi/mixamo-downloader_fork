# Mixamo Downloader
GUI to bulk download animations from [Mixamo](https://www.mixamo.com/).

This repository contains both the Python source code (in the `/src` folder) and an `.exe` file (in the `/dist` folder) to make things easier to Windows users.

### For Python users

Make sure you have [Python 3.10+](https://www.python.org/) installed on your computer, as well as the [PySide2](https://pypi.org/project/PySide2/) package:

```bash
pip install PySide2
```

Download the files from the `/src` folder to your own local directory, and double-click on the `main.pyw` script to launch the GUI.

### For non-technical users
If you don't have Python installed on your computer or you don't want to mess with all that coding stuff, download the `/dist` folder to your computer (~300MB) and run the `mixamo_downloader.exe`.

## How to use the Mixamo Downloader

1. Log into your Mixamo account.
2. Select/upload the character you want to animate.
3. Choose between downloading `All animations`, `Animations containing the word` and the `T-Pose (with skin)`.
4. You can optionally set an output folder where all animations will be saved.


=============================
以下、独自改良点に関する説明
=============================


📝 開発備忘録：安定性と利便性のための大幅アップデート (2026/03)
オリジナルのリポジトリをベースに、現代のMixamoサーバー環境への適合と、Apple Silicon搭載Macでのネイティブ動作、および数千規模のファイルを「完全放置」で完遂させるための抜本的な改良を行いました。

1. 技術スタックの刷新：PySide6 (Qt6) への移行

Apple Silicon (M1/M2/M3) ネイティブ対応: レガシーな PySide2 を廃止し、最新の PySide6 を採用。Rosetta 2を介さないネイティブ動作により、MacBook Air等の環境でメモリ管理の安定性とUIレスポンスが飛躍的に向上しました。

ライブラリの現代化: 最新のQt6仕様に合わせ、QtCore, QtWebEngineWidgets, QtWidgets などのモジュール構成を再構築しました。

2. 接続安定性の強化（Connection Aborted 対策）

ポーリング間隔の最適化 (time.sleep(3~5)): アニメーション生成の監視間隔を従来の1秒から延長。サーバーへのリクエスト密度を下げ、「Connection Aborted（強制切断）」を劇的に減少させました。

10件ごとのセッション・リフレッシュ: 10個のダウンロード成功ごとにHTTPセッションを完全に破棄・再構築（および15秒のクールダウン）を行います。これにより、長時間接続に伴うサーバー側からの拒絶を回避します。

3. エラーハンドリングの精密化

HTTP 202 (Accepted) の正当な処理: サーバーが生成中を返す「202」をエラーと誤認せず、「正常な待機状態」としてループを継続。無駄なリトライ消費やスキップを排除しました。

自律型リトライ・オーケストレーション: 一時的な通信エラーやタイムアウトが発生しても、3回までの自動リトライを実行。それでも失敗した場合はログを残して次へ進む「止まらない」設計を実現しました。

4. 利便性とディレクトリ管理のインテリジェント化

デフォルト保存先の自動解決: 保存先未指定時、実行スクリプト（src/）の親階層に Mixamo_Full_Download フォルダを自動特定・作成。環境構築の手間を省きました。

絶対パスの可視化: 開始時に保存先のフルパスをコンソールに明示。膨大なデータの着弾先を即座に確認可能です。

5. パフォーマンス最適化

存在チェックによる爆速スキップ: ダウンロード開始前にローカルファイルを確認し、同名かつ有効なファイルがある場合は通信自体をスキップ。中断後の再開をミリ秒単位で開始できます。





   > If no output folder is set, FBX files will be downloaded to the folder where the program is running.
  
5. Press the `Start download` button and wait until it's done.
6. You can cancel the process at any time by pressing the `Stop` button.

> [!IMPORTANT]
> Downloading all animations can be quite slow. We're dealing with a total of 2346 animations, so don't expect it to be lighting fast.

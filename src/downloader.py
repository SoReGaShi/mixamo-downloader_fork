# Stdlib modules
import json
import os
import requests
import time
import random

# Third-party modules
from PySide6 import QtCore, QtWebEngineWidgets, QtWidgets

HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "X-Api-Key": "mixamo2",
    "X-Requested-With": "XMLHttpRequest",
}

# All requests will be done through a session to improve performance.
session = requests.Session()

class MixamoDownloader(QtCore.QObject):
    """Bulk download animations from Mixamo."""
    
    finished = QtCore.Signal()
    total_tasks = QtCore.Signal(int)
    current_task = QtCore.Signal(int)

    task = 1
    stop = False

    def __init__(self, path=None, mode="all", query=None):
        super().__init__()
        
        # 保存先(path)が指定されていない（空の）場合のデフォルト設定
        if not path:
            # 1. このファイル(downloader.py)がある場所を取得
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # 2. その1つ上の階層（プロジェクトのルート）を取得
            project_root = os.path.dirname(current_file_dir)
            # 3. 1つ上の階層に「Mixamo_Full_Download」というパスを作成
            self.path = os.path.join(project_root, "Mixamo_Full_Download")
        else:
            self.path = path

        # フォルダが存在しなければ、ここで自動的に作成する（手動作成不要！）
        os.makedirs(self.path, exist_ok=True)
        
        self.mode = mode
        self.query = query
        self.product_name = ""

    def run(self):
        global session # セッションを書き換えるために必要

        # 🚨 【追加】ダウンロード開始時に保存先をコンソールに表示する
        print(f"🚀 ダウンロードを開始します...")
        print(f"📁 保存先: {os.path.abspath(self.path)}")
        print("-" * 30)

        character_id = self.get_primary_character_id()
        character_name = self.get_primary_character_name()
        if not character_id:
            return

        # DOWNLOAD MODE: TPOSE
        if self.mode == "tpose":
            self.total_tasks.emit(1)
            tpose_payload = self.build_tpose_payload(character_id, character_name)
            url = self.export_animation(character_id, tpose_payload)
            if url:
                self.download_animation(url)
            self.finished.emit()
            return

        # DOWNLOAD MODE: ALL / QUERY
        anim_data = {}
        if self.mode == "all":
            anim_data = self.get_all_animations_data()
        elif self.mode == "query":
            anim_data = self.get_queried_animations_data(self.query)

        downloaded_count = 0  # 全体の成功数
        session_dl_count = 0  # 現在のセッションでの成功数（10個でリセット）

        for anim_id, anim_name in anim_data.items():
            if self.stop:
                self.finished.emit()
                return

            # ====== 1. 爆速スキップ（ファイルが既に存在する場合はスルー） ======
            clean_name = anim_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
            file_full_path = os.path.join(self.path, f"{clean_name}.fbx") if self.path else f"{clean_name}.fbx"

            if os.path.exists(file_full_path) and os.path.getsize(file_full_path) > 0:
                self.task += 1
                self.current_task.emit(self.task)
                continue

            # ====== 2. 🚨 10個成功するごとに確実なセッションリセット ======
            if session_dl_count >= 10:
                print("🔄 10個処理しました。サーバー切断を防ぐため通信をリセットします（約15秒待機）...")
                session.close()
                session = requests.Session()
                time.sleep(15)
                session_dl_count = 0

            # ====== 3. ダウンロード処理と自動リトライ ======
            max_retries = 3
            success = False
            
            for attempt in range(max_retries):
                try:
                    anim_payload = self.build_animation_payload(character_id, anim_id)
                    url = self.export_animation(character_id, anim_payload)
                    
                    if url:
                        self.download_animation(url)
                        success = True
                    break 

                except Exception as e:
                    print(f"⚠️ エラー検知 ({attempt + 1}/{max_retries}回目): {e}")
                    
                    # エラー時はセッションをクリーンにして仕切り直す
                    session.close()
                    session = requests.Session()
                    
                    if attempt < max_retries - 1:
                        time.sleep(15) # エラー時はしっかり15秒休む
                    else:
                        print(f"❌ [{anim_name}] をスキップして次へ進みます。")
                        self.task += 1
                        self.current_task.emit(self.task)

            if success:
                downloaded_count += 1
                session_dl_count += 1
                # 成功時は少しだけ待って次へ
                time.sleep(random.uniform(2.5, 4.5))

        self.finished.emit()
        return

    def get_primary_character_id(self):
        response = session.get(f"https://www.mixamo.com/api/v1/characters/primary", headers=HEADERS)
        return response.json().get("primary_character_id")

    def get_primary_character_name(self):
        response = session.get(f"https://www.mixamo.com/api/v1/characters/primary", headers=HEADERS)
        return response.json().get("primary_character_name")

    def build_tpose_payload(self, character_id, character_name):
        self.product_name = character_name
        payload = {
            "character_id": character_id,
            "product_name": self.product_name,
            "type": "Character",
            "preferences": {"format":"fbx7_2019", "mesh":"t-pose"},
            "gms_hash": None
        }
        return json.dumps(payload)

    def get_queried_animations_data(self, query):
        page_num = 1
        params = {"limit": 96, "page": page_num, "type": "Motion", "query": query}
        response = session.get("https://www.mixamo.com/api/v1/products", headers=HEADERS, params=params)
        data = response.json()
        num_pages = data["pagination"]["num_pages"]
        animations = []

        while page_num <= num_pages:
            params["page"] = page_num
            response = session.get("https://www.mixamo.com/api/v1/products", headers=HEADERS, params=params)
            data = response.json()
            animations.extend(data["results"])
            page_num += 1

        anim_data = {}
        for animation in animations:      
            anim_data[animation["id"]] = animation["description"]

        self.total_tasks.emit(len(anim_data))    
        return anim_data

    def get_all_animations_data(self):
        anim_data = {}
        with open("mixamo_anims.json", "r") as file:
            anim_data = json.load(file)

        self.total_tasks.emit(len(anim_data))
        return anim_data

    def build_animation_payload(self, character_id, anim_id):
        response = session.get(f"https://www.mixamo.com/api/v1/products/{anim_id}?similar=0&character_id={character_id}", headers=HEADERS)
        res_json = response.json()
        self.product_name = res_json["description"]
        _type = res_json["type"]

        # 変換に最適な設定（FBX2019、60FPS、Skinなし）
        preferences = {
            "format": "fbx7_2019",
            "skin": "false",
            "fps": "60",
            "reducekf": "0"
        }

        gms_hash = res_json["details"]["gms_hash"]
        gms_hash_params = gms_hash["params"]
        param_values = [int(param[-1]) for param in gms_hash_params]       
        params_string = "," .join(str(val) for val in param_values)

        gms_hash["params"] = params_string
        gms_hash["overdrive"] = 0
        trim_start = int(gms_hash["trim"][0])
        trim_end = int(gms_hash["trim"][1])
        gms_hash["trim"] = [trim_start, trim_end]

        payload = {
            "character_id": character_id,
            "product_name": self.product_name,
            "type": _type,
            "preferences": preferences,
            "gms_hash": [gms_hash]
        }
        return json.dumps(payload)

    def export_animation(self, character_id, payload):
        response = session.post(f"https://www.mixamo.com/api/v1/animations/export", data=payload, headers=HEADERS)

        status = None
        timeout_counter = 0  # 無限ループ防止用のカウンター

        while status != "completed":
            time.sleep(3) # サーバーへの負荷を下げるために3秒待機
            timeout_counter += 1
            
            # 約90秒待っても終わらない場合は異常とみなす
            if timeout_counter > 30:
                raise Exception("サーバーでの処理がタイムアウトしました。")

            response = session.get(f"https://www.mixamo.com/api/v1/characters/{character_id}/monitor", headers=HEADERS)
            
            # 🚨 【修正箇所】 200番台（成功・処理中）はスルーし、400番以上の「本当のエラー」だけを弾く
            if response.status_code >= 400:
                raise Exception(f"サーバーエラー: HTTP {response.status_code}")

            status = response.json().get("status")
            
            # Mixamo側で処理失敗した場合
            if status == "failed":
                raise Exception("Mixamo側でアニメーションの生成に失敗しました。")
        
        return response.json().get("job_result")

    def download_animation(self, url):
        if url:
            response = session.get(url)
            clean_name = self.product_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")

            if self.path:
                os.makedirs(self.path, exist_ok=True)
                file_path = os.path.join(self.path, f"{clean_name}.fbx")
            else:
                file_path = f"{clean_name}.fbx"

            with open(file_path, "wb") as f:
                f.write(response.content)

            self.current_task.emit(self.task)
            self.task += 1

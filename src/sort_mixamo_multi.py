import os
import shutil

# --- パス設定（src直下から1つ上の階層を参照するように変更） ---
# このファイル(src/sort_mixamo_multi.py)の場所を取得
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 1つ上のプロジェクトルート階層を取得
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# 保存先・出力先をプロジェクトルート基準に設定
SOURCE_DIR = os.path.join(PROJECT_ROOT, "Mixamo_Full_Download")
DEST_DIR = os.path.join(PROJECT_ROOT, "Mixamo_Categorized")

# --- 分類ルール（変更なし） ---
CATEGORIES = {
    "01_移動・歩き・走り (Locomotion)": [
        "walk", "run", "sprint", "jog", "strafe", "turn", "step", "move", 
        "flee", "shuffle", "slide", "retreat", "advance", "catwalk"
    ],
    "02_待機・ポーズ (Idles)": [
        "idle", "breathing", "pose", "stand", "laying", "stretching", "wait", 
        "prone", "kneel", "crouch", "sleep", "floating"
    ],
    "03_パルクール・障害物移動 (Traversal)": [
        "jump", "climb", "hang", "roll", "dodge", "vault", "leap", "slip", 
        "crawl", "dive", "shimmy", "ledge", "sneak", "stealth"
    ],
    "04_素手格闘・アクション (Unarmed_Combat)": [
        "punch", "kick", "boxing", "mma", "fight", "uppercut", "jab", "hadouken", 
        "strike", "combat", "block", "sweep", "headbutt", "choke", "takedown", 
        "assassination", "strangl", "smash"
    ],
    "05_剣・近接武器 (Melee)": [
        "sword", "axe", "shield", "dagger", "stab", "slash", "melee", "blade", 
        "club", "spear", "knife", "torch", "pipe", "bayonet", "whip"
    ],
    "06_銃・火器 (Shooter)": [
        "rifle", "pistol", "gun", "shoot", "aim", "fire", "grenade", "reload", 
        "sniper", "handgun", "cannon", "artillery"
    ],
    "07_魔法・弓・ファンタジー (Magic_Bow)": [
        " bow", "arrow", "cast", "spell", "magic", "conjuring", "resurrection", "summon"
    ],
    "08_被弾・死亡・ダメージ (Hit_Death)": [
        " hit", "reaction", "dying", "death", "impact", "agony", "injured", 
        "knocked", "fall", "stumble", "damage", "flinch", "hurt", "dead", 
        "unconscious", "electrocuted", "pain", "convulsing", "seizure", "stroke", 
        "vomiting", "dazed", "dizzy"
    ],
    "09_ダンス・踊り (Dance)": [
        "dance", "dancing", "hip hop", "salsa", "breakdance", "samba", "capoeira", 
        "ballet", "rumba", "bboy", "swing", "macarena", "charleston", "bellydance", 
        "boogaloo", "shim sham", "moonwalk", "twist", "hokey pokey", "ymca", "cabbage patch"
    ],
    "10_スポーツ・運動 (Sports)": [
        "soccer", "baseball", "golf", "workout", "squat", "push up", "football", 
        "kettlebell", "situp", "burpee", "dribble", "catch", "pitch", "putt", 
        "goalkeeper", "goalie", "umpire", "gym", "juggling", "fitness", "plank", 
        "bicycle", "snatch", "hike", "quarterback", "receiver", "tackle", "batting"
    ],
    "11_日常動作・会話・感情 (Social_Everyday)": [
        " sit", "sitting", "talk", "phone", "laugh", "cheer", "wave", "clap", 
        "text", "drink", "drive", "type", "agree", "nod", "yell", "cry", "argue", 
        "gesture", "examine", "petting", "milking", "fishing", "shaking", 
        "inspecting", "rubbing", "shrugging", "typing", "praying", "greeting", 
        "kissing", "chat", "look", "search", "carry", "wheelbarrow", "box", 
        "briefcase", "suitcase", "pushing", "pulling", "victory", "defeat", "celebrat"
    ],
    "12_怪物・モンスター (Creature)": [
        "zombie", "mutant", "orc", "dwarf", "giant", "clown", "monster", "creature"
    ]
}

def sort_animations_multi():
    # パスを表示（安心のため）
    print(f"📁 読み込み元: {os.path.abspath(SOURCE_DIR)}")
    print(f"📁 分類先: {os.path.abspath(DEST_DIR)}")
    print("-" * 30)

    if not os.path.exists(SOURCE_DIR):
        print(f"❌ エラー: '{SOURCE_DIR}' が見つかりません。")
        print("Mixamo_Full_Download フォルダがプロジェクトルートにあるか確認してください。")
        return

    os.makedirs(DEST_DIR, exist_ok=True)
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.fbx')]
    
    category_counters = {cat: 1 for cat in CATEGORIES.keys()}
    category_counters["99_その他 (Others)"] = 1
    
    catalogs = {cat: [] for cat in CATEGORIES.keys()}
    catalogs["99_その他 (Others)"] = []

    print(f"合計 {len(files)} 個のファイルを仕分け中...\n")

    copy_count = 0

    for file_name in files:
        source_path = os.path.join(SOURCE_DIR, file_name)
        lower_name = file_name.lower()
        
        matched_categories = []
        for category, keywords in CATEGORIES.items():
            if any(keyword in lower_name for keyword in keywords):
                matched_categories.append(category)

        if not matched_categories:
            matched_categories.append("99_その他 (Others)")

        for category in matched_categories:
            idx = category_counters[category]
            new_filename = f"{idx:03d}_{file_name}"
            category_dir = os.path.join(DEST_DIR, category)
            os.makedirs(category_dir, exist_ok=True)
            
            dest_path = os.path.join(category_dir, new_filename)
            if not os.path.exists(dest_path):
                shutil.copy2(source_path, dest_path)
                copy_count += 1
            
            catalogs[category].append({
                "index": idx,
                "file_name": new_filename
            })
            category_counters[category] += 1

    # カタログテキストファイルの出力
    for category, items in catalogs.items():
        if not items:
            continue
        category_dir = os.path.join(DEST_DIR, category)
        catalog_path = os.path.join(category_dir, "_Catalog.txt")
        with open(catalog_path, "w", encoding="utf-8") as f:
            f.write("Index\tFileName\n")
            for item in items:
                idx_str = f"{item['index']:03d}"
                f.write(f"{idx_str}\t{item['file_name']}\n")

    print("-" * 30)
    print("✨ 仕分け完了！")
    print(f"📁 総コピーファイル数: {copy_count} 件")

if __name__ == "__main__":
    sort_animations_multi()

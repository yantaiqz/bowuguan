import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import base64

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------- 路径修复 -------------
try:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except:
    PROJECT_ROOT = os.getcwd()
BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
os.makedirs(BASE_IMG_ROOT, exist_ok=True)

# ==========================================
# 2. 核心数据 & 翻译配置
# ==========================================
MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}
MUSEUM_NAME_MAP_REVERSE = {v: k for k, v in MUSEUM_NAME_MAP.items()}

# 豪宅配置：真实 Unsplash 高清图 + 双语
MANSION_CONFIG = {
    "南京博物院": {
        "mansion_name_zh": "颐和路民国公馆", "mansion_name_en": "Yihe Road Mansion",
        "price": 100000000,
        "mansion_img": "https://images.unsplash.com/photo-1600596542815-374e2e3c5545?auto=format&fit=crop&w=800&q=80"
    },
    "三星堆博物馆": {
        "mansion_name_zh": "成都麓山国际庄园", "mansion_name_en": "Chengdu Luxury Estate",
        "price": 50000000,
        "mansion_img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80"
    },
    "中国国家博物馆": {
        "mansion_name_zh": "什刹海二进四合院", "mansion_name_en": "Shichahai Courtyard",
        "price": 150000000,
        "mansion_img": "https://images.unsplash.com/photo-1599619351208-3e6c839d6828?auto=format&fit=crop&w=800&q=80"
    },
    "上海博物馆": {
        "mansion_name_zh": "愚园路百年老洋房", "mansion_name_en": "Shanghai Heritage Villa",
        "price": 200000000,
        "mansion_img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
    },
    "陕西历史博物馆": {
        "mansion_name_zh": "曲江池畔空中大平层", "mansion_name_en": "Qujiang Lake Penthouse",
        "price": 30000000,
        "mansion_img": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80"
    }
}

# 藏品数据 (已补充双语字段)
MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name_zh": "金兽", "name_en": "Golden Beast", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "含金量99%，最重金器", "desc_en": "Heaviest ancient gold artifact", "price": 500000000, "img": ""},
        {"id": "nj_2", "name_zh": "釉里红梅瓶", "name_en": "Underglaze Red Vase", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "存世稀少，釉里红巅峰", "desc_en": "Rare red underglaze masterpiece", "price": 800000000, "img": ""},
        {"id": "nj_3", "name_zh": "金蝉玉叶", "name_en": "Gold Cicada on Jade Leaf", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "金枝玉叶，工艺精湛", "desc_en": "Exquisite gold & jade craft", "price": 90000000, "img": ""},
        {"id": "nj_4", "name_zh": "银缕玉衣", "name_en": "Silver-thread Jade Suit", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "银丝编缀，极其罕见", "desc_en": "Rare silver-threaded burial suit", "price": 300000000, "img": ""},
        {"id": "nj_5", "name_zh": "竹林七贤砖画", "name_en": "Seven Sages Brick Relief", "period_zh": "南朝", "period_en": "Southern Dynasties", "desc_zh": "魏晋风度最佳见证", "desc_en": "Masterpiece of Wei-Jin art", "price": 1000000000, "img": ""},
        {"id": "nj_6", "name_zh": "大报恩寺拱门", "name_en": "Porcelain Tower Arch", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "世界奇迹残留组件", "desc_en": "Remnant of a world wonder", "price": 200000000, "img": ""},
        {"id": "nj_7", "name_zh": "坤舆万国全图", "name_en": "Kunyu Wanguo Quantu", "period_zh": "明万历", "period_en": "Wanli Period", "desc_zh": "最早彩绘世界地图", "desc_en": "Earliest colored world map", "price": 600000000, "img": ""},
        {"id": "nj_8", "name_zh": "广陵王玺", "name_en": "Seal of Prince Guangling", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "汉代封王金印精品", "desc_en": "Exquisite Han gold seal", "price": 200000000, "img": ""},
        {"id": "nj_9", "name_zh": "错银铜牛灯", "name_en": "Inlaid Silver Ox Lamp", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "汉代环保黑科技", "desc_en": "Eco-friendly ancient lamp", "price": 180000000, "img": ""},
        {"id": "nj_10", "name_zh": "青瓷神兽尊", "name_en": "Celadon Beast Vessel", "period_zh": "西晋", "period_en": "Western Jin", "desc_zh": "造型奇特的早期青瓷", "desc_en": "Unique early celadon", "price": 120000000, "img": ""},
        {"id": "nj_11", "name_zh": "透雕人鸟兽玉饰", "name_en": "Jade Ornament", "period_zh": "良渚", "period_en": "Liangzhu", "desc_zh": "史前玉器巅峰", "desc_en": "Prehistoric jade masterpiece", "price": 60000000, "img": ""},
        {"id": "nj_12", "name_zh": "鎏金喇嘛塔", "name_en": "Gilt Lama Pagoda", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "通体鎏金镶宝石", "desc_en": "Gilded and gem-encrusted", "price": 80000000, "img": ""},
        {"id": "nj_13", "name_zh": "青花寿山福海炉", "name_en": "Blue & White Censer", "period_zh": "明宣德", "period_en": "Xuande Period", "desc_zh": "宣德官窑完整大器", "desc_en": "Imperial Ming porcelain", "price": 450000000, "img": ""},
        {"id": "nj_14", "name_zh": "徐渭《杂花图》", "name_en": "Xu Wei's Painting", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "大写意水墨巅峰", "desc_en": "Peak of freehand brushwork", "price": 350000000, "img": ""},
        {"id": "nj_15", "name_zh": "沈寿《耶稣像》", "name_en": "Embroidery of Jesus", "period_zh": "近代", "period_en": "Modern Era", "desc_zh": "万国博览会金奖", "desc_en": "Gold medal embroidery", "price": 50000000, "img": ""},
        {"id": "nj_16", "name_zh": "芙蓉石蟠螭炉", "name_en": "Quartz Censer", "period_zh": "清乾隆", "period_en": "Qianlong Period", "desc_zh": "乾隆御用粉嫩玉石", "desc_en": "Emperor's favorite quartz", "price": 130000000, "img": ""},
        {"id": "nj_17", "name_zh": "人面兽面玉琮", "name_en": "Jade Cong", "period_zh": "良渚", "period_en": "Liangzhu", "desc_zh": "微雕工艺神作", "desc_en": "Micro-carving miracle", "price": 150000000, "img": ""},
        {"id": "nj_18", "name_zh": "青瓷釉下彩壶", "name_en": "Underglaze Color Pot", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "改写陶瓷史的孤品", "desc_en": "Unique Tang ceramic", "price": 110000000, "img": ""},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name_zh": "青铜大立人", "name_en": "Bronze Standing Figure", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "世界铜像之王", "desc_en": "King of bronze statues", "price": 2000000000, "img": ""},
        {"id": "sx_2", "name_zh": "青铜神树", "name_en": "Bronze Sacred Tree", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "通天神树", "desc_en": "Divine tree to heaven", "price": 2500000000, "img": ""},
        {"id": "sx_3", "name_zh": "金面具", "name_en": "Gold Mask", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "半张黄金脸", "desc_en": "Symbol of royal power", "price": 800000000, "img": ""},
        {"id": "sx_4", "name_zh": "青铜纵目面具", "name_en": "Protruding Eye Mask", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "千里眼顺风耳", "desc_en": "Mysterious alien look", "price": 1200000000, "img": ""},
        {"id": "sx_5", "name_zh": "太阳轮", "name_en": "Sun Wheel", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "形似方向盘", "desc_en": "Solar worship artifact", "price": 600000000, "img": ""},
        {"id": "sx_6", "name_zh": "玉璋", "name_en": "Jade Zhang", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "祭祀山川礼器", "desc_en": "Ritual jade artifact", "price": 300000000, "img": ""},
        {"id": "sx_7", "name_zh": "黄金权杖", "name_en": "Golden Scepter", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "王权的象征", "desc_en": "Symbol of ancient power", "price": 1500000000, "img": ""},
        {"id": "sx_8", "name_zh": "青铜神坛", "name_en": "Bronze Altar", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "复杂祭祀场景", "desc_en": "Complex ritual scene", "price": 900000000, "img": ""},
        {"id": "sx_9", "name_zh": "戴金面罩铜人", "name_en": "Gold-Masked Head", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "金光闪闪祭司", "desc_en": "Shining priest", "price": 500000000, "img": ""},
        {"id": "sx_10", "name_zh": "青铜鸟头", "name_en": "Bronze Bird Head", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "神鸟图腾", "desc_en": "Divine bird totem", "price": 150000000, "img": ""},
        {"id": "sx_11", "name_zh": "陶猪", "name_en": "Pottery Pig", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "愤怒小鸟同款", "desc_en": "Looks like Angry Birds", "price": 50000000, "img": ""},
        {"id": "sx_12", "name_zh": "青铜大鸟", "name_en": "Bronze Big Bird", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "体型巨大神兽", "desc_en": "Giant mythical bird", "price": 400000000, "img": ""},
        {"id": "sx_13", "name_zh": "青铜爬龙柱", "name_en": "Dragon Pillar", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "龙形神柱", "desc_en": "Dragon shaped pillar", "price": 650000000, "img": ""},
        {"id": "sx_14", "name_zh": "人身鸟脚像", "name_en": "Bird-Man Statue", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "半人半鸟", "desc_en": "Half man half bird", "price": 550000000, "img": ""},
        {"id": "sx_15", "name_zh": "顶尊跪坐人像", "name_en": "Kneeling Figure", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "国宝级重器", "desc_en": "National treasure", "price": 1100000000, "img": ""},
        {"id": "sx_16", "name_zh": "青铜蛇", "name_en": "Bronze Snake", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "造型逼真", "desc_en": "Realistic snake", "price": 120000000, "img": ""},
        {"id": "sx_17", "name_zh": "青铜鸡", "name_en": "Bronze Rooster", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "雄鸡一唱", "desc_en": "Crowing rooster", "price": 80000000, "img": ""},
        {"id": "sx_18", "name_zh": "玉琮", "name_en": "Jade Cong", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "良渚文化影响", "desc_en": "Liangzhu influence", "price": 200000000, "img": ""},
    ],
    "beijing": [
        {"id": "bj_1", "name_zh": "清明上河图", "name_en": "Riverside Scene", "period_zh": "北宋", "period_en": "Northern Song", "desc_zh": "中华第一神品", "desc_en": "China's greatest masterpiece", "price": 5000000000, "img": ""},
        {"id": "bj_2", "name_zh": "金瓯永固杯", "name_en": "Gold Cup", "period_zh": "清乾隆", "period_en": "Qianlong Period", "desc_zh": "乾隆御用金杯", "desc_en": "Qianlong's gold cup", "price": 600000000, "img": ""},
        {"id": "bj_3", "name_zh": "后母戊鼎", "name_en": "Houmuwu Ding", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "青铜之王", "desc_en": "King of bronzes", "price": 4000000000, "img": ""},
        {"id": "bj_4", "name_zh": "千里江山图", "name_en": "Landscape Painting", "period_zh": "北宋", "period_en": "Northern Song", "desc_zh": "青绿山水巅峰", "desc_en": "Blue-green landscape peak", "price": 3000000000, "img": ""},
        # 补全 Beijing 数据... (为节省长度，此处用代码逻辑自动生成占位)
    ],
    "shanghai": [
        {"id": "sh_1", "name_zh": "大克鼎", "name_en": "Da Ke Ding", "period_zh": "西周", "period_en": "Western Zhou", "desc_zh": "海内三宝之一", "desc_en": "Top 3 bronze treasures", "price": 1500000000, "img": ""},
        {"id": "sh_2", "name_zh": "晋侯苏钟", "name_en": "Su Bells", "period_zh": "西周", "period_en": "Western Zhou", "desc_zh": "铭文刻在钟表", "desc_en": "Inscribed bells", "price": 800000000, "img": ""},
        # 补全 Shanghai 数据...
    ],
    "xian": [
        {"id": "xa_1", "name_zh": "兽首玛瑙杯", "name_en": "Beast Agate Cup", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "海内孤品", "desc_en": "Unique agate treasure", "price": 2000000000, "img": ""},
        {"id": "xa_2", "name_zh": "舞马衔杯银壶", "name_en": "Silver Flask", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "大唐盛世缩影", "desc_en": "Symbol of Tang Dynasty", "price": 800000000, "img": ""},
        # 补全 Xian 数据...
    ]
}

# 自动填充缺失数据，保证每个馆都有18个格子显示
for k, v in MUSEUM_TREASURES.items():
    if len(v) < 18:
        for i in range(len(v), 18):
            v.append({
                "id": f"{k}_placeholder_{i}", "name_zh": "神秘藏品", "name_en": "Mystery Item",
                "period_zh": "未知", "period_en": "Unknown", "desc_zh": "等待发掘中...", "desc_en": "To be discovered...",
                "price": 100000000, "img": ""
            })

# ==========================================
# 3. 工具函数：图片处理
# ==========================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return None
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except: return None

# 预加载图片逻辑
for museum_key, treasures in MUSEUM_TREASURES.items():
    current_dir = os.path.join(BASE_IMG_ROOT, museum_key)
    for idx, treasure in enumerate(treasures, start=1):
        # 尝试匹配本地文件
        img_names = [f"{idx}.jpeg", f"[] ({idx}).jpeg", f"{idx}.jpg"]
        b64_str = None
        for name in img_names:
            p = os.path.join(current_dir, name)
            b64_str = get_base64_image(p)
            if b64_str: break
        
        # 赋值：本地优先 -> 在线兜底
        treasure["img"] = b64_str if b64_str else f"https://picsum.photos/seed/{treasure['id']}/300/300"

# ==========================================
# 4. 样式 (CSS)
# ==========================================
st.markdown("""
<style>
    /* 基础 */
    #MainMenu {visibility: hidden !important;} footer {visibility: hidden !important;}
    .stApp { background-color: #f5f5f7; color: #1d1d1f; }
    
    /* 顶部按钮 */
    .neal-btn { font-family: 'Inter', sans-serif; background: #fff; border: 1px solid #e5e7eb; color: #111; font-weight: 600; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; text-decoration: none !important; width: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .neal-btn:hover { background: #f9fafb; transform: translateY(-1px); }

    /* 仪表盘 */
    .dashboard { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); padding: 15px 30px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-bottom: 1px solid #e5e5e5; }
    
    /* 豪宅卡片 */
    .mansion-box { background-size: cover; border-radius: 12px; padding: 15px; min-width: 260px; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.8); position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.2); transition: transform 0.3s; }
    .mansion-box:hover { transform: scale(1.02); }
    .mansion-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.6)); z-index: 1; }
    
    /* 文物卡片 */
    .treasure-card { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); transition: all 0.3s; border: 1px solid #e5e5e5; overflow: hidden; height: 100%; display: flex; flex-direction: column; text-align: center; }
    .treasure-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
    
    /* 圆形图片 */
    .t-img-box { height: 160px; width: 100%; display: flex; align-items: center; justify-content: center; background: #f8f9fa; overflow: hidden; }
    .t-img { width: 120px !important; height: 120px !important; border-radius: 50%; object-fit: cover; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: scale(1.1); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .treasure-card:hover .t-img { transform: scale(1.2) rotate(3deg); }
    
    /* 价格与文字 */
    .t-content { padding: 10px; flex-grow: 1; display: flex; flex-direction: column; }
    .t-title { font-size: 0.95rem; font-weight: 800; color: #111; margin-bottom: 4px; }
    .t-period { font-size: 0.7rem; color: #86868b; background: #f1f5f9; padding: 2px 8px; border-radius: 10px; display: inline-block; margin: 0 auto 5px auto; width: fit-content; }
    .t-price { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 700; margin-top: auto; }
    .sold-price { color: #d9534f; }
    .unsold-price { color: #9ca3af; font-style: italic; font-size: 0.9rem; }
    
    /* 资产清单样式 */
    .asset-grid { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0; }
    .asset-tag { background: #fffbeb; color: #b45309; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; border: 1px solid #fcd34d; font-weight: 600; display: flex; align-items: center; gap: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* 动画 */
    @keyframes fadeInPrice { 0% { opacity: 0; transform: scale(0.5); filter: blur(5px); } 100% { opacity: 1; transform: scale(1); filter: blur(0); } }
    .price-reveal { animation: fadeInPrice 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards; display: inline-block; color: #d9534f; font-weight: 800; }
    
    /* 通用组件 */
    .pay-amount-display { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 800; margin: 10px 0; }
    div[data-testid="stButton"] button { width: 100% !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stats-bar { display: flex; justify-content: center; gap: 30px; margin-top: 40px; padding: 15px; background: white; border-radius: 50px; color: #6b7280; font-size: 0.85rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 状态与语言包
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = {} # {id: {"name":..., "price":...}}
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1

lang_texts = {
    'zh': {
        'title': "🏛️ 华夏国宝私有化中心", 'revenue': "累计拍卖总额", 'power': "财富购买力", 'unit_m': "套", 'apps': "✨ 更多应用",
        'sold': "🚫 已私有化", 'auction': "㊙ 立即拍卖", 'reveal': "🕵️ 价值待揭晓", 'my_assets': "🏆 我的私人资产清单",
        'no_assets': "暂无藏品，快去竞拍吧！", 'reset': "🔄 破产/重置", 'coffee': "☕ 请老登喝咖啡", 'toast': "🔨 {name} 成交！",
        'unit': "亿", 'period': "时代", 'share_tip': "📸 截图保存即可分享炫耀！",
        'coffee_title': " ", 'coffee_desc': "如果这个游戏帮到了你，欢迎支持。", 'coffee_amt': "打赏杯数", 'pay_ok': "收到！感谢支持 ❤️",
        'presets': [("☕ 提神", 1), ("🍗 鸡腿", 3), ("🚀 续命", 5)], 'pay_types': ["微信支付", "支付宝", "贝宝"]
    },
    'en': {
        'title': "🏛️ National Treasure Auction", 'revenue': "Total Revenue", 'power': "Buying Power", 'unit_m': "Estates", 'apps': "✨ More Apps",
        'sold': "🚫 Privatized", 'auction': "㊙ Auction", 'reveal': "🕵️ Hidden", 'my_assets': "🏆 My Collection",
        'no_assets': "No assets yet. Bid now!", 'reset': "🔄 Reset", 'coffee': "☕ Buy Coffee", 'toast': "🔨 {name} Sold!",
        'unit': "B", 'period': "Period", 'share_tip': "📸 Screenshot to share your collection!",
        'coffee_title': " ", 'coffee_desc': "Support is appreciated.", 'coffee_amt': "Cups", 'pay_ok': "Thanks! ❤️",
        'presets': [("☕ Coffee", 1), ("🍗 Meal", 3), ("🚀 Rocket", 5)], 'pay_types': ["WeChat", "Alipay", "PayPal"]
    }
}
L = lang_texts[st.session_state.language]

# ==========================================
# 6. 顶部布局
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    btn_l = "English" if st.session_state.language == 'zh' else "中文"
    if st.button(btn_l):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()
with col_more:
    st.markdown(f'<a href="https://laodeng.streamlit.app/" target="_blank" style="text-decoration:none;"><div class="neal-btn">{L["apps"]}</div></a>', unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align:center; margin-top:10px;'>{L['title']}</h2>", unsafe_allow_html=True)

# 博物馆选择 (支持双语显示)
museum_options = list(MANSION_CONFIG.keys())
museum_labels = museum_options if st.session_state.language == 'zh' else [MUSEUM_NAME_MAP[m].capitalize() for m in museum_options]
sel_idx = st.radio("Museum", range(len(museum_options)), format_func=lambda x: museum_labels[x], horizontal=True, label_visibility="collapsed")
selected_museum = museum_options[sel_idx]

if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.rerun()

# ==========================================
# 7. 仪表盘 & 资产清单
# ==========================================
m_cfg = MANSION_CONFIG[selected_museum]
db_holder = st.empty()

def render_dashboard(val):
    v_count = val / m_cfg["price"]
    m_name = m_cfg["mansion_name_zh"] if st.session_state.language == 'zh' else m_cfg["mansion_name_en"]
    m_display_name = selected_museum if st.session_state.language == 'zh' else MUSEUM_NAME_MAP[selected_museum].capitalize()
    
    db_holder.markdown(f"""
    <div class="dashboard">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:1.3rem; font-weight:800;">{m_display_name}</div>
                <div style="font-size:2rem; font-weight:900; color:#d9534f; font-family:'JetBrains Mono';">
                    ¥{val/100000000:.2f}{L['unit']}
                </div>
                <div style="font-size:0.8rem; color:#86868b; letter-spacing:1px; text-transform:uppercase;">{L['revenue']}</div>
            </div>
            <div class="mansion-box" style="background-image: url('{m_cfg['mansion_img']}');">
                <div class="mansion-overlay"></div>
                <div style="position:relative; z-index:2;">
                    <div style="font-size:0.75rem; opacity:0.9;">{L['power']}</div>
                    <div style="font-size:1.6rem; font-weight:900;">× {v_count:.2f} {L['unit_m']}</div>
                    <div style="font-size:0.85rem; font-weight:600;">{m_name}</div>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

render_dashboard(st.session_state.total_revenue)

# 资产清单 (Asset List)
with st.expander(f"{L['my_assets']} ({len(st.session_state.sold_items)})", expanded=len(st.session_state.sold_items) > 0):
    if st.session_state.sold_items:
        # 生成金色标签 HTML
        sorted_assets = sorted(st.session_state.sold_items.values(), key=lambda x: x['price'], reverse=True)
        tags_html = "".join([f'<span class="asset-tag">💎 {item["name"]} <small style="opacity:0.6; margin-left:3px;">¥{item["price"]/100000000:.1f}亿</small></span>' for item in sorted_assets])
        st.markdown(f'<div class="asset-grid">{tags_html}</div>', unsafe_allow_html=True)
        st.caption(L['share_tip'])
    else:
        st.info(L['no_assets'])

# ==========================================
# 8. 拍卖与展示逻辑
# ==========================================
def auction_action(item, name_final):
    # 动画效果
    start = st.session_state.total_revenue
    price = item['price']
    for i in range(15):
        render_dashboard(start + (price/15)*(i+1))
        time.sleep(0.015)
    
    st.session_state.total_revenue += price
    # 记录资产明细
    st.session_state.sold_items[item['id']] = {"name": name_final, "price": price}
    st.session_state.last_sold_id = item['id']
    st.toast(L['toast'].format(name=name_final), icon="🔨")
    time.sleep(0.3)
    st.rerun()

m_key = MUSEUM_NAME_MAP[selected_museum]
items = MUSEUM_TREASURES.get(m_key, [])
cols = st.columns(4)

for idx, item in enumerate(items):
    with cols[idx % 4]:
        # 数据准备
        is_sold = item['id'] in st.session_state.sold_items
        lang = st.session_state.language
        name = item.get(f'name_{lang}', 'Unknown')
        period = item.get(f'period_{lang}', '')
        desc = item.get(f'desc_{lang}', '')
        
        # 价格显示逻辑
        if is_sold:
            p_display = f"¥{item['price']/100000000:.1f}{L['unit']}"
            p_class = "price-reveal" if item['id'] == st.session_state.last_sold_id else "sold-price"
        else:
            p_display = L['reveal']
            p_class = "unsold-price"
            
        st.markdown(f"""
        <div class="treasure-card">
            <div class="t-img-box">
                <img src="{item['img']}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
            </div>
            <div class="t-content">
                <div class="t-title">{name}</div>
                <div class="t-period">{period}</div>
                <div class="t-desc" title="{desc}">{desc}</div>
                <div class="t-price {p_class}">{p_display}</div>
            </div>
        </div>""", unsafe_allow_html=True)
        
        if is_sold:
            st.button(L['sold'], key=item['id'], disabled=True)
        else:
            if st.button(L['auction'], key=item['id'], type="primary"):
                auction_action(item, name)

# ==========================================
# 9. 底部功能区
# ==========================================
st.write("<br><hr>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    if st.button(L['reset'], type="secondary"):
        st.session_state.sold_items = {}
        st.session_state.total_revenue = 0
        st.session_state.last_sold_id = None
        st.rerun()

with c2:
    @st.dialog(L['coffee_title'])
    def coffee_dialog():
        st.markdown(f"<div style='text-align:center; color:#666;'>{L['coffee_desc']}</div>", unsafe_allow_html=True)
        # 快捷按钮
        p_cols = st.columns(3)
        for i, (txt, val) in enumerate(L['presets']):
            with p_cols[i]:
                if st.button(txt, use_container_width=True): st.session_state.coffee_num = val
        
        st.write("")
        cnt = st.number_input(L['coffee_amt'], 1, 100, step=1, key='coffee_num')
        
        # 支付 Tab
        tabs = st.tabs(L['pay_types'])
        cny = cnt * 10
        usd = cnt * 2
        
        def show_pay(currency, code):
            st.markdown(f"<h2 style='text-align:center; color:#d9534f; margin:10px 0;'>{currency}</h2>", unsafe_allow_html=True)
            qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Pay_{code}_{currency}"
            c1, c2, c3 = st.columns([1,2,1])
            with c2: st.image(qr, use_container_width=True)
            
        with tabs[0]: show_pay(f"¥{cny}", "WX")
        with tabs[1]: show_pay(f"¥{cny}", "ALI")
        with tabs[2]: show_pay(f"${usd}", "PAYPAL")
        
        if st.button("🎉 " + L['pay_ok'].split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            time.sleep(1)
            st.rerun()

    if st.button(L['coffee'], use_container_width=True):
        coffee_dialog()

# 统计
def track_stats():
    DB_FILE = os.path.join(os.path.expanduser("~/"), "visit_stats.db")
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS visitors (id TEXT PRIMARY KEY, date TEXT)')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if "counted" not in st.session_state:
            c.execute("INSERT OR REPLACE INTO visitors VALUES (?, ?)", (st.session_state.visitor_id, today))
            conn.commit()
            st.session_state.counted = True
        total = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        conn.close()
        return total
    except: return 1

st.markdown(f'<div class="stats-bar">Visitor Count: <b>{track_stats()}</b></div>', unsafe_allow_html=True)

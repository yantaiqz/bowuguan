import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import base64

# ==========================================
# 1. 全局配置 & 路径修复
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded" # 默认展开侧边栏
)

# ------------- 路径兼容 & 动态创建目录 -------------
try:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except:
    PROJECT_ROOT = os.getcwd()
BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
os.makedirs(BASE_IMG_ROOT, exist_ok=True)

# 博物馆名称映射
MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}

# 动态创建目录
for museum_pinyin in MUSEUM_NAME_MAP.values():
    os.makedirs(os.path.join(BASE_IMG_ROOT, museum_pinyin), exist_ok=True)

# ==========================================
# 2. 核心数据
# ==========================================
MANSION_CONFIG = {
    "南京博物院": {"mansion_name": "颐和路民国别墅", "price": 100000000, "mansion_img": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=400&q=80"},
    "三星堆博物馆": {"mansion_name": "成都麓山国际豪宅", "price": 50000000, "mansion_img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=400&q=80"},
    "中国国家博物馆": {"mansion_name": "什刹海四合院", "price": 150000000, "mansion_img": "https://images.unsplash.com/photo-1595130838493-2199b4226d9e?auto=format&fit=crop&w=400&q=80"},
    "上海博物馆": {"mansion_name": "愚园路老洋房", "price": 200000000, "mansion_img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=400&q=80"},
    "陕西历史博物馆": {"mansion_name": "曲江池畔大平层", "price": 30000000, "mansion_img": "https://images.unsplash.com/photo-1600607687940-472002695533?auto=format&fit=crop&w=400&q=80"}
}

MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name": "金兽", "period": "西汉", "desc": "含金量99%，最重金器", "price": 500000000, "img": ""},
        {"id": "nj_2", "name": "釉里红梅瓶", "period": "明洪武", "desc": "现存唯一带盖梅瓶", "price": 800000000, "img": ""},
        {"id": "nj_3", "name": "金蝉玉叶", "period": "明代", "desc": "金枝玉叶，工艺精湛", "price": 90000000, "img": ""},
        {"id": "nj_4", "name": "银缕玉衣", "period": "东汉", "desc": "银丝编缀，极其罕见", "price": 300000000, "img": ""},
        {"id": "nj_5", "name": "竹林七贤砖画", "period": "南朝", "desc": "魏晋风度最佳见证", "price": 1000000000, "img": ""},
        {"id": "nj_6", "name": "大报恩寺拱门", "period": "明代", "desc": "世界奇迹残留组件", "price": 200000000, "img": ""},
        {"id": "nj_7", "name": "坤舆万国全图", "period": "明万历", "desc": "最早彩绘世界地图", "price": 600000000, "img": ""},
        {"id": "nj_8", "name": "广陵王玺", "period": "东汉", "desc": "汉代封王金印精品", "price": 200000000, "img": ""},
        {"id": "nj_9", "name": "错银铜牛灯", "period": "东汉", "desc": "汉代环保黑科技", "price": 180000000, "img": ""},
        {"id": "nj_10", "name": "青瓷神兽尊", "period": "西晋", "desc": "造型奇特的早期青瓷", "price": 120000000, "img": ""},
        {"id": "nj_11", "name": "透雕人鸟兽玉饰", "period": "良渚", "desc": "史前玉器巅峰", "price": 60000000, "img": ""},
        {"id": "nj_12", "name": "鎏金喇嘛塔", "period": "明代", "desc": "通体鎏金镶宝石", "price": 80000000, "img": ""},
        {"id": "nj_13", "name": "青花寿山福海炉", "period": "明宣德", "desc": "宣德官窑完整大器", "price": 450000000, "img": ""},
        {"id": "nj_14", "name": "徐渭《杂花图》", "period": "明代", "desc": "大写意水墨巅峰", "price": 350000000, "img": ""},
        {"id": "nj_15", "name": "沈寿《耶稣像》", "period": "近代", "desc": "万国博览会金奖", "price": 50000000, "img": ""},
        {"id": "nj_16", "name": "芙蓉石蟠螭炉", "period": "清乾隆", "desc": "乾隆御用粉嫩玉石", "price": 130000000, "img": ""},
        {"id": "nj_17", "name": "人面兽面玉琮", "period": "良渚", "desc": "微雕工艺神作", "price": 150000000, "img": ""},
        {"id": "nj_18", "name": "青瓷釉下彩壶", "period": "唐代", "desc": "改写陶瓷史的孤品", "price": 110000000, "img": ""},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": ""},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 2500000000, "img": ""},
        {"id": "sx_3", "name": "金面具", "period": "商代", "desc": "半张黄金脸", "price": 800000000, "img": ""},
        {"id": "sx_4", "name": "青铜纵目面具", "period": "商代", "desc": "千里眼顺风耳", "price": 1200000000, "img": ""},
        {"id": "sx_5", "name": "太阳轮", "period": "商代", "desc": "形似方向盘", "price": 600000000, "img": ""},
        {"id": "sx_6", "name": "玉璋", "period": "商代", "desc": "祭祀山川礼器", "price": 300000000, "img": ""},
        {"id": "sx_7", "name": "黄金权杖", "period": "商代", "desc": "王权的象征", "price": 1500000000, "img": ""},
        {"id": "sx_8", "name": "青铜神坛", "period": "商代", "desc": "复杂祭祀场景", "price": 900000000, "img": ""},
        {"id": "sx_9", "name": "戴金面罩铜人", "period": "商代", "desc": "金光闪闪祭司", "price": 500000000, "img": ""},
        {"id": "sx_10", "name": "青铜鸟头", "period": "商代", "desc": "神鸟图腾", "price": 150000000, "img": ""},
        {"id": "sx_11", "name": "陶猪", "period": "商代", "desc": "愤怒小鸟同款", "price": 50000000, "img": ""},
        {"id": "sx_12", "name": "青铜大鸟", "period": "商代", "desc": "体型巨大神兽", "price": 400000000, "img": ""},
        {"id": "sx_13", "name": "青铜爬龙柱", "period": "商代", "desc": "龙形神柱", "price": 650000000, "img": ""},
        {"id": "sx_14", "name": "人身鸟脚像", "period": "商代", "desc": "半人半鸟", "price": 550000000, "img": ""},
        {"id": "sx_15", "name": "顶尊跪坐人像", "period": "商代", "desc": "国宝级重器", "price": 1100000000, "img": ""},
        {"id": "sx_16", "name": "青铜蛇", "period": "商代", "desc": "造型逼真", "price": 120000000, "img": ""},
        {"id": "sx_17", "name": "青铜鸡", "period": "商代", "desc": "雄鸡一唱", "price": 80000000, "img": ""},
        {"id": "sx_18", "name": "玉琮", "period": "商代", "desc": "良渚文化影响", "price": 200000000, "img": ""},
    ],
    "beijing": [
        {"id": "bj_1", "name": "清明上河图", "period": "北宋", "desc": "中华第一神品", "price": 5000000000, "img": ""},
        {"id": "bj_2", "name": "金瓯永固杯", "period": "清乾隆", "desc": "乾隆御用金杯", "price": 600000000, "img": ""},
        {"id": "bj_3", "name": "后母戊鼎", "period": "商代", "desc": "青铜之王", "price": 4000000000, "img": ""},
        {"id": "bj_4", "name": "千里江山图", "period": "北宋", "desc": "青绿山水巅峰", "price": 3000000000, "img": ""},
        {"id": "bj_5", "name": "四羊方尊", "period": "商代", "desc": "青铜铸造奇迹", "price": 2000000000, "img": ""},
        {"id": "bj_6", "name": "孝端皇后凤冠", "period": "明代", "desc": "点翠工艺巅峰", "price": 500000000, "img": ""},
        {"id": "bj_7", "name": "金缕玉衣", "period": "西汉", "desc": "中山靖王同款", "price": 1000000000, "img": ""},
        {"id": "bj_8", "name": "红山玉龙", "period": "新石器", "desc": "中华第一龙", "price": 1200000000, "img": ""},
        {"id": "bj_9", "name": "击鼓说唱俑", "period": "东汉", "desc": "汉代幽默感", "price": 300000000, "img": ""},
        {"id": "bj_10", "name": "人面鱼纹盆", "period": "仰韶", "desc": "史前文明微笑", "price": 250000000, "img": ""},
        {"id": "bj_11", "name": "大盂鼎", "period": "西周", "desc": "铭文极其珍贵", "price": 1800000000, "img": ""},
        {"id": "bj_12", "name": "虢季子白盘", "period": "西周", "desc": "晚清出土重器", "price": 1600000000, "img": ""},
        {"id": "bj_13", "name": "霁蓝白龙梅瓶", "period": "元代", "desc": "元代顶级瓷器", "price": 800000000, "img": ""},
        {"id": "bj_14", "name": "郎世宁百骏图", "period": "清代", "desc": "中西合璧", "price": 600000000, "img": ""},
        {"id": "bj_15", "name": "五牛图", "period": "唐代", "desc": "韩滉传世孤本", "price": 900000000, "img": ""},
        {"id": "bj_16", "name": "步辇图", "period": "唐代", "desc": "阎立本绘", "price": 1100000000, "img": ""},
        {"id": "bj_17", "name": "利簋", "period": "西周", "desc": "记录武王伐纣", "price": 700000000, "img": ""},
        {"id": "bj_18", "name": "鹳鱼石斧陶缸", "period": "仰韶", "desc": "绘画史第一页", "price": 400000000, "img": ""},
    ],
    "shanghai": [
        {"id": "sh_1", "name": "大克鼎", "period": "西周", "desc": "海内三宝之一", "price": 1500000000, "img": ""},
        {"id": "sh_2", "name": "晋侯苏钟", "period": "西周", "desc": "铭文刻在钟表", "price": 800000000, "img": ""},
        {"id": "sh_3", "name": "孙位高逸图", "period": "唐代", "desc": "唐代人物画孤本", "price": 1200000000, "img": ""},
        {"id": "sh_4", "name": "越王剑", "period": "春秋", "desc": "虽不如勾践剑", "price": 300000000, "img": ""},
        {"id": "sh_5", "name": "粉彩蝠桃纹瓶", "period": "清雍正", "desc": "雍正官窑极品", "price": 400000000, "img": ""},
        {"id": "sh_6", "name": "王羲之上虞帖", "period": "唐摹本", "desc": "书圣墨宝", "price": 2000000000, "img": ""},
        {"id": "sh_7", "name": "苦笋帖", "period": "唐怀素", "desc": "草书狂僧真迹", "price": 1000000000, "img": ""},
        {"id": "sh_8", "name": "青花瓶", "period": "元代", "desc": "元青花存世稀少", "price": 600000000, "img": ""},
        {"id": "sh_9", "name": "子仲姜盘", "period": "春秋", "desc": "盘内动物可旋转", "price": 500000000, "img": ""},
        {"id": "sh_10", "name": "牺尊", "period": "春秋", "desc": "极具神韵的牛形", "price": 350000000, "img": ""},
        {"id": "sh_11", "name": "商鞅方升", "period": "战国", "desc": "统一度量衡", "price": 1500000000, "img": ""},
        {"id": "sh_12", "name": "曹全碑", "period": "东汉", "desc": "汉隶书法典范", "price": 450000000, "img": ""},
        {"id": "sh_13", "name": "哥窑五足洗", "period": "南宋", "desc": "金丝铁线", "price": 300000000, "img": ""},
        {"id": "sh_14", "name": "透雕神兽玉璧", "period": "西汉", "desc": "汉代玉器巅峰", "price": 200000000, "img": ""},
        {"id": "sh_15", "name": "剔红花卉纹盘", "period": "元代", "desc": "张成造，漆器孤品", "price": 120000000, "img": ""},
        {"id": "sh_16", "name": "苏轼舣舟亭图", "period": "清代", "desc": "乾隆御览之宝", "price": 250000000, "img": ""},
        {"id": "sh_17", "name": "青花牡丹纹罐", "period": "元代", "desc": "元青花大器", "price": 550000000, "img": ""},
        {"id": "sh_18", "name": "缂丝莲塘乳鸭", "period": "南宋", "desc": "朱克柔真迹", "price": 800000000, "img": ""},
    ],
    "xian": [
        {"id": "xa_1", "name": "兽首玛瑙杯", "period": "唐代", "desc": "海内孤品", "price": 2000000000, "img": ""},
        {"id": "xa_2", "name": "舞马衔杯银壶", "period": "唐代", "desc": "大唐盛世缩影", "price": 800000000, "img": ""},
        {"id": "xa_3", "name": "皇后之玺", "period": "西汉", "desc": "吕后之印", "price": 1000000000, "img": ""},
        {"id": "xa_4", "name": "兵马俑(跪射)", "period": "秦代", "desc": "保存最完整", "price": 3000000000, "img": ""},
        {"id": "xa_5", "name": "葡萄花鸟香囊", "period": "唐代", "desc": "杨贵妃同款", "price": 500000000, "img": ""},
        {"id": "xa_6", "name": "鎏金铜蚕", "period": "西汉", "desc": "丝绸之路见证", "price": 300000000, "img": ""},
        {"id": "xa_7", "name": "独孤信印", "period": "西魏", "desc": "多面体印章", "price": 400000000, "img": ""},
        {"id": "xa_8", "name": "提梁倒注壶", "period": "五代", "desc": "神奇倒注构造", "price": 200000000, "img": ""},
        {"id": "xa_9", "name": "鸳鸯纹金碗", "period": "唐代", "desc": "金银器巅峰", "price": 600000000, "img": ""},
        {"id": "xa_10", "name": "三彩骆驼俑", "period": "唐代", "desc": "丝路乐队", "price": 450000000, "img": ""},
        {"id": "xa_11", "name": "阙楼仪仗图", "period": "唐代", "desc": "懿德太子墓", "price": 1500000000, "img": ""},
        {"id": "xa_12", "name": "鎏金铜龙", "period": "唐代", "desc": "气势磅礴", "price": 350000000, "img": ""},
        {"id": "xa_13", "name": "杜虎符", "period": "战国", "desc": "调兵遣将信物", "price": 500000000, "img": ""},
        {"id": "xa_14", "name": "何尊", "period": "西周", "desc": "最早出现'中国'", "price": 2500000000, "img": ""},
        {"id": "xa_15", "name": "多友鼎", "period": "西周", "desc": "铭文记录战争", "price": 800000000, "img": ""},
        {"id": "xa_16", "name": "日己觥", "period": "西周", "desc": "造型奇特酒器", "price": 400000000, "img": ""},
        {"id": "xa_17", "name": "雁鱼铜灯", "period": "西汉", "desc": "环保美学结合", "price": 550000000, "img": ""},
        {"id": "xa_18", "name": "金怪兽", "period": "战国", "desc": "匈奴文化代表", "price": 200000000, "img": ""},
    ]
}

# ==========================================
# 3. 工具函数 (Base64)
# ==========================================
def get_base64_image(image_path):
    try:
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            return None
        with open(image_path, "rb") as img_file:
            b64_data = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{b64_data}"
    except Exception as e:
        return None

# ==========================================
# 4. 图片加载逻辑
# ==========================================
for museum_cn, museum_pinyin in MUSEUM_NAME_MAP.items():
    treasures = MUSEUM_TREASURES.get(museum_pinyin, [])
    if not treasures: continue
    current_museum_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    
    for idx, treasure in enumerate(treasures, start=1):
        img_names = [f"{idx}.jpeg", f"[] ({idx}).jpeg", f"{idx}.jpg", f"[] ({idx}).jpg"]
        b64_str = None
        for img_name in img_names:
            b64_str = get_base64_image(os.path.join(current_museum_dir, img_name))
            if b64_str: break
        
        if b64_str:
            treasure["img"] = b64_str
        else:
            prefix = treasure['id'][:2]
            treasure["img"] = f"https://picsum.photos/seed/{prefix}{idx}/300/300"

# ==========================================
# 5. 样式
# ==========================================
st.markdown("""
<style>
    /* --- 基础 --- */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #f5f5f7 !important; color: #1d1d1f; }
    
    /* 侧边栏样式优化 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e5e5;
    }
    
    /* 侧边栏卡片 */
    .sidebar-card {
        background: #fbfbfd;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #eaeaea;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* --- 文物卡片 --- */
    .treasure-card {
        background: white; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); 
        transition: all 0.3s;
        border: 1px solid #f0f0f0; 
        overflow: hidden; height: 100%;
        display: flex; flex-direction: column;
    }
    .treasure-card:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.08); }
    
    .t-img-box { 
        height: 150px; width: 100%; 
        background: #f9f9f9;
        display: flex; align-items: center; justify-content: center; 
    }
    .t-img { 
        width: 100px !important; height: 100px !important;      
        border-radius: 50%; object-fit: cover;
        border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    }
    .t-content { padding: 10px !important; flex-grow: 1; display: flex; flex-direction: column; text-align: center; }
    .t-title { font-size: 0.95rem; font-weight: 700; color: #333; margin-bottom: 4px !important; }
    .t-desc { font-size: 0.75rem; color: #666; margin-bottom: 5px !important; flex-grow: 1; line-height: 1.3;}
    
    /* 价格与动画 */
    .sold-price { color: #d9534f; font-weight: 700; font-family: monospace; }
    .unsold-price { color: #ccc; font-style: italic; font-size: 0.8rem; }
    
    @keyframes fadeInPrice {
        0% { opacity: 0; transform: scale(0.5); color: green; }
        100% { opacity: 1; transform: scale(1); color: #d9534f; }
    }
    .price-reveal { animation: fadeInPrice 1s ease-out forwards; }
    
    /* 按钮微调 */
    div[data-testid="stButton"] button { border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 状态 & 逻辑
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())

# 语言文本
lang_texts = {
    'zh': {'coffee_btn': "☕ 请开发者喝咖啡", 'pay_title': "打赏", 'coffee_desc': "支持开发", 'presets': [("☕", 1), ("🍗", 3), ("🚀", 5)]},
    'en': {'coffee_btn': "☕ Buy me a coffee", 'pay_title': "Donate", 'coffee_desc': "Support", 'presets': [("☕", 1), ("🍗", 3), ("🚀", 5)]}
}
current_text = lang_texts[st.session_state.language]

def format_price(price):
    if price >= 100000000: return f"{price/100000000:.1f}亿"
    elif price >= 10000: return f"{price/10000:.0f}万"
    return str(price)

def track_stats():
    DB_FILE = os.path.join(os.path.expanduser("~/"), "visit_stats.db")
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        today = datetime.datetime.utcnow().date().isoformat()
        if "has_counted" not in st.session_state:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (st.session_state["visitor_id"], today))
            conn.commit()
            st.session_state["has_counted"] = True
        today_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        total_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        conn.close()
        return today_uv, total_uv
    except: return 1, 1

today_uv, total_uv = track_stats()

# ==========================================
# 7. 布局构建：侧边栏 (Dashboard)
# ==========================================
with st.sidebar:
    st.markdown("### 🏛️ 华夏国宝私有化")
    
    # 语言切换 & 更多
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("中/En", key="lang_switch", use_container_width=True):
            st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
            st.rerun()
    with c2:
        st.link_button("✨ 更多应用", "https://laodeng.streamlit.app/", use_container_width=True)

    st.divider()

    # 博物馆选择
    selected_museum = st.selectbox(
        "选择博物馆",
        list(MANSION_CONFIG.keys()),
        index=list(MANSION_CONFIG.keys()).index(st.session_state.current_museum)
    )
    if selected_museum != st.session_state.current_museum:
        st.session_state.current_museum = selected_museum
        st.rerun()

    st.divider()

    # 核心数据展示 (Dashboard)
    m_info = MANSION_CONFIG[st.session_state.current_museum]
    villa_count = st.session_state.total_revenue / m_info["price"] if m_info["price"] else 0
    
    st.markdown(f"""
    <div class="sidebar-card">
        <div style="font-size: 0.8rem; color: #888; margin-bottom:5px;">累计拍卖总额</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #d9534f; line-height: 1.2;">
            ¥{st.session_state.total_revenue / 100000000:.4f}亿
        </div>
    </div>
    <div class="sidebar-card" style="padding:0; overflow:hidden;">
        <img src="{m_info['mansion_img']}" style="width:100%; height:120px; object-fit:cover;">
        <div style="padding:10px;">
            <div style="font-size: 0.8rem; color:#666;">{m_info['mansion_name']}</div>
            <div style="font-size: 1.2rem; font-weight: 700;">× {villa_count:.2f} 套</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 底部操作
    st.divider()
    if st.button("🔄 破产重置", type="secondary", use_container_width=True):
        st.session_state.sold_items = set()
        st.session_state.total_revenue = 0
        st.rerun()

    if st.button(current_text['coffee_btn'], use_container_width=True, type="primary"):
        # 简化版打赏弹窗
        @st.dialog(current_text['pay_title'])
        def donate():
            st.image(os.path.join(PROJECT_ROOT, "wechat_pay.jpg") if os.path.exists(os.path.join(PROJECT_ROOT, "wechat_pay.jpg")) else "https://picsum.photos/200", caption="微信支付")
        donate()

    st.caption(f"今日访客: {today_uv} | 总访客: {total_uv}")

# ==========================================
# 8. 主区域：藏品明细 (Items)
# ==========================================
# 逻辑：侧边栏承载了Dashboard，主区域直接展示藏品列表，实现"明细在页面上部"
current_museum_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
items = MUSEUM_TREASURES.get(current_museum_pinyin, [])

# 标题
st.markdown(f"#### {st.session_state.current_museum} · 藏品列表")

# 拍卖动画函数
def auction_act(item):
    msg = st.toast(f"🔨 正在拍卖 {item['name']}...", icon="⏳")
    time.sleep(0.5)
    st.session_state.total_revenue += item['price']
    st.session_state.sold_items.add(item['id'])
    st.session_state.last_sold_id = item['id']
    msg.toast(f"✅ 成交！入账 ¥{format_price(item['price'])}", icon="💰")
    time.sleep(0.3)
    st.rerun()

# 渲染网格
cols_count = 4
rows = [items[i:i + cols_count] for i in range(0, len(items), cols_count)]

for row_items in rows:
    cols = st.columns(cols_count)
    for idx, item in enumerate(row_items):
        item_id = item['id']
        with cols[idx]:
            is_sold = item_id in st.session_state.sold_items
            
            # 价格显示逻辑
            price_html = ""
            if is_sold:
                anim_class = "price-reveal" if item_id == st.session_state.last_sold_id else ""
                price_html = f'<div class="sold-price {anim_class}">¥{format_price(item["price"])}</div>'
            else:
                price_html = '<div class="unsold-price">待价而沽</div>'
            
            # 卡片 HTML
            st.markdown(f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item['img']}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
                </div>
                <div class="t-content">
                    <div class="t-title">{item['name']}</div>
                    <div class="t-desc">{item['desc']}</div>
                    {price_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 按钮
            if is_sold:
                st.button("🚫 已私有化", key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                if st.button("㊙ 立即拍卖", key=f"btn_{item_id}", type="primary", use_container_width=True):
                    auction_act(item)

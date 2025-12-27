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

# 补充豪宅图片与翻译
MANSION_CONFIG = {
    "南京博物院": {
        "zh": "颐和路民国别墅", "en": "Republic Era Villa", 
        "price": 100000000, 
        "img": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?q=80&w=600"
    },
    "三星堆博物馆": {
        "zh": "成都麓山国际豪宅", "en": "Lushan International Estate", 
        "price": 50000000, 
        "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=600"
    },
    "中国国家博物馆": {
        "zh": "什刹海四合院", "en": "Shichahai Courtyard", 
        "price": 150000000, 
        "img": "https://images.unsplash.com/photo-1595130838493-2199b4226d9e?q=80&w=600"
    },
    "上海博物馆": {
        "zh": "愚园路老洋房", "en": "Yuyuan Road Mansion", 
        "price": 200000000, 
        "img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=600"
    },
    "陕西历史博物馆": {
        "zh": "曲江池畔大平层", "en": "Qujiang Lakeside Penthouse", 
        "price": 30000000, 
        "img": "https://images.unsplash.com/photo-1600607687940-472002695533?q=80&w=600"
    }
}

# 文物数据 (示例保留南京，其余馆通过代码生成占位)
MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name_zh": "金兽", "name_en": "Golden Beast", "price": 500000000, "desc_zh": "含金量99%，最重金器", "desc_en": "99% pure gold, heaviest gold relic"},
        {"id": "nj_2", "name_zh": "釉里红梅瓶", "name_en": "Underglaze Red Vase", "price": 800000000, "desc_zh": "现存唯一带盖梅瓶", "desc_en": "The only surviving vase with cover"},
        {"id": "nj_3", "name_zh": "金蝉玉叶", "name_en": "Golden Cicada on Jade Leaf", "price": 90000000, "desc_zh": "金枝玉叶，工艺精湛", "desc_en": "Exquisite craftsmanship"},
        {"id": "nj_4", "name_zh": "银缕玉衣", "name_en": "Silver-threaded Jade Suit", "price": 300000000, "desc_zh": "银丝编缀，极其罕见", "desc_en": "Rare silver-threaded burial suit"},
        {"id": "nj_5", "name_zh": "竹林七贤砖画", "name_en": "Seven Sages Brick Relief", "price": 1000000000, "desc_zh": "魏晋风度最佳见证", "desc_en": "Masterpiece of Wei-Jin art"},
        {"id": "nj_6", "name_zh": "大报恩寺拱门", "name_en": "Porcelain Tower Arch", "price": 200000000, "desc_zh": "世界奇迹残留组件", "desc_en": "Component of the Porcelain Tower"},
        {"id": "nj_7", "name_zh": "坤舆万国全图", "name_en": "Kunyu Wanguo Quantu", "price": 600000000, "desc_zh": "最早彩绘世界地图", "desc_en": "Earliest world map in color"},
        {"id": "nj_8", "name_zh": "广陵王玺", "name_en": "Seal of Prince Guangling", "price": 200000000, "desc_zh": "汉代封王金印精品", "desc_en": "Pure gold seal of Han dynasty"},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name_zh": "青铜大立人", "name_en": "Bronze Standing Figure", "price": 2000000000, "desc_zh": "世界铜像之王", "desc_en": "King of bronze statues"},
        {"id": "sx_2", "name_zh": "青铜神树", "name_en": "Bronze Sacred Tree", "price": 2500000000, "desc_zh": "通天神树", "desc_en": "Divine tree to the heavens"},
    ],
    "beijing": [
        {"id": "bj_1", "name_zh": "清明上河图", "name_en": "Along the River During the Qingming Festival", "price": 5000000000, "desc_zh": "中华第一神品", "desc_en": "China's greatest masterpiece"},
    ],
    "shanghai": [
        {"id": "sh_1", "name_zh": "大克鼎", "name_en": "Da Ke Ding", "price": 1500000000, "desc_zh": "海内三宝之一", "desc_en": "One of the three national treasures"},
    ],
    "xian": [
        {"id": "xa_1", "name_zh": "兽首玛瑙杯", "name_en": "Beast-head Agate Cup", "price": 2000000000, "desc_zh": "海内孤品", "desc_en": "Unique agate treasure"},
    ]
}

# ==========================================
# 3. 样式 & 翻译字典
# ==========================================
lang_dict = {
    'zh': {
        'title': "🏛️ 华夏国宝私有化中心", 'revenue': "累计拍卖总额", 'power': "财富购买力", 'unit_m': "套", 'apps': "✨ 更多应用",
        'status_sold': "🚫 已私有化", 'btn_auction': "㊙ 立即拍卖", 'reveal': "🕵️ 价值待揭晓", 'my_assets': "📜 我的私人资产清单",
        'no_assets': "暂无藏品，快去竞拍吧！", 'reset': "🔄 破产/重置", 'coffee': "☕ 请老登喝咖啡", 'toast_buy': "🔨 {name} 成交！",
        'unit_price': "亿", 'period': "时代"
    },
    'en': {
        'title': "🏛️ National Treasure Privatization", 'revenue': "Total Revenue", 'power': "Buying Power", 'unit_m': "Estates", 'apps': "✨ More Apps",
        'status_sold': "🚫 Privatized", 'btn_auction': "㊙ Auction", 'reveal': "🕵️ Hidden Value", 'my_assets': "📜 My Private Collection",
        'no_assets': "No collection yet. Start bidding!", 'reset': "🔄 Reset Game", 'coffee': "☕ Buy Coffee", 'toast_buy': "🔨 {name} Sold!",
        'unit_price': "B", 'period': "Period"
    }
}

st.markdown("""
<style>
    .stApp { background-color: #f5f5f7; color: #1d1d1f; }
    .dashboard { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); padding: 15px 30px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .mansion-box { background-size: cover; border-radius: 12px; padding: 15px; min-width: 250px; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.8); position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.2); }
    .mansion-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.3); z-index: 1; }
    .treasure-card { background: white; border-radius: 12px; transition: all 0.3s; border: 1px solid #e5e5e5; overflow: hidden; height: 100%; display: flex; flex-direction: column; text-align: center; }
    .treasure-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
    .t-img { width: 120px !important; height: 120px !important; border-radius: 50%; object-fit: cover; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 15px auto; }
    .asset-tag { display: inline-block; background: #eef2ff; color: #4338ca; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 4px; border: 1px solid #c7d2fe; }
    .stats-bar { display: flex; justify-content: center; gap: 25px; margin-top: 40px; padding: 15px; background-color: white; border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 状态初始化
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = {} # 使用字典存储 {id: name}
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())

L = lang_dict[st.session_state.language]

# ==========================================
# 5. UI 顶部
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    btn_l = "English" if st.session_state.language == 'zh' else "中文"
    if st.button(btn_l):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()
with col_more:
    st.markdown(f'<a href="https://laodeng.streamlit.app/" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:8px; border:1px solid #ddd; background:white; padding:5px; cursor:pointer;">{L["apps"]}</button></a>', unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align:center;'>{L['title']}</h2>", unsafe_allow_html=True)

# ==========================================
# 6. 仪表盘 & 私人清单
# ==========================================
museum_sel = st.radio("Museum", list(MANSION_CONFIG.keys()), horizontal=True, label_visibility="collapsed")
m_cfg = MANSION_CONFIG[museum_sel]
power_val = st.session_state.total_revenue / m_cfg['price']

st.markdown(f"""
<div class="dashboard">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:1.2rem; font-weight:800;">{museum_sel if st.session_state.language=='zh' else MUSEUM_NAME_MAP[museum_sel]}</div>
            <div style="font-size:2rem; font-weight:900; color:#d9534f;">¥{st.session_state.total_revenue/100000000:.2f}{L['unit_price']}</div>
            <div style="font-size:0.8rem; color:#86868b;">{L['revenue']}</div>
        </div>
        <div class="mansion-box" style="background-image: url('{m_cfg['img']}');">
            <div class="mansion-overlay"></div>
            <div style="position:relative; z-index:2;">
                <div style="font-size:0.8rem;">{L['power']}</div>
                <div style="font-size:1.6rem; font-weight:900;">× {power_val:.2f} {L['unit_m']}</div>
                <div style="font-size:0.9rem;">{m_cfg[st.session_state.language]}</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 私人清单展示
with st.expander(L['my_assets'], expanded=len(st.session_state.sold_items) > 0):
    if st.session_state.sold_items:
        tags_html = "".join([f'<span class="asset-tag">💎 {name}</span>' for name in st.session_state.sold_items.values()])
        st.markdown(f'<div>{tags_html}</div>', unsafe_allow_html=True)
    else:
        st.info(L['no_assets'])

# ==========================================
# 7. 拍卖逻辑
# ==========================================
def auction_action(item):
    price = item['price']
    name = item[f'name_{st.session_state.language}']
    st.session_state.total_revenue += price
    st.session_state.sold_items[item['id']] = name
    st.toast(L['toast_buy'].format(name=name), icon="🔨")
    time.sleep(0.5)
    st.rerun()

m_key = MUSEUM_NAME_MAP[museum_sel]
items = MUSEUM_TREASURES.get(m_key, [])
cols = st.columns(4)

for idx, item in enumerate(items):
    with cols[idx % 4]:
        is_sold = item['id'] in st.session_state.sold_items
        name = item[f'name_{st.session_state.language}']
        desc = item[f'desc_{st.session_state.language}']
        
        price_display = f"¥{item['price']/100000000:.1f}{L['unit_price']}" if is_sold else L['reveal']
        p_class = "sold-price" if is_sold else "unsold-price"
        img_url = f"https://picsum.photos/seed/{item['id']}/300/300"
        
        st.markdown(f"""
        <div class="treasure-card">
            <img src="{img_url}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
            <div style="padding:10px;">
                <div class="t-title">{name}</div>
                <div style="font-size:0.7rem; color:#888;">{desc}</div>
                <div class="t-price {p_class}">{price_display}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_sold:
            st.button(L['status_sold'], key=item['id'], disabled=True)
        else:
            if st.button(L['btn_auction'], key=item['id'], type="primary"):
                auction_action(item)

# ==========================================
# 8. 底部功能
# ==========================================
st.markdown("<br><hr>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    if st.button(L['reset']):
        st.session_state.sold_items = {}
        st.session_state.total_revenue = 0
        st.rerun()
with c2:
    if st.button(L['coffee'], use_container_width=True):
        st.balloons()

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

st.markdown(f'<div class="stats-bar">Vistor Count: {track_stats()}</div>', unsafe_allow_html=True)

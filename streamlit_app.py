import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import base64

# ==========================================
# 1. 全局配置 & 路径处理
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except:
    PROJECT_ROOT = os.getcwd()
BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
MANSION_IMG_ROOT = os.path.join(BASE_IMG_ROOT, "mansion")
os.makedirs(BASE_IMG_ROOT, exist_ok=True)
os.makedirs(MANSION_IMG_ROOT, exist_ok=True)

MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}

# ==========================================
# 2. 核心数据 (Mansion & Treasures)
# ==========================================
MANSION_CONFIG = {
    "南京博物院": {"mansion_name": "颐和路民国别墅", "price": 100000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "1.jpeg")},
    "三星堆博物馆": {"mansion_name": "成都麓山国际豪宅", "price": 50000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "5.jpeg")},
    "中国国家博物馆": {"mansion_name": "什刹海四合院", "price": 150000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "2.jpeg")},
    "上海博物馆": {"mansion_name": "愚园路老洋房", "price": 200000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "3.jpeg")},
    "陕西历史博物馆": {"mansion_name": "曲江池畔大平层", "price": 30000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "4.jpeg")}
}

MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name": "金兽", "period": "西汉", "desc": "含金量99%，最重金器", "price": 500000000, "img": ""},
        {"id": "nj_2", "name": "釉里红梅瓶", "period": "明洪武", "desc": "现存唯一带盖梅瓶", "price": 800000000, "img": ""},
        {"id": "nj_3", "name": "金蝉玉叶", "period": "明代", "desc": "金枝玉叶，工艺精湛", "price": 90000000, "img": ""},
        {"id": "nj_4", "name": "银缕玉衣", "period": "东汉", "desc": "银丝编缀，极其罕见", "price": 300000000, "img": ""},
        {"id": "nj_5", "name": "竹林七贤砖画", "period": "南朝", "desc": "魏晋风度最佳见证", "price": 1000000000, "img": ""},
        {"id": "nj_18", "name": "青瓷釉下彩壶", "period": "唐代", "desc": "改写陶瓷史的孤品", "price": 110000000, "img": ""},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": ""},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 1300000000, "img": ""},
        {"id": "sx_4", "name": "青铜纵目面具", "period": "商代", "desc": "千里眼顺风耳", "price": 1200000000, "img": ""},
    ],
    "beijing": [
        {"id": "bj_1", "name": "清明上河图", "period": "北宋", "desc": "中华第一神品", "price": 5000000000, "img": ""},
        {"id": "bj_3", "name": "后母戊鼎", "period": "商代", "desc": "青铜之王", "price": 4000000000, "img": ""},
    ],
    "shanghai": [
        {"id": "sh_1", "name": "大克鼎", "period": "西周", "desc": "海内三宝之一", "price": 1500000000, "img": ""},
    ],
    "xian": [
        {"id": "xa_1", "name": "兽首玛瑙杯", "period": "唐代", "desc": "海内孤品", "price": 2000000000, "img": ""},
        {"id": "xa_4", "name": "兵马俑(跪射)", "period": "秦代", "desc": "保存最完整", "price": 3000000000, "img": ""},
    ]
}

# ==========================================
# 3. 工具函数
# ==========================================
def get_base64_image(image_path):
    try:
        if not os.path.exists(image_path): return None
        with open(image_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except: return None

def format_price(price):
    if price >= 100000000: return f"{price/100000000:.1f}亿"
    elif price >= 10000: return f"{price/10000:.0f}万"
    return str(price)

# 自动加载图片逻辑
for pinyin, items in MUSEUM_TREASURES.items():
    for idx, item in enumerate(items, 1):
        path = os.path.join(BASE_IMG_ROOT, pinyin, f"{idx}.jpeg")
        b64 = get_base64_image(path)
        item["img"] = b64 if b64 else f"https://picsum.photos/seed/{item['id']}/300/300"

# ==========================================
# 4. 样式优化
# ==========================================
st.markdown("""
<style>
    [data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #f8f9fa; color: #1d1d1f; }
    .block-container { padding-top: 1.5rem !important; max-width: 1300px !important; }

    /* 左右分栏对齐 */
    .museum-card {
        background: white; padding: 25px; border-radius: 16px; 
        box-shadow: 0 2px 12px rgba(0,0,0,0.05); border: 1px solid #eee; height: 100%;
    }
    
    .dashboard {
        background: white; border-radius: 16px; padding: 25px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05); border: 1px solid #eee; height: 100%;
    }

    /* 藏品卡片 */
    .treasure-card {
        background: white; border-radius: 12px; border: 1px solid #eee;
        transition: all 0.3s ease; height: 100%; display: flex; flex-direction: column;
        overflow: hidden; text-align: center;
    }
    .treasure-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
    .t-img-box { height: 140px; display: flex; align-items: center; justify-content: center; background: #fafafa; }
    .t-img { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .t-content { padding: 12px; flex-grow: 1; }
    .t-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; }
    .t-period { font-size: 0.75rem; color: #86868b; background: #f5f5f7; padding: 2px 8px; border-radius: 10px; }
    .t-price { font-family: 'Monaco', monospace; font-weight: 700; color: #d9534f; margin-top: 8px; }

    /* 豪宅图覆盖文字 */
    .mansion-overlay-text {
        position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7);
        color: white; padding: 5px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600;
    }
    
    /* 统计条 */
    .stats-bar {
        display: flex; justify-content: center; gap: 40px; margin: 40px auto;
        padding: 15px 30px; background: white; border-radius: 50px; width: fit-content;
        border: 1px solid #eee; color: #86868b; font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 状态管理
# ==========================================
for key, val in [('language', 'zh'), ('sold_items', set()), ('total_revenue', 0), 
                 ('current_museum', '南京博物院'), ('visitor_id', str(uuid.uuid4()))]:
    if key not in st.session_state: st.session_state[key] = val

current_text = {
    'zh': {'detail': '📋 拍卖成交明细', 'count': '成交数量：', 'total': '成交总额：', 'buy': '立即拍卖'},
    'en': {'detail': '📋 Auction Details', 'count': 'Sold Count: ', 'total': 'Total Revenue: ', 'buy': 'Auction'}
}[st.session_state.language]

# ==========================================
# 6. 顶部 & 核心布局 (并排展示)
# ==========================================
# 标题
st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>🏛️ 华夏国宝拍卖中心</h2>", unsafe_allow_html=True)

# 创建核心布局：博物馆选择（左 3） | 仪表盘（右 7）
col_left, col_right = st.columns([0.3, 0.7], gap="large")

with col_left:
    st.markdown('<div class="museum-card">', unsafe_allow_html=True)
    st.markdown("##### 📍 选择博物馆")
    selected = st.radio("Museum Selector", list(MANSION_CONFIG.keys()), 
                        index=list(MANSION_CONFIG.keys()).index(st.session_state.current_museum),
                        label_visibility="collapsed")
    if selected != st.session_state.current_museum:
        st.session_state.current_museum = selected
        st.rerun()
    
    # 语言切换与重置并排
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🌐 En/中", use_container_width=True):
            st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
            st.rerun()
    with c_btn2:
        if st.button("🔄 重置", use_container_width=True):
            st.session_state.sold_items, st.session_state.total_revenue = set(), 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="dashboard">', unsafe_allow_html=True)
    m_info = MANSION_CONFIG[st.session_state.current_museum]
    v_count = st.session_state.total_revenue / m_info["price"]
    
    d_col1, d_col2 = st.columns([0.4, 0.6])
    with d_col1:
        st.markdown(f"#### {st.session_state.current_museum}")
        st.markdown(f"<h2 style='color: #d9534f; margin: 0;'>¥{st.session_state.total_revenue / 100000000:.2f}亿</h2>", unsafe_allow_html=True)
        st.caption("累计拍卖总额")
        st.markdown(f"**可兑换 {v_count:.2f} 套**<br><small>{m_info['mansion_name']}</small>", unsafe_allow_html=True)
    
    with d_col2:
        # 图片容器
        m_img = get_base64_image(m_info["mansion_img"]) or f"https://picsum.photos/seed/mansion/400/220"
        st.markdown(f"""
        <div style="position: relative; border-radius: 12px; overflow: hidden; height: 160px;">
            <div style="position: absolute; top: 8px; left: 10px; color: white; text-shadow: 1px 1px 4px black; font-weight: bold; z-index: 10;">
                🏠 {m_info['mansion_name']}
            </div>
            <img src="{m_img}" style="width: 100%; height: 100%; object-fit: cover;">
            <div class="mansion-overlay-text">× {v_count:.2f} Units</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. 成交明细 (折叠显示，更简洁)
# ==========================================
with st.expander(current_text['detail']):
    sold_treasures = [t for t in MUSEUM_TREASURES[MUSEUM_NAME_MAP[st.session_state.current_museum]] 
                     if t['id'] in st.session_state.sold_items]
    if not sold_treasures:
        st.write("暂无成交 records.")
    else:
        cols = st.columns(4)
        for i, t in enumerate(sold_treasures):
            cols[i % 4].markdown(f"✅ **{t['name']}** · {format_price(t['price'])}")
        st.divider()
        st.markdown(f"**{current_text['count']}** {len(sold_treasures)} | **{current_text['total']}** ¥{format_price(st.session_state.total_revenue)}")

# ==========================================
# 8. 藏品展示网格 (6列显示)
# ==========================================
items = MUSEUM_TREASURES[MUSEUM_NAME_MAP[st.session_state.current_museum]]
st.markdown(f"### 🏺 {st.session_state.current_museum} 藏品")



cols = st.columns(6, gap="small")
for idx, item in enumerate(items):
    with cols[idx % 6]:
        is_sold = item['id'] in st.session_state.sold_items
        st.markdown(f"""
        <div class="treasure-card" style="opacity: {0.5 if is_sold else 1};">
            <div class="t-img-box"><img src="{item['img']}" class="t-img"></div>
            <div class="t-content">
                <div class="t-title">{item['name']}</div>
                <div class="t-period">{item['period']}</div>
                <div class="t-price">¥{format_price(item['price'])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_sold:
            st.button("已售", key=f"btn_{item['id']}", disabled=True, use_container_width=True)
        else:
            if st.button(current_text['buy'], key=f"btn_{item['id']}", type="primary", use_container_width=True):
                st.session_state.total_revenue += item['price']
                st.session_state.sold_items.add(item['id'])
                st.toast(f"🎉 {item['name']} 拍卖成功！", icon="💰")
                time.sleep(0.5)
                st.rerun()

# ==========================================
# 9. 底部统计
# ==========================================
st.markdown(f"""
<div class="stats-bar">
    <div>今日访问 UV: <b>{random.randint(100, 200)}</b></div>
    <div style="border-left: 1px solid #eee; padding-left: 40px;">累计访问 UV: <b>{random.randint(5000, 6000)}</b></div>
</div>
""", unsafe_allow_html=True)

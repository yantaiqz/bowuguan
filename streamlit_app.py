import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import base64

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"  # 侧边栏默认展开显示明细
)

# 路径兼容处理
try:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except:
    PROJECT_ROOT = os.getcwd()

BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
os.makedirs(BASE_IMG_ROOT, exist_ok=True)

MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}

# ==========================================
# 2. CSS 样式优化 (核心布局调整)
# ==========================================
st.markdown("""
<style>
    /* 全局背景 */
    .stApp { background-color: #f5f7fa; }
    
    /* --- 1. 吸顶仪表盘 (Sticky Header) --- */
    .sticky-dashboard {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(0,0,0,0.05);
        padding: 15px 20px;
        margin: -1rem -1rem 20px -1rem; /* 抵消 stApp 的默认 padding */
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* 豪宅进度展示 */
    .mansion-progress {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .money-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem;
        font-weight: 800;
        color: #d9534f;
        background: #fff0f0;
        padding: 5px 15px;
        border-radius: 8px;
        border: 1px solid #ffcccc;
    }

    /* --- 2. 藏品卡片优化 --- */
    .treasure-card {
        background: white;
        border-radius: 12px;
        padding: 0;
        border: 1px solid #e1e4e8;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    .treasure-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border-color: #d1d5db;
    }
    
    /* 图片区域 */
    .card-img-container {
        width: 100%;
        height: 160px;
        background: #f8f9fa;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #f0f0f0;
        position: relative;
    }
    .card-img {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .treasure-card:hover .card-img {
        transform: scale(1.1) rotate(3deg);
    }
    
    /* 内容区域 */
    .card-body {
        padding: 15px;
        flex-grow: 1;
        text-align: center;
        display: flex;
        flex-direction: column;
    }
    .card-title { font-weight: 700; color: #333; margin-bottom: 5px; font-size: 1.05rem; }
    .card-period { 
        font-size: 0.75rem; color: #666; background: #eee; 
        padding: 2px 8px; border-radius: 10px; align-self: center; margin-bottom: 8px;
    }
    .card-desc { font-size: 0.85rem; color: #777; line-height: 1.4; margin-bottom: 10px; flex-grow: 1; }
    .card-price { font-weight: bold; font-family: monospace; color: #2AAD67; font-size: 1rem; }
    
    /* 已售出状态 */
    .sold-card { opacity: 0.6; filter: grayscale(1); pointer-events: none; }
    .sold-text { color: #d9534f; font-weight: bold; text-decoration: line-through; }

    /* 侧边栏表格优化 */
    .sidebar-table { width: 100%; font-size: 0.85rem; }
    .sidebar-table td { padding: 8px 0; border-bottom: 1px dashed #eee; }
    .sidebar-total { margin-top: 15px; padding-top: 10px; border-top: 2px solid #333; font-weight: bold; }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stSidebarUserContent"] { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 数据配置 (保持原逻辑)
# ==========================================
MANSION_CONFIG = {
    "南京博物院": { "mansion_name": "颐和路民国别墅", "price": 100000000, "mansion_img": "img/mansion/1.jpeg" },
    "三星堆博物馆": { "mansion_name": "成都麓山国际豪宅", "price": 50000000, "mansion_img": "img/mansion/2.jpeg" },
    "中国国家博物馆": { "mansion_name": "什刹海四合院", "price": 150000000, "mansion_img": "img/mansion/3.jpeg" },
    "上海博物馆": { "mansion_name": "愚园路老洋房", "price": 200000000, "mansion_img": "img/mansion/4.jpeg" },
    "陕西历史博物馆": { "mansion_name": "曲江池畔大平层", "price": 30000000, "mansion_img": "img/mansion/5.jpeg" }
}

# (此处省略 MUSEUM_TREASURES 数据，保持原样，假设数据已存在)
# 为了演示，这里填充占位数据，实际使用请将您原代码中的 MUSEUM_TREASURES 完整复制回这里
MUSEUM_TREASURES = {
    "nanjing": [{"id": f"nj_{i}", "name": f"南京宝藏_{i}", "period": "明清", "desc": "稀世珍宝", "price": 50000000 * i, "img": ""} for i in range(1, 19)],
    "sanxingdui": [{"id": f"sx_{i}", "name": f"青铜神兽_{i}", "period": "商代", "desc": "外星文明", "price": 60000000 * i, "img": ""} for i in range(1, 19)],
    "beijing": [{"id": f"bj_{i}", "name": f"国博重器_{i}", "period": "上古", "desc": "镇国之宝", "price": 80000000 * i, "img": ""} for i in range(1, 19)],
    "shanghai": [{"id": f"sh_{i}", "name": f"江南雅韵_{i}", "period": "宋元", "desc": "精致典雅", "price": 40000000 * i, "img": ""} for i in range(1, 19)],
    "xian": [{"id": f"xa_{i}", "name": f"大唐盛世_{i}", "period": "唐代", "desc": "气吞山河", "price": 30000000 * i, "img": ""} for i in range(1, 19)],
}

# ==========================================
# 4. 状态管理
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None

# ==========================================
# 5. 辅助函数
# ==========================================
def format_price(price):
    if price >= 100000000: return f"{price/100000000:.1f}亿"
    elif price >= 10000: return f"{price/10000:.0f}万"
    return str(price)

def get_image_url(item_id, idx, museum_pinyin):
    # 模拟图片获取逻辑，优先尝试本地，否则用 Picsum
    return f"https://picsum.photos/seed/{item_id}/300/300"

# ==========================================
# 6. 侧边栏布局 (Sidebar) - 放置明细与统计
# ==========================================
with st.sidebar:
    st.header("📋 拍卖行账本")
    
    # 语言切换
    if st.button("🌐 Switch Language (中/En)", use_container_width=True):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

    st.divider()
    
    # 成交明细
    current_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
    all_items = MUSEUM_TREASURES.get(current_pinyin, [])
    sold_list = [t for t in all_items if t['id'] in st.session_state.sold_items]
    
    if not sold_list:
        st.info("暂无成交记录" if st.session_state.language == 'zh' else "No records yet")
    else:
        st.markdown('<div class="sidebar-table"><table>', unsafe_allow_html=True)
        for item in sold_list:
             st.markdown(f"""
             <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px dashed #ddd; padding-bottom:4px;">
                <span>{item['name']}</span>
                <span style="color:#d9534f; font-family:monospace;">¥{format_price(item['price'])}</span>
             </div>
             """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 汇总
        st.markdown(f"""
        <div class="sidebar-total">
            <div>累计成交: {len(sold_list)} 件</div>
            <div style="font-size:1.2em; color:#d9534f;">总额: ¥{format_price(st.session_state.total_revenue)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 重置按钮
    if st.button("🗑️ 破产重置 / Reset", type="secondary", use_container_width=True):
        st.session_state.sold_items = set()
        st.session_state.total_revenue = 0
        st.rerun()
        
    # 打赏入口
    with st.expander("☕ 支持开发者 / Support"):
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Donate", caption="Scan via WeChat/Alipay")

# ==========================================
# 7. 主界面布局
# ==========================================

# --- A. 顶部吸顶仪表盘 ---
mansion_info = MANSION_CONFIG[st.session_state.current_museum]
current_ratio = st.session_state.total_revenue / mansion_info["price"]

dashboard_html = f"""
<div class="sticky-dashboard">
    <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:1.8rem;">🏛️</span>
        <div>
            <div style="font-weight:bold; font-size:1.1rem; color:#333;">{st.session_state.current_museum}</div>
            <div style="font-size:0.8rem; color:#666;">目标: {mansion_info['mansion_name']}</div>
        </div>
    </div>
    
    <div class="mansion-progress">
        <div style="text-align:right;">
            <div style="font-size:0.7rem; color:#888; text-transform:uppercase;">Current Revenue</div>
            <div class="money-tag">¥{format_price(st.session_state.total_revenue)}</div>
        </div>
        <div style="background:#333; color:white; padding:5px 12px; border-radius:6px; font-weight:bold;">
            x {current_ratio:.2f} 套
        </div>
    </div>
</div>
"""
st.markdown(dashboard_html, unsafe_allow_html=True)

# --- B. 博物馆选择 (Tabs) ---
# 使用 Tabs 替代 Radio，节省纵向空间且更符合现代 UI
museum_names = list(MANSION_CONFIG.keys())
selected_tab = st.selectbox("选择博物馆 / Select Museum", museum_names, index=museum_names.index(st.session_state.current_museum))

if selected_tab != st.session_state.current_museum:
    st.session_state.current_museum = selected_tab
    st.rerun()

# --- C. 藏品网格展示 ---
st.write("") # Spacer

current_items = MUSEUM_TREASURES.get(MUSEUM_NAME_MAP[st.session_state.current_museum], [])
cols_per_row = 4
rows = [current_items[i:i + cols_per_row] for i in range(0, len(current_items), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for idx, item in enumerate(row):
        with cols[idx]:
            is_sold = item['id'] in st.session_state.sold_items
            
            # 卡片容器类名
            card_class = "treasure-card sold-card" if is_sold else "treasure-card"
            
            # 构建 HTML 卡片
            img_src = item.get('img') or f"https://picsum.photos/seed/{item['id']}/300/300"
            price_display = f"¥{format_price(item['price'])}" if is_sold else "🕵️ 价值待揭晓"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="card-img-container">
                    <img src="{img_src}" class="card-img">
                </div>
                <div class="card-body">
                    <div class="card-title">{item['name']}</div>
                    <div class="card-period">{item['period']}</div>
                    <div class="card-desc">{item['desc']}</div>
                    <div class="card-price {'sold-text' if is_sold else ''}">{price_display}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 按钮逻辑 (放在卡片下方)
            if is_sold:
                st.button("🚫 已私有化", key=f"btn_{item['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("🔨 立即拍卖", key=f"btn_{item['id']}", type="primary", use_container_width=True):
                    # 拍卖动画逻辑
                    msg = st.toast(f"正在拍卖 {item['name']}...", icon="⏳")
                    time.sleep(0.5)
                    st.session_state.total_revenue += item['price']
                    st.session_state.sold_items.add(item['id'])
                    st.session_state.last_sold_id = item['id']
                    msg.toast(f"成交！入账 ¥{format_price(item['price'])}", icon="💰")
                    time.sleep(0.5)
                    st.rerun()
    
    st.write("") # 行间距

# ==========================================
# 8. 底部统计条
# ==========================================
st.markdown("---")
col_c, col_d = st.columns([8, 2])
with col_c:
    st.caption("© 2025 National Treasures Auction. All rights reserved.")
with col_d:
    st.caption(f"Visitor ID: {str(uuid.uuid4())[:8]}")

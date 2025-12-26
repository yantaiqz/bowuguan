import streamlit as st
import time
import random

# ==========================================
# 1. 全局配置与沉浸式 UI 注入
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 隐藏所有 Streamlit 原生组件：菜单、工具栏、页脚
st.markdown("""
<style>
    /* 彻底隐藏顶部工具栏和菜单 */
    [data-testid="stHeader"] {display: none !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    
    .stApp { 
        background-color: #f5f5f7 !important; 
        color: #1d1d1f; 
        padding-top: 0 !important;
    }

    /* --- 顶部博物馆导航栏 --- */
    .nav-container {
        background: #ffffff;
        padding: 10px 0;
        border-bottom: 1px solid #e5e5e5;
        text-align: center;
    }

    /* --- 房产展示区美化 --- */
    .mansion-box {
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        padding: 15px;
        min-width: 280px;
        color: white;
        text-shadow: 0 2px 10px rgba(0,0,0,0.8);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .mansion-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.3);
        z-index: 1;
    }
    .mansion-content { position: relative; z-index: 2; }

    /* --- 仪表盘吸顶 --- */
    .dashboard {
        position: sticky; 
        top: 0; 
        z-index: 999;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        padding: 15px 30px !important;
        border-bottom: 1px solid #e5e5e5;
        margin: 0 -1rem 20px -1rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    /* --- 文物卡片 --- */
    .treasure-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        transition: all 0.3s;
        border: 1px solid #e5e5e5;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .treasure-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
    .t-img { width: 100%; height: 180px; object-fit: cover; }
    .t-content { padding: 15px; flex-grow: 1; }
    .t-title { font-size: 1.1rem; font-weight: 800; color: #111; margin-bottom: 5px; }
    .t-price { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; color: #d9534f; font-weight: 700; }

    /* 横向选择器样式 */
    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 15px;
        background: white;
        padding: 15px;
        border-radius: 0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心映射数据
# ==========================================
MUSEUM_INFO = {
    "南京博物院": {
        "city": "南京",
        "mansion_name": "颐和路民国别墅",
        "mansion_price": 100000000,
        "mansion_img": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=400&q=80"
    },
    "三星堆博物馆": {
        "city": "三星堆",
        "mansion_name": "成都麓山国际豪宅",
        "mansion_price": 50000000,
        "mansion_img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=400&q=80"
    },
    "中国国家博物馆": {
        "city": "北京",
        "mansion_name": "什刹海四合院",
        "mansion_price": 150000000,
        "mansion_img": "https://images.unsplash.com/photo-1595130838493-2199b4226d9e?auto=format&fit=crop&w=400&q=80"
    },
    "上海博物馆": {
        "city": "上海",
        "mansion_name": "愚园路老洋房",
        "mansion_price": 200000000,
        "mansion_img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=400&q=80"
    },
    "陕西历史博物馆": {
        "city": "西安",
        "mansion_name": "曲江池畔大平层",
        "mansion_price": 30000000,
        "mansion_img": "https://images.unsplash.com/photo-1600607687940-472002695533?auto=format&fit=crop&w=400&q=80"
    }
}

# (此处 TREASURES 数据由于篇幅关系复用前文定义的 MUSEUM_DATA，仅需修改 Key 名为博物馆全称)
# 为了节省篇幅，建议将之前 MUSEUM_DATA 的 Key 从 "南京" 改为 "南京博物院" 等全称即可。
# 以下为简化后的数据结构示例：
MUSEUM_TREASURES = {
    "南京博物院": [
        {"id": "nj_1", "name": "金兽", "period": "西汉", "desc": "最重金器", "price": 500000000, "img": "https://picsum.photos/seed/nj1/400/300"},
        {"id": "nj_2", "name": "釉里红梅瓶", "period": "明洪武", "desc": "孤品大器", "price": 800000000, "img": "https://picsum.photos/seed/nj2/400/300"},
        {"id": "nj_3", "name": "金蝉玉叶", "period": "明代", "desc": "金枝玉叶", "price": 90000000, "img": "https://picsum.photos/seed/nj3/400/300"},
        {"id": "nj_4", "name": "银缕玉衣", "period": "东汉", "desc": "银丝编缀", "price": 300000000, "img": "https://picsum.photos/seed/nj4/400/300"},
    ],
    "三星堆博物馆": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/400/300"},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/400/300"},
    ],
    "中国国家博物馆": [{"id": "bj_1", "name": "清明上河图", "price": 5000000000, "img": "https://picsum.photos/seed/bj1/400/300"}],
    "上海博物馆": [{"id": "sh_1", "name": "大克鼎", "price": 1500000000, "img": "https://picsum.photos/seed/sh1/400/300"}],
    "陕西历史博物馆": [{"id": "xa_1", "name": "镶金兽首玛瑙杯", "price": 2000000000, "img": "https://picsum.photos/seed/xa1/400/300"}]
}

# ==========================================
# 3. 状态管理
# ==========================================
if 'sold_items' not in st.session_state: st.session_state.sold_items = set()
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"

# ==========================================
# 4. 顶部导航 (博物馆全称)
# ==========================================
st.markdown("<h2 style='text-align: center; margin-top: 20px; color: #111;'>🏛️ 华夏国宝私有化中心</h2>", unsafe_allow_html=True)

selected_museum = st.radio(
    "Select Museum",
    list(MUSEUM_INFO.keys()),
    index=list(MUSEUM_INFO.keys()).index(st.session_state.current_museum),
    horizontal=True,
    label_visibility="collapsed"
)

if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.rerun()

# ==========================================
# 5. 吸顶仪表盘 (房产配图)
# ==========================================
m_info = MUSEUM_INFO[st.session_state.current_museum]
villa_count = st.session_state.total_revenue / m_info["mansion_price"]

dashboard_html = f"""
<div class="dashboard">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
        <div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #111;">{st.session_state.current_museum}</div>
            <div style="font-size: 1.8rem; font-weight: 900; color: #d9534f;">¥{st.session_state.total_revenue / 100000000:.2f}亿</div>
            <div style="font-size: 0.8rem; color: #86868b; text-transform: uppercase;">累计拍卖总额</div>
        </div>
        
        <div class="mansion-box" style="background-image: url('{m_info["mansion_img"]}');">
            <div class="mansion-overlay"></div>
            <div class="mansion-content">
                <div style="font-size: 0.8rem; opacity: 0.9;">当前财富购买力：</div>
                <div style="font-size: 1.5rem; font-weight: 900;">× {villa_count:.1f} 套</div>
                <div style="font-size: 0.9rem; font-weight: 600;">{m_info["mansion_name"]}</div>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(dashboard_html, unsafe_allow_html=True)

# ==========================================
# 6. 拍卖核心函数
# ==========================================
def sell_item(item_id, price):
    if item_id not in st.session_state.sold_items:
        st.session_state.sold_items.add(item_id)
        st.session_state.total_revenue += price
        st.toast(f"🔨 恭喜！您成功购入了一件国宝", icon="💰")
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 7. 主内容展示区
# ==========================================
# 为了演示，此处仅获取当前选定馆藏。在实际使用中，请确保 MUSEUM_TREASURES 包含所有20件数据。
items = MUSEUM_TREASURES.get(st.session_state.current_museum, [])

cols = st.columns(4)
for idx, item in enumerate(items):
    with cols[idx % 4]:
        is_sold = item['id'] in st.session_state.sold_items
        
        st.markdown(f"""
        <div class="treasure-card">
            <img src="{item['img']}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
            <div class="t-content">
                <div class="t-title">{item['name']}</div>
                <div style="font-size: 0.8rem; color: #888; margin-bottom: 8px;">{item.get('period', '古代')}</div>
                <div class="t-price">¥{item['price']/100000000:.2f}亿</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_sold:
            st.button("已购入", key=item['id'], disabled=True, use_container_width=True)
        else:
            st.button("立即拍卖", key=item['id'], type="primary", use_container_width=True, 
                      on_click=sell_item, args=(item['id'], item['price']))

# ==========================================
# 8. 底部重置
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
if st.button("🔄 破产并清空所有藏品"):
    st.session_state.sold_items = set()
    st.session_state.total_revenue = 0
    st.rerun()

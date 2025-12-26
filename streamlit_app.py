import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    "南京博物院": [
        {"id": "nj_1", "name": "金兽", "period": "西汉", "desc": "含金量99%，最重金器", "price": 500000000, "img": "https://picsum.photos/seed/nj1/400/300"},
        {"id": "nj_2", "name": "釉里红梅瓶", "period": "明洪武", "desc": "现存唯一带盖梅瓶", "price": 800000000, "img": "https://picsum.photos/seed/nj2/400/300"},
        {"id": "nj_3", "name": "金蝉玉叶", "period": "明代", "desc": "金枝玉叶，工艺精湛", "price": 90000000, "img": "https://picsum.photos/seed/nj3/400/300"},
        {"id": "nj_4", "name": "银缕玉衣", "period": "东汉", "desc": "银丝编缀，极其罕见", "price": 300000000, "img": "https://picsum.photos/seed/nj4/400/300"},
        {"id": "nj_5", "name": "竹林七贤砖画", "period": "南朝", "desc": "魏晋风度最佳见证", "price": 1000000000, "img": "https://picsum.photos/seed/nj5/400/300"},
        {"id": "nj_6", "name": "大报恩寺拱门", "period": "明代", "desc": "世界奇迹残留组件", "price": 200000000, "img": "https://picsum.photos/seed/nj6/400/300"},
        {"id": "nj_7", "name": "坤舆万国全图", "period": "明万历", "desc": "最早彩绘世界地图", "price": 600000000, "img": "https://picsum.photos/seed/nj7/400/300"},
        {"id": "nj_8", "name": "广陵王玺", "period": "东汉", "desc": "汉代封王金印精品", "price": 200000000, "img": "https://picsum.photos/seed/nj8/400/300"},
    ],
    "三星堆博物馆": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/400/300"},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/400/300"},
        {"id": "sx_3", "name": "金面具", "period": "商代", "desc": "半张黄金脸", "price": 800000000, "img": "https://picsum.photos/seed/sx3/400/300"},
        {"id": "sx_4", "name": "青铜纵目面具", "period": "商代", "desc": "千里眼顺风耳", "price": 1200000000, "img": "https://picsum.photos/seed/sx4/400/300"},
        {"id": "sx_5", "name": "太阳轮", "period": "商代", "desc": "形似方向盘", "price": 600000000, "img": "https://picsum.photos/seed/sx5/400/300"},
        {"id": "sx_6", "name": "玉璋", "period": "商代", "desc": "祭祀山川礼器", "price": 300000000, "img": "https://picsum.photos/seed/sx6/400/300"},
        {"id": "sx_7", "name": "黄金权杖", "period": "商代", "desc": "王权的象征", "price": 1500000000, "img": "https://picsum.photos/seed/sx7/400/300"},
        {"id": "sx_8", "name": "青铜神坛", "period": "商代", "desc": "复杂祭祀场景", "price": 900000000, "img": "https://picsum.photos/seed/sx8/400/300"},
    ],
    "中国国家博物馆": [
        {"id": "bj_1", "name": "清明上河图", "period": "北宋", "desc": "中华第一神品", "price": 5000000000, "img": "https://picsum.photos/seed/bj1/400/300"},
        {"id": "bj_2", "name": "金瓯永固杯", "period": "清乾隆", "desc": "乾隆御用金杯", "price": 600000000, "img": "https://picsum.photos/seed/bj2/400/300"},
        {"id": "bj_3", "name": "后母戊鼎", "period": "商代", "desc": "青铜之王", "price": 4000000000, "img": "https://picsum.photos/seed/bj3/400/300"},
        {"id": "bj_4", "name": "千里江山图", "period": "北宋", "desc": "青绿山水巅峰", "price": 3000000000, "img": "https://picsum.photos/seed/bj4/400/300"},
        {"id": "bj_5", "name": "四羊方尊", "period": "商代", "desc": "青铜铸造奇迹", "price": 2000000000, "img": "https://picsum.photos/seed/bj5/400/300"},
        {"id": "bj_6", "name": "孝端皇后凤冠", "period": "明代", "desc": "点翠工艺巅峰", "price": 500000000, "img": "https://picsum.photos/seed/bj6/400/300"},
        {"id": "bj_7", "name": "金缕玉衣", "period": "西汉", "desc": "中山靖王同款", "price": 1000000000, "img": "https://picsum.photos/seed/bj7/400/300"},
        {"id": "bj_8", "name": "红山玉龙", "period": "新石器", "desc": "中华第一龙", "price": 1200000000, "img": "https://picsum.photos/seed/bj8/400/300"},
    ],
    "上海博物馆": [
        {"id": "sh_1", "name": "大克鼎", "period": "西周", "desc": "海内三宝之一", "price": 1500000000, "img": "https://picsum.photos/seed/sh1/400/300"},
        {"id": "sh_2", "name": "晋侯苏钟", "period": "西周", "desc": "铭文刻在钟表", "price": 800000000, "img": "https://picsum.photos/seed/sh2/400/300"},
        {"id": "sh_3", "name": "孙位高逸图", "period": "唐代", "desc": "唐代人物画孤本", "price": 1200000000, "img": "https://picsum.photos/seed/sh3/400/300"},
        {"id": "sh_4", "name": "越王剑", "period": "春秋", "desc": "虽不如勾践剑", "price": 300000000, "img": "https://picsum.photos/seed/sh4/400/300"},
        {"id": "sh_5", "name": "粉彩蝠桃纹瓶", "period": "清雍正", "desc": "雍正官窑极品", "price": 400000000, "img": "https://picsum.photos/seed/sh5/400/300"},
        {"id": "sh_6", "name": "王羲之上虞帖", "period": "唐摹本", "desc": "书圣墨宝", "price": 2000000000, "img": "https://picsum.photos/seed/sh6/400/300"},
        {"id": "sh_7", "name": "苦笋帖", "period": "唐怀素", "desc": "草书狂僧真迹", "price": 1000000000, "img": "https://picsum.photos/seed/sh7/400/300"},
        {"id": "sh_8", "name": "青花瓶", "period": "元代", "desc": "元青花存世稀少", "price": 600000000, "img": "https://picsum.photos/seed/sh8/400/300"},
    ],
    "陕西历史博物馆": [
        {"id": "xa_1", "name": "兽首玛瑙杯", "period": "唐代", "desc": "海内孤品", "price": 2000000000, "img": "https://picsum.photos/seed/xa1/400/300"},
        {"id": "xa_2", "name": "舞马衔杯银壶", "period": "唐代", "desc": "大唐盛世缩影", "price": 800000000, "img": "https://picsum.photos/seed/xa2/400/300"},
        {"id": "xa_3", "name": "皇后之玺", "period": "西汉", "desc": "吕后之印", "price": 1000000000, "img": "https://picsum.photos/seed/xa3/400/300"},
        {"id": "xa_4", "name": "兵马俑(跪射)", "period": "秦代", "desc": "保存最完整", "price": 3000000000, "img": "https://picsum.photos/seed/xa4/400/300"},
        {"id": "xa_5", "name": "葡萄花鸟香囊", "period": "唐代", "desc": "杨贵妃同款", "price": 500000000, "img": "https://picsum.photos/seed/xa5/400/300"},
        {"id": "xa_6", "name": "鎏金铜蚕", "period": "西汉", "desc": "丝绸之路见证", "price": 300000000, "img": "https://picsum.photos/seed/xa6/400/300"},
        {"id": "xa_7", "name": "独孤信印", "period": "西魏", "desc": "多面体印章", "price": 400000000, "img": "https://picsum.photos/seed/xa7/400/300"},
        {"id": "xa_8", "name": "提梁倒注壶", "period": "五代", "desc": "神奇倒注构造", "price": 200000000, "img": "https://picsum.photos/seed/xa8/400/300"},
    ]
}

# ==========================================
# 3. 样式合并
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    .stApp { background-color: #f5f5f7 !important; color: #1d1d1f; }
    .block-container { padding-top: 1rem !important; max-width: 1400px !important; }

    /* --- 仪表盘吸顶 --- */
    .dashboard {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        padding: 15px 30px !important;
        border-bottom: 1px solid #e5e5e5;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: all 0.1s ease;
    }

    /* --- 房产展示区美化 --- */
    .mansion-box {
        background-size: cover; background-position: center; border-radius: 12px;
        padding: 15px; min-width: 280px; color: white;
        text-shadow: 0 2px 10px rgba(0,0,0,0.8); position: relative;
        overflow: hidden; border: 1px solid rgba(255,255,255,0.2);
    }
    .mansion-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.3); z-index: 1; }
    .mansion-content { position: relative; z-index: 2; }

    /* --- 文物卡片 --- */
    .treasure-card {
        background: white; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03); transition: all 0.3s;
        border: 1px solid #e5e5e5; overflow: hidden; height: 100%;
        display: flex; flex-direction: column;
    }
    .treasure-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
    .t-img-box { height: 180px; width: 100%; overflow: hidden; background: #f0f0f0; display: flex; align-items: center; justify-content: center; }
    .t-img { width: 100%; height: 100%; object-fit: cover; transition: filter 0.3s ease; }
    .t-content { padding: 12px !important; flex-grow: 1; display: flex; flex-direction: column; }
    .t-title { font-size: 1rem; font-weight: 800; color: #111; margin-bottom: 4px !important; }
    .t-period { font-size: 0.75rem; color: #86868b; background: #f5f5f7; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 6px !important; width: fit-content; }
    .t-desc { font-size: 0.8rem; color: #555; line-height: 1.4; margin-bottom: 8px !important; flex-grow: 1; }
    .t-price { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 700; color: #d9534f; margin: 5px 0 !important; }

    div[data-testid="stButton"] button { width: 100% !important; border-radius: 6px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 状态初始化
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"

# 防止旧缓存导致 Key Error
if st.session_state.current_museum not in MANSION_CONFIG:
    st.session_state.current_museum = list(MANSION_CONFIG.keys())[0]

# ==========================================
# 5. 顶部功能区
# ==========================================
col_title, col_lang = st.columns([0.9, 0.1])
with col_title:
    st.markdown("<h2 style='margin-top: 0; color: #111;'>🏛️ 华夏国宝私有化中心</h2>", unsafe_allow_html=True)
with col_lang:
    if st.button("En/中", key="lang_switch"):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

# 博物馆选择器
selected_museum = st.radio(
    "Select Museum",
    list(MANSION_CONFIG.keys()),
    index=list(MANSION_CONFIG.keys()).index(st.session_state.current_museum),
    horizontal=True,
    label_visibility="collapsed"
)

if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.rerun()

# ==========================================
# 6. 核心功能：动态仪表盘 & 动画逻辑
# ==========================================

# 创建一个空的容器用于放置仪表盘，以便我们可以单独更新它
dashboard_placeholder = st.empty()

def render_dashboard(current_revenue_display):
    """
    渲染仪表盘 HTML 到 placeholder
    """
    m_info = MANSION_CONFIG[st.session_state.current_museum]
    villa_count = current_revenue_display / m_info["price"] if m_info["price"] else 0
    
    html = f"""
    <div class="dashboard">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
            <div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #111;">{st.session_state.current_museum}</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #d9534f; transition: all 0.2s;">
                    ¥{current_revenue_display / 100000000:.4f}亿
                </div>
                <div style="font-size: 0.8rem; color: #86868b; text-transform: uppercase;">累计拍卖总额</div>
            </div>
            <div class="mansion-box" style="background-image: url('{m_info["mansion_img"]}');">
                <div class="mansion-overlay"></div>
                <div class="mansion-content">
                    <div style="font-size: 0.8rem; opacity: 0.9;">当前财富购买力：</div>
                    <div style="font-size: 1.5rem; font-weight: 900;">× {villa_count:.2f} 套</div>
                    <div style="font-size: 0.9rem; font-weight: 600;">{m_info["mansion_name"]}</div>
                </div>
            </div>
        </div>
    </div>
    """
    dashboard_placeholder.markdown(html, unsafe_allow_html=True)

# 初始渲染（使用当前真实总金额）
render_dashboard(st.session_state.total_revenue)

def format_price(price):
    if price >= 100000000: return f"{price/100000000:.1f}亿"
    elif price >= 10000: return f"{price/10000:.0f}万"
    return str(price)

def auction_animation(item_price, item_name):
    """
    执行拍卖动画：让仪表盘数字快速跳动
    """
    start_revenue = st.session_state.total_revenue
    target_revenue = start_revenue + item_price
    
    # 动画参数：20帧，每帧间隔极短
    steps = 20
    step_val = item_price / steps
    
    # 显示一个临时的 Toast
    msg = st.toast(f"🔨 正在拍卖 {item_name}...", icon="⏳")
    
    for i in range(steps):
        # 计算当前动画帧的数值
        current_step_val = start_revenue + (step_val * (i + 1))
        # 刷新仪表盘
        render_dashboard(current_step_val)
        # 暂停极短时间以产生动画效果
        time.sleep(0.015)
        
    # 动画结束，更新真实状态
    st.session_state.total_revenue = target_revenue
    st.session_state.sold_items.add(item_id)
    msg.toast(f"✅ 成交！入账 ¥{format_price(item_price)}", icon="💰")
    time.sleep(0.5) # 让用户看清最后的结果
    st.rerun() # 重新运行以刷新按钮状态

# ==========================================
# 7. 商品展示区
# ==========================================
items = MUSEUM_TREASURES.get(st.session_state.current_museum, [])
cols_per_row = 4
rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]

for row_items in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for idx, item in enumerate(row_items):
        item_id = item['id']
        with cols[idx]:
            is_sold = item_id in st.session_state.sold_items
            
            # 卡片 HTML
            st.markdown(f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item['img']}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
                </div>
                <div class="t-content">
                    <div class="t-title">{item['name']}</div>
                    <div class="t-period">{item.get('period', '古代')}</div>
                    <div class="t-desc" title="{item['desc']}">{item['desc']}</div>
                    <div class="t-price">¥{format_price(item['price'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 按钮逻辑
            if is_sold:
                st.button("🚫 已私有化", key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                # 关键修改：这里不使用 on_click 回调，而是直接判断 if st.button
                # 这样我们可以在 st.rerun() 之前执行动画代码
                if st.button("㊙ 立即拍卖", key=f"btn_{item_id}", type="primary", use_container_width=True):
                    auction_animation(item['price'], item['name'])

# ==========================================
# 8. 底部功能
# ==========================================
st.write("<br>", unsafe_allow_html=True)
if st.button("🔄 破产并清空所有藏品", type="secondary", use_container_width=True):
    st.session_state.sold_items = set()
    st.session_state.total_revenue = 0
    st.rerun()

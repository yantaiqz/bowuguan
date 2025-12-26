import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import pandas as pd

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="Nanjing Museum Treasures | 南博宝藏拍卖",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 核心数据：南京博物院20大镇馆之宝
# ==========================================
# 替换失效图片链接为可靠的占位图/备用链接
VILLA_PRICE = 100000000  # 1亿/栋

TREASURES = [
    {"id": 1, "name": "金兽", "period": "西汉", "desc": "中国考古发现最重的金器，含金量99%，国宝级。", "price": 500000000, "img": "https://picsum.photos/seed/treasure1/800/600"},
    {"id": 2, "name": "釉里红岁寒三友纹梅瓶", "period": "明洪武", "desc": "现存唯一一件带盖的洪武釉里红梅瓶，举世无双。", "price": 800000000, "img": "https://picsum.photos/seed/treasure2/800/600"},
    {"id": 3, "name": "金蝉玉叶", "period": "明代", "desc": "金蝉与玉叶的完美结合，寓意'金枝玉叶'，工艺精湛。", "price": 90000000, "img": "https://picsum.photos/seed/treasure3/800/600"},
    {"id": 4, "name": "青瓷神兽尊", "period": "西晋", "desc": "早期青瓷的代表作，造型奇特，不仅是酒器更是艺术品。", "price": 120000000, "img": "https://picsum.photos/seed/treasure4/800/600"},
    {"id": 5, "name": "透雕人鸟兽玉饰", "period": "良渚文化", "desc": "良渚玉器工艺的巅峰，神秘的史前图腾。", "price": 60000000, "img": "https://picsum.photos/seed/treasure5/800/600"},
    {"id": 6, "name": "银缕玉衣", "period": "东汉", "desc": "全长1.7米，用玉2600余片，银丝编缀，极其罕见。", "price": 300000000, "img": "https://picsum.photos/seed/treasure6/800/600"},
    {"id": 7, "name": "人面兽面组合纹玉琮", "period": "良渚文化", "desc": "玉琮之王，刻纹精细到需要在显微镜下才能看清。", "price": 150000000, "img": "https://picsum.photos/seed/treasure7/800/600"},
    {"id": 8, "name": "广陵王玺金印", "period": "东汉", "desc": "汉代封王金印，做工精致，是汉代金印中的精品。", "price": 200000000, "img": "https://picsum.photos/seed/treasure8/800/600"},
    {"id": 9, "name": "错银铜牛灯", "period": "东汉", "desc": "环保设计的先驱，烟尘可通过牛角吸入腹中。", "price": 180000000, "img": "https://picsum.photos/seed/treasure9/800/600"},
    {"id": 10, "name": "竹林七贤与荣启期砖画", "period": "南朝", "desc": "大型模印拼嵌砖画，魏晋风度的最佳实物见证。", "price": 1000000000, "img": "https://picsum.photos/seed/treasure10/800/600"},
    {"id": 11, "name": "青花寿山福海纹香炉", "period": "明宣德", "desc": "宣德官窑大器，完整传世仅此一件，故宫也没这么大的。", "price": 450000000, "img": "https://picsum.photos/seed/treasure11/800/600"},
    {"id": 12, "name": "鎏金喇嘛塔", "period": "明代", "desc": "阿育王塔风格，通体鎏金，镶嵌宝石。", "price": 80000000, "img": "https://picsum.photos/seed/treasure12/800/600"},
    {"id": 13, "name": "青瓷釉下彩盘口壶", "period": "唐代", "desc": "打破了“唐代无釉下彩”的断言，陶瓷史上的里程碑。", "price": 110000000, "img": "https://picsum.photos/seed/treasure13/800/600"},
    {"id": 14, "name": "利玛窦《坤舆万国全图》", "period": "明万历", "desc": "现存最早的彩绘世界地图，改变了中国人的世界观。", "price": 600000000, "img": "https://picsum.photos/seed/treasure14/800/600"},
    {"id": 15, "name": "徐渭《杂花图卷》", "period": "明代", "desc": "大写意花鸟画的巅峰之作，笔墨淋漓。", "price": 350000000, "img": "https://picsum.photos/seed/treasure15/800/600"},
    {"id": 16, "name": "沈寿绣品《耶稣像》", "period": "近代", "desc": "仿真绣代表作，曾在巴拿马万国博览会获金奖。", "price": 50000000, "img": "https://picsum.photos/seed/treasure16/800/600"},
    {"id": 17, "name": "大报恩寺琉璃拱门", "period": "明代", "desc": "明代世界七大奇迹之一的残留组件，极尽奢华。", "price": 200000000, "img": "https://picsum.photos/seed/treasure17/800/600"},
    {"id": 18, "name": "芙蓉石蟠螭耳盖炉", "period": "清乾隆", "desc": "整块芙蓉石雕刻而成，乾隆御用，粉嫩通透。", "price": 130000000, "img": "https://picsum.photos/seed/treasure18/800/600"},
    {"id": 19, "name": "雕漆剔红山水人物纹盒", "period": "明永乐", "desc": "永乐宫廷漆器的标准器，堆漆肥厚，色泽纯正。", "price": 40000000, "img": "https://picsum.photos/seed/treasure19/800/600"},
    {"id": 20, "name": "建元四年金兽", "period": "西汉", "desc": "底座刻有铭文，研究汉代金银工艺的重要标准器。", "price": 160000000, "img": "https://picsum.photos/seed/treasure20/800/600"},
]

# ==========================================
# 3. 样式表 (CSS) - 修复兼容性问题
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    .stApp { 
        background-color: #f5f5f7 !important; 
        color: #1d1d1f; 
        padding-bottom: 2rem !important;
    }
    /* 修复Streamlit默认间距 */
    .block-container {
        padding-top: 1rem !important;
        max-width: 1400px !important;
    }
    
    /* --- 卡片容器 --- */
    .treasure-card {
        background: white;
        border-radius: 16px;
        padding: 0 !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        border: 1px solid #e5e5e5;
        overflow: hidden;
        height: 100%;
    }
    .treasure-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 8px 30px rgba(0,0,0,0.12); 
    }
    
    /* --- 图片样式 --- */
    .t-img-box {
        height: 200px;
        width: 100%;
        overflow: hidden;
        background: #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .t-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: filter 0.3s ease;
    }

    /* --- 内容样式 --- */
    .t-content { 
        padding: 15px !important;
        height: calc(100% - 200px);
        display: flex;
        flex-direction: column;
    }
    .t-title { 
        font-size: 1.1rem; 
        font-weight: 800; 
        color: #111; 
        margin-bottom: 4px !important; 
    }
    .t-period { 
        font-size: 0.8rem; 
        color: #86868b; 
        background: #f5f5f7; 
        padding: 2px 8px; 
        border-radius: 4px; 
        display: inline-block; 
        margin-bottom: 8px !important;
    }
    .t-desc { 
        font-size: 0.85rem; 
        color: #555; 
        height: 4.5em; 
        overflow: hidden; 
        text-overflow: ellipsis; 
        line-height: 1.5;
        margin-bottom: 10px !important;
        flex-grow: 1;
    }
    .t-price { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 1.1rem; 
        font-weight: 700; 
        color: #d9534f; 
        margin: 10px 0 !important;
    }
    
    /* --- 状态标签 --- */
    .sold-tag {
        background: #e5e7eb; 
        color: #9ca3af; 
        font-weight: bold;
        text-align: center; 
        padding: 10px; 
        border-radius: 8px;
        margin-top: 10px;
    }

    /* --- 顶部仪表盘 --- */
    .dashboard {
        position: sticky; 
        top: 0; 
        z-index: 100;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 15px 20px !important;
        border-bottom: 1px solid #e5e5e5;
        margin: 0 -1rem 20px -1rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .villa-icon { font-size: 2rem; margin-right: 10px; }
    .dash-val { 
        font-size: 1.8rem; 
        font-weight: 900; 
        color: #d9534f; 
        font-family: 'Inter', sans-serif; 
        line-height: 1;
    }
    .dash-label { 
        font-size: 0.8rem; 
        color: #86868b; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-top: 5px !important;
    }

    /* --- 按钮样式覆盖 --- */
    div[data-testid="stButton"] {
        margin-top: auto !important;
    }
    div[data-testid="stButton"] button {
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s !important;
        padding: 0.5rem 0 !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: scale(1.02) !important;
    }
    
    /* 修复禁用按钮样式 */
    button[disabled] {
        background-color: #e5e7eb !important;
        color: #9ca3af !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 状态管理 - 初始化默认值
# ==========================================
if 'sold_items' not in st.session_state:
    st.session_state.sold_items = set()  # 存储已卖出的ID
if 'total_revenue' not in st.session_state:
    st.session_state.total_revenue = 0
if 'trigger_refresh' not in st.session_state:
    st.session_state.trigger_refresh = False

# ==========================================
# 5. 顶部仪表盘 (实时计算)
# ==========================================
# 修复除零错误
villa_count = st.session_state.total_revenue / VILLA_PRICE if VILLA_PRICE != 0 else 0
total_revenue_yi = st.session_state.total_revenue / 100000000

dashboard_html = f"""
<div class="dashboard">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.2rem; margin-right: 15px;">🏛️</div>
            <div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #111;">南博宝藏拍卖行</div>
                <div style="font-size: 0.8rem; color: #888;">NANJING MUSEUM AUCTION</div>
            </div>
        </div>
        <div style="text-align: right; display: flex; gap: 40px; align-items: center;">
            <div>
                <div class="dash-val">¥{total_revenue_yi:.2f}亿</div>
                <div class="dash-label">当前拍卖总额</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div class="villa-icon">🏡</div>
                <div style="text-align: left;">
                    <div class="dash-val" style="color: #2AAD67;">× {villa_count:.1f}栋</div>
                    <div class="dash-label">折合颐和路民国别墅</div>
                </div>
            </div>
            
        </div>
    </div>
</div>
"""
st.markdown(dashboard_html, unsafe_allow_html=True)
# ==========================================
# 6. 核心函数
# ==========================================
# 辅助函数：格式化金额
def format_price(price):
    if price >= 100000000:
        return f"{price/100000000:.1f}亿"
    elif price >= 10000:
        return f"{price/10000:.0f}万"
    return str(price)

# 拍卖逻辑函数 - 修复状态更新逻辑
def sell_item(item_id, price):
    if item_id not in st.session_state.sold_items:
        st.session_state.sold_items.add(item_id)
        st.session_state.total_revenue += price
        # 使用状态标记触发刷新，而非直接rerun
        st.session_state.trigger_refresh = True
        st.toast(f"🔨 成交！入账 ¥{format_price(price)}", icon="💰")

# 重置函数
def reset_auction():
    st.session_state.sold_items = set()
    st.session_state.total_revenue = 0
    st.session_state.trigger_refresh = True
    st.toast("🔄 所有拍卖记录已重置", icon="✅")

# ==========================================
# 7. 主内容区 (Grid Layout)
# ==========================================
# 布局：每行4个
cols_per_row = 4
rows = [TREASURES[i:i + cols_per_row] for i in range(0, len(TREASURES), cols_per_row)]

for row_items in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for idx, item in enumerate(row_items):
        with cols[idx]:
            is_sold = item['id'] in st.session_state.sold_items
            
            # 卡片内容 - 修复HTML结构
            card_html = f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item['img']}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
                </div>
                <div class="t-content">
                    <div class="t-title">{item['name']}</div>
                    <div class="t-period">{item['period']}</div>
                    <div class="t-desc" title="{item['desc']}">{item['desc']}</div>
                    <div class="t-price">¥{format_price(item['price'])}</div>
                </div>
                
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 按钮逻辑 - 移除key重复问题
            if is_sold:
                st.button(
                    "🚫 已私有化", 
                    key=f"btn_sold_{item['id']}_{random.randint(1,1000)}", 
                    disabled=True, 
                    use_container_width=True
                )
            else:
                st.button(
                    "🔨 立即拍卖", 
                    key=f"btn_{item['id']}_{random.randint(1,1000)}", 
                    type="primary", 
                    use_container_width=True,
                    on_click=sell_item,
                    args=(item['id'], item['price'])
                )

# ==========================================
# 8. 底部重置区
# ==========================================
st.divider()
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.button(
        "🔄 重置所有拍卖记录", 
        type="secondary", 
        use_container_width=True,
        on_click=reset_auction
    )

st.markdown("""
<div style="text-align: center; color: #999; margin-top: 20px; font-size: 0.8rem;">
    注：本页面所有文物价格均为虚拟估值，仅供娱乐与价值感知参考。<br>
    民国别墅均价参考南京颐和路片区2024年挂牌行情。
</div>
""", unsafe_allow_html=True)

# ==========================================
# 9. 自动刷新逻辑 (修复rerun问题)
# ==========================================
if st.session_state.trigger_refresh:
    st.session_state.trigger_refresh = False
    # 使用streamlit的自动刷新机制，而非强制rerun
    st.rerun()

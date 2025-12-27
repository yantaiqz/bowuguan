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

# 补充豪宅图片与翻译 (真实 Unsplash 豪宅图)
MANSION_CONFIG = {
    "南京博物院": {
        "zh": "颐和路民国公馆", "en": "Republic Era Mansion", 
        "price": 100000000, 
        "img": "https://images.unsplash.com/photo-1600596542815-374e2e3c5545?q=80&w=600&auto=format&fit=crop"
    },
    "三星堆博物馆": {
        "zh": "成都麓山国际庄园", "en": "Chengdu Luxury Estate", 
        "price": 50000000, 
        "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=600&auto=format&fit=crop"
    },
    "中国国家博物馆": {
        "zh": "什刹海二进四合院", "en": "Beijing Courtyard House", 
        "price": 150000000, 
        "img": "https://images.unsplash.com/photo-1599619351208-3e6c839d6828?q=80&w=600&auto=format&fit=crop"
    },
    "上海博物馆": {
        "zh": "愚园路百年老洋房", "en": "Shanghai Heritage Villa", 
        "price": 200000000, 
        "img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=600&auto=format&fit=crop"
    },
    "陕西历史博物馆": {
        "zh": "曲江池畔空中大平层", "en": "Qujiang Lake Penthouse", 
        "price": 30000000, 
        "img": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?q=80&w=600&auto=format&fit=crop"
    }
}

# 文物数据 (结构升级：支持双语)
MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name_zh": "金兽", "name_en": "Golden Beast", "price": 500000000, "desc_zh": "含金量99%，最重金器", "desc_en": "Heaviest ancient gold item"},
        {"id": "nj_2", "name_zh": "釉里红梅瓶", "name_en": "Red Underglaze Vase", "price": 800000000, "desc_zh": "现存唯一带盖梅瓶", "desc_en": "Unique Ming vase with cover"},
        {"id": "nj_3", "name_zh": "金蝉玉叶", "name_en": "Gold Cicada on Jade Leaf", "price": 90000000, "desc_zh": "金枝玉叶，工艺精湛", "desc_en": "Exquisite Ming craftsmanship"},
        {"id": "nj_4", "name_zh": "银缕玉衣", "name_en": "Silver-threaded Jade Suit", "price": 300000000, "desc_zh": "银丝编缀，极其罕见", "desc_en": "Rare Han burial suit"},
        {"id": "nj_5", "name_zh": "竹林七贤砖画", "name_en": "Seven Sages Brick Relief", "price": 1000000000, "desc_zh": "魏晋风度最佳见证", "desc_en": "Masterpiece of Wei-Jin art"},
        {"id": "nj_6", "name_zh": "大报恩寺拱门", "name_en": "Porcelain Tower Arch", "price": 200000000, "desc_zh": "世界奇迹残留组件", "desc_en": "Remnant of a world wonder"},
        {"id": "nj_7", "name_zh": "坤舆万国全图", "name_en": "Kunyu Wanguo Quantu", "price": 600000000, "desc_zh": "最早彩绘世界地图", "desc_en": "Earliest colored world map"},
        {"id": "nj_8", "name_zh": "广陵王玺", "name_en": "Seal of Prince Guangling", "price": 200000000, "desc_zh": "汉代封王金印精品", "desc_en": "Exquisite Han gold seal"},
        {"id": "nj_9", "name_zh": "错银铜牛灯", "name_en": "Inlaid Silver Ox Lamp", "price": 180000000, "desc_zh": "汉代环保黑科技", "desc_en": "Eco-friendly ancient lamp"},
        {"id": "nj_10", "name_zh": "青瓷神兽尊", "name_en": "Celadon Beast Vessel", "price": 120000000, "desc_zh": "造型奇特的早期青瓷", "desc_en": "Unique early celadon"},
        {"id": "nj_11", "name_zh": "透雕人鸟兽玉饰", "name_en": "Jade Ornament", "price": 60000000, "desc_zh": "良渚玉器巅峰", "desc_en": "Prehistoric jade masterpiece"},
        {"id": "nj_12", "name_zh": "鎏金喇嘛塔", "name_en": "Gilt Lama Pagoda", "price": 80000000, "desc_zh": "通体鎏金镶宝石", "desc_en": "Gilded and gem-encrusted"},
        {"id": "nj_13", "name_zh": "青花寿山福海炉", "name_en": "Blue & White Incense Burner", "price": 450000000, "desc_zh": "宣德官窑完整大器", "desc_en": "Imperial Ming porcelain"},
        {"id": "nj_14", "name_zh": "徐渭《杂花图》", "name_en": "Xu Wei's Painting", "price": 350000000, "desc_zh": "大写意水墨巅峰", "desc_en": "Peak of freehand brushwork"},
        {"id": "nj_15", "name_zh": "沈寿《耶稣像》", "name_en": "Embroidery of Jesus", "price": 50000000, "desc_zh": "万国博览会金奖", "desc_en": "Gold medal embroidery"},
        {"id": "nj_16", "name_zh": "芙蓉石蟠螭炉", "name_en": "Quartz Censer", "price": 130000000, "desc_zh": "乾隆御用粉嫩玉石", "desc_en": "Qianlong's favorite quartz"},
        {"id": "nj_17", "name_zh": "人面兽面玉琮", "name_en": "Jade Cong", "price": 150000000, "desc_zh": "微雕工艺神作", "desc_en": "Micro-carving miracle"},
        {"id": "nj_18", "name_zh": "青瓷釉下彩壶", "name_en": "Underglaze Color Pot", "price": 110000000, "desc_zh": "改写陶瓷史的孤品", "desc_en": "Unique Tang ceramic"},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name_zh": "青铜大立人", "name_en": "Bronze Standing Figure", "price": 2000000000, "desc_zh": "世界铜像之王", "desc_en": "King of bronze statues"},
        {"id": "sx_2", "name_zh": "青铜神树", "name_en": "Bronze Sacred Tree", "price": 2500000000, "desc_zh": "通天神树", "desc_en": "Divine tree to heaven"},
        {"id": "sx_3", "name_zh": "金面具", "name_en": "Gold Mask", "price": 800000000, "desc_zh": "半张黄金脸", "desc_en": "Symbol of royal power"},
        {"id": "sx_4", "name_zh": "青铜纵目面具", "name_en": "Protruding Eye Mask", "price": 1200000000, "desc_zh": "千里眼顺风耳", "desc_en": "Mysterious alien look"},
        {"id": "sx_5", "name_zh": "太阳轮", "name_en": "Sun Wheel", "price": 600000000, "desc_zh": "形似方向盘", "desc_en": "Looks like a steering wheel"},
        {"id": "sx_6", "name_zh": "玉璋", "name_en": "Jade Zhang", "price": 300000000, "desc_zh": "祭祀山川礼器", "desc_en": "Ritual jade artifact"},
        {"id": "sx_7", "name_zh": "黄金权杖", "name_en": "Golden Scepter", "price": 1500000000, "desc_zh": "王权的象征", "desc_en": "Symbol of ancient power"},
        {"id": "sx_8", "name_zh": "青铜神坛", "name_en": "Bronze Altar", "price": 900000000, "desc_zh": "复杂祭祀场景", "desc_en": "Complex ritual scene"},
        # 简化后续数据以节省空间，实际项目请补全...
        {"id": "sx_9", "name_zh": "戴金面罩铜人", "name_en": "Gold-Masked Head", "price": 500000000, "desc_zh": "金光闪闪祭司", "desc_en": "Shining priest"},
        {"id": "sx_10", "name_zh": "青铜鸟头", "name_en": "Bronze Bird Head", "price": 150000000, "desc_zh": "神鸟图腾", "desc_en": "Divine bird totem"},
        {"id": "sx_11", "name_zh": "陶猪", "name_en": "Pottery Pig", "price": 50000000, "desc_zh": "愤怒小鸟同款", "desc_en": "Looks like Angry Birds"},
        {"id": "sx_12", "name_zh": "青铜大鸟", "name_en": "Bronze Big Bird", "price": 400000000, "desc_zh": "体型巨大神兽", "desc_en": "Giant mythical bird"},
        {"id": "sx_13", "name_zh": "青铜爬龙柱", "name_en": "Dragon Pillar", "price": 650000000, "desc_zh": "龙形神柱", "desc_en": "Dragon shaped pillar"},
        {"id": "sx_14", "name_zh": "人身鸟脚像", "name_en": "Bird-Man Statue", "price": 550000000, "desc_zh": "半人半鸟", "desc_en": "Half man half bird"},
        {"id": "sx_15", "name_zh": "顶尊跪坐人像", "name_en": "Kneeling Figure", "price": 1100000000, "desc_zh": "国宝级重器", "desc_en": "National treasure"},
        {"id": "sx_16", "name_zh": "青铜蛇", "name_en": "Bronze Snake", "price": 120000000, "desc_zh": "造型逼真", "desc_en": "Realistic snake"},
        {"id": "sx_17", "name_zh": "青铜鸡", "name_en": "Bronze Rooster", "price": 80000000, "desc_zh": "雄鸡一唱", "desc_en": "Crowing rooster"},
        {"id": "sx_18", "name_zh": "玉琮", "name_en": "Jade Cong", "price": 200000000, "desc_zh": "良渚文化影响", "desc_en": "Liangzhu influence"},
    ],
    "beijing": [
        {"id": "bj_1", "name_zh": "清明上河图", "name_en": "Riverside Scene at Qingming", "price": 5000000000, "desc_zh": "中华第一神品", "desc_en": "China's greatest painting"},
        {"id": "bj_2", "name_zh": "金瓯永固杯", "name_en": "Gold Cup of Eternal Stability", "price": 600000000, "desc_zh": "乾隆御用金杯", "desc_en": "Qianlong's gold cup"},
        {"id": "bj_3", "name_zh": "后母戊鼎", "name_en": "Houmuwu Ding", "price": 4000000000, "desc_zh": "青铜之王", "desc_en": "King of bronzes"},
        {"id": "bj_4", "name_zh": "千里江山图", "name_en": "Thousand Li of Rivers and Mountains", "price": 3000000000, "desc_zh": "青绿山水巅峰", "desc_en": "Blue-green landscape masterpiece"},
        # ... (此处省略部分重复数据结构，逻辑同上)
    ],
    "shanghai": [
        {"id": "sh_1", "name_zh": "大克鼎", "name_en": "Da Ke Ding", "price": 1500000000, "desc_zh": "海内三宝之一", "desc_en": "Top 3 bronze treasures"},
        {"id": "sh_2", "name_zh": "晋侯苏钟", "name_en": "Jin Hou Su Bells", "price": 800000000, "desc_zh": "铭文刻在钟表", "desc_en": "Inscriptions on bells"},
        # ...
    ],
    "xian": [
        {"id": "xa_1", "name_zh": "兽首玛瑙杯", "name_en": "Beast Head Agate Cup", "price": 2000000000, "desc_zh": "海内孤品", "desc_en": "Unique agate treasure"},
        {"id": "xa_2", "name_zh": "舞马衔杯银壶", "name_en": "Dancing Horse Silver Flask", "price": 800000000, "desc_zh": "大唐盛世缩影", "desc_en": "Symbol of Tang Dynasty"},
        # ...
    ]
}

# 兜底补充数据 (防止 KeyError)
for k, v in MUSEUM_TREASURES.items():
    if len(v) < 4: # 简单填充演示数据
        for i in range(18 - len(v)):
            v.append({"id": f"{k}_x{i}", "name_zh": "神秘藏品", "name_en": "Mystery Item", "price": 100000000, "desc_zh": "待发掘", "desc_en": "To be discovered"})

# ==========================================
# 3. 样式 & 翻译字典
# ==========================================
lang_dict = {
    'zh': {
        'title': "🏛️ 华夏国宝私有化中心", 
        'revenue': "累计拍卖总额", 
        'power': "财富购买力", 
        'unit_m': "套", 
        'apps': "✨ 更多应用",
        'status_sold': "🚫 已私有化", 
        'btn_auction': "㊙ 立即拍卖", 
        'reveal': "🕵️ 价值待揭晓", 
        'my_assets': "📜 我的私人资产清单",
        'no_assets': "暂无藏品，快去竞拍吧！", 
        'reset': "🔄 破产/重置", 
        'coffee': "☕ 请老登喝咖啡", 
        'toast_buy': "🔨 {name} 成交！",
        'unit_price': "亿", 
        'period': "时代",
        'coffee_title': " ", 
        'coffee_desc': "如果这个游戏帮到了你，欢迎支持。", 
        'coffee_amount': "请输入打赏杯数", 
        'pay_success': "收到！感谢打赏。❤️",
        'presets': [("☕ 提神", 1), ("🍗 鸡腿", 3), ("🚀 续命", 5)],
        'pay_types': ["微信支付", "支付宝", "贝宝"]
    },
    'en': {
        'title': "🏛️ National Treasure Privatization", 
        'revenue': "Total Revenue", 
        'power': "Buying Power", 
        'unit_m': "Estates", 
        'apps': "✨ More Apps",
        'status_sold': "🚫 Privatized", 
        'btn_auction': "㊙ Auction", 
        'reveal': "🕵️ Hidden Value", 
        'my_assets': "📜 My Private Collection",
        'no_assets': "No collection yet. Start bidding!", 
        'reset': "🔄 Reset Game", 
        'coffee': "☕ Buy Me Coffee", 
        'toast_buy': "🔨 {name} Sold!",
        'unit_price': "B", 
        'period': "Period",
        'coffee_title': " ", 
        'coffee_desc': "Support is appreciated.", 
        'coffee_amount': "Enter Coffee Count", 
        'pay_success': "Received! Thanks! ❤️",
        'presets': [("☕ Coffee", 1), ("🍗 Meal", 3), ("🚀 Rocket", 5)],
        'pay_types': ["WeChat", "Alipay", "PayPal"]
    }
}

st.markdown("""
<style>
    .stApp { background-color: #f5f5f7; color: #1d1d1f; }
    
    /* 顶部按钮 */
    .neal-btn { font-family: 'Inter', sans-serif; background: #fff; border: 1px solid #e5e7eb; color: #111; font-weight: 600; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; text-decoration: none !important; width: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .neal-btn:hover { background: #f9fafb; transform: translateY(-1px); }

    /* 仪表盘 */
    .dashboard { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); padding: 15px 30px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-bottom: 1px solid #e5e5e5; }
    
    /* 豪宅卡片 */
    .mansion-box { background-size: cover; border-radius: 12px; padding: 15px; min-width: 250px; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.8); position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.2); transition: transform 0.3s; }
    .mansion-box:hover { transform: scale(1.02); }
    .mansion-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.6)); z-index: 1; }
    
    /* 文物卡片 */
    .treasure-card { background: white; border-radius: 12px; transition: all 0.3s; border: 1px solid #e5e5e5; overflow: hidden; height: 100%; display: flex; flex-direction: column; text-align: center; }
    .treasure-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
    
    /* 圆形图片 */
    .t-img-box { height: 160px; width: 100%; display: flex; align-items: center; justify-content: center; background: #f8f9fa; overflow: hidden; }
    .t-img { width: 120px !important; height: 120px !important; border-radius: 50%; object-fit: cover; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: scale(1.1); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .treasure-card:hover .t-img { transform: scale(1.2) rotate(3deg); }
    
    /* 资产标签 */
    .asset-tag { display: inline-block; background: #fffbeb; color: #b45309; padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; margin: 5px; border: 1px solid #fcd34d; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    
    /* 价格显现动画 */
    @keyframes fadeInPrice { 0% { opacity: 0; transform: scale(0.5); filter: blur(5px); } 100% { opacity: 1; transform: scale(1); filter: blur(0); } }
    .price-reveal { animation: fadeInPrice 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards; display: inline-block; color: #d9534f; font-weight: 800; }
    
    /* 通用 */
    .pay-amount-display { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 800; margin: 10px 0; }
    div[data-testid="stButton"] button { width: 100% !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stats-bar { display: flex; justify-content: center; gap: 25px; margin-top: 40px; padding: 15px; background-color: white; border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); color: #6b7280; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 状态初始化
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = {} # 改为字典 {id: name}
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1

L = lang_dict[st.session_state.language]

# ==========================================
# 5. UI 顶部
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    btn_l = "English" if st.session_state.language == 'zh' else "中文"
    if st.button(btn_l, key="lang_btn"):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()
with col_more:
    st.markdown(f'<a href="https://laodeng.streamlit.app/" target="_blank" style="text-decoration:none;"><div class="neal-btn">{L["apps"]}</div></a>', unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align:center; margin-top:10px;'>{L['title']}</h2>", unsafe_allow_html=True)

# 博物馆选择
museum_sel = st.radio("Museum", list(MANSION_CONFIG.keys()), horizontal=True, label_visibility="collapsed")
if museum_sel != st.session_state.current_museum:
    st.session_state.current_museum = museum_sel
    st.rerun()

# ==========================================
# 6. 仪表盘 & 私人清单 (新增)
# ==========================================
m_cfg = MANSION_CONFIG[museum_sel]
power_val = st.session_state.total_revenue / m_cfg['price']

dashboard_placeholder = st.empty()
def render_dashboard(val):
    v_count = val / m_cfg["price"]
    # 动态获取博物馆名称翻译
    m_name_display = museum_sel if st.session_state.language == 'zh' else MUSEUM_NAME_MAP[museum_sel].capitalize() + " Museum"
    
    dashboard_placeholder.markdown(f"""
    <div class="dashboard">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:1.3rem; font-weight:800;">{m_name_display}</div>
                <div style="font-size:2rem; font-weight:900; color:#d9534f; font-family:'JetBrains Mono';">
                    ¥{val/100000000:.2f}{L['unit_price']}
                </div>
                <div style="font-size:0.8rem; color:#86868b; text-transform:uppercase; letter-spacing:1px;">{L['revenue']}</div>
            </div>
            <div class="mansion-box" style="background-image: url('{m_cfg['img']}');">
                <div class="mansion-overlay"></div>
                <div style="position:relative; z-index:2;">
                    <div style="font-size:0.75rem; opacity:0.9;">{L['power']}</div>
                    <div style="font-size:1.6rem; font-weight:900;">× {v_count:.2f} {L['unit_m']}</div>
                    <div style="font-size:0.85rem; font-weight:600;">{m_cfg[st.session_state.language]}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

render_dashboard(st.session_state.total_revenue)

# --- 新增：资产清单 ---
with st.expander(f"{L['my_assets']} ({len(st.session_state.sold_items)})", expanded=len(st.session_state.sold_items) > 0):
    if st.session_state.sold_items:
        # 生成金色标签
        tags_html = "".join([f'<span class="asset-tag">💎 {name}</span>' for name in st.session_state.sold_items.values()])
        st.markdown(f'<div style="line-height:2.5;">{tags_html}</div>', unsafe_allow_html=True)
    else:
        st.caption(L['no_assets'])

# ==========================================
# 7. 拍卖逻辑 & 展示
# ==========================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return None
    with open(image_path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode()
    return f"data:image/jpeg;base64,{b64_data}"

def auction_action(item):
    price = item['price']
    name = item.get(f'name_{st.session_state.language}', item.get('name_zh'))
    
    # 动画
    start = st.session_state.total_revenue
    for i in range(15):
        render_dashboard(start + (price/15)*(i+1))
        time.sleep(0.015)
        
    st.session_state.total_revenue += price
    st.session_state.sold_items[item['id']] = name
    st.session_state.last_sold_id = item['id']
    st.toast(L['toast_buy'].format(name=name), icon="🔨")
    time.sleep(0.3)
    st.rerun()

m_key = MUSEUM_NAME_MAP[museum_sel]
# 获取数据并处理双语回退
raw_items = MUSEUM_TREASURES.get(m_key, [])
cols = st.columns(4)

current_dir = os.path.join(BASE_IMG_ROOT, m_key)

for idx, item in enumerate(raw_items):
    with cols[idx % 4]:
        # 1. 状态判断
        is_sold = item['id'] in st.session_state.sold_items
        
        # 2. 文本处理 (自动回退到中文)
        lang = st.session_state.language
        name = item.get(f'name_{lang}', item.get('name_zh', 'Unknown'))
        desc = item.get(f'desc_{lang}', item.get('desc_zh', ''))
        
        # 3. 价格显示
        if is_sold:
            price_txt = f"¥{item['price']/100000000:.1f}{L['unit_price']}"
            p_class = "price-reveal" if item['id'] == st.session_state.last_sold_id else "sold-price"
        else:
            price_txt = L['reveal']
            p_class = "unsold-price"
            
        # 4. 图片加载
        img_names = [f"{idx+1}.jpeg", f"[] ({idx+1}).jpeg", f"{idx+1}.jpg"]
        b64_str = None
        for iname in img_names:
            p = os.path.join(current_dir, iname)
            b64_str = get_base64_image(p)
            if b64_str: break
        
        img_src = b64_str if b64_str else f"https://picsum.photos/seed/{item['id']}/300/300"

        # 5. 渲染卡片
        st.markdown(f"""
        <div class="treasure-card">
            <div class="t-img-box">
                <img src="{img_src}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
            </div>
            <div style="padding:12px; flex-grow:1; display:flex; flex-direction:column; text-align:center;">
                <div style="font-weight:800; margin-bottom:4px; font-size:0.95rem;">{name}</div>
                <div style="font-size:0.75rem; color:#888; margin-bottom:8px; line-height:1.3;">{desc}</div>
                <div style="margin-top:auto; font-family:'JetBrains Mono'; font-weight:700;" class="{p_class}">
                    {price_txt}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 6. 按钮
        if is_sold:
            st.button(L['status_sold'], key=item['id'], disabled=True)
        else:
            if st.button(L['btn_auction'], key=item['id'], type="primary"):
                auction_action(item)

# ==========================================
# 8. 底部功能
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
        cnt = st.number_input(L['coffee_amount'], 1, 100, step=1, key='coffee_num')
        
        # 支付 Tab
        tabs = st.tabs(L['pay_types'])
        cny = cnt * 10
        usd = cnt * 2
        
        def show_pay(idx, currency):
            st.markdown(f"<h2 style='text-align:center; color:#d9534f;'>{currency}</h2>", unsafe_allow_html=True)
            # 演示用二维码
            qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Pay_{currency}"
            st.image(qr, width=150)
            
        with tabs[0]: show_pay(0, f"¥{cny}")
        with tabs[1]: show_pay(1, f"¥{cny}")
        with tabs[2]: show_pay(2, f"${usd}")
        
        if st.button("🎉 " + L['pay_success'].split('!')[0], type="primary"):
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

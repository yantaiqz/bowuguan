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
    page_title="Auction Game | 拍卖大师",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 样式合并 (基础样式 + 游戏样式 + 咖啡加强版)
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {display: none;}
    .stApp { background-color: #FFFFFF !important; }

    /* --- 游戏专用样式 --- */
    .game-container {
        max-width: 800px;
        margin: 0 auto;
        text-align: center;
        padding: 20px;
    }
    .item-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 10px;
    }
    .item-image {
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        max-height: 400px;
        object-fit: cover;
    }
    .score-display {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 20px;
        font-weight: 600;
    }
    .price-reveal {
        font-size: 3rem;
        font-weight: 900;
        color: #2AAD67;
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- 右上角按钮 --- */
    .neal-btn {
        font-family: 'Inter', sans-serif; background: #fff;
        border: 1px solid #e5e7eb; color: #111; font-weight: 600;
        padding: 8px 16px; border-radius: 8px; cursor: pointer;
        transition: all 0.2s; display: inline-flex; align-items: center;
        justify-content: center; text-decoration: none !important;
        width: 100%;
    }
    .neal-btn:hover { background: #f9fafb; transform: translateY(-1px); }
    .neal-btn-link { text-decoration: none; width: 100%; display: block; }

    /* --- 咖啡打赏 & 统计模块 (保留原逻辑) --- */
    .metric-container { display: flex; justify-content: center; gap: 20px; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef; }
    .metric-box { text-align: center; }
    .pay-amount-display { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 800; margin: 10px 0; color: #d9534f;}
    .pay-label { font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .color-wechat { color: #2AAD67; }
    .color-alipay { color: #1677ff; }
    .color-paypal { color: #003087; }
    
    /* 按钮微调 */
    div[data-testid="stButton"] button { border-radius: 8px; }
    [data-testid="button-lang_switch"] { position: fixed; top: 20px; right: 120px; z-index: 999; width: 80px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 游戏数据 (模拟数据)
# ==========================================
GAME_ITEMS = [
    {"id": 1, "name": "Banksy's 'Girl with Balloon'", "price": 25400000, "img": "https://upload.wikimedia.org/wikipedia/en/0/06/GirlWithBalloon.jpg"},
    {"id": 2, "name": "Action Comics #1 (Superman)", "price": 3250000, "img": "https://upload.wikimedia.org/wikipedia/en/5/5a/Action_Comics_1.jpg"},
    {"id": 3, "name": "Steve Jobs' Old Birkenstocks", "price": 218750, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Birkenstock_Boston_suede.jpg/640px-Birkenstock_Boston_suede.jpg"},
    {"id": 4, "name": "Solid Gold LEGO Brick", "price": 15000, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Lego_Brick_4x2.svg/640px-Lego_Brick_4x2.svg.png"},
    {"id": 5, "name": "Michael Jordan's 'Last Dance' Jersey", "price": 10100000, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Jordan_lipofsky.jpg/437px-Jordan_lipofsky.jpg"},
]

# ==========================================
# 4. 状态初始化
# ==========================================
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()
    st.session_state.access_status = 'free'
    st.session_state.unlock_time = None
if 'language' not in st.session_state:
    st.session_state.language = 'zh'
if 'coffee_num' not in st.session_state:
    st.session_state.coffee_num = 1
if 'visitor_id' not in st.session_state:
    st.session_state["visitor_id"] = str(uuid.uuid4())

# --- 游戏状态 ---
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
if 'round_index' not in st.session_state:
    st.session_state.round_index = 0
if 'round_state' not in st.session_state:
    st.session_state.round_state = 'guessing' # guessing, result, end
if 'shuffled_items' not in st.session_state:
    items = GAME_ITEMS.copy()
    random.shuffle(items)
    st.session_state.shuffled_items = items

# ==========================================
# 5. 常量与文本配置
# ==========================================
FREE_PERIOD_SECONDS = 600 # 增加到10分钟以便体验游戏
ACCESS_DURATION_HOURS = 24
UNLOCK_CODE = "vip888"
DB_FILE = os.path.join(os.path.expanduser("~/"), "visit_stats.db")

lang_texts = {
    'zh': {
        'coffee_desc': '如果这个游戏让你开心了，欢迎支持老登的创作。',
        'coffee_btn': "☕ 请开发者喝咖啡",
        'coffee_title': " ",
        'coffee_amount': "请输入打赏杯数",
        'pay_wechat': '微信支付', 'pay_alipay': '支付宝', 'pay_paypal': '贝宝',
        'pay_success': "收到！感谢打赏。❤️",
        'game_title': '拍卖价格猜猜猜',
        'guess_btn': '出价！',
        'next_btn': '下一个',
        'result_perfect': '太神了！完美出价！',
        'result_good': '很接近了！',
        'result_bad': '差得有点远...',
        'actual_price': '实际成交价',
        'your_guess': '你的估价',
        'score': '总分',
        'game_over': '游戏结束',
        'restart': '再玩一次'
    },
    'en': {
        'coffee_desc': 'If you enjoyed this game, support is appreciated.',
        'coffee_btn': "☕ Buy me a coffee",
        'coffee_title': " ",
        'coffee_amount': "Enter Coffee Count",
        'pay_wechat': 'WeChat', 'pay_alipay': 'Alipay', 'pay_paypal': 'PayPal',
        'pay_success': "Received! Thanks! ❤️",
        'game_title': 'The Auction Game',
        'guess_btn': 'Make Bid',
        'next_btn': 'Next Item',
        'result_perfect': 'Perfect Bid!',
        'result_good': 'Pretty Close!',
        'result_bad': 'Way off...',
        'actual_price': 'Sold For',
        'your_guess': 'Your Bid',
        'score': 'Score',
        'game_over': 'Game Over',
        'restart': 'Play Again'
    }
}
current_text = lang_texts[st.session_state.language]

# ==========================================
# 6. 右上角功能区
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    l_btn = "En" if st.session_state.language == 'zh' else "中"
    if st.button(l_btn, key="lang_switch"):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()
with col_more:
    st.markdown("""<a href="#" class="neal-btn-link"><button class="neal-btn">✨ 更多应用</button></a>""", unsafe_allow_html=True)

# ==========================================
# 7. 权限校验逻辑
# ==========================================
current_time = datetime.datetime.now()
access_granted = False

if st.session_state.access_status == 'free':
    time_elapsed = (current_time - st.session_state.start_time).total_seconds()
    if time_elapsed < FREE_PERIOD_SECONDS:
        access_granted = True
        st.info(f"⏳ **免费试用中... 剩余 {int(FREE_PERIOD_SECONDS - time_elapsed)} 秒。**")
    else:
        st.session_state.access_status = 'locked'
        st.rerun()
elif st.session_state.access_status == 'unlocked':
    unlock_expiry = st.session_state.unlock_time + datetime.timedelta(hours=ACCESS_DURATION_HOURS)
    if current_time < unlock_expiry:
        access_granted = True
    else:
        st.session_state.access_status = 'locked'
        st.rerun()

if not access_granted:
    st.error("🔒 **试用结束，请输入解锁码继续游戏**")
    st.info(f"解锁码提示：{UNLOCK_CODE}")
    with st.form("lock_form"):
        if st.form_submit_button("解锁") and st.text_input("Code", type="password") == UNLOCK_CODE:
            st.session_state.access_status, st.session_state.unlock_time = 'unlocked', datetime.datetime.now()
            st.rerun()
    st.stop()

# ==========================================
# 8. 游戏核心逻辑 (内容区)
# ==========================================
st.divider()

def calculate_score(guess, actual):
    # 简单的评分逻辑：误差越小分越高
    diff_percent = abs(guess - actual) / actual
    if diff_percent < 0.05: return 1000
    if diff_percent > 1: return 0
    return int((1 - diff_percent) * 1000)

# 游戏容器
with st.container():
    # 标题栏
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 5px;'>{current_text['game_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-display' style='text-align:center;'>{current_text['score']}: <span style='color:#2AAD67'>{st.session_state.game_score}</span></div>", unsafe_allow_html=True)

    # 检查是否游戏结束
    if st.session_state.round_index >= len(st.session_state.shuffled_items):
        st.markdown(f"<h2 style='text-align:center;'>🎉 {current_text['game_over']}!</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>Final Score: {st.session_state.game_score}</h3>", unsafe_allow_html=True)
        if st.button(current_text['restart'], use_container_width=True, type="primary"):
            st.session_state.round_index = 0
            st.session_state.game_score = 0
            st.session_state.round_state = 'guessing'
            random.shuffle(st.session_state.shuffled_items)
            st.rerun()
    else:
        # 获取当前物品
        current_item = st.session_state.shuffled_items[st.session_state.round_index]

        # 布局：左图右操作，或上下结构
        c_game = st.container()
        
        with c_game:
            # 图片显示
            st.markdown(f"""
            <div style="display:flex; justify-content:center;">
                <img src="{current_item['img']}" class="item-image" style="max-height: 300px; max-width: 100%;">
            </div>
            <div class="item-title" style="text-align:center; font-size: 1.5rem;">{current_item['name']}</div>
            """, unsafe_allow_html=True)

            st.write("") # Spacer

            # 猜测阶段
            if st.session_state.round_state == 'guessing':
                # 使用 Number Input 结合 Slider 增强体验
                col_input, col_space = st.columns([1, 0.01]) # Centering trick
                
                guess_val = st.number_input(
                    f"{current_text['your_guess']} ($)", 
                    min_value=0, 
                    value=1000, 
                    step=100,
                    format="%d"
                )
                
                if st.button(current_text['guess_btn'], type="primary", use_container_width=True):
                    st.session_state.last_guess = guess_val
                    st.session_state.round_score = calculate_score(guess_val, current_item['price'])
                    st.session_state.game_score += st.session_state.round_score
                    st.session_state.round_state = 'result'
                    st.rerun()

            # 结果阶段
            elif st.session_state.round_state == 'result':
                actual = current_item['price']
                guess = st.session_state.last_guess
                score = st.session_state.round_score
                
                # 评价文案
                if score >= 900: comment = current_text['result_perfect']
                elif score >= 500: comment = current_text['result_good']
                else: comment = current_text['result_bad']

                st.markdown(f"""
                <div style="text-align: center; background: #f0fdf4; padding: 20px; border-radius: 12px; border: 1px solid #bbf7d0;">
                    <div style="color: #666; font-size: 0.9rem;">{current_text['actual_price']}</div>
                    <div class="price-reveal">${actual:,}</div>
                    <div style="margin-top: 10px; color: #444;">{current_text['your_guess']}: ${guess:,}</div>
                    <div style="margin-top: 15px; font-weight: bold; font-size: 1.2rem; color: #d97706;">+ {score} pts</div>
                    <div style="color: #888;">{comment}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button(current_text['next_btn'], type="primary", use_container_width=True):
                    st.session_state.round_index += 1
                    st.session_state.round_state = 'guessing'
                    st.rerun()

# ==========================================
# 9. 咖啡打赏与统计 (融合原逻辑)
# ==========================================

def get_txt(key): return lang_texts[st.session_state.language][key]

st.markdown("<br><br>", unsafe_allow_html=True)    
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    @st.dialog(" " + get_txt('coffee_title'), width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="text-align:center; color:#666; margin-bottom:15px;">{get_txt('coffee_desc')}</div>""", unsafe_allow_html=True)
        
        presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
        def set_val(n): st.session_state.coffee_num = n
        
        cols = st.columns(3, gap="small")
        for i, (icon, num) in enumerate(presets):
            with cols[i]:
                if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}"): set_val(num)
        
        st.write("")
        col_amount, col_total = st.columns([1, 1], gap="small")
        with col_amount: 
            cnt = st.number_input(get_txt('coffee_amount'), 1, 100, step=1, key='coffee_num')
        
        cny_total = cnt * 10
        usd_total = cnt * 2

        def render_pay_tab(title, amount_str, color_class, img_path, qr_data_suffix, link_url=None):
            with st.container(border=True):
                st.markdown(f"""
                    <div style="text-align: center; padding-bottom: 10px;">
                        <div class="pay-label {color_class}">{title}</div>
                        <div class="pay-amount-display {color_class}">{amount_str}</div>
                    </div>
                """, unsafe_allow_html=True)
                c_img_1, c_img_2, c_img_3 = st.columns([1, 4, 1])
                with c_img_2:
                    qr_data = f"Donate_{cny_total}_{qr_data_suffix}"
                    if link_url: qr_data = link_url
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={qr_data}", use_container_width=True)
                
                if link_url:
                    st.write("")
                    st.link_button(f"👉 Pay {amount_str}", link_url, type="primary", use_container_width=True)
                else:
                    st.markdown(f"""<div style="text-align: center; padding-top: 10px; font-size:0.8rem; color:#999;">请使用手机扫描上方二维码</div>""", unsafe_allow_html=True)
                    
        st.write("")
        t1, t2, t3 = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay'), get_txt('pay_paypal')])
        with t1: render_pay_tab("WeChat Pay", f"¥{cny_total}", "color-wechat", "wechat_pay.jpg", "WeChat")
        with t2: render_pay_tab("Alipay", f"¥{cny_total}", "color-alipay", "ali_pay.jpg", "Alipay")
        with t3: render_pay_tab("PayPal", f"${usd_total}", "color-paypal", "paypal.png", "PayPal", "https://paypal.me/yourid")
        
        st.write("")
        if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            time.sleep(1.5)
            st.rerun()

    if st.button(get_txt('coffee_btn'), use_container_width=True):
        show_coffee_window()

# ==========================================
# 10. 数据库统计逻辑
# ==========================================
def track_stats():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        today = datetime.datetime.utcnow().date().isoformat()
        vid = st.session_state["visitor_id"]
        
        if "has_counted" not in st.session_state:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (vid, today))
            conn.commit()
            st.session_state["has_counted"] = True
        
        t_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        a_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        conn.close()
        return t_uv, a_uv
    except:
        return 0, 0

today_uv, total_uv = track_stats()

st.markdown(f"""
<div style="display: flex; justify-content: center; gap: 25px; margin-top: 40px; padding: 15px; color: #999; font-size: 0.8rem;">
    <div>今日访客: <b>{today_uv}</b></div>
    <div>历史访客: <b>{total_uv}</b></div>
</div>
""", unsafe_allow_html=True)

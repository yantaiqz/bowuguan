import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import os

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------- 核心修复：图片路径配置 -------------
# 1. 定义项目根目录（自动获取当前脚本所在目录）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 2. 定义图片存储目录（必须在项目内，建议创建：项目根目录/images/nanjing/）
# 请确保你的图片放在：项目文件夹/images/nanjing/ 下，并重命名为 1.jpeg ~ 18.jpeg（去掉特殊字符）
IMG_DIR = os.path.join(PROJECT_ROOT, "img", "nanjing")
# 3. 确保目录存在（自动创建）
os.makedirs(IMG_DIR, exist_ok=True)

# ==========================================
# 2. 核心数据：五大博物馆 (完整版 - 每个馆18件)
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
    "三星堆博物馆": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/400/300"},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/400/300"},
        {"id": "sx_3", "name": "金面具", "period": "商代", "desc": "半张黄金脸", "price": 800000000, "img": "https://picsum.photos/seed/sx3/400/300"},
        {"id": "sx_4", "name": "青铜纵目面具", "period": "商代", "desc": "千里眼顺风耳", "price": 1200000000, "img": "https://picsum.photos/seed/sx4/400/300"},
        {"id": "sx_5", "name": "太阳轮", "period": "商代", "desc": "形似方向盘", "price": 600000000, "img": "https://picsum.photos/seed/sx5/400/300"},
        {"id": "sx_6", "name": "玉璋", "period": "商代", "desc": "祭祀山川礼器", "price": 300000000, "img": "https://picsum.photos/seed/sx6/400/300"},
        {"id": "sx_7", "name": "黄金权杖", "period": "商代", "desc": "王权的象征", "price": 1500000000, "img": "https://picsum.photos/seed/sx7/400/300"},
        {"id": "sx_8", "name": "青铜神坛", "period": "商代", "desc": "复杂祭祀场景", "price": 900000000, "img": "https://picsum.photos/seed/sx8/400/300"},
        {"id": "sx_9", "name": "戴金面罩铜人", "period": "商代", "desc": "金光闪闪祭司", "price": 500000000, "img": "https://picsum.photos/seed/sx9/400/300"},
        {"id": "sx_10", "name": "青铜鸟头", "period": "商代", "desc": "神鸟图腾", "price": 150000000, "img": "https://picsum.photos/seed/sx10/400/300"},
        {"id": "sx_11", "name": "陶猪", "period": "商代", "desc": "愤怒小鸟同款", "price": 50000000, "img": "https://picsum.photos/seed/sx11/400/300"},
        {"id": "sx_12", "name": "青铜大鸟", "period": "商代", "desc": "体型巨大神兽", "price": 400000000, "img": "https://picsum.photos/seed/sx12/400/300"},
        {"id": "sx_13", "name": "青铜爬龙柱", "period": "商代", "desc": "龙形神柱", "price": 650000000, "img": "https://picsum.photos/seed/sx13/400/300"},
        {"id": "sx_14", "name": "人身鸟脚像", "period": "商代", "desc": "半人半鸟", "price": 550000000, "img": "https://picsum.photos/seed/sx14/400/300"},
        {"id": "sx_15", "name": "顶尊跪坐人像", "period": "商代", "desc": "国宝级重器", "price": 1100000000, "img": "https://picsum.photos/seed/sx15/400/300"},
        {"id": "sx_16", "name": "青铜蛇", "period": "商代", "desc": "造型逼真", "price": 120000000, "img": "https://picsum.photos/seed/sx16/400/300"},
        {"id": "sx_17", "name": "青铜鸡", "period": "商代", "desc": "雄鸡一唱", "price": 80000000, "img": "https://picsum.photos/seed/sx17/400/300"},
        {"id": "sx_18", "name": "玉琮", "period": "商代", "desc": "良渚文化影响", "price": 200000000, "img": "https://picsum.photos/seed/sx18/400/300"},
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
        {"id": "bj_9", "name": "击鼓说唱俑", "period": "东汉", "desc": "汉代幽默感", "price": 300000000, "img": "https://picsum.photos/seed/bj9/400/300"},
        {"id": "bj_10", "name": "人面鱼纹盆", "period": "仰韶", "desc": "史前文明微笑", "price": 250000000, "img": "https://picsum.photos/seed/bj10/400/300"},
        {"id": "bj_11", "name": "大盂鼎", "period": "西周", "desc": "铭文极其珍贵", "price": 1800000000, "img": "https://picsum.photos/seed/bj11/400/300"},
        {"id": "bj_12", "name": "虢季子白盘", "period": "西周", "desc": "晚清出土重器", "price": 1600000000, "img": "https://picsum.photos/seed/bj12/400/300"},
        {"id": "bj_13", "name": "霁蓝白龙梅瓶", "period": "元代", "desc": "元代顶级瓷器", "price": 800000000, "img": "https://picsum.photos/seed/bj13/400/300"},
        {"id": "bj_14", "name": "郎世宁百骏图", "period": "清代", "desc": "中西合璧", "price": 600000000, "img": "https://picsum.photos/seed/bj14/400/300"},
        {"id": "bj_15", "name": "五牛图", "period": "唐代", "desc": "韩滉传世孤本", "price": 900000000, "img": "https://picsum.photos/seed/bj15/400/300"},
        {"id": "bj_16", "name": "步辇图", "period": "唐代", "desc": "阎立本绘", "price": 1100000000, "img": "https://picsum.photos/seed/bj16/400/300"},
        {"id": "bj_17", "name": "利簋", "period": "西周", "desc": "记录武王伐纣", "price": 700000000, "img": "https://picsum.photos/seed/bj17/400/300"},
        {"id": "bj_18", "name": "鹳鱼石斧陶缸", "period": "仰韶", "desc": "绘画史第一页", "price": 400000000, "img": "https://picsum.photos/seed/bj18/400/300"},
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
        {"id": "sh_9", "name": "子仲姜盘", "period": "春秋", "desc": "盘内动物可旋转", "price": 500000000, "img": "https://picsum.photos/seed/sh9/400/300"},
        {"id": "sh_10", "name": "牺尊", "period": "春秋", "desc": "极具神韵的牛形", "price": 350000000, "img": "https://picsum.photos/seed/sh10/400/300"},
        {"id": "sh_11", "name": "商鞅方升", "period": "战国", "desc": "统一度量衡", "price": 1500000000, "img": "https://picsum.photos/seed/sh11/400/300"},
        {"id": "sh_12", "name": "曹全碑", "period": "东汉", "desc": "汉隶书法典范", "price": 450000000, "img": "https://picsum.photos/seed/sh12/400/300"},
        {"id": "sh_13", "name": "哥窑五足洗", "period": "南宋", "desc": "金丝铁线", "price": 300000000, "img": "https://picsum.photos/seed/sh13/400/300"},
        {"id": "sh_14", "name": "透雕神兽玉璧", "period": "西汉", "desc": "汉代玉器巅峰", "price": 200000000, "img": "https://picsum.photos/seed/sh14/400/300"},
        {"id": "sh_15", "name": "剔红花卉纹盘", "period": "元代", "desc": "张成造，漆器孤品", "price": 120000000, "img": "https://picsum.photos/seed/sh15/400/300"},
        {"id": "sh_16", "name": "苏轼舣舟亭图", "period": "清代", "desc": "乾隆御览之宝", "price": 250000000, "img": "https://picsum.photos/seed/sh16/400/300"},
        {"id": "sh_17", "name": "青花牡丹纹罐", "period": "元代", "desc": "元青花大器", "price": 550000000, "img": "https://picsum.photos/seed/sh17/400/300"},
        {"id": "sh_18", "name": "缂丝莲塘乳鸭", "period": "南宋", "desc": "朱克柔真迹", "price": 800000000, "img": "https://picsum.photos/seed/sh18/400/300"},
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
        {"id": "xa_9", "name": "鸳鸯纹金碗", "period": "唐代", "desc": "金银器巅峰", "price": 600000000, "img": "https://picsum.photos/seed/xa9/400/300"},
        {"id": "xa_10", "name": "三彩骆驼俑", "period": "唐代", "desc": "丝路乐队", "price": 450000000, "img": "https://picsum.photos/seed/xa10/400/300"},
        {"id": "xa_11", "name": "阙楼仪仗图", "period": "唐代", "desc": "懿德太子墓", "price": 1500000000, "img": "https://picsum.photos/seed/xa11/400/300"},
        {"id": "xa_12", "name": "鎏金铜龙", "period": "唐代", "desc": "气势磅礴", "price": 350000000, "img": "https://picsum.photos/seed/xa12/400/300"},
        {"id": "xa_13", "name": "杜虎符", "period": "战国", "desc": "调兵遣将信物", "price": 500000000, "img": "https://picsum.photos/seed/xa13/400/300"},
        {"id": "xa_14", "name": "何尊", "period": "西周", "desc": "最早出现'中国'", "price": 2500000000, "img": "https://picsum.photos/seed/xa14/400/300"},
        {"id": "xa_15", "name": "多友鼎", "period": "西周", "desc": "铭文记录战争", "price": 800000000, "img": "https://picsum.photos/seed/xa15/400/300"},
        {"id": "xa_16", "name": "日己觥", "period": "西周", "desc": "造型奇特酒器", "price": 400000000, "img": "https://picsum.photos/seed/xa16/400/300"},
        {"id": "xa_17", "name": "雁鱼铜灯", "period": "西汉", "desc": "环保美学结合", "price": 550000000, "img": "https://picsum.photos/seed/xa17/400/300"},
        {"id": "xa_18", "name": "金怪兽", "period": "战国", "desc": "匈奴文化代表", "price": 200000000, "img": "https://picsum.photos/seed/xa18/400/300"},
    ]
}


import base64

def get_base64_image(image_path):
    """将本地图片转换为 Base64 字符串，供 HTML 使用"""
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode()
    # 假设是 jpeg 格式，如果是 png 请改为 image/png
    return f"data:image/jpeg;base64,{b64_data}"

# ==========================================
# 图片加载逻辑修正
# ==========================================

# 建议手动将图片重命名为 1.jpeg, 2.jpeg ... 18.jpeg 放在 img/nanjing 目录下
for idx, treasure in enumerate(MUSEUM_TREASURES["南京博物院"], start=1):
    # 1. 尝试匹配简单文件名：1.jpeg
    img_name_simple = f"{idx}.jpeg"
    # 2. 尝试匹配你原本的特殊文件名：[] (1).jpeg
    img_name_complex = f"[] ({idx}).jpeg"
    
    path_simple = os.path.join(IMG_DIR, img_name_simple)
    path_complex = os.path.join(IMG_DIR, img_name_complex)

    # 优先使用简单文件名，其次尝试特殊文件名
    final_path = path_simple if os.path.exists(path_simple) else path_complex

    # 获取 Base64 字符串
    b64_str = get_base64_image(final_path)

    if b64_str:
        treasure["img"] = b64_str  # 成功获取本地图片
    else:
        # 如果本地没图，使用在线占位图作为保底，防止页面坏掉
        treasure["img"] = f"https://picsum.photos/seed/nj{idx}/400/300"

# ==========================================
# 3. 样式 (CSS 动画核心)
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #f5f5f7 !important; color: #1d1d1f; padding-top: 0 !important; }
    .block-container { padding-top: 1rem !important; max-width: 1400px !important; }

    /* --- 仪表盘 (Sticky) --- */
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

    /* --- 核心修改：圆形图片 --- */
    .t-img { 
        width: 140px !important;       /* 强制固定宽度 */
        height: 140px !important;      /* 强制固定高度 */
        object-fit: cover;             /* 裁剪防止变形 */
        border-radius: 50%;            /* 变圆 */
        border: 4px solid white;       /* 增加白色边框提升质感 */
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* 添加阴影 */
        transition: all 0.3s ease; 
    }
    
    .t-content { padding: 12px !important; flex-grow: 1; display: flex; flex-direction: column; }
    .t-title { font-size: 1rem; font-weight: 800; color: #111; margin-bottom: 4px !important; }
    .t-period { font-size: 0.75rem; color: #86868b; background: #f5f5f7; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 6px !important; width: fit-content; }
    .t-desc { font-size: 0.8rem; color: #555; line-height: 1.4; margin-bottom: 8px !important; flex-grow: 1; }
    
    /* --- 价格样式 --- */
    .t-price { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 1rem; 
        font-weight: 700; 
        margin: 5px 0 !important; 
    }
    .sold-price { color: #d9534f; }
    .unsold-price { color: #9ca3af; font-style: italic; font-size: 0.9rem; letter-spacing: 1px; }

    /* --- 关键动画：成交后价签显现 --- */
    @keyframes fadeInPrice {
        0% { 
            opacity: 0; 
            transform: scale(0.8) translateY(10px); 
            color: #28a745; 
            filter: blur(5px);
        }
        50% {
            opacity: 0.6;
            transform: scale(1.1);
        }
        100% { 
            opacity: 1; 
            transform: scale(1) translateY(0); 
            color: #d9534f; 
            filter: blur(0);
        }
    }

    .price-reveal {
        animation: fadeInPrice 1.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        display: inline-block;
    }

    /* 按钮覆盖 */
    div[data-testid="stButton"] button { width: 100% !important; border-radius: 6px !important; font-weight: 600 !important; }
    
    /* 咖啡统计 */
    .stats-bar { display: flex; justify-content: center; gap: 25px; margin-top: 40px; padding: 15px 25px; background-color: white; border-radius: 50px; border: 1px solid #eee; color: #6b7280; font-size: 0.85rem; width: fit-content; margin-left: auto; margin-right: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 状态初始化
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1

# 防止旧缓存错误
if st.session_state.current_museum not in MANSION_CONFIG:
    st.session_state.current_museum = list(MANSION_CONFIG.keys())[0]

# 语言包
lang_texts = {
    'zh': {'coffee_desc': '如果这个游戏帮到了你，欢迎支持。', 'coffee_btn': "☕ 请开发者喝咖啡", 'coffee_title': " ", 'coffee_amount': "请输入打赏杯数", 'pay_success': "收到！感谢打赏。❤️"},
    'en': {'coffee_desc': 'Support is appreciated.', 'coffee_btn': "☕ Buy me a coffee", 'coffee_title': " ", 'coffee_amount': "Enter Coffee Count", 'pay_success': "Received! Thanks! ❤️"}
}
current_text = lang_texts[st.session_state.language]

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

dashboard_placeholder = st.empty()

def render_dashboard(current_revenue_display):
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

# 初始渲染
render_dashboard(st.session_state.total_revenue)

def format_price(price):
    if price >= 100000000: return f"{price/100000000:.1f}亿"
    elif price >= 10000: return f"{price/10000:.0f}万"
    return str(price)

def auction_animation(item_price, item_name, item_id):
    start_revenue = st.session_state.total_revenue
    target_revenue = start_revenue + item_price
    steps = 20
    step_val = item_price / steps
    
    msg = st.toast(f"🔨 正在拍卖 {item_name}...", icon="⏳")
    
    for i in range(steps):
        current_step_val = start_revenue + (step_val * (i + 1))
        render_dashboard(current_step_val)
        time.sleep(0.015)
        
    st.session_state.total_revenue = target_revenue
    st.session_state.sold_items.add(item_id)
    st.session_state.last_sold_id = item_id 
    
    msg.toast(f"✅ 成交！入账 ¥{format_price(item_price)}", icon="💰")
    time.sleep(0.5)
    st.rerun()

# ==========================================
# 7. 商品展示区 (修改：隐藏未拍卖价格)
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
            
            # --- 关键修改：显示逻辑 ---
            if is_sold:
                # 已卖出：显示真实价格
                display_price = f"¥{format_price(item['price'])}"
                price_class = "t-price sold-price"
                # 如果是刚刚卖出的，添加渐显动画
                if item_id == st.session_state.get('last_sold_id'):
                    price_class += " price-reveal"
            else:
                # 未卖出：隐藏价格，显示占位符
                display_price = "🕵️ 价值待揭晓"
                price_class = "t-price unsold-price"
            
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
                    <div class="{price_class}">{display_price}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_sold:
                st.button("🚫 已私有化", key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                if st.button("㊙ 立即拍卖", key=f"btn_{item_id}", type="primary", use_container_width=True):
                    auction_animation(item['price'], item['name'], item_id)

# ==========================================
# 8. 底部功能
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    if st.button("🔄 破产/重置", type="secondary", use_container_width=True):
        st.session_state.sold_items = set()
        st.session_state.total_revenue = 0
        st.session_state.last_sold_id = None
        st.rerun()

with c2:
    @st.dialog(" " + current_text['coffee_title'], width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="text-align:center; color:#666; margin-bottom:15px;">{current_text['coffee_desc']}</div>""", unsafe_allow_html=True)
        col_amount, col_qr = st.columns([1, 1], gap="small")
        with col_amount: 
            cnt = st.number_input(current_text['coffee_amount'], 1, 100, step=1, key='coffee_num_input')
        cny_total = cnt * 10
        with st.container(border=True):
            st.markdown(f"""<div style="text-align:center; font-size:1.5rem; font-weight:800; color:#d9534f;">¥{cny_total}</div>""", unsafe_allow_html=True)
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Donate_{cny_total}", use_container_width=True)
        if st.button("🎉 " + current_text['pay_success'].split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            time.sleep(1)
            st.rerun()

    if st.button(current_text['coffee_btn'], use_container_width=True):
        show_coffee_window()

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

st.markdown(f"""
<div class="stats-bar">
    <div style="text-align: center;"><div>今日 UV</div><div style="font-weight:700; color:#111;">{today_uv}</div></div>
    <div style="border-left:1px solid #eee; padding-left:25px; text-align: center;"><div>历史 UV</div><div style="font-weight:700; color:#111;">{total_uv}</div></div>
</div>
""", unsafe_allow_html=True)

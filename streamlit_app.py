import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import base64

# ==========================================
# 1. 全局配置 & 路径修复（优化：更简洁的路径处理）
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------- 修复：路径兼容 & 动态创建目录 -------------
try:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except:
    PROJECT_ROOT = os.getcwd()
BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
MANSION_IMG_ROOT = os.path.join(BASE_IMG_ROOT, "mansion")  # 明确别墅图片目录
os.makedirs(BASE_IMG_ROOT, exist_ok=True)
os.makedirs(MANSION_IMG_ROOT, exist_ok=True)  # 确保mansion目录存在

# 定义博物馆名称映射
MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}
MUSEUM_NAME_MAP_REVERSE = {v: k for k, v in MUSEUM_NAME_MAP.items()}

# 动态创建所有博物馆的图片目录
for museum_pinyin in MUSEUM_NAME_MAP.values():
    museum_img_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    os.makedirs(museum_img_dir, exist_ok=True)

# ==========================================
# 2. 核心数据（优化：图片路径容错、数据格式统一）
# ==========================================
MANSION_CONFIG = {
    "南京博物院": {
        "mansion_name": "颐和路民国别墅", 
        "price": 100000000, 
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "1.jpeg")  # 绝对路径更稳定
    },
    "三星堆博物馆": {
        "mansion_name": "成都麓山国际豪宅", 
        "price": 50000000, 
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "5.jpeg")
    },
    "中国国家博物馆": {
        "mansion_name": "什刹海四合院", 
        "price": 150000000, 
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "2.jpeg")
    },
    "上海博物馆": {
        "mansion_name": "愚园路老洋房", 
        "price": 200000000, 
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "3.jpeg")
    },
    "陕西历史博物馆": {
        "mansion_name": "曲江池畔大平层", 
        "price": 3000000, 
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "4.jpeg")
    }
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
        {"id": "nj_14", "name": "徐渭《杂花图》", "period": "明代", "desc": "大写意花鸟巅峰", "price": 350000000, "img": ""},
        {"id": "nj_15", "name": "沈寿《耶稣像》", "period": "清代", "desc": "苏绣艺术的巅峰之作", "price": 180000000, "img": ""},
        {"id": "nj_16", "name": "芙蓉石蟠螭炉", "period": "清乾隆", "desc": "乾隆御用粉嫩玉石", "price": 130000000, "img": ""},
        {"id": "nj_17", "name": "人面兽面玉琮", "period": "良渚", "desc": "微雕工艺神作", "price": 150000000, "img": ""},
        {"id": "nj_18", "name": "青瓷釉下彩壶", "period": "唐代", "desc": "改写陶瓷史的孤品", "price": 110000000, "img": ""},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/300/300"},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/300/300"},
        {"id": "sx_3", "name": "金面具", "period": "商代", "desc": "半张黄金脸", "price": 800000000, "img": "https://picsum.photos/seed/sx3/300/300"},
        {"id": "sx_4", "name": "青铜纵目面具", "period": "商代", "desc": "千里眼顺风耳", "price": 1200000000, "img": "https://picsum.photos/seed/sx4/300/300"},
        {"id": "sx_5", "name": "太阳轮", "period": "商代", "desc": "形似方向盘", "price": 600000000, "img": "https://picsum.photos/seed/sx5/300/300"},
        {"id": "sx_6", "name": "玉璋", "period": "商代", "desc": "祭祀山川礼器", "price": 300000000, "img": "https://picsum.photos/seed/sx6/300/300"},
        {"id": "sx_7", "name": "黄金权杖", "period": "商代", "desc": "王权的象征", "price": 1500000000, "img": "https://picsum.photos/seed/sx7/300/300"},
        {"id": "sx_8", "name": "青铜神坛", "period": "商代", "desc": "复杂祭祀场景", "price": 900000000, "img": "https://picsum.photos/seed/sx8/300/300"},
        {"id": "sx_9", "name": "戴金面罩铜人", "period": "商代", "desc": "金光闪闪祭司", "price": 500000000, "img": "https://picsum.photos/seed/sx9/300/300"},
        {"id": "sx_10", "name": "青铜鸟", "period": "商代", "desc": "神鸟图腾", "price": 150000000, "img": "https://picsum.photos/seed/sx10/300/300"},
        {"id": "sx_11", "name": "陶猪", "period": "商代", "desc": "愤怒小鸟同款", "price": 50000000, "img": "https://picsum.photos/seed/sx11/300/300"},
        {"id": "sx_12", "name": "青铜大鸟", "period": "商代", "desc": "体型巨大神兽", "price": 400000000, "img": "https://picsum.photos/seed/sx12/300/300"},
        {"id": "sx_13", "name": "青铜爬龙柱", "period": "商代", "desc": "龙形神柱", "price": 650000000, "img": "https://picsum.photos/seed/sx13/300/300"},
        {"id": "sx_14", "name": "人身鸟脚像", "period": "商代", "desc": "半人半鸟", "price": 550000000, "img": "https://picsum.photos/seed/sx14/300/300"},
        {"id": "sx_15", "name": "顶尊跪坐人像", "period": "商代", "desc": "国宝级重器", "price": 1100000000, "img": "https://picsum.photos/seed/sx15/300/300"},
        {"id": "sx_16", "name": "青铜蛇", "period": "商代", "desc": "造型逼真", "price": 120000000, "img": "https://picsum.photos/seed/sx16/300/300"},
        {"id": "sx_17", "name": "青铜鸡", "period": "商代", "desc": "雄鸡一唱", "price": 80000000, "img": "https://picsum.photos/seed/sx17/300/300"},
        {"id": "sx_18", "name": "玉琮", "period": "商代", "desc": "良渚文化影响", "price": 200000000, "img": "https://picsum.photos/seed/sx18/300/300"},
    ],
    "beijing": [
        {"id": "bj_1", "name": "清明上河图", "period": "北宋", "desc": "中华第一神品", "price": 5000000000, "img": "https://picsum.photos/seed/bj1/300/300"},
        {"id": "bj_2", "name": "金瓯永固杯", "period": "清乾隆", "desc": "乾隆御用金杯", "price": 600000000, "img": "https://picsum.photos/seed/bj2/300/300"},
        {"id": "bj_3", "name": "后母戊鼎", "period": "商代", "desc": "青铜之王", "price": 4000000000, "img": "https://picsum.photos/seed/bj3/300/300"},
        {"id": "bj_4", "name": "千里江山图", "period": "北宋", "desc": "青绿山水巅峰", "price": 3000000000, "img": "https://picsum.photos/seed/bj4/300/300"},
        {"id": "bj_5", "name": "四羊方尊", "period": "商代", "desc": "青铜铸造奇迹", "price": 2000000000, "img": "https://picsum.photos/seed/bj5/300/300"},
        {"id": "bj_6", "name": "孝端皇后凤冠", "period": "明代", "desc": "点翠工艺巅峰", "price": 500000000, "img": "https://picsum.photos/seed/bj6/300/300"},
        {"id": "bj_7", "name": "金缕玉衣", "period": "西汉", "desc": "中山靖王同款", "price": 1000000000, "img": "https://picsum.photos/seed/bj7/300/300"},
        {"id": "bj_8", "name": "红山玉龙", "period": "新石器", "desc": "中华第一龙", "price": 1200000000, "img": "https://picsum.photos/seed/bj8/300/300"},
        {"id": "bj_9", "name": "击鼓说唱俑", "period": "东汉", "desc": "汉代幽默感", "price": 300000000, "img": "https://picsum.photos/seed/bj9/300/300"},
        {"id": "bj_10", "name": "人面鱼纹盆", "period": "仰韶", "desc": "史前文明微笑", "price": 250000000, "img": "https://picsum.photos/seed/bj10/300/300"},
        {"id": "bj_11", "name": "大盂鼎", "period": "西周", "desc": "铭文极其珍贵", "price": 1800000000, "img": "https://picsum.photos/seed/bj11/300/300"},
        {"id": "bj_12", "name": "虢季子白盘", "period": "西周", "desc": "晚清出土重器", "price": 1600000000, "img": "https://picsum.photos/seed/bj12/300/300"},
        {"id": "bj_13", "name": "霁蓝白龙梅瓶", "period": "元代", "desc": "元代顶级瓷器", "price": 800000000, "img": "https://picsum.photos/seed/bj13/300/300"},
        {"id": "bj_14", "name": "郎世宁百骏图", "period": "清代", "desc": "中西合璧", "price": 600000000, "img": "https://picsum.photos/seed/bj14/300/300"},
        {"id": "bj_15", "name": "五牛图", "period": "唐代", "desc": "韩滉传世孤本", "price": 900000000, "img": "https://picsum.photos/seed/bj15/300/300"},
        {"id": "bj_16", "name": "步辇图", "period": "唐代", "desc": "阎立本绘", "price": 800000000, "img": "https://picsum.photos/seed/bj16/300/300"},
        {"id": "bj_17", "name": "利簋", "period": "西周", "desc": "记录武王伐纣", "price": 700000000, "img": "https://picsum.photos/seed/bj17/300/300"},
        {"id": "bj_18", "name": "鹳鱼石斧陶缸", "period": "仰韶", "desc": "绘画史第一页", "price": 400000000, "img": "https://picsum.photos/seed/bj18/300/300"},
    ],
    "shanghai": [
        {"id": "sh_1", "name": "大克鼎", "period": "西周", "desc": "海内三宝之一", "price": 1500000000, "img": "https://picsum.photos/seed/sh1/300/300"},
        {"id": "sh_2", "name": "晋侯苏钟", "period": "西周", "desc": "铭文刻在钟表", "price": 800000000, "img": "https://picsum.photos/seed/sh2/300/300"},
        {"id": "sh_3", "name": "孙位高逸图", "period": "唐代", "desc": "唐代人物画孤本", "price": 1200000000, "img": "https://picsum.photos/seed/sh3/300/300"},
        {"id": "sh_4", "name": "越王剑", "period": "春秋", "desc": "虽不如勾践剑", "price": 300000000, "img": "https://picsum.photos/seed/sh4/300/300"},
        {"id": "sh_5", "name": "粉彩蝠桃纹瓶", "period": "清雍正", "desc": "雍正官窑极品", "price": 400000000, "img": "https://picsum.photos/seed/sh5/300/300"},
        {"id": "sh_6", "name": "王羲之上虞帖", "period": "唐摹本", "desc": "书圣墨宝", "price": 2000000000, "img": "https://picsum.photos/seed/sh6/300/300"},
        {"id": "sh_7", "name": "苦笋帖", "period": "唐怀素", "desc": "草书狂僧真迹", "price": 1000000000, "img": "https://picsum.photos/seed/sh7/300/300"},
        {"id": "sh_8", "name": "青花瓶", "period": "元代", "desc": "元青花存世稀少", "price": 600000000, "img": "https://picsum.photos/seed/sh8/300/300"},
        {"id": "sh_9", "name": "子仲姜盘", "period": "春秋", "desc": "盘内动物可旋转", "price": 500000000, "img": "https://picsum.photos/seed/sh9/300/300"},
        {"id": "sh_10", "name": "牺尊", "period": "春秋", "desc": "极具神韵的牛形", "price": 350000000, "img": "https://picsum.photos/seed/sh10/300/300"},
        {"id": "sh_11", "name": "商鞅方升", "period": "战国", "desc": "统一度量衡", "price": 1500000000, "img": "https://picsum.photos/seed/sh11/300/300"},
        {"id": "sh_12", "name": "曹全碑", "period": "东汉", "desc": "汉代隶书巅峰", "price": 450000000, "img": "https://picsum.photos/seed/sh12/300/300"},
        {"id": "sh_13", "name": "哥窑五足洗", "period": "南宋", "desc": "金丝铁线", "price": 300000000, "img": "https://picsum.photos/seed/sh13/300/300"},
        {"id": "sh_14", "name": "透雕神兽玉璧", "period": "西汉", "desc": "汉代玉器巅峰", "price": 200000000, "img": "https://picsum.photos/seed/sh14/300/300"},
        {"id": "sh_15", "name": "剔红花卉纹盘", "period": "元代", "desc": "张成造，漆器孤品", "price": 120000000, "img": "https://picsum.photos/seed/sh15/300/300"},
        {"id": "sh_16", "name": "苏轼舣舟亭图", "period": "清代", "desc": "乾隆御览之宝", "price": 250000000, "img": "https://picsum.photos/seed/sh16/300/300"},
        {"id": "sh_17", "name": "青花牡丹纹罐", "period": "元代", "desc": "元青花大器", "price": 550000000, "img": "https://picsum.photos/seed/sh17/300/300"},
        {"id": "sh_18", "name": "缂丝莲塘乳鸭", "period": "南宋", "desc": "缂丝工艺巅峰", "price": 800000000, "img": "https://picsum.photos/seed/sh18/300/300"},
    ],
    "xian": [
        {"id": "xa_1", "name": "兽首玛瑙杯", "period": "唐代", "desc": "海内孤品", "price": 2000000000, "img": "https://picsum.photos/seed/xa1/300/300"},
        {"id": "xa_2", "name": "舞马衔杯银壶", "period": "唐代", "desc": "大唐盛世缩影", "price": 800000000, "img": "https://picsum.photos/seed/xa2/300/300"},
        {"id": "xa_3", "name": "皇后之玺", "period": "西汉", "desc": "吕后之印", "price": 1000000000, "img": "https://picsum.photos/seed/xa3/300/300"},
        {"id": "xa_4", "name": "兵马俑(跪射)", "period": "秦代", "desc": "保存最完整", "price": 3000000000, "img": "https://picsum.photos/seed/xa4/300/300"},
        {"id": "xa_5", "name": "葡萄花鸟香囊", "period": "唐代", "desc": "杨贵妃同款", "price": 500000000, "img": "https://picsum.photos/seed/xa5/300/300"},
        {"id": "xa_6", "name": "鎏金铜蚕", "period": "西汉", "desc": "丝绸之路见证", "price": 300000000, "img": "https://picsum.photos/seed/xa6/300/300"},
        {"id": "xa_7", "name": "独孤信印", "period": "西魏", "desc": "多面体印章", "price": 400000000, "img": "https://picsum.photos/seed/xa7/300/300"},
        {"id": "xa_8", "name": "提梁倒注壶", "period": "五代", "desc": "神奇倒注构造", "price": 200000000, "img": "https://picsum.photos/seed/xa8/300/300"},
        {"id": "xa_9", "name": "鸳鸯纹金碗", "period": "唐代", "desc": "金银器巅峰", "price": 600000000, "img": "https://picsum.photos/seed/xa9/300/300"},
        {"id": "xa_10", "name": "三彩骆驼俑", "period": "唐代", "desc": "丝路乐队", "price": 450000000, "img": "https://picsum.photos/seed/xa10/300/300"},
        {"id": "xa_11", "name": "阙楼仪仗图", "period": "唐代", "desc": "懿德太子墓", "price": 1500000000, "img": "https://picsum.photos/seed/xa11/300/300"},
        {"id": "xa_12", "name": "鎏金铜龙", "period": "唐代", "desc": "气势磅礴", "price": 350000000, "img": "https://picsum.photos/seed/xa12/300/300"},
        {"id": "xa_13", "name": "杜虎符", "period": "战国", "desc": "调兵遣将信物", "price": 500000000, "img": "https://picsum.photos/seed/xa13/300/300"},
        {"id": "xa_14", "name": "何尊", "period": "西周", "desc": "最早出现'中国'", "price": 2500000000, "img": "https://picsum.photos/seed/xa14/300/300"},
        {"id": "xa_15", "name": "多友鼎", "period": "西周", "desc": "铭文记录战争", "price": 800000000, "img": "https://picsum.photos/seed/xa15/300/300"},
        {"id": "xa_16", "name": "日己觥", "period": "西周", "desc": "造型奇特酒器", "price": 400000000, "img": "https://picsum.photos/seed/xa16/300/300"},
        {"id": "xa_17", "name": "雁鱼铜灯", "period": "西汉", "desc": "环保美学结合", "price": 550000000, "img": "https://picsum.photos/seed/xa17/300/300"},
        {"id": "xa_18", "name": "金怪兽", "period": "战国", "desc": "匈奴文化代表", "price": 200000000, "img": "https://picsum.photos/seed/xa18/300/300"},
    ]
}

# ==========================================
# 3. 工具函数（优化：增加图片占位、容错增强）
# ==========================================
def get_base64_image(image_path):
    """将本地图片转换为 Base64 字符串（增加异常处理）"""
    try:
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            return None
        with open(image_path, "rb") as img_file:
            b64_data = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{b64_data}"
    except Exception as e:
        print(f"读取图片失败 {image_path}：{e}")
        return None

def format_price(price):
    """格式化价格显示（亿/万单位转换）"""
    if price >= 100000000: 
        return f"{price/100000000:.1f}亿"
    elif price >= 10000: 
        return f"{price/10000:.0f}万"
    return str(price)

# ==========================================
# 4. 通用图片加载逻辑（优化：占位图统一、容错更强）
# ==========================================
for museum_cn, museum_pinyin in MUSEUM_NAME_MAP.items():
    treasures = MUSEUM_TREASURES.get(museum_pinyin, [])
    if not treasures:
        continue
    
    current_museum_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    
    for idx, treasure in enumerate(treasures, start=1):
        img_names = [
            f"{idx}.jpeg",
            f"{idx}.jpg",
            f"[] ({idx}).jpeg",
            f"[] ({idx}).jpg"
        ]
        b64_str = None
        
        for img_name in img_names:
            img_path = os.path.join(current_museum_dir, img_name)
            b64_str = get_base64_image(img_path)
            if b64_str:
                break
        
        # 优化：占位图种子更稳定，避免重复
        if b64_str:
            treasure["img"] = b64_str
        else:
            prefix = treasure['id'][:2]
            treasure["img"] = f"https://picsum.photos/seed/{prefix}_{idx}_unique/300/300"

# ==========================================
# 5. 样式优化（核心：统一视觉、增加层级、修复冲突）
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    .stApp { 
        background-color: #f5f5f7 !important; 
        color: #1d1d1f; 
        padding-top: 0 !important; 
    }
    .block-container { 
        padding-top: 1rem !important; 
        max-width: 1400px !important; 
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* --- 外链按钮样式 --- */
    .neal-btn {
        font-family: 'Inter', sans-serif; 
        background: #fff;
        border: 1px solid #e5e7eb; 
        color: #111; 
        font-weight: 600;
        padding: 8px 16px; 
        border-radius: 8px; 
        cursor: pointer;
        transition: all 0.2s; 
        display: inline-flex; 
        align-items: center;
        text-decoration: none !important;
        width: 100%; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .neal-btn:hover { 
        background: #f9fafb; 
        transform: translateY(-1px); 
    }
    .neal-btn-link { 
        text-decoration: none; 
        width: 100%; 
        display: block; 
    }

    /* --- 仪表盘 (优化：更精致的卡片、间距调整) --- */
    .dashboard {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 20px 30px !important;
        border-bottom: 1px solid #e5e5e5;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: all 0.1s ease;
    }

    /* --- 明细面板样式（优化：更强的视觉层级、间距调整） --- */
    .detail-panel {
        background: #ffffff;
        border-radius: 16px;
        padding: 25px 30px;
        margin-bottom: 25px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.04);
        border: 1px solid #e5e7eb;
    }
    .detail-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #111;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .detail-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .detail-table th {
        background-color: #f8f9fa;
        color: #6b7280;
        font-weight: 600;
        padding: 12px 15px;
        text-align: left;
        border-bottom: 2px solid #e5e7eb;
    }
    .detail-table td {
        padding: 12px 15px;
        color: #1d1d1f;
        border-bottom: 1px solid #f3f4f6;
    }
    .detail-table tr:hover td {
        background-color: #f9fafb;
    }
    .detail-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        font-weight: 600;
        color: #111;
    }
    .empty-detail {
        text-align: center;
        padding: 40px 0;
        color: #9ca3af;
        font-size: 0.9rem;
    }

    /* --- 房产展示区美化（优化：图片容器样式） --- */
    .mansion-img-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .mansion-overlay-text {
        position: absolute;
        bottom: 20px;
        left: 20px;
        color: #fff;
        background-color: rgba(0,0,0,0.7);
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        z-index: 10;
    }

    /* --- 藏品卡片美化（核心优化：统一尺寸、更细腻的hover效果） --- */
    .treasure-card {
        background: #ffffff; 
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03); 
        transition: all 0.3s ease;
        border: 1px solid #e5e5e5; 
        overflow: hidden; 
        height: 100%;
        display: flex; 
        flex-direction: column;
    }
    .treasure-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 12px 30px rgba(0,0,0,0.1); 
        border-color: #d1d5db;
    }
    
    /* --- 图片容器 --- */
    .t-img-box { 
        height: 180px; 
        width: 100%; 
        overflow: hidden;
        background: #f8f9fa;
        display: flex; 
        align-items: center; 
        justify-content: center; 
        position: relative;
    }

    /* --- 圆形无留白图片 --- */
    .t-img { 
        width: 130px !important;       
        height: 130px !important;      
        border-radius: 50%;            
        object-fit: cover;             
        object-position: center center;
        transform: scale(1.1);         
        border: 3px solid white;       
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    }
    
    .treasure-card:hover .t-img {
        transform: scale(1.15);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .t-content { 
        padding: 15px !important; 
        flex-grow: 1; 
        display: flex; 
        flex-direction: column; 
        text-align: center;
    }
    .t-title { 
        font-size: 1rem; 
        font-weight: 600; 
        margin-bottom: 8px !important; 
        color: #1d1d1f;
    }
    .t-period { 
        font-size: 0.75rem; 
        color: #86868b; 
        background: #f5f5f7; 
        padding: 2px 8px; 
        border-radius: 10px; 
        display: inline-block; 
        margin-bottom: 8px !important; 
        width: fit-content; 
        margin-left: auto; 
        margin-right: auto;
    }
    .t-desc { 
        font-size: 0.8rem; 
        color: #555; 
        line-height: 1.4; 
        margin-bottom: 12px !important; 
        flex-grow: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    
    /* --- 价格样式 --- */
    .t-price { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 1rem; 
        font-weight: 700; 
        margin: 8px 0 !important; 
    }
    .sold-price { color: #d9534f; }
    .unsold-price { color: #9ca3af; font-style: italic; font-size: 0.9rem; letter-spacing: 1px; }

    /* --- 动画 --- */
    @keyframes fadeInPrice {
        0% { opacity: 0; transform: scale(0.8) translateY(10px); color: #28a745; filter: blur(5px); }
        50% { opacity: 0.6; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1) translateY(0); color: #d9534f; filter: blur(0); }
    }
    .price-reveal { animation: fadeInPrice 1.5s cubic-bezier(0.22, 1, 0.36, 1) forwards; display: inline-block; }

    /* --- 支付卡片样式 --- */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&display=swap');
    .pay-label { font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .pay-amount-display { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 800; margin: 10px 0; }
    .pay-instruction { font-size: 0.8rem; color: #94a3b8; margin-top: 15px; margin-bottom: 5px; }
    .color-wechat { color: #2AAD67; }
    .color-alipay { color: #1677ff; }
    .color-paypal { color: #003087; }

    /* 全局按钮（优化：更圆润、间距调整） */
    div[data-testid="stButton"] button { 
        width: 100% !important; 
        border-radius: 8px !important; 
        font-weight: 600 !important;
        padding: 10px 0 !important;
    }
    
    /* 统计条（优化：更精致的边框和阴影） */
    .stats-bar { 
        display: flex; 
        justify-content: center; 
        gap: 30px; 
        margin-top: 50px; 
        padding: 18px 30px; 
        background-color: white; 
        border-radius: 50px; 
        border: 1px solid #eee; 
        color: #6b7280; 
        font-size: 0.85rem; 
        width: fit-content; 
        margin-left: auto; 
        margin-right: auto; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .stats-bar > div {
        text-align: center;
        min-width: 80px;
    }
    .stats-bar > div:nth-child(2) {
        border-left:1px solid #eee; 
        padding-left:30px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 状态初始化（优化：默认值更合理）
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1
if 'has_counted' not in st.session_state: st.session_state["has_counted"] = False

# 语言包
lang_texts = {
    'zh': {
        'coffee_desc': '如果这个游戏帮到了你，欢迎支持。', 
        'coffee_btn': "☕ 请开发者喝咖啡", 
        'coffee_title': " ", 
        'coffee_amount': "请输入打赏杯数", 
        'pay_success': "收到！感谢打赏。❤️",
        'pay_wechat': '微信支付',
        'pay_alipay': '支付宝',
        'pay_paypal': '贝宝',
        'presets': [("☕ 提神", 1), ("🍗 鸡腿", 3), ("🚀 续命", 5)],
        'detail_title': '📋 拍卖成交明细',
        'detail_col1': '藏品名称',
        'detail_col2': '年代',
        'detail_col3': '成交价格',
        'detail_col4': '状态',
        'detail_empty': '暂无成交记录，快去拍卖第一件国宝吧！',
        'detail_summary_total': '累计成交总额：',
        'detail_summary_count': '成交藏品数量：'
    },
    'en': {
        'coffee_desc': 'Support is appreciated.', 
        'coffee_btn': "☕ Buy me a coffee", 
        'coffee_title': " ", 
        'coffee_amount': "Enter Coffee Count", 
        'pay_success': "Received! Thanks! ❤️",
        'pay_wechat': 'WeChat',
        'pay_alipay': 'Alipay',
        'pay_paypal': 'PayPal',
        'presets': [("☕ Coffee", 1), ("🍗 Meal", 3), ("🚀 Rocket", 5)],
        'detail_title': '📋 Auction Transaction Details',
        'detail_col1': 'Treasure Name',
        'detail_col2': 'Period',
        'detail_col3': 'Transaction Price',
        'detail_col4': 'Status',
        'detail_empty': 'No transaction records yet, go auction your first national treasure!',
        'detail_summary_total': 'Total Transaction Amount：',
        'detail_summary_count': 'Number of Sold Treasures：'
    }
}
current_text = lang_texts[st.session_state.language]

# ==========================================
# 7. 顶部功能区（优化：排版更紧凑、视觉更协调）
# ==========================================
# 顶部操作栏：语言切换 + 更多应用
col_top_1, col_top_2, col_top_3 = st.columns([0.8, 0.1, 0.1])
with col_top_2:
    l_btn = "En" if st.session_state.language == 'zh' else "中"
    if st.button(l_btn, key="lang_switch", use_container_width=True):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

with col_top_3:
    st.markdown("""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ 更多</button>
        </a>""", unsafe_allow_html=True)

# 标题 + 博物馆选择器
st.markdown("<h2 style='margin-top: 15px; margin-bottom: 20px; color: #111; text-align: center;'>🏛️ 华夏国宝私有化中心</h2>", unsafe_allow_html=True)

# 优化：博物馆选择器居中显示
col_museum_1, col_museum_2, col_museum_3 = st.columns([0.2, 0.6, 0.2])
with col_museum_2:
    selected_museum = st.radio(
        "选择博物馆",
        list(MANSION_CONFIG.keys()),
        index=list(MANSION_CONFIG.keys()).index(st.session_state.current_museum),
        horizontal=True,
        label_visibility="collapsed",
        key="museum_selector"
    )

if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.rerun()

# ==========================================
# 8. 明细面板置顶（核心修复：表格列数匹配、语言包适配）
# ==========================================
def render_auction_detail():
    """渲染拍卖成交明细面板，放置在页面上部核心位置"""
    current_museum_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
    all_treasures = MUSEUM_TREASURES.get(current_museum_pinyin, [])
    sold_treasures = [t for t in all_treasures if t['id'] in st.session_state.sold_items]
    
    # 初始化HTML（列表拼接，避免语法错误）
    detail_html = []
    detail_html.append(f'<div class="detail-panel">')
    detail_html.append(f'  <div class="detail-title">{current_text["detail_title"]}</div>')
    
    if not sold_treasures:
        # 优化：使用语言包文本，避免硬编码
        detail_html.append(f'  <div class="empty-detail">{current_text["detail_empty"]}</div>')
    else:
        # 修复：表格列数与<th>、<td>匹配（4列）
        detail_html.append(f'  <table class="detail-table">')
        detail_html.append(f'    <thead>')
        detail_html.append(f'      <tr>')
        detail_html.append(f'        <th>{current_text["detail_col1"]}</th>')
        detail_html.append(f'        <th>{current_text["detail_col2"]}</th>')
        detail_html.append(f'        <th>{current_text["detail_col3"]}</th>')
        detail_html.append(f'        <th>{current_text["detail_col4"]}</th>')
        detail_html.append(f'      </tr>')
        detail_html.append(f'    </thead>')
        detail_html.append(f'    <tbody>')
        
        for treasure in sold_treasures:
            price_str = f"¥{format_price(treasure['price'])}"
            status = "✅ 已成交" if st.session_state.language == 'zh' else "✅ Sold"
            detail_html.append(f'      <tr>')
            detail_html.append(f'        <td>{treasure["name"]}</td>')
            detail_html.append(f'        <td>{treasure["period"]}</td>')
            detail_html.append(f'        <td class="sold-price">{price_str}</td>')
            detail_html.append(f'        <td>{status}</td>')
            detail_html.append(f'      </tr>')
        
        detail_html.append(f'    </tbody>')
        detail_html.append(f'  </table>')
        
        # 明细汇总
        total_count = len(sold_treasures)
        total_amount = f"¥{format_price(st.session_state.total_revenue)}"
        detail_html.append(f'  <div class="detail-summary">')
        detail_html.append(f'    <div>{current_text["detail_summary_count"]} {total_count}</div>')
        detail_html.append(f'    <div>{current_text["detail_summary_total"]} {total_amount}</div>')
        detail_html.append(f'  </div>')
    
    detail_html.append(f'</div>')
    final_html = "\n".join(detail_html)
    st.markdown(final_html, unsafe_allow_html=True)

# 执行明细面板渲染
render_auction_detail()

# ==========================================
# 9. 仪表盘模块（优化：图片显示、叠加文本错位修复）
# ==========================================

# 1. 辅助函数：将本地图片转为 Base64 字符串
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f"data:image/jpeg;base64,{data}"
    return f"https://picsum.photos/seed/mansion/400/250"

# 2. 定义统一高度
FIXED_HEIGHT = "200px" 

# 3. CSS 样式增强
st.markdown(f"""
<style>
    /* 左右公用的对齐容器 */
    .align-container {{
        height: {FIXED_HEIGHT};
        display: flex;
        flex-direction: column;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e5e5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        background: white;
    }}

    /* 左侧面板：居中对齐内容 */
    .dashboard-left {{
        padding: 20px;
        justify-content: center;
    }}

    /* 右侧面板：定位标题和叠加层 */
    .mansion-right {{
        position: relative;
    }}
    
    .mansion-img-fit {{
        width: 100%;
        height: 100%;
        object-fit: cover; /* 关键：图片自动裁剪填充，不留白不变形 */
    }}

    .mansion-top-label {{
        position: absolute;
        top: 10px; left: 10px;
        background: rgba(255, 255, 255, 0.9);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: bold;
        color: #333;
        z-index: 2;
    }}

    .mansion-overlay-bottom {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(transparent, rgba(0,0,0,0.7));
        color: white;
        padding: 10px;
        font-size: 0.8rem;
        z-index: 2;
    }}
</style>
""", unsafe_allow_html=True)

# 4. 布局渲染
col1, col2 = dashboard_placeholder.columns([0.4, 0.6], gap="small")

with col1:
    # 使用统一的 align-container 类
    st.markdown(f"""
    <div class="align-container dashboard-left">
        <div style="font-size: 1.1rem; font-weight: 700; color: #666; margin-bottom: 5px;">{st.session_state.current_museum}</div>
        <div style="font-size: 1.8rem; font-weight: 900; color: #d9534f;">
            ¥{current_revenue_display / 100000000:.4f}亿
        </div>
        <div style="font-size: 0.75rem; color: #999; text-transform: uppercase; margin-top: 5px;">累计拍卖总额</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # 获取图片
    img_src = get_image_base64(m_info["mansion_img"])
    overlay_text = f"财富购买力：× {villa_count:.2f} 套" if st.session_state.language == 'zh' else f"Purchasing Power: × {villa_count:.2f}"
    
    # 纯 HTML 实现高度对齐和置顶标题
    st.markdown(f"""
    <div class="align-container mansion-right">
        <div class="mansion-top-label">🏠 {m_info['mansion_name']}</div>
        
        <img src="{img_src}" class="mansion-img-fit">
        
        <div class="mansion-overlay-bottom">
            {overlay_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    
# ==========================================
# 10. 拍卖动画（优化：减少重渲染，提升流畅度）
# ==========================================
def auction_animation(item_price, item_name, item_id):
    if item_id in st.session_state.sold_items:
        return  # 避免重复拍卖
    
    start_revenue = st.session_state.total_revenue
    target_revenue = start_revenue + item_price
    steps = 15  # 减少步骤，提升流畅度
    step_val = item_price / steps
    
    msg = st.toast(f"🔨 正在拍卖 {item_name}...", icon="⏳")
    
    for i in range(steps):
        current_step_val = start_revenue + (step_val * (i + 1))
        render_dashboard(current_step_val)
        time.sleep(0.02)  # 调整间隔，更流畅
    
    # 更新状态
    st.session_state.total_revenue = target_revenue
    st.session_state.sold_items.add(item_id)
    st.session_state.last_sold_id = item_id 
    
    msg.toast(f"✅ 成交！入账 ¥{format_price(item_price)}", icon="💰")
    time.sleep(0.8)
    st.rerun()

# ==========================================
# 11. 商品展示区（优化：卡片间距、列数适配）
# ==========================================
current_museum_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
items = MUSEUM_TREASURES.get(current_museum_pinyin, [])

# 优化：根据屏幕宽度调整列数（宽屏6列，更紧凑）
cols_per_row = 6
if len(items) < 6:
    cols_per_row = len(items)
rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]

# 增加分区标题
st.markdown(f"<h3 style='margin: 30px 0 20px 0; color: #111;'>📜 {st.session_state.current_museum} 藏品列表</h3>", unsafe_allow_html=True)

for row_items in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for idx, item in enumerate(row_items):
        item_id = item['id']
        with cols[idx]:
            is_sold = item_id in st.session_state.sold_items
            
            # 价格显示逻辑
            if is_sold:
                display_price = f"¥{format_price(item['price'])}"
                price_class = "t-price sold-price"
                if item_id == st.session_state.get('last_sold_id'):
                    price_class += " price-reveal"
            else:
                display_price = "🕵️ 价值待揭晓" if st.session_state.language == 'zh' else "🕵️ Value to be revealed"
                price_class = "t-price unsold-price"
            
            # 图片容错
            item_img = item.get('img', f"https://picsum.photos/seed/{item_id}/300/300")
            
            # 渲染藏品卡片
            st.markdown(f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item_img}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
                </div>
                <div class="t-content">
                    <div class="t-title">{item['name']}</div>
                    <div class="t-period">{item.get('period', '古代' if st.session_state.language == 'zh' else 'Ancient')}</div>
                    <div class="t-desc" title="{item['desc']}">{item['desc']}</div>
                    <div class="{price_class}">{display_price}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 拍卖按钮
            if is_sold:
                btn_text = "🚫 已私有化" if st.session_state.language == 'zh' else "🚫 Already Sold"
                st.button(btn_text, key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                btn_text = "㊙ 立即拍卖" if st.session_state.language == 'zh' else "㊙ Auction Now"
                if st.button(btn_text, key=f"btn_{item_id}", type="primary", use_container_width=True):
                    auction_animation(item['price'], item['name'], item_id)

# ==========================================
# 12. 底部功能（优化：间距、按钮样式）
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([0.25, 0.5, 0.25], gap="medium")

# 重置按钮
with c1:
    reset_text = "🔄 破产/重置" if st.session_state.language == 'zh' else "🔄 Reset"
    if st.button(reset_text, type="secondary", use_container_width=True):
        st.session_state.sold_items = set()
        st.session_state.total_revenue = 0
        st.session_state.last_sold_id = None
        st.rerun()

# 咖啡打赏按钮
with c2:
    @st.dialog(" " + current_text['coffee_title'], width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="text-align:center; color:#666; margin-bottom:15px;">{current_text['coffee_desc']}</div>""", unsafe_allow_html=True)
        
        presets = current_text['presets']
        def set_val(n): st.session_state.coffee_num = n
        
        p_cols = st.columns(3, gap="small")
        for i, (label, num) in enumerate(presets):
            with p_cols[i]:
                if st.button(label, use_container_width=True, key=f"preset_{i}"):
                    set_val(num)
        
        st.write("")
        
        # 自定义输入
        col_amount, col_padding = st.columns([1, 1], gap="small")
        with col_amount: 
            cnt = st.number_input(current_text['coffee_amount'], 1, 100, step=1, key='coffee_num')
        
        cny_total = cnt * 10
        usd_total = cnt * 2

        # 支付卡片渲染
        def render_pay_tab(title, amount_str, color_class, img_name, qr_suffix, link=None):
            with st.container(border=True):
                st.markdown(f"""<div style="text-align: center; padding-bottom: 10px;">
                    <div class="pay-label {color_class}">{title}</div>
                    <div class="pay-amount-display {color_class}">{amount_str}</div></div>""", unsafe_allow_html=True)
                
                c_img_1, c_img_2, c_img_3 = st.columns([1, 4, 1])
                with c_img_2:
                    local_img_path = os.path.join(PROJECT_ROOT, img_name)
                    if os.path.exists(local_img_path):
                        st.image(local_img_path, use_container_width=True)
                    else:
                        qr_data = f"Donate_{cny_total}_{qr_suffix}" if not link else link
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}", use_container_width=True)
                
                if link:
                    st.write("")
                    st.link_button(f"👉 Pay {amount_str}", link, type="primary", use_container_width=True)
                else:
                    tip_text = "扫码支付后点击下方按钮确认" if st.session_state.language == 'zh' else 'Scan QR code and click the button below to confirm'
                    st.markdown(f"""<div class="pay-instruction" style="text-align: center;">{tip_text}</div>""", unsafe_allow_html=True)

        # 支付选项卡
        t1, t2, t3 = st.tabs([current_text['pay_wechat'], current_text['pay_alipay'], current_text['pay_paypal']])
        with t1: render_pay_tab("WeChat Pay", f"¥{cny_total}", "color-wechat", "wechat_pay.jpg", "WeChat")
        with t2: render_pay_tab("Alipay", f"¥{cny_total}", "color-alipay", "ali_pay.jpg", "Alipay")
        with t3: render_pay_tab("PayPal", f"${usd_total}", "color-paypal", "paypal.png", "PayPal", "https://paypal.me/ytqz")

        st.write("")
        if st.button("🎉 " + current_text['pay_success'].split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            time.sleep(1)
            st.rerun()

    if st.button(current_text['coffee_btn'], use_container_width=True):
        show_coffee_window()

# ==========================================
# 13. 访问统计（优化：统计条样式、数据容错）
# ==========================================
def track_stats():
    DB_FILE = os.path.join(os.path.expanduser("~/"), "visit_stats.db")
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        today = datetime.datetime.utcnow().date().isoformat()
        
        if not st.session_state["has_counted"]:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (st.session_state["visitor_id"], today))
            conn.commit()
            st.session_state["has_counted"] = True
        
        today_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        total_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        conn.close()
        return today_uv, total_uv
    except Exception as e:
        print(f"统计失败：{e}")
        return 1, 1

today_uv, total_uv = track_stats()

st.markdown(f"""
<div class="stats-bar">
    <div><div>今日 UV</div><div style="font-weight:700; color:#111;">{today_uv}</div></div>
    <div><div>历史 UV</div><div style="font-weight:700; color:#111;">{total_uv}</div></div>
</div>
""", unsafe_allow_html=True)

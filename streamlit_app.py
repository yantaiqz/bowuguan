import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import base64

# ==========================================
# 1. 全局配置 & 路径修复（极简版：移除冗余注释，简化路径逻辑）
# ==========================================
st.set_page_config(
    page_title="国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 路径兼容 & 目录创建（极简写法）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
MANSION_IMG_ROOT = os.path.join(BASE_IMG_ROOT, "mansion")
for dir_path in [BASE_IMG_ROOT, MANSION_IMG_ROOT]:
    os.makedirs(dir_path, exist_ok=True)

# 博物馆名称映射（保持核心功能）
MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}

# 动态创建博物馆图片目录
for museum_pinyin in MUSEUM_NAME_MAP.values():
    os.makedirs(os.path.join(BASE_IMG_ROOT, museum_pinyin), exist_ok=True)

# ==========================================
# 2. 核心数据（保持不变，移除冗余注释）
# ==========================================
MANSION_CONFIG = {
    "南京博物院": {"mansion_name": "颐和路民国别墅", "price": 100000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "1.jpeg")},
    "三星堆博物馆": {"mansion_name": "成都麓山国际豪宅", "price": 50000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "5.jpeg")},
    "中国国家博物馆": {"mansion_name": "什刹海四合院", "price": 150000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "2.jpeg")},
    "上海博物馆": {"mansion_name": "愚园路老洋房", "price": 200000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "3.jpeg")},
    "陕西历史博物馆": {"mansion_name": "曲江池畔大平层", "price": 3000000, "mansion_img": os.path.join(MANSION_IMG_ROOT, "4.jpeg")}
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
        {"id": "nj_11", "name": "玉琮", "period": "良渚", "desc": "史前玉器巅峰", "price": 60000000, "img": ""},
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
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树", "price": 1300000000, "img": "https://picsum.photos/seed/sx2/300/300"},
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
# 3. 工具函数（极简版：保留核心功能，移除冗余注释）
# ==========================================
def get_base64_image(image_path):
    try:
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            return None
        with open(image_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception as e:
        print(f"读取图片失败 {image_path}：{e}")
        return None

def format_price(price):
    if price >= 100000000: 
        return f"{price/100000000:.1f}亿"
    elif price >= 10000: 
        return f"{price/10000:.0f}万"
    return str(price)

# ==========================================
# 4. 通用图片加载逻辑（保持不变，简化循环写法）
# ==========================================
for museum_cn, museum_pinyin in MUSEUM_NAME_MAP.items():
    treasures = MUSEUM_TREASURES.get(museum_pinyin, [])
    current_museum_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    for idx, treasure in enumerate(treasures, start=1):
        img_names = [f"{idx}.jpeg", f"{idx}.jpg", f"[] ({idx}).jpeg", f"[] ({idx}).jpg"]
        b64_str = None
        for img_name in img_names:
            b64_str = get_base64_image(os.path.join(current_museum_dir, img_name))
            if b64_str:
                break
        treasure["img"] = b64_str if b64_str else f"https://picsum.photos/seed/{treasure['id'][:2]}_{idx}_unique/300/300"

# ==========================================
# 5. 样式优化（核心：极简风格，压缩间距，移除冗余样式）
# ==========================================
st.markdown("""
<style>
    /* 基础极简设置：隐藏冗余元素，简化背景 */
    #MainMenu, footer, [data-testid="stHeader"] {visibility: hidden !important;}
    .stApp { background-color: #f8f9fa !important; color: #212529; padding-top: 0 !important; }
    .block-container { 
        padding-top: 0.5rem !important; 
        max-width: 1300px !important; 
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* 仪表盘：简化样式，压缩内边距 */
    .dashboard {
        background: #ffffff;
        padding: 15px 20px !important;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        height: 100%;
    }

    /* 明细面板：极简风格，减少间距 */
    .detail-panel {
        background: #ffffff;
        border-radius: 12px;
        padding: 15px 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        border: 1px solid #e9ecef;
    }
    .detail-title { font-size: 1.1rem; font-weight: 600; color: #212529; margin-bottom: 12px; }
    .detail-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .detail-table th { background-color: #f8f9fa; color: #6c757d; padding: 8px 10px; text-align: left; border-bottom: 1px solid #e9ecef; }
    .detail-table td { padding: 8px 10px; border-bottom: 1px solid #f1f3f5; }
    .detail-summary { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 12px; border-top: 1px solid #e9ecef; font-weight: 600; }
    .empty-detail { text-align: center; padding: 20px 0; color: #adb5bd; font-size: 0.85rem; }

    /* 藏品卡片：简化hover效果，压缩内边距 */
    .treasure-card {
        background: #ffffff; 
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02); 
        transition: all 0.2s ease;
        border: 1px solid #e9ecef; 
        overflow: hidden; 
        height: 100%;
        display: flex; 
        flex-direction: column;
    }
    .treasure-card:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
    }
    .t-img-box { 
        height: 150px; 
        width: 100%; 
        overflow: hidden;
        background: #f8f9fa;
        display: flex; 
        align-items: center; 
        justify-content: center; 
        position: relative;
    }
    .t-img { 
        width: 110px !important;       
        height: 110px !important;      
        border-radius: 50%;            
        object-fit: cover;             
        border: 2px solid white;       
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        transition: all 0.3s ease; 
    }
    .treasure-card:hover .t-img { transform: scale(1.05); }
    .t-content { 
        padding: 10px !important; 
        flex-grow: 1; 
        display: flex; 
        flex-direction: column; 
        text-align: center;
    }
    .t-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 5px !important; color: #212529; }
    .t-period { 
        font-size: 0.7rem; 
        color: #6c757d; 
        background: #f8f9fa; 
        padding: 2px 6px; 
        border-radius: 6px; 
        display: inline-block; 
        margin-bottom: 5px !important; 
        margin-left: auto; 
        margin-right: auto;
    }
    .t-desc { 
        font-size: 0.75rem; 
        color: #495057; 
        line-height: 1.3; 
        margin-bottom: 8px !important; 
        flex-grow: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        display: -webkit-box;
    }
    .t-price { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 0.9rem; 
        font-weight: 600; 
        margin: 5px 0 !important; 
    }
    .sold-price { color: #dc3545; }
    .unsold-price { color: #adb5bd; font-style: italic; font-size: 0.8rem; }

    /* 全局按钮：简化样式，统一尺寸 */
    div[data-testid="stButton"] button { 
        width: 100% !important; 
        border-radius: 6px !important; 
        font-weight: 500 !important;
        padding: 8px 0 !important;
        font-size: 0.85rem !important;
    }
    .stats-bar { 
        display: flex; 
        justify-content: center; 
        gap: 20px; 
        margin-top: 30px; 
        padding: 12px 20px; 
        background-color: white; 
        border-radius: 30px; 
        border: 1px solid #e9ecef; 
        color: #6c757d; 
        font-size: 0.8rem; 
        margin-left: auto; 
        margin-right: auto; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 状态初始化（极简版：一行初始化，移除冗余注释）
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1
if 'has_counted' not in st.session_state: st.session_state["has_counted"] = False

# 语言包（保留核心文本，移除冗余）
lang_texts = {
    'zh': {
        'coffee_desc': '如果这个游戏帮到了你，欢迎支持。', 
        'coffee_btn': "☕ 请开发者喝咖啡", 
        'coffee_amount': "请输入打赏杯数", 
        'pay_success': "收到！感谢打赏。❤️",
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
        'coffee_amount': "Enter Coffee Count", 
        'pay_success': "Received! Thanks! ❤️",
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
# 7. 核心布局（极简优化：移除顶部冗余按钮，压缩分栏间距）
# ==========================================
# 简化标题：移除多余间距
st.markdown("<h2 style='margin: 10px 0 15px 0; color: #212529; text-align: center;'>🏛️ 华夏国宝私有化中心</h2>", unsafe_allow_html=True)

# 核心分栏：调整比例为2:8，缩小间距
col_museum_left, col_dashboard_right = st.columns([0.2, 0.8], gap="small")

# 左栏：博物馆选择器（简化容器样式，压缩内边距）
with col_museum_left:
    st.markdown("""<div style="background: #fff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); border: 1px solid #e9ecef;">""", unsafe_allow_html=True)
    selected_museum = st.radio(
        "选择博物馆",
        list(MANSION_CONFIG.keys()),
        index=list(MANSION_CONFIG.keys()).index(st.session_state.current_museum),
        horizontal=False,
        label_visibility="visible",
        key="museum_selector"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# 博物馆切换逻辑（保持不变）
if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.rerun()

# 右栏：仪表盘（简化渲染，压缩内边距）
with col_dashboard_right:
    def render_dashboard(current_revenue_display):
        m_info = MANSION_CONFIG[st.session_state.current_museum]
        villa_count = current_revenue_display / m_info["price"] if m_info["price"] > 0 else 0
        
        st.markdown('<div class="dashboard">', unsafe_allow_html=True)
        col1, col2 = st.columns([0.35, 0.65], gap="small")
        with col1:
            st.markdown(f"""
            <div style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 1.2rem; font-weight: 600; color: #212529; margin-bottom: 8px;">{st.session_state.current_museum}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #dc3545; margin-bottom: 5px;">
                    ¥{current_revenue_display / 100000000:.4f}亿
                </div>
                <div style="font-size: 0.7rem; color: #6c757d; text-transform: uppercase;">累计拍卖总额</div>
                <div style="font-size: 0.9rem; margin-top: 10px; color: #212529; font-weight: 500;">
                    可兑换 {villa_count:.2f} 套 {m_info['mansion_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div style="text-align: left; margin-bottom: 5px; color: #212529; font-size: 1rem; font-weight: 500;">🏠 {m_info['mansion_name']}</div>""", unsafe_allow_html=True)
            img_path = get_base64_image(m_info["mansion_img"]) if os.path.exists(m_info["mansion_img"]) else f"https://picsum.photos/seed/mansion_{st.session_state.current_museum}/400/200"
            st.markdown(f"""
            <div style="position: relative; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <img src="{img_path}" style="width: 100%; height: auto; display: block;" />
                <div style="position: absolute; bottom: 8px; right: 8px; color: #fff; background: rgba(0,0,0,0.7); padding: 6px 10px; border-radius: 6px; font-weight: 500; font-size: 0.8rem;">
                    × {villa_count:.2f} 套
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    render_dashboard(st.session_state.total_revenue)

# ==========================================
# 8. 明细面板（极简版：移除冗余HTML拼接，简化逻辑）
# ==========================================
def render_auction_detail():
    current_museum_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
    all_treasures = MUSEUM_TREASURES.get(current_museum_pinyin, [])
    sold_treasures = [t for t in all_treasures if t['id'] in st.session_state.sold_items]
    
    detail_html = [f'<div class="detail-panel">', f'  <div class="detail-title">{current_text["detail_title"]}</div>']
    if not sold_treasures:
        detail_html.append(f'  <div class="empty-detail">{current_text["detail_empty"]}</div>')
    else:
        detail_html.extend([
            f'  <table class="detail-table">',
            f'    <thead><tr>',
            f'      <th>{current_text["detail_col1"]}</th>',
            f'      <th>{current_text["detail_col2"]}</th>',
            f'      <th>{current_text["detail_col3"]}</th>',
            f'      <th>{current_text["detail_col4"]}</th>',
            f'    </tr></thead><tbody>'
        ])
        for treasure in sold_treasures:
            price_str = f"¥{format_price(treasure['price'])}"
            status = "✅ 已成交" if st.session_state.language == 'zh' else "✅ Sold"
            detail_html.append(f'      <tr><td>{treasure["name"]}</td><td>{treasure["period"]}</td><td class="sold-price">{price_str}</td><td>{status}</td></tr>')
        detail_html.extend([
            f'    </tbody></table>',
            f'  <div class="detail-summary">',
            f'    <div>{current_text["detail_summary_count"]} {len(sold_treasures)}</div>',
            f'    <div>{current_text["detail_summary_total"]} ¥{format_price(st.session_state.total_revenue)}</div>',
            f'  </div>'
        ])
    detail_html.append(f'</div>')
    st.markdown("\n".join(detail_html), unsafe_allow_html=True)

render_auction_detail()

# ==========================================
# 9. 拍卖动画（极简版：减少步骤，提升流畅度）
# ==========================================
def auction_animation(item_price, item_name, item_id):
    if item_id in st.session_state.sold_items:
        return
    start_revenue = st.session_state.total_revenue
    target_revenue = start_revenue + item_price
    steps = 10
    step_val = item_price / steps
    
    msg = st.toast(f"🔨 正在拍卖 {item_name}...", icon="⏳")
    for i in range(steps):
        with col_dashboard_right:
            render_dashboard(start_revenue + (step_val * (i + 1)))
        time.sleep(0.02)
    
    st.session_state.total_revenue = target_revenue
    st.session_state.sold_items.add(item_id)
    st.session_state.last_sold_id = item_id 
    msg.toast(f"✅ 成交！入账 ¥{format_price(item_price)}", icon="💰")
    time.sleep(0.5)
    st.rerun()

# ==========================================
# 10. 商品展示区（极简优化：调整列数为8列，压缩间距）
# ==========================================
current_museum_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
items = MUSEUM_TREASURES.get(current_museum_pinyin, [])

# 优化列数：更紧凑，8列布局
cols_per_row = 8 if len(items) >= 8 else len(items)
rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]

# 简化标题：减少间距
st.markdown(f"<h3 style='margin: 20px 0 12px 0; color: #212529;'>📜 {st.session_state.current_museum} 藏品列表</h3>", unsafe_allow_html=True)

for row_items in rows:
    cols = st.columns(cols_per_row, gap="small")
    for idx, item in enumerate(row_items):
        item_id = item['id']
        with cols[idx]:
            is_sold = item_id in st.session_state.sold_items
            display_price = f"¥{format_price(item['price'])}" if is_sold else "🕵️ 价值待揭晓"
            price_class = "t-price sold-price" if is_sold else "t-price unsold-price"
            if is_sold and item_id == st.session_state.get('last_sold_id'):
                price_class += " price-reveal"
            
            item_img = item.get('img', f"https://picsum.photos/seed/{item_id}/300/300")
            st.markdown(f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item_img}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
                </div>
                <div class="t-content">
                    <div class="t-title">{item['name']}</div>
                    <div class="t-period">{item.get('period', '古代')}</div>
                    <div class="t-desc" title="{item['desc']}">{item['desc']}</div>
                    <div class="{price_class}">{display_price}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 简化按钮文本
            if is_sold:
                st.button("🚫 已私有化", key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                if st.button("㊙ 立即拍卖", key=f"btn_{item_id}", type="primary", use_container_width=True):
                    auction_animation(item['price'], item['name'], item_id)

# ==========================================
# 11. 底部功能（极简版：移除多余分栏，压缩间距）
# ==========================================
st.write("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([0.3, 0.7], gap="small")

# 重置按钮
with c1:
    if st.button("🔄 重置数据", type="secondary", use_container_width=True):
        st.session_state.sold_items = set()
        st.session_state.total_revenue = 0
        st.session_state.last_sold_id = None
        st.rerun()

# 打赏按钮（简化弹窗内容）
with c2:
    @st.dialog("支持开发者", width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="text-align:center; color:#6c757d; margin-bottom:10px;">{current_text['coffee_desc']}</div>""", unsafe_allow_html=True)
        cnt = st.number_input(current_text['coffee_amount'], 1, 100, step=1, key='coffee_num')
        if st.button("🎉 确认打赏", type="primary", use_container_width=True):
            st.balloons()
            st.rerun()
    if st.button(current_text['coffee_btn'], use_container_width=True):
        show_coffee_window()

# ==========================================
# 12. 访问统计（极简版：保留核心功能）
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
    <div><div>今日 UV</div><div style="font-weight:600; color:#212529;">{today_uv}</div></div>
    <div><div>历史 UV</div><div style="font-weight:600; color:#212529;">{total_uv}</div></div>
</div>
""", unsafe_allow_html=True)

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

# 定义博物馆名称映射（中英双语）
MUSEUM_NAME_MAP = {
    "南京博物院": "Nanjing Museum",
    "三星堆博物馆": "Sanxingdui Museum",
    "中国国家博物馆": "National Museum of China",
    "上海博物馆": "Shanghai Museum",
    "陕西历史博物馆": "Shaanxi History Museum"
}
MUSEUM_NAME_MAP_PINYIN = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}
# 反向映射（拼音->中文）
MUSEUM_NAME_MAP_REVERSE = {v: k for k, v in MUSEUM_NAME_MAP_PINYIN.items()}

# 动态创建所有博物馆的图片目录
for museum_pinyin in MUSEUM_NAME_MAP_PINYIN.values():
    museum_img_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    os.makedirs(museum_img_dir, exist_ok=True)

# ==========================================
# 2. 核心数据（优化：图片路径容错、数据格式统一、中英双语）
# ==========================================
# 别墅配置（中英双语）
MANSION_CONFIG = {
    "南京博物院": {
        "mansion_name_zh": "颐和路民国别墅",
        "mansion_name_en": "Republic of China Villa on Yihe Road",
        "price": 100000000,
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "1.jpeg")  # 绝对路径更稳定
    },
    "三星堆博物馆": {
        "mansion_name_zh": "成都麓山国际豪宅",
        "mansion_name_en": "Chengdu Lushan International Luxury Mansion",
        "price": 50000000,
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "5.jpeg")
    },
    "中国国家博物馆": {
        "mansion_name_zh": "什刹海四合院",
        "mansion_name_en": "Shichahai Courtyard House",
        "price": 150000000,
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "2.jpeg")
    },
    "上海博物馆": {
        "mansion_name_zh": "愚园路老洋房",
        "mansion_name_en": "Old Western-style House on Yuyuan Road",
        "price": 200000000,
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "3.jpeg")
    },
    "陕西历史博物馆": {
        "mansion_name_zh": "曲江池畔大平层",
        "mansion_name_en": "Large Flat by Qujiang Pool",
        "price": 3000000,
        "mansion_img": os.path.join(MANSION_IMG_ROOT, "4.jpeg")
    }
}

# 藏品数据（中英双语：名称、年代、描述）
MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name_zh": "金兽", "name_en": "Golden Beast", "period_zh": "西汉", "period_en": "Western Han Dynasty", "desc_zh": "含金量99%，最重金器", "desc_en": "99% gold content, the heaviest gold artifact", "price": 500000000, "img": ""},
        {"id": "nj_2", "name_zh": "釉里红梅瓶", "name_en": "Underglaze Red Plum Vase", "period_zh": "明洪武", "period_en": "Hongwu Period, Ming Dynasty", "desc_zh": "现存唯一带盖梅瓶", "desc_en": "The only existing plum vase with a cover", "price": 800000000, "img": ""},
        {"id": "nj_3", "name_zh": "金蝉玉叶", "name_en": "Golden Cicada on Jade Leaf", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "金枝玉叶，工艺精湛", "desc_en": "Exquisite craftsmanship of gold and jade", "price": 90000000, "img": ""},
        {"id": "nj_4", "name_zh": "银缕玉衣", "name_en": "Silver-thread Jade Burial Suit", "period_zh": "东汉", "period_en": "Eastern Han Dynasty", "desc_zh": "银丝编缀，极其罕见", "desc_en": "Woven with silver threads, extremely rare", "price": 300000000, "img": ""},
        {"id": "nj_5", "name_zh": "竹林七贤砖画", "name_en": "Brick Painting of the Seven Sages of the Bamboo Grove", "period_zh": "南朝", "period_en": "Southern Dynasties", "desc_zh": "魏晋风度最佳见证", "desc_en": "The best witness of Wei and Jin demeanor", "price": 1000000000, "img": ""},
        {"id": "nj_6", "name_zh": "大报恩寺拱门", "name_en": "Gate Arch of the Great Bao'en Temple", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "世界奇迹残留组件", "desc_en": "Remaining component of a world wonder", "price": 200000000, "img": ""},
        {"id": "nj_7", "name_zh": "坤舆万国全图", "name_en": "Kunyu Wanguo Quantu (Universal Map)", "period_zh": "明万历", "period_en": "Wanli Period, Ming Dynasty", "desc_zh": "最早彩绘世界地图", "desc_en": "The earliest colored world map", "price": 600000000, "img": ""},
        {"id": "nj_8", "name_zh": "广陵王玺", "name_en": "Seal of the Prince of Guangling", "period_zh": "东汉", "period_en": "Eastern Han Dynasty", "desc_zh": "汉代封王金印精品", "desc_en": "Exquisite gold seal of a Han Dynasty prince", "price": 200000000, "img": ""},
        {"id": "nj_9", "name_zh": "错银铜牛灯", "name_en": "Silver-Inlaid Bronze Ox Lamp", "period_zh": "东汉", "period_en": "Eastern Han Dynasty", "desc_zh": "汉代环保黑科技", "desc_en": "Environmental protection technology of the Han Dynasty", "price": 180000000, "img": ""},
        {"id": "nj_10", "name_zh": "青瓷神兽尊", "name_en": "Celadon Beast Zun", "period_zh": "西晋", "period_en": "Western Jin Dynasty", "desc_zh": "造型奇特的早期青瓷", "desc_en": "Early celadon with a strange shape", "price": 120000000, "img": ""},
        {"id": "nj_11", "name_zh": "透雕人鸟兽玉饰", "name_en": "Openwork Jade Ornament of Human, Bird and Beast", "period_zh": "良渚", "period_en": "Liangzhu Culture", "desc_zh": "史前玉器巅峰", "desc_en": "Peak of prehistoric jade artifacts", "price": 60000000, "img": ""},
        {"id": "nj_12", "name_zh": "鎏金喇嘛塔", "name_en": "Gilded Lama Pagoda", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "通体鎏金镶宝石", "desc_en": "Entirely gilded and inlaid with gems", "price": 80000000, "img": ""},
        {"id": "nj_13", "name_zh": "青花寿山福海炉", "name_en": "Blue and White Censer with Longevity Mountain and Fortune Sea", "period_zh": "明宣德", "period_en": "Xuande Period, Ming Dynasty", "desc_zh": "宣德官窑完整大器", "desc_en": "Complete large official kiln work of Xuande Period", "price": 450000000, "img": ""},
        {"id": "nj_14", "name_zh": "徐渭《杂花图》", "name_en": "Xu Wei's 'Miscellaneous Flowers Painting'", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "大写意花鸟巅峰", "desc_en": "Peak of freehand flower and bird painting", "price": 350000000, "img": ""},
        {"id": "nj_15", "name_zh": "沈寿《耶稣像》", "name_en": "Shen Shou's 'Portrait of Jesus'", "period_zh": "清代", "period_en": "Qing Dynasty", "desc_zh": "苏绣艺术的巅峰之作", "desc_en": "Masterpiece of Suzhou embroidery art", "price": 180000000, "img": ""},
        {"id": "nj_16", "name_zh": "芙蓉石蟠螭炉", "name_en": "Rose Quartz Censer with Coiled Chi Dragon", "period_zh": "清乾隆", "period_en": "Qianlong Period, Qing Dynasty", "desc_zh": "乾隆御用粉嫩玉石", "desc_en": "Pastel jade used by Emperor Qianlong", "price": 130000000, "img": ""},
        {"id": "nj_17", "name_zh": "人面兽面玉琮", "name_en": "Jade Cong with Human and Beast Faces", "period_zh": "良渚", "period_en": "Liangzhu Culture", "desc_zh": "微雕工艺神作", "desc_en": "Masterpiece of miniature carving technology", "price": 150000000, "img": ""},
        {"id": "nj_18", "name_zh": "青瓷釉下彩壶", "name_en": "Celadon Pot with Underglaze Color", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "改写陶瓷史的孤品", "desc_en": "Unique piece that rewrote ceramic history", "price": 110000000, "img": ""},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name_zh": "青铜大立人", "name_en": "Giant Bronze Standing Figure", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "世界铜像之王", "desc_en": "King of world bronze statues", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/300/300"},
        {"id": "sx_2", "name_zh": "青铜神树", "name_en": "Bronze Sacred Tree", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "通天神树", "desc_en": "Heaven-reaching sacred tree", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/300/300"},
        {"id": "sx_3", "name_zh": "金面具", "name_en": "Golden Mask", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "半张黄金脸", "desc_en": "Half a golden face", "price": 800000000, "img": "https://picsum.photos/seed/sx3/300/300"},
        {"id": "sx_4", "name_zh": "青铜纵目面具", "name_en": "Bronze Mask with Protruding Eyes", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "千里眼顺风耳", "desc_en": "Eyes that see far and ears that hear well", "price": 1200000000, "img": "https://picsum.photos/seed/sx4/300/300"},
        {"id": "sx_5", "name_zh": "太阳轮", "name_en": "Sun Wheel", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "形似方向盘", "desc_en": "Shaped like a steering wheel", "price": 600000000, "img": "https://picsum.photos/seed/sx5/300/300"},
        {"id": "sx_6", "name_zh": "玉璋", "name_en": "Jade Zhang", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "祭祀山川礼器", "desc_en": "Ritual vessel for worshipping mountains and rivers", "price": 300000000, "img": "https://picsum.photos/seed/sx6/300/300"},
        {"id": "sx_7", "name_zh": "黄金权杖", "name_en": "Golden Scepter", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "王权的象征", "desc_en": "Symbol of royal power", "price": 1500000000, "img": "https://picsum.photos/seed/sx7/300/300"},
        {"id": "sx_8", "name_zh": "青铜神坛", "name_en": "Bronze Sacred Altar", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "复杂祭祀场景", "desc_en": "Complex sacrificial scene", "price": 900000000, "img": "https://picsum.photos/seed/sx8/300/300"},
        {"id": "sx_9", "name_zh": "戴金面罩铜人", "name_en": "Bronze Figure with Golden Mask", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "金光闪闪祭司", "desc_en": "Shining golden priest", "price": 500000000, "img": "https://picsum.photos/seed/sx9/300/300"},
        {"id": "sx_10", "name_zh": "青铜鸟", "name_en": "Bronze Bird", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "神鸟图腾", "desc_en": "Sacred bird totem", "price": 150000000, "img": "https://picsum.photos/seed/sx10/300/300"},
        {"id": "sx_11", "name_zh": "陶猪", "name_en": "Pottery Pig", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "愤怒小鸟同款", "desc_en": "Same style as Angry Birds", "price": 50000000, "img": "https://picsum.photos/seed/sx11/300/300"},
        {"id": "sx_12", "name_zh": "青铜大鸟", "name_en": "Giant Bronze Bird", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "体型巨大神兽", "desc_en": "Giant mythical beast", "price": 400000000, "img": "https://picsum.photos/seed/sx12/300/300"},
        {"id": "sx_13", "name_zh": "青铜爬龙柱", "name_en": "Bronze Column with Coiled Dragon", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "龙形神柱", "desc_en": "Dragon-shaped sacred column", "price": 650000000, "img": "https://picsum.photos/seed/sx13/300/300"},
        {"id": "sx_14", "name_zh": "人身鸟脚像", "name_en": "Figure with Human Body and Bird Feet", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "半人半鸟", "desc_en": "Half human, half bird", "price": 550000000, "img": "https://picsum.photos/seed/sx14/300/300"},
        {"id": "sx_15", "name_zh": "顶尊跪坐人像", "name_en": "Kneeling Figure with Zun on Head", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "国宝级重器", "desc_en": "National treasure-level heavy artifact", "price": 1100000000, "img": "https://picsum.photos/seed/sx15/300/300"},
        {"id": "sx_16", "name_zh": "青铜蛇", "name_en": "Bronze Snake", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "造型逼真", "desc_en": "Realistic shape", "price": 120000000, "img": "https://picsum.photos/seed/sx16/300/300"},
        {"id": "sx_17", "name_zh": "青铜鸡", "name_en": "Bronze Rooster", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "雄鸡一唱", "desc_en": "The rooster crows", "price": 80000000, "img": "https://picsum.photos/seed/sx17/300/300"},
        {"id": "sx_18", "name_zh": "玉琮", "name_en": "Jade Cong", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "良渚文化影响", "desc_en": "Influenced by Liangzhu Culture", "price": 200000000, "img": "https://picsum.photos/seed/sx18/300/300"},
    ],
    "beijing": [
        {"id": "bj_1", "name_zh": "清明上河图", "name_en": "Along the River During the Qingming Festival", "period_zh": "北宋", "period_en": "Northern Song Dynasty", "desc_zh": "中华第一神品", "desc_en": "The first divine work of China", "price": 5000000000, "img": "https://picsum.photos/seed/bj1/300/300"},
        {"id": "bj_2", "name_zh": "金瓯永固杯", "name_en": "Golden Cup of Eternal National Prosperity", "period_zh": "清乾隆", "period_en": "Qianlong Period, Qing Dynasty", "desc_zh": "乾隆御用金杯", "desc_en": "Golden cup used by Emperor Qianlong", "price": 600000000, "img": "https://picsum.photos/seed/bj2/300/300"},
        {"id": "bj_3", "name_zh": "后母戊鼎", "name_en": "Houmuwu Ding", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "青铜之王", "desc_en": "King of bronzes", "price": 4000000000, "img": "https://picsum.photos/seed/bj3/300/300"},
        {"id": "bj_4", "name_zh": "千里江山图", "name_en": "A Thousand Li of Rivers and Mountains", "period_zh": "北宋", "period_en": "Northern Song Dynasty", "desc_zh": "青绿山水巅峰", "desc_en": "Peak of blue and green landscape painting", "price": 3000000000, "img": "https://picsum.photos/seed/bj4/300/300"},
        {"id": "bj_5", "name_zh": "四羊方尊", "name_en": "Four-Goat Square Zun", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "青铜铸造奇迹", "desc_en": "Miracle of bronze casting", "price": 2000000000, "img": "https://picsum.photos/seed/bj5/300/300"},
        {"id": "bj_6", "name_zh": "孝端皇后凤冠", "name_en": "Phoenix Crown of Empress Xiaoduan", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "点翠工艺巅峰", "desc_en": "Peak of kingfisher feather inlay craft", "price": 500000000, "img": "https://picsum.photos/seed/bj6/300/300"},
        {"id": "bj_7", "name_zh": "金缕玉衣", "name_en": "Gold-thread Jade Burial Suit", "period_zh": "西汉", "period_en": "Western Han Dynasty", "desc_zh": "中山靖王同款", "desc_en": "Same style as the Prince of Zhongshan Jing", "price": 1000000000, "img": "https://picsum.photos/seed/bj7/300/300"},
        {"id": "bj_8", "name_zh": "红山玉龙", "name_en": "Hongshan Jade Dragon", "period_zh": "新石器", "period_en": "Neolithic Age", "desc_zh": "中华第一龙", "desc_en": "The first dragon of China", "price": 1200000000, "img": "https://picsum.photos/seed/bj8/300/300"},
        {"id": "bj_9", "name_zh": "击鼓说唱俑", "name_en": "Drum-Beating Storytelling Figurine", "period_zh": "东汉", "period_en": "Eastern Han Dynasty", "desc_zh": "汉代幽默感", "desc_en": "Sense of humor in the Han Dynasty", "price": 300000000, "img": "https://picsum.photos/seed/bj9/300/300"},
        {"id": "bj_10", "name_zh": "人面鱼纹盆", "name_en": "Basin with Human-Fish Pattern", "period_zh": "仰韶", "period_en": "Yangshao Culture", "desc_zh": "史前文明微笑", "desc_en": "Smile of prehistoric civilization", "price": 250000000, "img": "https://picsum.photos/seed/bj10/300/300"},
        {"id": "bj_11", "name_zh": "大盂鼎", "name_en": "Great Yu Ding", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "铭文极其珍贵", "desc_en": "Extremely precious inscriptions", "price": 1800000000, "img": "https://picsum.photos/seed/bj11/300/300"},
        {"id": "bj_12", "name_zh": "虢季子白盘", "name_en": "Guo Jizi Bai Plate", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "晚清出土重器", "desc_en": "Heavy artifact unearthed in the late Qing Dynasty", "price": 1600000000, "img": "https://picsum.photos/seed/bj12/300/300"},
        {"id": "bj_13", "name_zh": "霁蓝白龙梅瓶", "name_en": "Blue Glaze Plum Vase with White Dragon", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "元代顶级瓷器", "desc_en": "Top-grade porcelain of the Yuan Dynasty", "price": 800000000, "img": "https://picsum.photos/seed/bj13/300/300"},
        {"id": "bj_14", "name_zh": "郎世宁百骏图", "name_en": "Giuseppe Castiglione's 'Hundred Horses'", "period_zh": "清代", "period_en": "Qing Dynasty", "desc_zh": "中西合璧", "desc_en": "Combination of Chinese and Western art", "price": 600000000, "img": "https://picsum.photos/seed/bj14/300/300"},
        {"id": "bj_15", "name_zh": "五牛图", "name_en": "Five Oxen Painting", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "韩滉传世孤本", "desc_en": "Only surviving work by Han Huang", "price": 900000000, "img": "https://picsum.photos/seed/bj15/300/300"},
        {"id": "bj_16", "name_zh": "步辇图", "name_en": "Portrait of the Emperor Receiving the Tibetan Envoy", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "阎立本绘", "desc_en": "Painted by Yan Liben", "price": 800000000, "img": "https://picsum.photos/seed/bj16/300/300"},
        {"id": "bj_17", "name_zh": "利簋", "name_en": "Li Gui", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "记录武王伐纣", "desc_en": "Records King Wu's conquest of Zhou", "price": 700000000, "img": "https://picsum.photos/seed/bj17/300/300"},
        {"id": "bj_18", "name_zh": "鹳鱼石斧陶缸", "name_en": "Pottery Vat with Stork, Fish and Stone Axe", "period_zh": "仰韶", "period_en": "Yangshao Culture", "desc_zh": "绘画史第一页", "desc_en": "First page of Chinese painting history", "price": 400000000, "img": "https://picsum.photos/seed/bj18/300/300"},
    ],
    "shanghai": [
        {"id": "sh_1", "name_zh": "大克鼎", "name_en": "Great Ke Ding", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "海内三宝之一", "desc_en": "One of the three national treasures", "price": 1500000000, "img": "https://picsum.photos/seed/sh1/300/300"},
        {"id": "sh_2", "name_zh": "晋侯苏钟", "name_en": "Marquis Jin Su Bells", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "铭文刻在钟表", "desc_en": "Inscriptions carved on bells", "price": 800000000, "img": "https://picsum.photos/seed/sh2/300/300"},
        {"id": "sh_3", "name_zh": "孙位高逸图", "name_en": "Sun Wei's 'Portrait of Recluses'", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "唐代人物画孤本", "desc_en": "Only surviving figure painting of the Tang Dynasty", "price": 1200000000, "img": "https://picsum.photos/seed/sh3/300/300"},
        {"id": "sh_4", "name_zh": "越王剑", "name_en": "Sword of the Yue King", "period_zh": "春秋", "period_en": "Spring and Autumn Period", "desc_zh": "虽不如勾践剑", "desc_en": "Not as famous as Gou Jian's sword", "price": 300000000, "img": "https://picsum.photos/seed/sh4/300/300"},
        {"id": "sh_5", "name_zh": "粉彩蝠桃纹瓶", "name_en": "Famille Rose Vase with Bat and Peach Pattern", "period_zh": "清雍正", "period_en": "Yongzheng Period, Qing Dynasty", "desc_zh": "雍正官窑极品", "desc_en": "Top-grade official kiln work of Yongzheng Period", "price": 400000000, "img": "https://picsum.photos/seed/sh5/300/300"},
        {"id": "sh_6", "name_zh": "王羲之上虞帖", "name_en": "Wang Xizhi's 'Shangyu Tie'", "period_zh": "唐摹本", "period_en": "Tang Dynasty Copy", "desc_zh": "书圣墨宝", "desc_en": "Treasure of the Sage of Calligraphy", "price": 2000000000, "img": "https://picsum.photos/seed/sh6/300/300"},
        {"id": "sh_7", "name_zh": "苦笋帖", "name_en": "Bitter Bamboo Shoot Tie", "period_zh": "唐怀素", "period_en": "Huaisu, Tang Dynasty", "desc_zh": "草书狂僧真迹", "desc_en": "Authentic work of the wild cursive calligrapher", "price": 1000000000, "img": "https://picsum.photos/seed/sh7/300/300"},
        {"id": "sh_8", "name_zh": "青花瓶", "name_en": "Blue and White Vase", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "元青花存世稀少", "desc_en": "Rare surviving Yuan blue and white porcelain", "price": 600000000, "img": "https://picsum.photos/seed/sh8/300/300"},
        {"id": "sh_9", "name_zh": "子仲姜盘", "name_en": "Zizhong Jiang Plate", "period_zh": "春秋", "period_en": "Spring and Autumn Period", "desc_zh": "盘内动物可旋转", "desc_en": "Animals in the plate can rotate", "price": 500000000, "img": "https://picsum.photos/seed/sh9/300/300"},
        {"id": "sh_10", "name_zh": "牺尊", "name_en": "Animal-shaped Zun", "period_zh": "春秋", "period_en": "Spring and Autumn Period", "desc_zh": "极具神韵的牛形", "desc_en": "Vivid ox-shaped sculpture", "price": 350000000, "img": "https://picsum.photos/seed/sh10/300/300"},
        {"id": "sh_11", "name_zh": "商鞅方升", "name_en": "Shang Yang's Measuring Vessel", "period_zh": "战国", "period_en": "Warring States Period", "desc_zh": "统一度量衡", "desc_en": "Unified weights and measures", "price": 1500000000, "img": "https://picsum.photos/seed/sh11/300/300"},
        {"id": "sh_12", "name_zh": "曹全碑", "name_en": "Cao Quan Stele", "period_zh": "东汉", "period_en": "Eastern Han Dynasty", "desc_zh": "汉代隶书巅峰", "desc_en": "Peak of Han Dynasty clerical script", "price": 450000000, "img": "https://picsum.photos/seed/sh12/300/300"},
        {"id": "sh_13", "name_zh": "哥窑五足洗", "name_en": "Ge Kiln Five-foot Washer", "period_zh": "南宋", "period_en": "Southern Song Dynasty", "desc_zh": "金丝铁线", "desc_en": "Golden threads and iron wires (crackle pattern)", "price": 300000000, "img": "https://picsum.photos/seed/sh13/300/300"},
        {"id": "sh_14", "name_zh": "透雕神兽玉璧", "name_en": "Openwork Jade Bi with Mythical Beasts", "period_zh": "西汉", "period_en": "Western Han Dynasty", "desc_zh": "汉代玉器巅峰", "desc_en": "Peak of Han Dynasty jade artifacts", "price": 200000000, "img": "https://picsum.photos/seed/sh14/300/300"},
        {"id": "sh_15", "name_zh": "剔红花卉纹盘", "name_en": "Red Carved Lacquer Plate with Flower Pattern", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "张成造，漆器孤品", "desc_en": "Made by Zhang Cheng, unique lacquerware", "price": 120000000, "img": "https://picsum.photos/seed/sh15/300/300"},
        {"id": "sh_16", "name_zh": "苏轼舣舟亭图", "name_en": "Su Shi's 'Yizhou Pavilion Painting'", "period_zh": "清代", "period_en": "Qing Dynasty", "desc_zh": "乾隆御览之宝", "desc_en": "Treasure reviewed by Emperor Qianlong", "price": 250000000, "img": "https://picsum.photos/seed/sh16/300/300"},
        {"id": "sh_17", "name_zh": "青花牡丹纹罐", "name_en": "Blue and White Jar with Peony Pattern", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "元青花大器", "desc_en": "Large Yuan blue and white porcelain jar", "price": 550000000, "img": "https://picsum.photos/seed/sh17/300/300"},
        {"id": "sh_18", "name_zh": "缂丝莲塘乳鸭", "name_en": "Kesi Silk with Lotus Pond and Ducklings", "period_zh": "南宋", "period_en": "Southern Song Dynasty", "desc_zh": "缂丝工艺巅峰", "desc_en": "Peak of Kesi silk weaving craft", "price": 800000000, "img": "https://picsum.photos/seed/sh18/300/300"},
    ],
    "xian": [
        {"id": "xa_1", "name_zh": "兽首玛瑙杯", "name_en": "Agate Cup with Animal Head", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "海内孤品", "desc_en": "Unique domestic artifact", "price": 2000000000, "img": "https://picsum.photos/seed/xa1/300/300"},
        {"id": "xa_2", "name_zh": "舞马衔杯银壶", "name_en": "Silver Pot with Dancing Horse Holding Cup", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "大唐盛世缩影", "desc_en": "Epitome of the prosperous Tang Dynasty", "price": 800000000, "img": "https://picsum.photos/seed/xa2/300/300"},
        {"id": "xa_3", "name_zh": "皇后之玺", "name_en": "Seal of the Empress", "period_zh": "西汉", "period_en": "Western Han Dynasty", "desc_zh": "吕后之印", "desc_en": "Seal of Empress Lü Zhi", "price": 1000000000, "img": "https://picsum.photos/seed/xa3/300/300"},
        {"id": "xa_4", "name_zh": "兵马俑(跪射)", "name_en": "Terracotta Warrior (Kneeling Archer)", "period_zh": "秦代", "period_en": "Qin Dynasty", "desc_zh": "保存最完整", "desc_en": "Best preserved", "price": 3000000000, "img": "https://picsum.photos/seed/xa4/300/300"},
        {"id": "xa_5", "name_zh": "葡萄花鸟香囊", "name_en": "Incense Sachet with Grape, Flower and Bird", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "杨贵妃同款", "desc_en": "Same style as Yang Guifei's", "price": 500000000, "img": "https://picsum.photos/seed/xa5/300/300"},
        {"id": "xa_6", "name_zh": "鎏金铜蚕", "name_en": "Gilded Bronze Silkworm", "period_zh": "西汉", "period_en": "Western Han Dynasty", "desc_zh": "丝绸之路见证", "desc_en": "Witness of the Silk Road", "price": 300000000, "img": "https://picsum.photos/seed/xa6/300/300"},
        {"id": "xa_7", "name_zh": "独孤信印", "name_en": "Du Gu Xin's Seal", "period_zh": "西魏", "period_en": "Western Wei Dynasty", "desc_zh": "多面体印章", "desc_en": "Multi-faceted seal", "price": 400000000, "img": "https://picsum.photos/seed/xa7/300/300"},
        {"id": "xa_8", "name_zh": "提梁倒注壶", "name_en": "Handle Pot with Inverted Pouring", "period_zh": "五代", "period_en": "Five Dynasties", "desc_zh": "神奇倒注构造", "desc_en": "Magical inverted pouring structure", "price": 200000000, "img": "https://picsum.photos/seed/xa8/300/300"},
        {"id": "xa_9", "name_zh": "鸳鸯纹金碗", "name_en": "Golden Bowl with Mandarin Duck Pattern", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "金银器巅峰", "desc_en": "Peak of gold and silver artifacts", "price": 600000000, "img": "https://picsum.photos/seed/xa9/300/300"},
        {"id": "xa_10", "name_zh": "三彩骆驼俑", "name_en": "Tri-color Glazed Camel Figurine", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "丝路乐队", "desc_en": "Silk Road band", "price": 450000000, "img": "https://picsum.photos/seed/xa10/300/300"},
        {"id": "xa_11", "name_zh": "阙楼仪仗图", "name_en": "Tower and Guard of Honor Painting", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "懿德太子墓", "desc_en": "Tomb of Prince Yide", "price": 1500000000, "img": "https://picsum.photos/seed/xa11/300/300"},
        {"id": "xa_12", "name_zh": "鎏金铜龙", "name_en": "Gilded Bronze Dragon", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "气势磅礴", "desc_en": "Majestic momentum", "price": 350000000, "img": "https://picsum.photos/seed/xa12/300/300"},
        {"id": "xa_13", "name_zh": "杜虎符", "name_en": "Du Hu Tally", "period_zh": "战国", "period_en": "Warring States Period", "desc_zh": "调兵遣将信物", "desc_en": "Token for mobilizing troops", "price": 500000000, "img": "https://picsum.photos/seed/xa13/300/300"},
        {"id": "xa_14", "name_zh": "何尊", "name_en": "He Zun", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "最早出现'中国'", "desc_en": "First appearance of 'China' in inscriptions", "price": 2500000000, "img": "https://picsum.photos/seed/xa14/300/300"},
        {"id": "xa_15", "name_zh": "多友鼎", "name_en": "Duoyou Ding", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "铭文记录战争", "desc_en": "Inscriptions recording wars", "price": 800000000, "img": "https://picsum.photos/seed/xa15/300/300"},
        {"id": "xa_16", "name_zh": "日己觥", "name_en": "Riji Gong", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "造型奇特酒器", "desc_en": "Wine vessel with a strange shape", "price": 400000000, "img": "https://picsum.photos/seed/xa16/300/300"},
        {"id": "xa_17", "name_zh": "雁鱼铜灯", "name_en": "Bronze Lamp with Wild Goose and Fish", "period_zh": "西汉", "period_en": "Western Han Dynasty", "desc_zh": "环保美学结合", "desc_en": "Combination of environmental protection and aesthetics", "price": 550000000, "img": "https://picsum.photos/seed/xa17/300/300"},
        {"id": "xa_18", "name_zh": "金怪兽", "name_en": "Golden Monster", "period_zh": "战国", "period_en": "Warring States Period", "desc_zh": "匈奴文化代表", "desc_en": "Representative of Xiongnu culture", "price": 200000000, "img": "https://picsum.photos/seed/xa18/300/300"},
    ]
}

# ==========================================
# 3. 工具函数（优化：增加图片占位、容错增强、双语价格格式化）
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

def format_price(price, lang='zh'):
    """格式化价格显示（亿/万单位转换，中英双语）"""
    if price >= 100000000:
        if lang == 'zh':
            return f"{price/100000000:.1f}亿"
        else:
            return f"{price/100000000:.1f} Billion"
    elif price >= 10000:
        if lang == 'zh':
            return f"{price/10000:.0f}万"
        else:
            return f"{price/10000:.0f} Ten Thousand"
    return str(price)

# ==========================================
# 4. 通用图片加载逻辑（优化：占位图统一、容错更强）
# ==========================================
for museum_cn, museum_pinyin in MUSEUM_NAME_MAP_PINYIN.items():
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

    /* --- 别墅图片容器样式 --- */
    .mansion-img-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .mansion-overlay-text {
        position: absolute;
        bottom: 10px;
        right: 10px;
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
if 'has_counted' not in st.session_state: st.session_state["has_counted"] = False

# 语言包（全面扩充，适配所有界面元素）
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
        'detail_summary_count': '成交藏品数量：',
        'main_title': '🏛️ 华夏国宝私有化中心',
        'museum_selector_label': '选择博物馆',
        'collection_list_title': '📜 {} 藏品列表',
        'purchasing_power': '当前财富购买力：<br>× {} 套',
        'value_to_be_revealed': '🕵️ 价值待揭晓',
        'already_sold': '🚫 已私有化',
        'auction_now': '㊙ 立即拍卖',
        'reset': '🔄 破产/重置',
        'ancient': '古代',
        'auctioning': '🔨 正在拍卖 {}...',
        'auction_success': '✅ 成交！入账 ¥{}',
        'today_uv': '今日 UV',
        'total_uv': '历史 UV'
    },
    'en': {
        'coffee_desc': 'If this game helps you, your support is appreciated.', 
        'coffee_btn': "☕ Buy me a coffee", 
        'coffee_title': " ", 
        'coffee_amount': "Enter the number of coffees to donate", 
        'pay_success': "Received! Thank you for your support. ❤️",
        'pay_wechat': 'WeChat Pay',
        'pay_alipay': 'Alipay',
        'pay_paypal': 'PayPal',
        'presets': [("☕ Refresh", 1), ("🍗 Meal", 3), ("🚀 Sustain", 5)],
        'detail_title': '📋 Auction Transaction Details',
        'detail_col1': 'Treasure Name',
        'detail_col2': 'Period',
        'detail_col3': 'Transaction Price',
        'detail_col4': 'Status',
        'detail_empty': 'No transaction records yet, go auction your first national treasure!',
        'detail_summary_total': 'Total Transaction Amount：',
        'detail_summary_count': 'Number of Sold Treasures：',
        'main_title': '🏛️ Chinese National Treasures Privatization Center',
        'museum_selector_label': 'Select Museum',
        'collection_list_title': '📜 {} Collection List',
        'purchasing_power': 'Current Wealth Purchasing Power：<br>× {} Sets',
        'value_to_be_revealed': '🕵️ Value to be revealed',
        'already_sold': '🚫 Already Sold',
        'auction_now': '㊙ Auction Now',
        'reset': '🔄 Reset',
        'ancient': 'Ancient',
        'auctioning': '🔨 Auctioning {}...',
        'auction_success': '✅ Sold! Revenue ¥{}',
        'today_uv': 'Today UV',
        'total_uv': 'Total UV'
    }
}
current_text = lang_texts[st.session_state.language]
current_lang = st.session_state.language

# ==========================================
# 7. 顶部功能区（优化：排版更紧凑、视觉更协调、双语适配）
# ==========================================
# 顶部操作栏：语言切换 + 更多应用
col_top_1, col_top_2, col_top_3 = st.columns([0.8, 0.1, 0.1])
with col_top_2:
    l_btn = "En" if current_lang == 'zh' else "中"
    if st.button(l_btn, key="lang_switch", use_container_width=True):
        st.session_state.language = 'en' if current_lang == 'zh' else 'zh'
        st.rerun()

with col_top_3:
    st.markdown("""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ More</button>
        </a>""", unsafe_allow_html=True)

# 标题 + 博物馆选择器
st.markdown(f"<h2 style='margin-top: 15px; margin-bottom: 20px; color: #111; text-align: center;'>{current_text['main_title']}</h2>", unsafe_allow_html=True)

# 优化：博物馆选择器居中显示
col_museum_2, col_museum_3 = st.columns([0.6, 0.2])

m_info = MANSION_CONFIG[st.session_state.current_museum]
# 获取别墅名称（双语）
mansion_name = m_info[f"mansion_name_{current_lang}"]
villa_count = st.session_state.total_revenue / m_info["price"] if m_info["price"] > 0 else 0  # 避免除零错误

with col_museum_2:
    # 博物馆选项（双语显示）
    museum_options = [f"{cn} | {en}" for cn, en in MUSEUM_NAME_MAP.items()]
    museum_cn_list = list(MUSEUM_NAME_MAP.keys())
    current_museum_index = museum_cn_list.index(st.session_state.current_museum)
    current_museum_option = museum_options[current_museum_index]
    
    selected_museum_option = st.radio(
        current_text['museum_selector_label'],
        museum_options,
        index=current_museum_index,
        horizontal=True,
        label_visibility="collapsed",
        key="museum_selector"
    )
    # 解析选中的博物馆中文名称
    selected_museum_cn = selected_museum_option.split(" | ")[0]

with col_museum_3:
    # 右侧图片 + 叠加文本（修复：绝对定位更稳定）
    img_container = st.container()
    with img_container:
        # 图片容错：如果本地图片不存在，使用占位图
        if os.path.exists(m_info["mansion_img"]):
            img_path = m_info["mansion_img"]
        else:
            img_path = f"https://picsum.photos/seed/mansion_{st.session_state.current_museum}/400/250"
        
        # 2. 再放图片（去掉 caption 参数）
        st.image(
            img_path,
            width=400,
            use_column_width=True
        )
        
        # 修复：叠加文本定位，避免错位
   
        purchasing_power_text = current_text['purchasing_power'].format(f"{villa_count:.2f}")
        st.markdown(f"""
        <div class="mansion-overlay-text">
            {purchasing_power_text} {mansion_name}
        </div>
        """, unsafe_allow_html=True)

if selected_museum_cn != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum_cn
    st.rerun()

# ==========================================
# 8. 明细面板置顶（核心修复：表格列数匹配、语言包适配、双语藏品信息）
# ==========================================
def render_auction_detail():
    """渲染拍卖成交明细面板，放置在页面上部核心位置"""
    current_museum_pinyin = MUSEUM_NAME_MAP_PINYIN[st.session_state.current_museum]
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
            # 藏品信息（双语）
            treasure_name = treasure[f"name_{current_lang}"]
            treasure_period = treasure[f"period_{current_lang}"]
            price_str = f"¥{format_price(treasure['price'], current_lang)}"
            status = "✅ 已成交" if current_lang == 'zh' else "✅ Sold"
            detail_html.append(f'      <tr>')
            detail_html.append(f'        <td>{treasure_name}</td>')
            detail_html.append(f'        <td>{treasure_period}</td>')
            detail_html.append(f'        <td class="sold-price">{price_str}</td>')
            detail_html.append(f'        <td>{status}</td>')
            detail_html.append(f'      </tr>')
        
        detail_html.append(f'    </tbody>')
        detail_html.append(f'  </table>')
        
        # 明细汇总
        total_count = len(sold_treasures)
        total_amount = f"¥{format_price(st.session_state.total_revenue, current_lang)}"
        detail_html.append(f'  <div class="detail-summary">')
        detail_html.append(f'    <div>{current_text["detail_summary_count"]} {total_count}</div>')
        detail_html.append(f'    <div style="font-size: 1.8rem; font-weight: 900; color: #d9534f; margin-bottom: 8px;">{current_text["detail_summary_total"]} {total_amount}</div>')
        detail_html.append(f'  </div>')
    
    detail_html.append(f'</div>')
    final_html = "\n".join(detail_html)
    st.markdown(final_html, unsafe_allow_html=True)

# 执行明细面板渲染
render_auction_detail()

# ==========================================
# 9. 仪表盘渲染（补充缺失的函数，适配双语）
# ==========================================
def render_dashboard(current_revenue):
    """渲染仪表盘（显示当前收益）"""
    revenue_str = f"¥{format_price(current_revenue, current_lang)}"
    dashboard_html = f"""
    <div class="dashboard">
        <div style="font-size: 1.5rem; font-weight: 700; color: #d9534f;">
            {current_text['detail_summary_total']} {revenue_str}
        </div>
    </div>
    """
    st.markdown(dashboard_html, unsafe_allow_html=True)

# ==========================================
# 10. 拍卖动画（优化：减少重渲染，提升流畅度、双语提示）
# ==========================================
def auction_animation(item_price, item_name, item_id):
    if item_id in st.session_state.sold_items:
        return  # 避免重复拍卖
    
    start_revenue = st.session_state.total_revenue
    target_revenue = start_revenue + item_price
    steps = 15  # 减少步骤，提升流畅度
    step_val = item_price / steps
    
    # 双语提示
    auctioning_text = current_text['auctioning'].format(item_name)
    msg = st.toast(auctioning_text, icon="⏳")
    
    for i in range(steps):
        current_step_val = start_revenue + (step_val * (i + 1))
        render_dashboard(current_step_val)
        time.sleep(0.02)  # 调整间隔，更流畅
    
    # 更新状态
    st.session_state.total_revenue = target_revenue
    st.session_state.sold_items.add(item_id)
    st.session_state.last_sold_id = item_id 
    
    # 双语成交提示
    success_text = current_text['auction_success'].format(format_price(item_price, current_lang))
    msg.toast(success_text, icon="💰")
    time.sleep(0.8)
    st.rerun()

# ==========================================
# 11. 商品展示区（优化：卡片间距、列数适配、双语藏品信息）
# ==========================================
current_museum_pinyin = MUSEUM_NAME_MAP_PINYIN[st.session_state.current_museum]
items = MUSEUM_TREASURES.get(current_museum_pinyin, [])

# 优化：根据屏幕宽度调整列数（宽屏6列，更紧凑）
cols_per_row = 6
if len(items) < 6:
    cols_per_row = len(items)
rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]

# 增加分区标题（双语）
museum_name_display = f"{st.session_state.current_museum} | {MUSEUM_NAME_MAP[st.session_state.current_museum]}"
collection_title = current_text['collection_list_title'].format(museum_name_display)
st.markdown(f"<h3 style='margin: 30px 0 20px 0; color: #111;'>{collection_title}</h3>", unsafe_allow_html=True)

for row_items in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for idx, item in enumerate(row_items):
        item_id = item['id']
        with cols[idx]:
            is_sold = item_id in st.session_state.sold_items
            
            # 价格显示逻辑（双语）
            if is_sold:
                display_price = f"¥{format_price(item['price'], current_lang)}"
                price_class = "t-price sold-price"
                if item_id == st.session_state.get('last_sold_id'):
                    price_class += " price-reveal"
            else:
                display_price = current_text['value_to_be_revealed']
                price_class = "t-price unsold-price"
            
            # 图片容错
            item_img = item.get('img', f"https://picsum.photos/seed/{item_id}/300/300")
            
            # 藏品信息（双语）
            item_name = item[f"name_{current_lang}"]
            item_period = item.get(f"period_{current_lang}", current_text['ancient'])
            item_desc = item[f"desc_{current_lang}"]
            
            # 渲染藏品卡片
            st.markdown(f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item_img}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};">
                </div>
                <div class="t-content">
                    <div class="t-title">{item_name}</div>
                    <div class="t-period">{item_period}</div>
                    <div class="t-desc" title="{item_desc}">{item_desc}</div>
                    <div class="{price_class}">{display_price}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 拍卖按钮（双语）
            if is_sold:
                btn_text = current_text['already_sold']
                st.button(btn_text, key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                btn_text = current_text['auction_now']
                if st.button(btn_text, key=f"btn_{item_id}", type="primary", use_container_width=True):
                    # 传入双语藏品名称用于提示
                    auction_animation(item['price'], item_name, item_id)

# ==========================================
# 12. 底部功能（优化：间距、按钮样式、双语适配）
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([0.25, 0.5, 0.25], gap="medium")

# 重置按钮
with c1:
    reset_text = current_text['reset']
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
                    tip_text = "扫码支付后点击下方按钮确认" if current_lang == 'zh' else 'Scan the QR code and click the button below to confirm'
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
# 13. 访问统计（优化：统计条样式、数据容错、双语适配）
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
    <div><div>{current_text['today_uv']}</div><div style="font-weight:700; color:#111;">{today_uv}</div></div>
    <div><div>{current_text['total_uv']}</div><div style="font-weight:700; color:#111;">{total_uv}</div></div>
</div>
""", unsafe_allow_html=True)

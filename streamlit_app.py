import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import random
import base64

# ==========================================
# 1. 全局配置 & 路径修复
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
    # 兜底：应对 Streamlit 云端/临时环境的路径异常
    PROJECT_ROOT = os.getcwd()
BASE_IMG_ROOT = os.path.join(PROJECT_ROOT, "img")
os.makedirs(BASE_IMG_ROOT, exist_ok=True)

# 定义博物馆名称映射（解决键不匹配问题）
MUSEUM_NAME_MAP = {
    "南京博物院": "nanjing",
    "三星堆博物馆": "sanxingdui",
    "中国国家博物馆": "beijing",
    "上海博物馆": "shanghai",
    "陕西历史博物馆": "xian"
}
# 反向映射（备用）
MUSEUM_NAME_MAP_REVERSE = {v: k for k, v in MUSEUM_NAME_MAP.items()}

# 动态创建所有博物馆的图片目录
for museum_pinyin in MUSEUM_NAME_MAP.values():
    museum_img_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    os.makedirs(museum_img_dir, exist_ok=True)

# ==========================================
# 2. 核心数据（完善翻译、补充豪宅图片、优化藏品信息）
# ==========================================
# 完善豪宅配置：补充高清图片 + 中英双语名称
MANSION_CONFIG = {
    "南京博物院": {
        "mansion_name_zh": "颐和路民国别墅",
        "mansion_name_en": "Republic of China Villa on Yihe Road",
        "price": 100000000,
        "mansion_img": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",  # 提升分辨率
        "mansion_desc_zh": "民国时期军政要员宅邸，中西合璧建筑风格",
        "mansion_desc_en": "Residence of military and political dignitaries in the Republic of China, with a combination of Chinese and Western architectural styles"
    },
    "三星堆博物馆": {
        "mansion_name_zh": "成都麓山国际豪宅",
        "mansion_name_en": "Chengdu Lushan International Luxury Mansion",
        "price": 50000000,
        "mansion_img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",  # 提升分辨率
        "mansion_desc_zh": "天府之国核心区域，高尔夫球场旁高端宅邸",
        "mansion_desc_en": "Core area of the Land of Abundance, high-end mansion next to the golf course"
    },
    "中国国家博物馆": {
        "mansion_name_zh": "什刹海四合院",
        "mansion_name_en": "Shichahai Courtyard House",
        "price": 150000000,
        "mansion_img": "https://images.unsplash.com/photo-1595130838493-2199b4226d9e?auto=format&fit=crop&w=800&q=80",  # 提升分辨率
        "mansion_desc_zh": "北京内城核心，传统二进四合院，独门独院",
        "mansion_desc_en": "Core of Beijing's inner city, traditional two-yard courtyard, single-family and single-yard"
    },
    "上海博物馆": {
        "mansion_name_zh": "愚园路老洋房",
        "mansion_name_en": "Old Western-style House on Yuyuan Road",
        "price": 200000000,
        "mansion_img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",  # 提升分辨率
        "mansion_desc_zh": "沪上百年历史洋房，梧桐掩映，闹中取静",
        "mansion_desc_en": "Century-old Western-style house in Shanghai, shaded by parasol trees, quiet in the hustle and bustle"
    },
    "陕西历史博物馆": {
        "mansion_name_zh": "曲江池畔大平层",
        "mansion_name_en": "Large Flat by Qujiang Pool",
        "price": 30000000,
        "mansion_img": "https://images.unsplash.com/photo-1600607687940-472002695533?auto=format&fit=crop&w=800&q=80",  # 提升分辨率
        "mansion_desc_zh": "西安曲江新区，一线湖景，高端改善型住宅",
        "mansion_desc_en": "Xi'an Qujiang New District, first-line lake view, high-end improved residence"
    }
}

# 完善藏品数据：补充中英双语 + 填充默认图片（解决nanjing藏品img为空问题）
MUSEUM_TREASURES = {
    "nanjing": [
        {"id": "nj_1", "name_zh": "金兽", "name_en": "Golden Beast", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "含金量99%，最重金器", "desc_en": "99% gold content, the heaviest gold artifact", "price": 500000000, "img": "https://picsum.photos/seed/nj1/300/300"},
        {"id": "nj_2", "name_zh": "釉里红梅瓶", "name_en": "Underglaze Red Plum Vase", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "存世稀少，釉里红巅峰之作", "desc_en": "Rare in the world, the pinnacle of underglaze red", "price": 800000000, "img": "https://picsum.photos/seed/nj2/300/300"},
        {"id": "nj_3", "name_zh": "金蝉玉叶", "name_en": "Golden Cicada on Jade Leaf", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "金枝玉叶，工艺精湛", "desc_en": "Golden branch and jade leaf, exquisite craftsmanship", "price": 90000000, "img": "https://picsum.photos/seed/nj3/300/300"},
        {"id": "nj_4", "name_zh": "银缕玉衣", "name_en": "Silver-thread Jade Burial Suit", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "银丝编缀，极其罕见", "desc_en": "Woven with silver threads, extremely rare", "price": 300000000, "img": "https://picsum.photos/seed/nj4/300/300"},
        {"id": "nj_5", "name_zh": "竹林七贤砖画", "name_en": "Brick Painting of the Seven Sages of the Bamboo Grove", "period_zh": "南朝", "period_en": "Southern Dynasties", "desc_zh": "魏晋风度最佳见证", "desc_en": "The best witness of the demeanor of the Wei and Jin Dynasties", "price": 1000000000, "img": "https://picsum.photos/seed/nj5/300/300"},
        {"id": "nj_6", "name_zh": "大报恩寺拱门", "name_en": "Gate of the Great Bao'en Temple", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "世界奇迹残留组件", "desc_en": "Remaining components of a world wonder", "price": 200000000, "img": "https://picsum.photos/seed/nj6/300/300"},
        {"id": "nj_7", "name_zh": "坤舆万国全图", "name_en": "Kunyu Wanguo Quantu", "period_zh": "明万历", "period_en": "Wanli Period of Ming Dynasty", "desc_zh": "最早彩绘世界地图", "desc_en": "The earliest colored world map", "price": 600000000, "img": "https://picsum.photos/seed/nj7/300/300"},
        {"id": "nj_8", "name_zh": "广陵王玺", "name_en": "Seal of the King of Guangling", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "汉代封王金印精品", "desc_en": "Exquisite gold seal of a feudal lord in the Han Dynasty", "price": 200000000, "img": "https://picsum.photos/seed/nj8/300/300"},
        {"id": "nj_9", "name_zh": "错银铜牛灯", "name_en": "Silver-inlaid Bronze Ox Lamp", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "汉代环保黑科技", "desc_en": "Environmental protection black technology of the Han Dynasty", "price": 180000000, "img": "https://picsum.photos/seed/nj9/300/300"},
        {"id": "nj_10", "name_zh": "青瓷神兽尊", "name_en": "Celadon Beast Zun", "period_zh": "西晋", "period_en": "Western Jin", "desc_zh": "造型奇特的早期青瓷", "desc_en": "Early celadon with a strange shape", "price": 120000000, "img": "https://picsum.photos/seed/nj10/300/300"},
        {"id": "nj_11", "name_zh": "透雕人鸟兽玉饰", "name_en": "Openwork Jade Ornament of Human, Bird and Beast", "period_zh": "良渚", "period_en": "Liangzhu Culture", "desc_zh": "史前玉器巅峰", "desc_en": "The pinnacle of prehistoric jade artifacts", "price": 60000000, "img": "https://picsum.photos/seed/nj11/300/300"},
        {"id": "nj_12", "name_zh": "鎏金喇嘛塔", "name_en": "Gilt Lama Pagoda", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "通体鎏金镶宝石", "desc_en": "Entirely gilded and inlaid with gems", "price": 80000000, "img": "https://picsum.photos/seed/nj12/300/300"},
        {"id": "nj_13", "name_zh": "青花寿山福海炉", "name_en": "Blue and White Furnace with Longevity Mountain and Fortune Sea", "period_zh": "明宣德", "period_en": "Xuande Period of Ming Dynasty", "desc_zh": "宣德官窑完整大器", "desc_en": "Complete masterpiece of Xuande official kiln", "price": 450000000, "img": "https://picsum.photos/seed/nj13/300/300"},
        {"id": "nj_14", "name_zh": "徐渭《杂花图》", "name_en": "Xu Wei's 'Miscellaneous Flowers Painting'", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "大写意水墨巅峰", "desc_en": "The pinnacle of freehand brushwork in ink painting", "price": 350000000, "img": "https://picsum.photos/seed/nj14/300/300"},
        {"id": "nj_15", "name_zh": "沈寿《耶稣像》", "name_en": "Shen Shou's 'Portrait of Jesus'", "period_zh": "近代", "period_en": "Modern Times", "desc_zh": "万国博览会金奖", "desc_en": "Gold medal at the World Expo", "price": 50000000, "img": "https://picsum.photos/seed/nj15/300/300"},
        {"id": "nj_16", "name_zh": "芙蓉石蟠螭炉", "name_en": "Rose Quartz Furnace with Coiling Chi Dragon", "period_zh": "清乾隆", "period_en": "Qianlong Period of Qing Dynasty", "desc_zh": "乾隆御用粉嫩玉石", "desc_en": "Qianlong's personal delicate pink jade", "price": 130000000, "img": "https://picsum.photos/seed/nj16/300/300"},
        {"id": "nj_17", "name_zh": "人面兽面玉琮", "name_en": "Jade Cong with Human and Beast Faces", "period_zh": "良渚", "period_en": "Liangzhu Culture", "desc_zh": "微雕工艺神作", "desc_en": "Masterpiece of miniature carving craftsmanship", "price": 150000000, "img": "https://picsum.photos/seed/nj17/300/300"},
        {"id": "nj_18", "name_zh": "青瓷釉下彩壶", "name_en": "Celadon Pot with Underglaze Color", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "改写陶瓷史的孤品", "desc_en": "Unique piece that rewrote the history of ceramics", "price": 110000000, "img": "https://picsum.photos/seed/nj18/300/300"},
    ],
    "sanxingdui": [
        {"id": "sx_1", "name_zh": "青铜大立人", "name_en": "Bronze Giant Standing Figure", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "世界铜像之王", "desc_en": "King of world bronze statues", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/300/300"},
        {"id": "sx_2", "name_zh": "青铜神树", "name_en": "Bronze Sacred Tree", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "通天神树", "desc_en": "Heaven-reaching sacred tree", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/300/300"},
        {"id": "sx_3", "name_zh": "金面具", "name_en": "Golden Mask", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "半张黄金脸", "desc_en": "Half a golden face", "price": 800000000, "img": "https://picsum.photos/seed/sx3/300/300"},
        {"id": "sx_4", "name_zh": "青铜纵目面具", "name_en": "Bronze Mask with Protruding Eyes", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "千里眼顺风耳", "desc_en": "Clairvoyance and clairaudience", "price": 1200000000, "img": "https://picsum.photos/seed/sx4/300/300"},
        {"id": "sx_5", "name_zh": "太阳轮", "name_en": "Sun Wheel", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "形似方向盘", "desc_en": "Shaped like a steering wheel", "price": 600000000, "img": "https://picsum.photos/seed/sx5/300/300"},
        {"id": "sx_6", "name_zh": "玉璋", "name_en": "Jade Zhang", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "祭祀山川礼器", "desc_en": "Ritual vessel for worshipping mountains and rivers", "price": 300000000, "img": "https://picsum.photos/seed/sx6/300/300"},
        {"id": "sx_7", "name_zh": "黄金权杖", "name_en": "Golden Scepter", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "王权的象征", "desc_en": "Symbol of royal power", "price": 1500000000, "img": "https://picsum.photos/seed/sx7/300/300"},
        {"id": "sx_8", "name_zh": "青铜神坛", "name_en": "Bronze Sacred Altar", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "复杂祭祀场景", "desc_en": "Complex sacrificial scene", "price": 900000000, "img": "https://picsum.photos/seed/sx8/300/300"},
        {"id": "sx_9", "name_zh": "戴金面罩铜人", "name_en": "Bronze Figure with Golden Mask", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "金光闪闪祭司", "desc_en": "Shining golden priest", "price": 500000000, "img": "https://picsum.photos/seed/sx9/300/300"},
        {"id": "sx_10", "name_zh": "青铜鸟头", "name_en": "Bronze Bird Head", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "神鸟图腾", "desc_en": "Sacred bird totem", "price": 150000000, "img": "https://picsum.photos/seed/sx10/300/300"},
        {"id": "sx_11", "name_zh": "陶猪", "name_en": "Pottery Pig", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "愤怒小鸟同款", "desc_en": "Same style as Angry Birds", "price": 50000000, "img": "https://picsum.photos/seed/sx11/300/300"},
        {"id": "sx_12", "name_zh": "青铜大鸟", "name_en": "Giant Bronze Bird", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "体型巨大神兽", "desc_en": "Giant mythical beast", "price": 400000000, "img": "https://picsum.photos/seed/sx12/300/300"},
        {"id": "sx_13", "name_zh": "青铜爬龙柱", "name_en": "Bronze Column with Coiling Dragon", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "龙形神柱", "desc_en": "Dragon-shaped sacred column", "price": 650000000, "img": "https://picsum.photos/seed/sx13/300/300"},
        {"id": "sx_14", "name_zh": "人身鸟脚像", "name_en": "Figure with Human Body and Bird Feet", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "半人半鸟", "desc_en": "Half human and half bird", "price": 550000000, "img": "https://picsum.photos/seed/sx14/300/300"},
        {"id": "sx_15", "name_zh": "顶尊跪坐人像", "name_en": "Kneeling Figure Holding a Zun on Head", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "国宝级重器", "desc_en": "National treasure-level heavy artifact", "price": 1100000000, "img": "https://picsum.photos/seed/sx15/300/300"},
        {"id": "sx_16", "name_zh": "青铜蛇", "name_en": "Bronze Snake", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "造型逼真", "desc_en": "Realistic shape", "price": 120000000, "img": "https://picsum.photos/seed/sx16/300/300"},
        {"id": "sx_17", "name_zh": "青铜鸡", "name_en": "Bronze Chicken", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "雄鸡一唱", "desc_en": "Rooster crows", "price": 80000000, "img": "https://picsum.photos/seed/sx17/300/300"},
        {"id": "sx_18", "name_zh": "玉琮", "name_en": "Jade Cong", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "良渚文化影响", "desc_en": "Influenced by Liangzhu Culture", "price": 200000000, "img": "https://picsum.photos/seed/sx18/300/300"},
    ],
    "beijing": [
        {"id": "bj_1", "name_zh": "清明上河图", "name_en": "Along the River During the Qingming Festival", "period_zh": "北宋", "period_en": "Northern Song Dynasty", "desc_zh": "中华第一神品", "desc_en": "The first masterpiece of China", "price": 5000000000, "img": "https://picsum.photos/seed/bj1/300/300"},
        {"id": "bj_2", "name_zh": "金瓯永固杯", "name_en": "Golden Cup of Eternal National Prosperity", "period_zh": "清乾隆", "period_en": "Qianlong Period of Qing Dynasty", "desc_zh": "乾隆御用金杯", "desc_en": "Qianlong's personal golden cup", "price": 600000000, "img": "https://picsum.photos/seed/bj2/300/300"},
        {"id": "bj_3", "name_zh": "后母戊鼎", "name_en": "Houmuwu Ding", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "青铜之王", "desc_en": "King of bronzes", "price": 4000000000, "img": "https://picsum.photos/seed/bj3/300/300"},
        {"id": "bj_4", "name_zh": "千里江山图", "name_en": "A Thousand Li of Rivers and Mountains", "period_zh": "北宋", "period_en": "Northern Song Dynasty", "desc_zh": "青绿山水巅峰", "desc_en": "The pinnacle of blue and green landscape painting", "price": 3000000000, "img": "https://picsum.photos/seed/bj4/300/300"},
        {"id": "bj_5", "name_zh": "四羊方尊", "name_en": "Four-goat Square Zun", "period_zh": "商代", "period_en": "Shang Dynasty", "desc_zh": "青铜铸造奇迹", "desc_en": "Miracle of bronze casting", "price": 2000000000, "img": "https://picsum.photos/seed/bj5/300/300"},
        {"id": "bj_6", "name_zh": "孝端皇后凤冠", "name_en": "Phoenix Crown of Empress Xiaoduan", "period_zh": "明代", "period_en": "Ming Dynasty", "desc_zh": "点翠工艺巅峰", "desc_en": "The pinnacle of kingfisher feather craftsmanship", "price": 500000000, "img": "https://picsum.photos/seed/bj6/300/300"},
        {"id": "bj_7", "name_zh": "金缕玉衣", "name_en": "Gold-thread Jade Burial Suit", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "中山靖王同款", "desc_en": "Same style as the Prince of Zhongshan Jing", "price": 1000000000, "img": "https://picsum.photos/seed/bj7/300/300"},
        {"id": "bj_8", "name_zh": "红山玉龙", "name_en": "Hongshan Jade Dragon", "period_zh": "新石器", "period_en": "Neolithic Age", "desc_zh": "中华第一龙", "desc_en": "The first dragon of China", "price": 1200000000, "img": "https://picsum.photos/seed/bj8/300/300"},
        {"id": "bj_9", "name_zh": "击鼓说唱俑", "name_en": "Drum-beating and Story-telling Figurine", "period_zh": "东汉", "period_en": "Eastern Han", "desc_zh": "汉代幽默感", "desc_en": "Sense of humor in the Han Dynasty", "price": 300000000, "img": "https://picsum.photos/seed/bj9/300/300"},
        {"id": "bj_10", "name_zh": "人面鱼纹盆", "name_en": "Basin with Human Face and Fish Pattern", "period_zh": "仰韶", "period_en": "Yangshao Culture", "desc_zh": "史前文明微笑", "desc_en": "Smile of prehistoric civilization", "price": 250000000, "img": "https://picsum.photos/seed/bj10/300/300"},
        {"id": "bj_11", "name_zh": "大盂鼎", "name_en": "Great Yu Ding", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "铭文极其珍贵", "desc_en": "Extremely precious inscriptions", "price": 1800000000, "img": "https://picsum.photos/seed/bj11/300/300"},
        {"id": "bj_12", "name_zh": "虢季子白盘", "name_en": "Guo Jizi Bai Plate", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "晚清出土重器", "desc_en": "Heavy artifact unearthed in the late Qing Dynasty", "price": 1600000000, "img": "https://picsum.photos/seed/bj12/300/300"},
        {"id": "bj_13", "name_zh": "霁蓝白龙梅瓶", "name_en": "Blue Glaze Plum Vase with White Dragon", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "元代顶级瓷器", "desc_en": "Top-grade porcelain of the Yuan Dynasty", "price": 800000000, "img": "https://picsum.photos/seed/bj13/300/300"},
        {"id": "bj_14", "name_zh": "郎世宁百骏图", "name_en": "Giuseppe Castiglione's 'Hundred Horses Painting'", "period_zh": "清代", "period_en": "Qing Dynasty", "desc_zh": "中西合璧", "desc_en": "Combination of Chinese and Western styles", "price": 600000000, "img": "https://picsum.photos/seed/bj14/300/300"},
        {"id": "bj_15", "name_zh": "五牛图", "name_en": "Five Oxen Painting", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "韩滉传世孤本", "desc_en": "Surviving sole copy of Han Huang", "price": 900000000, "img": "https://picsum.photos/seed/bj15/300/300"},
        {"id": "bj_16", "name_zh": "步辇图", "name_en": "Portrait of the Emperor on a Palanquin", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "阎立本绘", "desc_en": "Painted by Yan Liben", "price": 1100000000, "img": "https://picsum.photos/seed/bj16/300/300"},
        {"id": "bj_17", "name_zh": "利簋", "name_en": "Li Gui", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "记录武王伐纣", "desc_en": "Records King Wu's conquest of Zhou", "price": 700000000, "img": "https://picsum.photos/seed/bj17/300/300"},
        {"id": "bj_18", "name_zh": "鹳鱼石斧陶缸", "name_en": "Pottery Vat with Stork, Fish and Stone Axe", "period_zh": "仰韶", "period_en": "Yangshao Culture", "desc_zh": "绘画史第一页", "desc_en": "The first page of the history of painting", "price": 400000000, "img": "https://picsum.photos/seed/bj18/300/300"},
    ],
    "shanghai": [
        {"id": "sh_1", "name_zh": "大克鼎", "name_en": "Great Ke Ding", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "海内三宝之一", "desc_en": "One of the three treasures at home and abroad", "price": 1500000000, "img": "https://picsum.photos/seed/sh1/300/300"},
        {"id": "sh_2", "name_zh": "晋侯苏钟", "name_en": "Marquis Jin Su Bells", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "铭文刻在钟表", "desc_en": "Inscriptions carved on bells", "price": 800000000, "img": "https://picsum.photos/seed/sh2/300/300"},
        {"id": "sh_3", "name_zh": "孙位高逸图", "name_en": "Sun Wei's 'Portrait of High Scholars'", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "唐代人物画孤本", "desc_en": "Sole copy of figure painting in the Tang Dynasty", "price": 1200000000, "img": "https://picsum.photos/seed/sh3/300/300"},
        {"id": "sh_4", "name_zh": "越王剑", "name_en": "Sword of the King of Yue", "period_zh": "春秋", "period_en": "Spring and Autumn Period", "desc_zh": "虽不如勾践剑", "desc_en": "Though not as good as Gou Jian's sword", "price": 300000000, "img": "https://picsum.photos/seed/sh4/300/300"},
        {"id": "sh_5", "name_zh": "粉彩蝠桃纹瓶", "name_en": "Famille Rose Vase with Bat and Peach Pattern", "period_zh": "清雍正", "period_en": "Yongzheng Period of Qing Dynasty", "desc_zh": "雍正官窑极品", "desc_en": "Top grade of Yongzheng official kiln", "price": 400000000, "img": "https://picsum.photos/seed/sh5/300/300"},
        {"id": "sh_6", "name_zh": "王羲之上虞帖", "name_en": "Wang Xizhi's 'Shangyu Tie'", "period_zh": "唐摹本", "period_en": "Tang Dynasty Copy", "desc_zh": "书圣墨宝", "desc_en": "Treasure of the Sage of Calligraphy", "price": 2000000000, "img": "https://picsum.photos/seed/sh6/300/300"},
        {"id": "sh_7", "name_zh": "苦笋帖", "name_en": "Bitter Bamboo Shoot Tie", "period_zh": "唐怀素", "period_en": "Huaisu of Tang Dynasty", "desc_zh": "草书狂僧真迹", "desc_en": "Authentic work of the wild cursive monk", "price": 1000000000, "img": "https://picsum.photos/seed/sh7/300/300"},
        {"id": "sh_8", "name_zh": "青花瓶", "name_en": "Blue and White Vase", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "元青花存世稀少", "desc_en": "Yuan blue and white is rare in the world", "price": 600000000, "img": "https://picsum.photos/seed/sh8/300/300"},
        {"id": "sh_9", "name_zh": "子仲姜盘", "name_en": "Zizhong Jiang Plate", "period_zh": "春秋", "period_en": "Spring and Autumn Period", "desc_zh": "盘内动物可旋转", "desc_en": "Animals in the plate can rotate", "price": 500000000, "img": "https://picsum.photos/seed/sh9/300/300"},
        {"id": "sh_10", "name_zh": "牺尊", "name_en": "Animal Zun", "period_zh": "春秋", "period_en": "Spring and Autumn Period", "desc_zh": "极具神韵的牛形", "desc_en": "Cow shape with great charm", "price": 350000000, "img": "https://picsum.photos/seed/sh10/300/300"},
        {"id": "sh_11", "name_zh": "秦权", "name_en": "Qin Weight", "period_zh": "秦代", "period_en": "Qin Dynasty", "desc_zh": "统一度量衡", "desc_en": "Unify weights and measures", "price": 1500000000, "img": "https://picsum.photos/seed/sh11/300/300"},
        {"id": "sh_12", "name_zh": "怀素自叙帖", "name_en": "Huaisu's 'Autobiography Tie'", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "草书巅峰之作", "desc_en": "Pinnacle work of cursive calligraphy", "price": 1800000000, "img": "https://picsum.photos/seed/sh12/300/300"},  # 修复原数据缺失问题
        {"id": "sh_13", "name_zh": "哥窑五足洗", "name_en": "Ge Kiln Five-foot Washing Vessel", "period_zh": "南宋", "period_en": "Southern Song Dynasty", "desc_zh": "金丝铁线", "desc_en": "Golden thread and iron wire", "price": 300000000, "img": "https://picsum.photos/seed/sh13/300/300"},
        {"id": "sh_14", "name_zh": "透雕神兽玉璧", "name_en": "Openwork Jade Bi with Mythical Beasts", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "汉代玉器巅峰", "desc_en": "The pinnacle of Han Dynasty jade artifacts", "price": 200000000, "img": "https://picsum.photos/seed/sh14/300/300"},
        {"id": "sh_15", "name_zh": "剔红花卉纹盘", "name_en": "Red Carved Plate with Flower Pattern", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "张成造，漆器孤品", "desc_en": "Made by Zhang Cheng, unique lacquerware", "price": 120000000, "img": "https://picsum.photos/seed/sh15/300/300"},
        {"id": "sh_16", "name_zh": "苏轼舣舟亭图", "name_en": "Su Shi's 'Yizhou Pavilion Painting'", "period_zh": "清代", "period_en": "Qing Dynasty", "desc_zh": "乾隆御览之宝", "desc_en": "Treasure reviewed by Emperor Qianlong", "price": 250000000, "img": "https://picsum.photos/seed/sh16/300/300"},
        {"id": "sh_17", "name_zh": "青花牡丹纹罐", "name_en": "Blue and White Jar with Peony Pattern", "period_zh": "元代", "period_en": "Yuan Dynasty", "desc_zh": "元青花大器", "desc_en": "Large Yuan blue and white artifact", "price": 550000000, "img": "https://picsum.photos/seed/sh17/300/300"},
        {"id": "sh_18", "name_zh": "缂丝莲塘乳鸭", "name_en": "Kesi 'Lotus Pond and Ducklings'", "period_zh": "南宋", "period_en": "Southern Song Dynasty", "desc_zh": "朱克柔真迹", "desc_en": "Authentic work of Zhu Kerou", "price": 800000000, "img": "https://picsum.photos/seed/sh18/300/300"},
    ],
    "xian": [
        {"id": "xa_1", "name_zh": "镶金兽首玛瑙杯", "name_en": "Gold-inlaid Agate Cup with Beast Head", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "海内孤品", "desc_en": "Unique piece at home and abroad", "price": 2000000000, "img": "https://picsum.photos/seed/xa1/300/300"},
        {"id": "xa_2", "name_zh": "舞马衔杯银壶", "name_en": "Silver Pot with Dancing Horse Holding Cup", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "大唐盛世缩影", "desc_en": "Epitome of the prosperous Tang Dynasty", "price": 800000000, "img": "https://picsum.photos/seed/xa2/300/300"},
        {"id": "xa_3", "name_zh": "皇后之玺", "name_en": "Seal of the Empress", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "吕后之印", "desc_en": "Seal of Empress Lü", "price": 1000000000, "img": "https://picsum.photos/seed/xa3/300/300"},
        {"id": "xa_4", "name_zh": "兵马俑(跪射)", "name_en": "Terracotta Army (Kneeling Archer)", "period_zh": "秦代", "period_en": "Qin Dynasty", "desc_zh": "保存最完整", "desc_en": "The most well-preserved", "price": 3000000000, "img": "https://picsum.photos/seed/xa4/300/300"},
        {"id": "xa_5", "name_zh": "葡萄花鸟香囊", "name_en": "Grape, Flower and Bird Sachet", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "杨贵妃同款", "desc_en": "Same style as Yang Guifei", "price": 500000000, "img": "https://picsum.photos/seed/xa5/300/300"},
        {"id": "xa_6", "name_zh": "鎏金铜蚕", "name_en": "Gilt Bronze Silkworm", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "丝绸之路见证", "desc_en": "Witness of the Silk Road", "price": 300000000, "img": "https://picsum.photos/seed/xa6/300/300"},
        {"id": "xa_7", "name_zh": "独孤信印", "name_en": "Du Gu Xin's Seal", "period_zh": "西魏", "period_en": "Western Wei Dynasty", "desc_zh": "多面体印章", "desc_en": "Polyhedral seal", "price": 400000000, "img": "https://picsum.photos/seed/xa7/300/300"},
        {"id": "xa_8", "name_zh": "提梁倒注壶", "name_en": "Handle Pot with Inverted Pouring", "period_zh": "五代", "period_en": "Five Dynasties", "desc_zh": "神奇倒注构造", "desc_en": "Magical inverted pouring structure", "price": 200000000, "img": "https://picsum.photos/seed/xa8/300/300"},
        {"id": "xa_9", "name_zh": "鸳鸯纹金碗", "name_en": "Golden Bowl with Mandarin Duck Pattern", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "金银器巅峰", "desc_en": "The pinnacle of gold and silver artifacts", "price": 600000000, "img": "https://picsum.photos/seed/xa9/300/300"},
        {"id": "xa_10", "name_zh": "三彩骆驼俑", "name_en": "Tri-color Glazed Camel Figurine", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "丝路乐队", "desc_en": "Silk Road band", "price": 450000000, "img": "https://picsum.photos/seed/xa10/300/300"},
        {"id": "xa_11", "name_zh": "阙楼仪仗图", "name_en": "Tower and Guard of Honor Painting", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "懿德太子墓", "desc_en": "Tomb of Prince Yide", "price": 1500000000, "img": "https://picsum.photos/seed/xa11/300/300"},
        {"id": "xa_12", "name_zh": "鎏金铜龙", "name_en": "Gilt Bronze Dragon", "period_zh": "唐代", "period_en": "Tang Dynasty", "desc_zh": "气势磅礴", "desc_en": "Majestic momentum", "price": 350000000, "img": "https://picsum.photos/seed/xa12/300/300"},
        {"id": "xa_13", "name_zh": "杜虎符", "name_en": "Du Hu Tally", "period_zh": "战国", "period_en": "Warring States Period", "desc_zh": "调兵遣将信物", "desc_en": "Token for dispatching troops", "price": 500000000, "img": "https://picsum.photos/seed/xa13/300/300"},
        {"id": "xa_14", "name_zh": "何尊", "name_en": "He Zun", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "最早出现'中国'", "desc_en": "The earliest appearance of 'China'", "price": 2500000000, "img": "https://picsum.photos/seed/xa14/300/300"},
        {"id": "xa_15", "name_zh": "多友鼎", "name_en": "Duoyou Ding", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "铭文记录战争", "desc_en": "Inscriptions record wars", "price": 800000000, "img": "https://picsum.photos/seed/xa15/300/300"},
        {"id": "xa_16", "name_zh": "日己觥", "name_en": "Riji Gong", "period_zh": "西周", "period_en": "Western Zhou Dynasty", "desc_zh": "造型奇特酒器", "desc_en": "Wine vessel with a strange shape", "price": 400000000, "img": "https://picsum.photos/seed/xa16/300/300"},
        {"id": "xa_17", "name_zh": "雁鱼铜灯", "name_en": "Wild Goose and Fish Bronze Lamp", "period_zh": "西汉", "period_en": "Western Han", "desc_zh": "环保美学结合", "desc_en": "Combination of environmental protection and aesthetics", "price": 550000000, "img": "https://picsum.photos/seed/xa17/300/300"},
        {"id": "xa_18", "name_zh": "金怪兽", "name_en": "Golden Monster", "period_zh": "战国", "period_en": "Warring States Period", "desc_zh": "匈奴文化代表", "desc_en": "Representative of Xiongnu culture", "price": 200000000, "img": "https://picsum.photos/seed/xa18/300/300"},
    ]
}

# ==========================================
# 3. 工具函数修复（Base64 转换 + 异常处理）
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
        print(f"读取图片失败 {image_path}：{str(e)}")
        return None

# ==========================================
# 4. 通用图片加载逻辑（修复路径 + 键匹配）
# ==========================================
for museum_cn, museum_pinyin in MUSEUM_NAME_MAP.items():
    # 获取当前博物馆的藏品列表
    treasures = MUSEUM_TREASURES.get(museum_pinyin, [])
    if not treasures:
        continue
    
    # 当前博物馆的图片目录
    current_museum_dir = os.path.join(BASE_IMG_ROOT, museum_pinyin)
    
    # 遍历藏品加载图片
    for idx, treasure in enumerate(treasures, start=1):
        # 支持两种文件名格式：简化版 & 复杂版
        img_names = [
            f"{idx}.jpeg",
            f"[] ({idx}).jpeg",
            f"{idx}.jpg",
            f"[] ({idx}).jpg"
        ]
        b64_str = None
        
        # 遍历文件名格式，找到存在的图片
        for img_name in img_names:
            img_path = os.path.join(current_museum_dir, img_name)
            b64_str = get_base64_image(img_path)
            if b64_str:
                break
        
        # 赋值图片路径：本地图片优先，否则保留原有占位图
        if b64_str:
            treasure["img"] = b64_str

# ==========================================
# 5. 样式（保留原有 + 优化图片兜底 + 补充明细清单样式）
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #f5f5f7 !important; color: #1d1d1f; padding-top: 0 !important; }
    .block-container { padding-top: 1rem !important; max-width: 1400px !important; }

    /* --- 外链按钮样式 --- */
    .neal-btn {
        font-family: 'Inter', sans-serif; background: #fff;
        border: 1px solid #e5e7eb; color: #111; font-weight: 600;
        padding: 8px 16px; border-radius: 8px; cursor: pointer;
        transition: all 0.2s; display: inline-flex; align-items: center;
        text-decoration: none !important;
        width: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .neal-btn:hover { background: #f9fafb; transform: translateY(-1px); }
    .neal-btn-link { text-decoration: none; width: 100%; display: block; }

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

    /* --- 图片容器 --- */
    .t-img-box { 
        height: 180px; 
        width: 100%; 
        overflow: hidden;
        background: #f8f9fa;
        display: flex; 
        align-items: center; 
        justify-content: center; 
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
        transform: scale(1.2) rotate(3deg); 
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }

    .t-content { padding: 12px !important; flex-grow: 1; display: flex; flex-direction: column; text-align: center; }
    .t-title { font-size: 1rem; font-weight: 800; color: #111; margin-bottom: 4px !important; }
    .t-period { font-size: 0.75rem; color: #86868b; background: #f5f5f7; padding: 2px 8px; border-radius: 10px; display: inline-block; margin-bottom: 6px !important; width: fit-content; margin-left: auto; margin-right: auto;}
    .t-desc { font-size: 0.8rem; color: #555; line-height: 1.4; margin-bottom: 8px !important; flex-grow: 1; }

    /* --- 价格样式 --- */
    .t-price { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 700; margin: 5px 0 !important; }
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
    .color-alipay { color: #108ee9; }
    .color-paypal { color: #003087; }

    /* --- 统计栏 --- */
    .stats-bar { display: flex; justify-content: center; gap: 25px; margin-top: 40px; padding: 15px 25px; background-color: white; border-radius: 50px; border: 1px solid #eee; color: #6b7280; font-size: 0.85rem; width: fit-content; margin-left: auto; margin-right: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }

    /* --- 私有化国宝明细清单样式 --- */
    .treasure-detail-container {
        background: white; border-radius: 16px; padding: 20px; margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e5e5e5;
    }
    .detail-title { font-size: 1.2rem; font-weight: 800; color: #111; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
    .detail-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; }
    .detail-card { background: #f9fafb; border-radius: 12px; padding: 12px; border: 1px solid #e5e7eb; }
    .detail-card-name { font-weight: 700; color: #111; font-size: 0.9rem; margin-bottom: 5px; }
    .detail-card-period { font-size: 0.7rem; color: #86868b; background: #f5f5f7; padding: 2px 6px; border-radius: 8px; display: inline-block; margin-bottom: 5px; }
    .detail-card-price { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #d9534f; font-weight: 600; }
    .no-treasure-text { color: #86868b; font-size: 0.9rem; text-align: center; padding: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 状态初始化
# ==========================================
if 'language' not in st.session_state: st.session_state.language = 'zh'
if 'sold_items' not in st.session_state: st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state: st.session_state.total_revenue = 0
if 'current_museum' not in st.session_state: st.session_state.current_museum = "南京博物院"
if 'last_sold_id' not in st.session_state: st.session_state.last_sold_id = None
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1

if st.session_state.current_museum not in MANSION_CONFIG:
    st.session_state.current_museum = list(MANSION_CONFIG.keys())[0]

# 完善语言包：覆盖所有页面文本
lang_texts = {
    'zh': {
        'page_title': "华夏国宝私有化中心",
        'museum_selector': "选择博物馆",
        'total_revenue': "累计拍卖总额",
        'purchasing_power': "当前财富购买力：",
        'mansion_set': "套",
        'auction_btn': "㊙ 立即拍卖",
        'sold_btn': "🚫 已私有化",
        'reset_btn': "🔄 破产/重置",
        'coffee_desc': '如果这个游戏帮到了你，欢迎支持。', 
        'coffee_btn': "☕ 请开发者喝咖啡", 
        'coffee_title': " ", 
        'coffee_amount': "请输入打赏杯数", 
        'pay_success': "收到！感谢打赏。❤️",
        'pay_wechat': '微信支付',
        'pay_alipay': '支付宝',
        'pay_paypal': '贝宝',
        'presets': [("☕ 提神", 1), ("🍗 鸡腿", 3), ("🚀 续命", 5)],
        'today_uv': "今日 UV",
        'history_uv': "历史 UV",
        'treasure_detail_title': "🏆 已私有化国宝明细清单（可分享炫耀）",
        'no_sold_treasure': "暂未私有化任何国宝，快去开启拍卖吧！",
        'price_yuan': "¥",
        'auctioning': "正在拍卖",
        'deal_success': "成交！入账"
    },
    'en': {
        'page_title': "Chinese National Treasures Privatization Center",
        'museum_selector': "Select Museum",
        'total_revenue': "Total Auction Revenue",
        'purchasing_power': "Current Wealth Purchasing Power:",
        'mansion_set': "sets",
        'auction_btn': "㊙ Auction Now",
        'sold_btn': "🚫 Already Privatized",
        'reset_btn': "🔄 Bankruptcy/Reset",
        'coffee_desc': 'Support is appreciated.', 
        'coffee_btn': "☕ Buy me a coffee", 
        'coffee_title': " ", 
        'coffee_amount': "Enter Coffee Count", 
        'pay_success': "Received! Thanks! ❤️",
        'pay_wechat': 'WeChat',
        'pay_alipay': 'Alipay',
        'pay_paypal': 'PayPal',
        'presets': [("☕ Coffee", 1), ("🍗 Meal", 3), ("🚀 Rocket", 5)],
        'today_uv': "Today UV",
        'history_uv': "Total UV",
        'treasure_detail_title': "🏆 Privatized National Treasures Details (Share to Show Off)",
        'no_sold_treasure': "No national treasures privatized yet, go start the auction!",
        'price_yuan': "¥",
        'auctioning': "Auctioning",
        'deal_success': "Deal! Revenue"
    }
}
current_text = lang_texts[st.session_state.language]

# ==========================================
# 7. 顶部功能区（完善中英切换同步文本）
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    l_btn = "En" if st.session_state.language == 'zh' else "中"
    if st.button(l_btn, key="lang_switch"):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

with col_more:
    st.markdown("""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ 更多好玩应用 | More Fun Apps</button>
        </a>""", unsafe_allow_html=True)

st.markdown(f"<h2 style='margin-top: 10px; color: #111;'>🏛️ {current_text['page_title']}</h2>", unsafe_allow_html=True)

# 博物馆选择器（同步语言文本）
selected_museum = st.radio(
    current_text['museum_selector'],
    list(MANSION_CONFIG.keys()),
    index=list(MANSION_CONFIG.keys()).index(st.session_state.current_museum),
    horizontal=True,
    label_visibility="visible"  # 显示语言化标签
)

if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.rerun()

# ==========================================
# 8. 核心功能（修复藏品数据获取 + 完善双语展示）
# ==========================================
dashboard_placeholder = st.empty()

def render_dashboard(current_revenue_display):
    m_info = MANSION_CONFIG[st.session_state.current_museum]
    villa_count = current_revenue_display / m_info["price"] if m_info["price"] else 0
    # 双语切换豪宅名称和描述
    mansion_name = m_info["mansion_name_zh"] if st.session_state.language == 'zh' else m_info["mansion_name_en"]
    
    html = f"""
    <div class="dashboard">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
            <div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #111;">{st.session_state.current_museum}</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #d9534f; transition: all 0.2s;">
                    {current_text['price_yuan']}{current_revenue_display / 100000000:.4f}亿
                </div>
                <div style="font-size: 0.8rem; color: #86868b; text-transform: uppercase;">{current_text['total_revenue']}</div>
            </div>
            <div class="mansion-box" style="background-image: url('{m_info["mansion_img"]}');">
                <div class="mansion-overlay"></div>
                <div class="mansion-content">
                    <div style="font-size: 0.8rem; opacity: 0.9;">{current_text['purchasing_power']}</div>
                    <div style="font-size: 1.5rem; font-weight: 900;">× {villa_count:.2f} {current_text['mansion_set']}</div>
                    <div style="font-size: 0.9rem; font-weight: 600;">{mansion_name}</div>
                </div>
            </div>
        </div>
    </div>
    """
    dashboard_placeholder.markdown(html, unsafe_allow_html=True)

render_dashboard(st.session_state.total_revenue)

def format_price(price):
    if price >= 100000000: 
        return f"{current_text['price_yuan']}{price/100000000:.1f}亿"
    elif price >= 10000: 
        return f"{current_text['price_yuan']}{price/10000:.0f}万"
    return f"{current_text['price_yuan']}{str(price)}"

def auction_animation(item_price, item_name, item_id):
    start_revenue = st.session_state.total_revenue
    target_revenue = start_revenue + item_price
    steps = 20
    step_val = item_price / steps
    
    msg = st.toast(f"🔨 {current_text['auctioning']} {item_name}...", icon="⏳")
    
    for i in range(steps):
        current_step_val = start_revenue + (step_val * (i + 1))
        render_dashboard(current_step_val)
        time.sleep(0.015)
    
    st.session_state.total_revenue = target_revenue
    st.session_state.sold_items.add(item_id)
    st.session_state.last_sold_id = item_id 
    
    msg.toast(f"✅ {current_text['deal_success']} {format_price(item_price)}", icon="💰")
    time.sleep(0.5)
    st.rerun()

# ==========================================
# 9. 商品展示区（修复数据键映射 + 完善双语展示）
# ==========================================
# 关键修复：通过映射获取正确的藏品数据
current_museum_pinyin = MUSEUM_NAME_MAP[st.session_state.current_museum]
items = MUSEUM_TREASURES.get(current_museum_pinyin, [])

cols_per_row = 4
rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]

for row_items in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for idx, item in enumerate(row_items):
        item_id = item['id']
        with cols[idx]:
            is_sold = item_id in st.session_state.sold_items
            
            # 双语切换藏品信息
            item_name = item["name_zh"] if st.session_state.language == 'zh' else item["name_en"]
            item_period = item["period_zh"] if st.session_state.language == 'zh' else item["period_en"]
            item_desc = item["desc_zh"] if st.session_state.language == 'zh' else item["desc_en"]
            
            if is_sold:
                display_price = format_price(item['price'])
                price_class = "t-price sold-price"
                if item_id == st.session_state.get('last_sold_id'):
                    price_class += " price-reveal"
            else:
                display_price = "🕵️ 价值待揭晓" if st.session_state.language == 'zh' else "🕵️ Value to be Revealed"
                price_class = "t-price unsold-price"
            
            # 图片加载容错：若img为空，填充默认占位图
            item_img = item.get('img', f"https://picsum.photos/seed/{item_id}/300/300")
            
            st.markdown(f"""
            <div class="treasure-card">
                <div class="t-img-box">
                    <img src="{item_img}" class="t-img" style="filter: {'grayscale(100%)' if is_sold else 'none'};"></img>
                </div>
                <div class="t-content">
                    <div class="t-title">{item_name}</div>
                    <div class="t-period">{item_period}</div>
                    <div class="t-desc" title="{item_desc}">{item_desc}</div>
                    <div class="{price_class}">{display_price}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_sold:
                st.button(current_text['sold_btn'], key=f"btn_{item_id}", disabled=True, use_container_width=True)
            else:
                if st.button(current_text['auction_btn'], key=f"btn_{item_id}", type="primary", use_container_width=True):
                    auction_animation(item['price'], item_name, item_id)

# ==========================================
# 10. 新增：已私有化国宝明细清单（支持分享炫耀）
# ==========================================
st.markdown("---", unsafe_allow_html=True)
st.markdown(f"<div class='detail-title'>{current_text['treasure_detail_title']}</div>", unsafe_allow_html=True)

# 收集所有已私有化的国宝（跨博物馆）
all_sold_treasures = []
for museum_pinyin, treasures in MUSEUM_TREASURES.items():
    for treasure in treasures:
        if treasure['id'] in st.session_state.sold_items:
            # 补充博物馆名称（便于明细展示）
            treasure['museum_cn'] = MUSEUM_NAME_MAP_REVERSE.get(museum_pinyin, "未知博物馆")
            all_sold_treasures.append(treasure)

# 渲染明细清单
if all_sold_treasures:
    # 按价格从高到低排序（更有炫耀感）
    all_sold_treasures.sort(key=lambda x: x['price'], reverse=True)
    st.markdown(f"""<div class='treasure-detail-container'><div class='detail-grid'>""", unsafe_allow_html=True)
    for treasure in all_sold_treasures:
        # 双语切换明细信息
        treasure_name = treasure["name_zh"] if st.session_state.language == 'zh' else treasure["name_en"]
        treasure_period = treasure["period_zh"] if st.session_state.language == 'zh' else treasure["period_en"]
        treasure_price = format_price(treasure["price"])
        
        st.markdown(f"""
        <div class='detail-card'>
            <div class='detail-card-name'>{treasure_name}</div>
            <div class='detail-card-period'>{treasure_period} | {treasure['museum_cn']}</div>
            <div class='detail-card-price'>{treasure_price}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 新增分享提示
    if st.session_state.language == 'zh':
        st.markdown("<p style='text-align: center; color: #86868b; font-size: 0.8rem;'>📸 截图保存即可分享炫耀你的国宝收藏！</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align: center; color: #86868b; font-size: 0.8rem;'>📸 Screenshot and save to share your national treasure collection!</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='treasure-detail-container'><p class='no-treasure-text'>{current_text['no_sold_treasure']}</p></div>", unsafe_allow_html=True)

# ==========================================
# 11. 底部功能（完善双语同步）
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])

# 重置按钮
with c1:
    if st.button(current_text['reset_btn'], type="secondary", use_container_width=True):
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
                    st.markdown(f"""<div class="pay-instruction" style="text-align: center;">请使用手机扫描上方二维码 | Please scan the QR code above with your phone</div>""", unsafe_allow_html=True)

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
    except:
        return 1, 1

today_uv, total_uv = track_stats()

st.markdown(f"""
<div class="stats-bar">
    <div style="text-align: center;"><div>{current_text['today_uv']}</div><div style="font-weight:700; color:#111;">{today_uv}</div></div>
    <div style="border-left:1px solid #eee; padding-left:25px; text-align: center;"><div>{current_text['history_uv']}</div><div style="font-weight:700; color:#111;">{total_uv}</div></div>
</div>
""", unsafe_allow_html=True)

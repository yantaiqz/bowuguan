import streamlit as st
import time
import random

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="National Treasures Auction | 国宝拍卖行",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="collapsed" # 默认收起侧边栏
)

# ==========================================
# 2. 核心数据：五大博物馆 (扩充至 ~20件/馆)
# ==========================================
# 豪宅参照物配置
MANSION_CONFIG = {
    "南京": {"name": "颐和路民国别墅", "price": 100000000}, # 1亿
    "三星堆": {"name": "成都麓山国际别墅", "price": 50000000}, # 5000万
    "北京": {"name": "什刹海四合院", "price": 150000000}, # 1.5亿
    "上海": {"name": "愚园路老洋房", "price": 200000000}, # 2亿
    "西安": {"name": "曲江池畔大平层", "price": 30000000}, # 3000万
}

MUSEUM_DATA = {
    "南京": [
        {"id": "nj_1", "name": "金兽", "period": "西汉", "desc": "含金量99%，最重金器", "price": 500000000, "img": "https://picsum.photos/seed/nj1/400/300"},
        {"id": "nj_2", "name": "釉里红梅瓶", "period": "明洪武", "desc": "现存唯一带盖梅瓶", "price": 800000000, "img": "https://picsum.photos/seed/nj2/400/300"},
        {"id": "nj_3", "name": "金蝉玉叶", "period": "明代", "desc": "金枝玉叶，工艺精湛", "price": 90000000, "img": "https://picsum.photos/seed/nj3/400/300"},
        {"id": "nj_4", "name": "银缕玉衣", "period": "东汉", "desc": "银丝编缀，极其罕见", "price": 300000000, "img": "https://picsum.photos/seed/nj4/400/300"},
        {"id": "nj_5", "name": "竹林七贤砖画", "period": "南朝", "desc": "魏晋风度最佳见证", "price": 1000000000, "img": "https://picsum.photos/seed/nj5/400/300"},
        {"id": "nj_6", "name": "大报恩寺拱门", "period": "明代", "desc": "世界奇迹残留组件", "price": 200000000, "img": "https://picsum.photos/seed/nj6/400/300"},
        {"id": "nj_7", "name": "坤舆万国全图", "period": "明万历", "desc": "最早彩绘世界地图", "price": 600000000, "img": "https://picsum.photos/seed/nj7/400/300"},
        {"id": "nj_8", "name": "广陵王玺", "period": "东汉", "desc": "汉代封王金印精品", "price": 200000000, "img": "https://picsum.photos/seed/nj8/400/300"},
        {"id": "nj_9", "name": "错银铜牛灯", "period": "东汉", "desc": "汉代环保黑科技", "price": 180000000, "img": "https://picsum.photos/seed/nj9/400/300"},
        {"id": "nj_10", "name": "青瓷神兽尊", "period": "西晋", "desc": "造型奇特的早期青瓷", "price": 120000000, "img": "https://picsum.photos/seed/nj10/400/300"},
        {"id": "nj_11", "name": "透雕人鸟兽玉饰", "period": "良渚", "desc": "史前玉器巅峰", "price": 60000000, "img": "https://picsum.photos/seed/nj11/400/300"},
        {"id": "nj_12", "name": "鎏金喇嘛塔", "period": "明代", "desc": "通体鎏金镶宝石", "price": 80000000, "img": "https://picsum.photos/seed/nj12/400/300"},
        {"id": "nj_13", "name": "青花寿山福海炉", "period": "明宣德", "desc": "宣德官窑完整大器", "price": 450000000, "img": "https://picsum.photos/seed/nj13/400/300"},
        {"id": "nj_14", "name": "徐渭《杂花图》", "period": "明代", "desc": "大写意水墨巅峰", "price": 350000000, "img": "https://picsum.photos/seed/nj14/400/300"},
        {"id": "nj_15", "name": "沈寿《耶稣像》", "period": "近代", "desc": "万国博览会金奖", "price": 50000000, "img": "https://picsum.photos/seed/nj15/400/300"},
        {"id": "nj_16", "name": "芙蓉石蟠螭炉", "period": "清乾隆", "desc": "乾隆御用粉嫩玉石", "price": 130000000, "img": "https://picsum.photos/seed/nj16/400/300"},
        {"id": "nj_17", "name": "人面兽面玉琮", "period": "良渚", "desc": "微雕工艺神作", "price": 150000000, "img": "https://picsum.photos/seed/nj17/400/300"},
        {"id": "nj_18", "name": "青瓷釉下彩壶", "period": "唐代", "desc": "改写陶瓷史的孤品", "price": 110000000, "img": "https://picsum.photos/seed/nj18/400/300"},
    ],
    "三星堆": [
        {"id": "sx_1", "name": "青铜大立人", "period": "商代", "desc": "世界铜像之王", "price": 2000000000, "img": "https://picsum.photos/seed/sx1/400/300"},
        {"id": "sx_2", "name": "青铜神树", "period": "商代", "desc": "通天神树，宇宙中心", "price": 2500000000, "img": "https://picsum.photos/seed/sx2/400/300"},
        {"id": "sx_3", "name": "金面具", "period": "商代", "desc": "半张黄金脸，王权象征", "price": 800000000, "img": "https://picsum.photos/seed/sx3/400/300"},
        {"id": "sx_4", "name": "青铜纵目面具", "period": "商代", "desc": "千里眼顺风耳原型", "price": 1200000000, "img": "https://picsum.photos/seed/sx4/400/300"},
        {"id": "sx_5", "name": "太阳轮", "period": "商代", "desc": "形似方向盘的神器", "price": 600000000, "img": "https://picsum.photos/seed/sx5/400/300"},
        {"id": "sx_6", "name": "玉璋", "period": "商代", "desc": "祭祀山川的礼器", "price": 300000000, "img": "https://picsum.photos/seed/sx6/400/300"},
        {"id": "sx_7", "name": "黄金权杖", "period": "商代", "desc": "古蜀王权的象征", "price": 1500000000, "img": "https://picsum.photos/seed/sx7/400/300"},
        {"id": "sx_8", "name": "青铜神坛", "period": "商代", "desc": "复杂的祭祀场景", "price": 900000000, "img": "https://picsum.photos/seed/sx8/400/300"},
        {"id": "sx_9", "name": "戴金面罩铜人头像", "period": "商代", "desc": "金光闪闪的祭司", "price": 500000000, "img": "https://picsum.photos/seed/sx9/400/300"},
        {"id": "sx_10", "name": "青铜鸟头", "period": "商代", "desc": "神鸟图腾", "price": 150000000, "img": "https://picsum.photos/seed/sx10/400/300"},
        {"id": "sx_11", "name": "陶猪", "period": "商代", "desc": "愤怒的小鸟同款猪", "price": 50000000, "img": "https://picsum.photos/seed/sx11/400/300"},
        {"id": "sx_12", "name": "青铜大鸟", "period": "商代", "desc": "体型巨大的神兽", "price": 400000000, "img": "https://picsum.photos/seed/sx12/400/300"},
        {"id": "sx_13", "name": "青铜爬龙柱", "period": "商代", "desc": "龙形神柱", "price": 650000000, "img": "https://picsum.photos/seed/sx13/400/300"},
        {"id": "sx_14", "name": "青铜人身鸟脚像", "period": "商代", "desc": "奇特的半人半鸟", "price": 550000000, "img": "https://picsum.photos/seed/sx14/400/300"},
        {"id": "sx_15", "name": "顶尊跪坐人像", "period": "商代", "desc": "国宝级重器", "price": 1100000000, "img": "https://picsum.photos/seed/sx15/400/300"},
        {"id": "sx_16", "name": "青铜蛇", "period": "商代", "desc": "造型逼真的青铜蛇", "price": 120000000, "img": "https://picsum.photos/seed/sx16/400/300"},
        {"id": "sx_17", "name": "青铜鸡", "period": "商代", "desc": "雄鸡一唱天下白", "price": 80000000, "img": "https://picsum.photos/seed/sx17/400/300"},
        {"id": "sx_18", "name": "玉琮", "period": "商代", "desc": "受良渚文化影响", "price": 200000000, "img": "https://picsum.photos/seed/sx18/400/300"},
    ],
    "北京": [
        {"id": "bj_1", "name": "清明上河图", "period": "北宋", "desc": "中华第一神品", "price": 5000000000, "img": "https://picsum.photos/seed/bj1/400/300"},
        {"id": "bj_2", "name": "金瓯永固杯", "period": "清乾隆", "desc": "乾隆御用金杯", "price": 600000000, "img": "https://picsum.photos/seed/bj2/400/300"},
        {"id": "bj_3", "name": "后母戊鼎", "period": "商代", "desc": "镇国之宝，青铜之王", "price": 4000000000, "img": "https://picsum.photos/seed/bj3/400/300"},
        {"id": "bj_4", "name": "千里江山图", "period": "北宋", "desc": "青绿山水巅峰", "price": 3000000000, "img": "https://picsum.photos/seed/bj4/400/300"},
        {"id": "bj_5", "name": "四羊方尊", "period": "商代", "desc": "青铜铸造奇迹", "price": 2000000000, "img": "https://picsum.photos/seed/bj5/400/300"},
        {"id": "bj_6", "name": "孝端皇后凤冠", "period": "明代", "desc": "点翠工艺巅峰", "price": 500000000, "img": "https://picsum.photos/seed/bj6/400/300"},
        {"id": "bj_7", "name": "金缕玉衣", "period": "西汉", "desc": "中山靖王同款", "price": 1000000000, "img": "https://picsum.photos/seed/bj7/400/300"},
        {"id": "bj_8", "name": "红山玉龙", "period": "新石器", "desc": "中华第一龙", "price": 1200000000, "img": "https://picsum.photos/seed/bj8/400/300"},
        {"id": "bj_9", "name": "击鼓说唱俑", "period": "东汉", "desc": "汉代艺术的幽默感", "price": 300000000, "img": "https://picsum.photos/seed/bj9/400/300"},
        {"id": "bj_10", "name": "人面鱼纹彩陶盆", "period": "仰韶", "desc": "史前文明的微笑", "price": 250000000, "img": "https://picsum.photos/seed/bj10/400/300"},
        {"id": "bj_11", "name": "大盂鼎", "period": "西周", "desc": "铭文极其珍贵", "price": 1800000000, "img": "https://picsum.photos/seed/bj11/400/300"},
        {"id": "bj_12", "name": "虢季子白盘", "period": "西周", "desc": "晚清出土重器", "price": 1600000000, "img": "https://picsum.photos/seed/bj12/400/300"},
        {"id": "bj_13", "name": "霁蓝釉白龙纹梅瓶", "period": "元代", "desc": "元代顶级瓷器", "price": 800000000, "img": "https://picsum.photos/seed/bj13/400/300"},
        {"id": "bj_14", "name": "郎世宁《百骏图》", "period": "清代", "desc": "中西合璧代表作", "price": 600000000, "img": "https://picsum.photos/seed/bj14/400/300"},
        {"id": "bj_15", "name": "五牛图", "period": "唐代", "desc": "韩滉传世孤本", "price": 900000000, "img": "https://picsum.photos/seed/bj15/400/300"},
        {"id": "bj_16", "name": "步辇图", "period": "唐代", "desc": "阎立本绘文成公主", "price": 1100000000, "img": "https://picsum.photos/seed/bj16/400/300"},
        {"id": "bj_17", "name": "利簋", "period": "西周", "desc": "记录武王伐纣", "price": 700000000, "img": "https://picsum.photos/seed/bj17/400/300"},
        {"id": "bj_18", "name": "彩绘鹳鱼石斧图陶缸", "period": "仰韶", "desc": "中国绘画史第一页", "price": 400000000, "img": "https://picsum.photos/seed/bj18/400/300"},
    ],
    "上海": [
        {"id": "sh_1", "name": "大克鼎", "period": "西周", "desc": "海内三宝之一", "price": 1500000000, "img": "https://picsum.photos/seed/sh1/400/300"},
        {"id": "sh_2", "name": "晋侯苏钟", "period": "西周", "desc": "铭文刻在钟表", "price": 800000000, "img": "https://picsum.photos/seed/sh2/400/300"},
        {"id": "sh_3", "name": "孙位高逸图", "period": "唐代", "desc": "唐代人物画孤本", "price": 1200000000, "img": "https://picsum.photos/seed/sh3/400/300"},
        {"id": "sh_4", "name": "越王剑", "period": "春秋", "desc": "虽不如勾践剑，亦神兵", "price": 300000000, "img": "https://picsum.photos/seed/sh4/400/300"},
        {"id": "sh_5", "name": "粉彩蝠桃纹瓶", "period": "清雍正", "desc": "雍正官窑极品", "price": 400000000, "img": "https://picsum.photos/seed/sh5/400/300"},
        {"id": "sh_6", "name": "王羲之《上虞帖》", "period": "唐摹本", "desc": "书圣墨宝", "price": 2000000000, "img": "https://picsum.photos/seed/sh6/400/300"},
        {"id": "sh_7", "name": "苦笋帖", "period": "唐怀素", "desc": "草书狂僧真迹", "price": 1000000000, "img": "https://picsum.photos/seed/sh7/400/300"},
        {"id": "sh_8", "name": "景德镇窑青花瓶", "period": "元代", "desc": "元青花存世稀少", "price": 600000000, "img": "https://picsum.photos/seed/sh8/400/300"},
        {"id": "sh_9", "name": "子仲姜盘", "period": "春秋", "desc": "盘内动物可旋转", "price": 500000000, "img": "https://picsum.photos/seed/sh9/400/300"},
        {"id": "sh_10", "name": "牺尊", "period": "春秋", "desc": "极具神韵的牛形青铜", "price": 350000000, "img": "https://picsum.photos/seed/sh10/400/300"},
        {"id": "sh_11", "name": "商鞅方升", "period": "战国", "desc": "统一度量衡的铁证", "price": 1500000000, "img": "https://picsum.photos/seed/sh11/400/300"},
        {"id": "sh_12", "name": "曹全碑", "period": "东汉", "desc": "汉隶书法的典范", "price": 450000000, "img": "https://picsum.photos/seed/sh12/400/300"},
        {"id": "sh_13", "name": "哥窑五足洗", "period": "南宋", "desc": "金丝铁线，宋瓷神韵", "price": 300000000, "img": "https://picsum.photos/seed/sh13/400/300"},
        {"id": "sh_14", "name": "透雕神兽纹玉璧", "period": "西汉", "desc": "汉代玉器工艺巅峰", "price": 200000000, "img": "https://picsum.photos/seed/sh14/400/300"},
        {"id": "sh_15", "name": "剔红花卉纹盘", "period": "元代", "desc": "张成造，漆器孤品", "price": 120000000, "img": "https://picsum.photos/seed/sh15/400/300"},
        {"id": "sh_16", "name": "钱维城《苏轼舣舟亭图》", "period": "清代", "desc": "乾隆御览之宝", "price": 250000000, "img": "https://picsum.photos/seed/sh16/400/300"},
        {"id": "sh_17", "name": "青花缠枝牡丹纹罐", "period": "元代", "desc": "元青花大器", "price": 550000000, "img": "https://picsum.photos/seed/sh17/400/300"},
        {"id": "sh_18", "name": "缂丝莲塘乳鸭图", "period": "南宋", "desc": "朱克柔真迹，丝织神品", "price": 800000000, "img": "https://picsum.photos/seed/sh18/400/300"},
    ],
    "西安": [
        {"id": "xa_1", "name": "镶金兽首玛瑙杯", "period": "唐代", "desc": "海内孤品，禁止出境", "price": 2000000000, "img": "https://picsum.photos/seed/xa1/400/300"},
        {"id": "xa_2", "name": "舞马衔杯纹银壶", "period": "唐代", "desc": "大唐盛世的缩影", "price": 800000000, "img": "https://picsum.photos/seed/xa2/400/300"},
        {"id": "xa_3", "name": "皇后之玺", "period": "西汉", "desc": "吕后之印，国宝级", "price": 1000000000, "img": "https://picsum.photos/seed/xa3/400/300"},
        {"id": "xa_4", "name": "兵马俑(跪射俑)", "period": "秦代", "desc": "保存最完整的兵马俑", "price": 3000000000, "img": "https://picsum.photos/seed/xa4/400/300"},
        {"id": "xa_5", "name": "葡萄花鸟纹银香囊", "period": "唐代", "desc": "杨贵妃同款黑科技", "price": 500000000, "img": "https://picsum.photos/seed/xa5/400/300"},
        {"id": "xa_6", "name": "鎏金铜蚕", "period": "西汉", "desc": "丝绸之路的历史见证", "price": 300000000, "img": "https://picsum.photos/seed/xa6/400/300"},
        {"id": "xa_7", "name": "独孤信多面体印", "period": "西魏", "desc": "最牛老丈人的印章", "price": 400000000, "img": "https://picsum.photos/seed/xa7/400/300"},
        {"id": "xa_8", "name": "青釉提梁倒注壶", "period": "五代", "desc": "倒着注水的神奇构造", "price": 200000000, "img": "https://picsum.photos/seed/xa8/400/300"},
        {"id": "xa_9", "name": "鸳鸯莲瓣纹金碗", "period": "唐代", "desc": "大唐金银器巅峰", "price": 600000000, "img": "https://picsum.photos/seed/xa9/400/300"},
        {"id": "xa_10", "name": "三彩载乐骆驼俑", "period": "唐代", "desc": "丝路乐队", "price": 450000000, "img": "https://picsum.photos/seed/xa10/400/300"},
        {"id": "xa_11", "name": "阙楼仪仗图", "period": "唐代", "desc": "懿德太子墓壁画", "price": 1500000000, "img": "https://picsum.photos/seed/xa11/400/300"},
        {"id": "xa_12", "name": "鎏金铁芯铜龙", "period": "唐代", "desc": "气势磅礴的唐龙", "price": 350000000, "img": "https://picsum.photos/seed/xa12/400/300"},
        {"id": "xa_13", "name": "杜虎符", "period": "战国", "desc": "调兵遣将的信物", "price": 500000000, "img": "https://picsum.photos/seed/xa13/400/300"},
        {"id": "xa_14", "name": "何尊", "period": "西周", "desc": "最早出现'中国'二字", "price": 2500000000, "img": "https://picsum.photos/seed/xa14/400/300"},
        {"id": "xa_15", "name": "多友鼎", "period": "西周", "desc": "长篇铭文记录战争", "price": 800000000, "img": "https://picsum.photos/seed/xa15/400/300"},
        {"id": "xa_16", "name": "日己觥", "period": "西周", "desc": "造型奇特的酒器", "price": 400000000, "img": "https://picsum.photos/seed/xa16/400/300"},
        {"id": "xa_17", "name": "彩绘雁鱼铜灯", "period": "西汉", "desc": "环保与美学的结合", "price": 550000000, "img": "https://picsum.photos/seed/xa17/400/300"},
        {"id": "xa_18", "name": "金怪兽", "period": "战国", "desc": "匈奴文化的代表", "price": 200000000, "img": "https://picsum.photos/seed/xa18/400/300"},
    ]
}

# ==========================================
# 3. 样式表 (CSS)
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    .stApp { 
        background-color: #f5f5f7 !important; 
        color: #1d1d1f; 
        padding-bottom: 2rem !important;
    }
    .block-container {
        padding-top: 1rem !important;
        max-width: 1400px !important;
    }
    
    /* --- 卡片容器 --- */
    .treasure-card {
        background: white;
        border-radius: 12px;
        padding: 0 !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        transition: transform 0.2s;
        border: 1px solid #e5e5e5;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .treasure-card:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 8px 25px rgba(0,0,0,0.08); 
    }
    
    /* --- 图片样式 --- */
    .t-img-box {
        height: 180px;
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
        padding: 12px !important;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    .t-title { 
        font-size: 1rem; 
        font-weight: 800; 
        color: #111; 
        margin-bottom: 4px !important; 
    }
    .t-period { 
        font-size: 0.75rem; 
        color: #86868b; 
        background: #f5f5f7; 
        padding: 2px 6px; 
        border-radius: 4px; 
        display: inline-block; 
        margin-bottom: 6px !important;
        width: fit-content;
    }
    .t-desc { 
        font-size: 0.8rem; 
        color: #555; 
        line-height: 1.4;
        margin-bottom: 8px !important;
        flex-grow: 1;
    }
    .t-price { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 1rem; 
        font-weight: 700; 
        color: #d9534f; 
        margin: 5px 0 !important;
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
    .dash-val { 
        font-size: 1.5rem; 
        font-weight: 900; 
        color: #d9534f; 
        font-family: 'Inter', sans-serif; 
        line-height: 1;
    }
    .dash-label { 
        font-size: 0.75rem; 
        color: #86868b; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-top: 5px !important;
    }

    /* --- 按钮样式覆盖 --- */
    div[data-testid="stButton"] button {
        width: 100% !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* --- Radio Button 横向样式 --- */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 20px;
        justify-content: center;
        background: white;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e5e5e5;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 状态管理 - 初始化默认值
# ==========================================
if 'sold_items' not in st.session_state:
    st.session_state.sold_items = set() 
if 'total_revenue' not in st.session_state:
    st.session_state.total_revenue = 0
if 'trigger_refresh' not in st.session_state:
    st.session_state.trigger_refresh = False
if 'current_museum' not in st.session_state:
    st.session_state.current_museum = "南京" # 默认城市

# ==========================================
# 5. 顶部导航 (替代侧边栏)
# ==========================================
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏛️ 国宝拍卖行 | National Treasures Auction</h1>", unsafe_allow_html=True)

# 使用 horizontal radio 作为顶部导航
selected_museum = st.radio(
    "📍 切换博物馆 / Switch Museum:",
    list(MUSEUM_DATA.keys()),
    index=list(MUSEUM_DATA.keys()).index(st.session_state.current_museum),
    horizontal=True,
    label_visibility="collapsed"
)

# 切换逻辑
if selected_museum != st.session_state.current_museum:
    st.session_state.current_museum = selected_museum
    st.session_state.trigger_refresh = True

# ==========================================
# 6. 顶部仪表盘 (动态换算)
# ==========================================
curr_city = st.session_state.current_museum
mansion_cfg = MANSION_CONFIG[curr_city]
mansion_name = mansion_cfg["name"]
mansion_price = mansion_cfg["price"]

# 修复除零错误
villa_count = st.session_state.total_revenue / mansion_price if mansion_price != 0 else 0
total_revenue_yi = st.session_state.total_revenue / 100000000

dashboard_html = f"""
<div class="dashboard">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.2rem; margin-right: 15px;">🏛️</div>
            <div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #111;">{curr_city}宝藏拍卖行</div>
                <div style="font-size: 0.8rem; color: #888;">NATIONAL TREASURES AUCTION</div>
            </div>
        </div>
        <div style="text-align: right; display: flex; gap: 40px; align-items: center;">
            <div>
                <div class="dash-val">¥{total_revenue_yi:.2f}亿</div>
                <div class="dash-label">当前拍卖总额</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 10px;">🏡</div>
                <div style="text-align: left;">
                    <div class="dash-val" style="color: #2AAD67;">× {villa_count:.1f}套</div>
                    <div class="dash-label">折合{mansion_name}</div>
                </div>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(dashboard_html, unsafe_allow_html=True)

# ==========================================
# 7. 核心函数
# ==========================================
def format_price(price):
    if price >= 100000000:
        return f"{price/100000000:.1f}亿"
    elif price >= 10000:
        return f"{price/10000:.0f}万"
    return str(price)

def sell_item(item_id, price):
    if item_id not in st.session_state.sold_items:
        st.session_state.sold_items.add(item_id)
        st.session_state.total_revenue += price
        st.session_state.trigger_refresh = True
        st.toast(f"🔨 成交！入账 ¥{format_price(price)}", icon="💰")

def reset_auction():
    st.session_state.sold_items = set()
    st.session_state.total_revenue = 0
    st.session_state.trigger_refresh = True
    st.toast("🔄 所有拍卖记录已重置", icon="✅")

# ==========================================
# 8. 主内容区 (当前城市的文物)
# ==========================================
current_treasures = MUSEUM_DATA[curr_city]

# 布局：每行4个
cols_per_row = 4
rows = [current_treasures[i:i + cols_per_row] for i in range(0, len(current_treasures), cols_per_row)]

for row_items in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for idx, item in enumerate(row_items):
        with cols[idx]:
            is_sold = item['id'] in st.session_state.sold_items
            
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
            
            # 按钮
            if is_sold:
                st.button("🚫 已私有化", key=f"btn_sold_{item['id']}", disabled=True, use_container_width=True)
            else:
                st.button(
                    "🔨 立即拍卖", 
                    key=f"btn_{item['id']}", 
                    type="primary", 
                    use_container_width=True,
                    on_click=sell_item,
                    args=(item['id'], item['price'])
                )

# ==========================================
# 9. 底部重置区
# ==========================================
st.divider()
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.button("🔄 重置所有拍卖记录", type="secondary", use_container_width=True, on_click=reset_auction)

# ==========================================
# 10. 自动刷新逻辑
# ==========================================
if st.session_state.trigger_refresh:
    st.session_state.trigger_refresh = False
    st.rerun()

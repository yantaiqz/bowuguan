import streamlit as st

# 必须先定义 CSS 样式，否则 class="dash-val" 无效
st.markdown("""
<style>
    /* 定义仪表盘容器样式 */
    .dashboard {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        padding: 15px 20px;
        border-bottom: 1px solid #e5e5e5;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    /* 定义数字样式 */
    .dash-val { 
        font-size: 1.8rem; 
        font-weight: 900; 
        color: #d9534f; 
        font-family: sans-serif; 
    }
    
    /* 定义标签样式 */
    .dash-label { 
        font-size: 0.8rem; 
        color: #86868b; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
    }
    
    /* 定义图标样式 */
    .villa-icon { 
        font-size: 2rem; 
        margin-right: 10px; 
    }
</style>
""", unsafe_allow_html=True)

# 渲染 HTML 内容（补全了最外层的 .dashboard div）
st.markdown("""
<div class="dashboard">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.2rem; margin-right: 15px;">🏛️</div>
            <div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #111;">南博宝藏拍卖行</div>
            </div>
        </div>

        <div style="text-align: right; display: flex; gap: 40px;">
            <div>
                <div class="dash-val">¥8.00亿</div>
                <div class="dash-label">当前拍卖总额</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div class="villa-icon">🏡</div>
                <div style="text-align: left;">
                    <div class="dash-val" style="color: #2AAD67;">× 8.0栋</div>
                    <div class="dash-label">折合颐和路民国别墅</div>
                </div>
            </div>
        </div>
        
    </div>
</div>
""", unsafe_allow_html=True) # 关键：必须加这个参数

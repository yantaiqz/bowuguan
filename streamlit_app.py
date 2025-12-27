<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>优化后页面 - 明细置顶</title>
    <style>
        /* 全局样式重置与基础配置 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "Microsoft YaHei", sans-serif;
        }

        :root {
            /* 统一配色方案，提升视觉一致性 */
            --primary-color: #165DFF;
            --secondary-color: #F5F7FA;
            --text-primary: #333333;
            --text-secondary: #666666;
            --border-color: #E5E6EB;
            --hover-color: #EFF6FF;
        }

        body {
            background-color: #FAFAFA;
            color: var(--text-primary);
            line-height: 1.6;
        }

        /* 页面容器：居中约束宽度，避免过大/过小 */
        .page-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* 头部样式 */
        header {
            padding: 20px 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 30px;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: var(--primary-color);
        }

        .nav-menu {
            display: flex;
            gap: 30px;
        }

        .nav-menu a {
            text-decoration: none;
            color: var(--text-secondary);
            transition: color 0.3s ease;
        }

        .nav-menu a:hover {
            color: var(--primary-color);
        }

        /* 核心：明细模块（置顶放置，视觉优先级最高） */
        .detail-module {
            background-color: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            padding: 24px;
            margin-bottom: 30px;
            transition: box-shadow 0.3s ease;
        }

        .detail-module:hover {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        }

        .detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .detail-title {
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .detail-actions {
            display: flex;
            gap: 16px;
        }

        .btn {
            padding: 8px 16px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background-color: var(--primary-color);
            color: #FFFFFF;
        }

        .btn-primary:hover {
            background-color: #0E4BDB;
        }

        .btn-default {
            background-color: var(--secondary-color);
            color: var(--text-secondary);
        }

        .btn-default:hover {
            background-color: var(--hover-color);
        }

        .detail-list {
            width: 100%;
            border-collapse: collapse;
        }

        .detail-list th,
        .detail-list td {
            padding: 12px 16px;
            text-align: left;
            font-size: 14px;
        }

        .detail-list th {
            background-color: var(--secondary-color);
            color: var(--text-secondary);
            font-weight: 500;
        }

        .detail-list tbody tr {
            border-bottom: 1px solid var(--border-color);
            transition: background-color 0.3s ease;
        }

        .detail-list tbody tr:hover {
            background-color: var(--hover-color);
        }

        .detail-list td {
            color: var(--text-primary);
        }

        /* 其他页面模块（示例：统计、表单） */
        .other-modules {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }

        .module-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            padding: 24px;
            transition: box-shadow 0.3s ease;
        }

        .module-card:hover {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        }

        .module-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-primary);
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--border-color);
        }

        .stat-item:last-child {
            border-bottom: none;
        }

        /* 底部样式 */
        footer {
            padding: 20px 0;
            text-align: center;
            color: var(--text-secondary);
            font-size: 14px;
            border-top: 1px solid var(--border-color);
            margin-top: 40px;
        }

        /* 响应式适配：移动端优化 */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 16px;
                align-items: flex-start;
            }

            .detail-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 16px;
            }

            .other-modules {
                grid-template-columns: 1fr;
            }

            .detail-list th,
            .detail-list td {
                padding: 10px 8px;
                font-size: 13px;
            }

            .detail-actions {
                width: 100%;
                justify-content: space-between;
            }
        }
    </style>
</head>
<body>
    <div class="page-container">
        <!-- 页面头部 -->
        <header>
            <div class="header-content">
                <div class="logo">系统平台</div>
                <nav class="nav-menu">
                    <a href="#">首页</a>
                    <a href="#">数据</a>
                    <a href="#">设置</a>
                </nav>
            </div>
        </header>

        <!-- 核心：明细模块（置顶，位于头部之后、其他模块之前） -->
        <section class="detail-module">
            <div class="detail-header">
                <h2 class="detail-title">业务明细列表</h2>
                <div class="detail-actions">
                    <button class="btn btn-default">导出明细</button>
                    <button class="btn btn-primary">新增记录</button>
                </div>
            </div>
            <table class="detail-list">
                <thead>
                    <tr>
                        <th>序号</th>
                        <th>业务名称</th>
                        <th>金额</th>
                        <th>状态</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>产品采购</td>
                        <td>¥12,800.00</td>
                        <td>已完成</td>
                        <td>2025-12-20</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>客户回款</td>
                        <td>¥25,600.00</td>
                        <td>已完成</td>
                        <td>2025-12-22</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>费用报销</td>
                        <td>¥1,560.00</td>
                        <td>审核中</td>
                        <td>2025-12-25</td>
                    </tr>
                </tbody>
            </table>
        </section>

        <!-- 其他页面模块（示例） -->
        <section class="other-modules">
            <div class="module-card">
                <h3 class="module-title">数据统计汇总</h3>
                <div class="stat-item">
                    <span>本月总营收</span>
                    <span>¥156,800.00</span>
                </div>
                <div class="stat-item">
                    <span>本月总支出</span>
                    <span>¥89,200.00</span>
                </div>
                <div class="stat-item">
                    <span>本月净利润</span>
                    <span>¥67,600.00</span>
                </div>
            </div>
            <div class="module-card">
                <h3 class="module-title">快速操作表单</h3>
                <div class="stat-item">
                    <span>待审核记录</span>
                    <span>3 条</span>
                </div>
                <div class="stat-item">
                    <span>待跟进业务</span>
                    <span>8 条</span>
                </div>
                <div class="stat-item">
                    <span>即将到期任务</span>
                    <span>2 条</span>
                </div>
            </div>
        </section>

        <!-- 页面底部 -->
        <footer>
            © 2025 系统平台 版权所有
        </footer>
    </div>
</body>
</html>

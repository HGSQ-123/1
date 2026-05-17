# 电商利润分析工具 - E-commerce Profit Analyzer

📊 一个面向电商卖家的利润分析 SaaS 工具，支持淘宝/拼多多/抖音/京东等平台订单数据一键分析。

## ✨ 功能

- 🔐 **用户系统**：注册/登录、免费版(3次/月) / Pro版(无限)
- 🛒 **多平台**：淘宝、拼多多、抖音小店、京东、通用格式
- 📊 **智能分析**：自动计算营收、成本、净利润、利润率
- 🏆 **产品排名**：一眼看出哪个产品最赚钱、哪个在亏
- 📈 **趋势图表**：每日销售额/利润交互式折线图
- 📥 **一键导出**：Excel + CSV 报告下载
- 💰 **支付系统**：模拟支付(测试) + 微信/支付宝接口框架
- 🔧 **管理后台**：用户管理、支付记录、使用统计

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
streamlit run app.py
```

### 3. 打开浏览器
访问 http://localhost:8501

## 📋 数据格式

上传的 Excel/CSV 需包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| 日期 | 订单日期 | 2026-05-01 |
| 产品名称 | 产品名 | 蓝牙耳机 |
| 售价 | 单价 | 89.9 |
| 成本 | 单品成本 | 45 |
| 数量 | 销售数量 | 23 |

## 📁 项目结构

```
├── app.py              # 主应用
├── auth.py             # 用户认证模块
├── platforms.py        # 多平台适配
├── payment.py          # 支付模块
├── pages/
│   ├── 1_💎_支付升级.py  # 支付升级页面
│   └── 2_🔧_管理后台.py  # 管理员后台
├── requirements.txt    # 依赖
├── example_orders.csv  # 测试数据
└── .streamlit/
    └── config.toml     # 主题配置
```

## ☁️ 部署到 Streamlit Cloud

1. 将代码推送到 GitHub
2. 访问 https://share.streamlit.io
3. 点击 "New app"，选择仓库和分支
4. Main file path 填写 `app.py`
5. 点击 Deploy

## 🔌 接入真实支付

编辑 `payment.py`，填写对应配置：

**微信支付：**
```python
WECHAT_CONFIG = {
    "appid": "你的AppID",
    "mchid": "你的商户号",
    "api_key": "你的API密钥",
    "notify_url": "https://你的域名/api/wechat_notify",
}
```

**支付宝：**
```python
ALIPAY_CONFIG = {
    "app_id": "你的AppID",
    "private_key": "你的应用私钥",
    "alipay_public_key": "支付宝公钥",
    "notify_url": "https://你的域名/api/alipay_notify",
}
```

## 📝 许可

内部项目，仅供学习交流。

"""
电商平台适配模块 - Platform Presets
支持主流电商平台订单格式的自动识别和列名映射
"""

# ==================== 平台预设配置 ====================
PLATFORM_PRESETS = {
    "淘宝/天猫": {
        "icon": "🛒",
        "description": "支持淘宝/天猫后台导出的订单报表",
        "column_keywords": {
            "date": ["订单创建时间", "下单时间", "付款时间", "日期"],
            "product": ["商品名称", "宝贝标题", "商品", "产品"],
            "price": ["商品单价", "宝贝单价", "售价", "实付金额"],
            "cost": ["成本", "进货价"],
            "qty": ["购买数量", "数量", "件数"],
        },
        "notes": "导出路径：千牛卖家中心 → 交易管理 → 已卖出的宝贝 → 导出",
    },
    "拼多多": {
        "icon": "📱",
        "description": "支持拼多多商家后台导出的订单数据",
        "column_keywords": {
            "date": ["订单确认时间", "成交时间", "下单时间", "日期"],
            "product": ["商品名称", "商品标题", "商品"],
            "price": ["商品单价", "成交单价", "售价"],
            "cost": ["成本", "采购价"],
            "qty": ["商品数量", "成交数量", "数量"],
        },
        "notes": "导出路径：商家后台 → 订单管理 → 订单查询 → 批量导出",
    },
    "抖音小店": {
        "icon": "🎬",
        "description": "支持抖店后台导出的订单明细",
        "column_keywords": {
            "date": ["下单时间", "付款时间", "订单创建时间", "日期"],
            "product": ["商品名称", "商品标题", "商品"],
            "price": ["商品单价", "支付金额", "售价", "实付金额"],
            "cost": ["成本", "进货价"],
            "qty": ["购买数量", "商品数量", "数量"],
        },
        "notes": "导出路径：抖店后台 → 订单 → 订单管理 → 导出",
    },
    "京东": {
        "icon": "🐶",
        "description": "支持京东商家后台订单导出",
        "column_keywords": {
            "date": ["下单时间", "订单日期", "日期"],
            "product": ["商品名称", "SKU名称", "商品"],
            "price": ["商品单价", "京东价", "售价"],
            "cost": ["成本", "采购价"],
            "qty": ["商品数量", "购买数量", "数量"],
        },
        "notes": "导出路径：京麦后台 → 订单管理 → 订单查询 → 导出",
    },
    "通用格式": {
        "icon": "📊",
        "description": "手动匹配列名，适配任意格式的表格",
        "column_keywords": {
            "date": ["日期", "date", "时间", "time"],
            "product": ["产品", "product", "名称", "name", "商品", "货品"],
            "price": ["售价", "price", "单价", "销售价", "卖价"],
            "cost": ["成本", "cost", "进价", "进货价", "采购价"],
            "qty": ["数量", "qty", "quantity", "件数", "销量"],
        },
        "notes": "适用于所有表格，需手动指定每列含义",
    },
}


def detect_platform(df_columns: list) -> str:
    """
    根据列名自动检测平台类型
    返回平台名称，默认返回"通用格式"
    """
    cols_lower = [c.strip().lower() for c in df_columns]

    best_match = "通用格式"
    best_score = 0

    for platform_name, preset in PLATFORM_PRESETS.items():
        if platform_name == "通用格式":
            continue

        score = 0
        for col_type, keywords in preset["column_keywords"].items():
            for kw in keywords:
                if any(kw.lower() in col for col in cols_lower):
                    score += 1
                    break

        # 至少匹配4种列类型才算
        if score >= 4 and score > best_score:
            best_score = score
            best_match = platform_name

    return best_match


def get_platform_keywords(platform_name: str) -> dict:
    """获取指定平台的列名关键词"""
    if platform_name in PLATFORM_PRESETS:
        return PLATFORM_PRESETS[platform_name]["column_keywords"]
    return PLATFORM_PRESETS["通用格式"]["column_keywords"]


def get_platform_info(platform_name: str) -> dict:
    """获取平台完整信息"""
    return PLATFORM_PRESETS.get(platform_name, PLATFORM_PRESETS["通用格式"])


def auto_detect_columns_with_platform(df_columns: list, platform_name: str = "通用格式") -> dict:
    """
    根据平台预设自动检测列名映射
    返回: {"date": "列名", "product": "列名", ...}
    """
    keywords = get_platform_keywords(platform_name)
    col_map = {}
    all_cols = [c.strip() for c in df_columns]

    for col_type, kw_list in keywords.items():
        for col in all_cols:
            col_lower = col.lower()
            if any(kw.lower() in col_lower for kw in kw_list):
                col_map[col_type] = col
                break

    return col_map

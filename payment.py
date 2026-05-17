"""
支付模块 - Payment Module
支持：微信支付 / 支付宝 / 模拟支付（测试用）

真实支付需要申请：
- 微信支付：https://pay.weixin.qq.com （需营业执照 + 商户号）
- 支付宝：https://open.alipay.com （需营业执照 + 应用ID）

申请到商户号后，替换下方对应函数中的 TODO 部分即可。
"""

import hashlib
import time
import uuid
import auth
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


# ==================== 模拟支付（开发测试用） ====================
def mock_pay(user_id: int, tier: str = "pro", amount: float = 9.9) -> tuple:
    """
    模拟支付 - 直接升级用户
    正式上线后删除此函数
    返回: (success: bool, message: str)
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        # 记录支付
        conn.execute(
            "INSERT INTO payments (user_id, amount, tier, status) VALUES (?, ?, ?, 'completed')",
            (user_id, amount, tier),
        )
        # 升级用户
        conn.execute("UPDATE users SET tier = ? WHERE id = ?", (tier, user_id))
        conn.commit()
        return True, f"升级成功！已是 {tier.upper()} 会员"
    except Exception as e:
        return False, f"升级失败：{e}"
    finally:
        conn.close()


# ==================== 微信支付（真实接口框架） ====================
WECHAT_CONFIG = {
    "appid": "",       # TODO: 替换为你的微信支付 AppID
    "mchid": "",       # TODO: 替换为你的商户号
    "api_key": "",     # TODO: 替换为你的 API 密钥
    "notify_url": "",  # TODO: 替换为你的回调地址
}


def wechat_create_order(user_id: int, amount: float, tier: str) -> dict:
    """
    微信支付 - 创建预支付订单
    需要先申请微信商户号，填写 WECHAT_CONFIG
    文档：https://pay.weixin.qq.com/doc/v3/merchant/4012791856
    """
    if not WECHAT_CONFIG["appid"]:
        return {"error": "微信支付未配置，请填写 WECHAT_CONFIG"}

    # TODO: 调用微信支付统一下单 API
    # 参考代码结构：
    # order = {
    #     "appid": WECHAT_CONFIG["appid"],
    #     "mchid": WECHAT_CONFIG["mchid"],
    #     "out_trade_no": f"ORDER_{user_id}_{int(time.time())}",
    #     "total_fee": int(amount * 100),  # 单位：分
    #     "body": f"电商利润分析工具 {tier.upper()} 会员",
    #     "notify_url": WECHAT_CONFIG["notify_url"],
    # }
    # sign = _wechat_sign(order)
    # order["sign"] = sign
    # response = requests.post("https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi", json=order)
    # return response.json()

    return {"status": "pending", "message": "微信支付接口待配置"}


def wechat_verify_notify(notify_data: dict) -> bool:
    """
    微信支付回调验证
    收到微信支付成功通知后调用
    """
    # TODO: 验证签名，更新用户会员状态
    # if notify_data["return_code"] == "SUCCESS":
    #     user_id = int(notify_data["out_trade_no"].split("_")[1])
    #     auth.upgrade_user(user_id, "pro")
    #     return True
    return False


def _wechat_sign(data: dict) -> str:
    """微信支付签名"""
    sorted_items = sorted(data.items())
    sign_str = "&".join(f"{k}={v}" for k, v in sorted_items if v)
    sign_str += f"&key={WECHAT_CONFIG['api_key']}"
    return hashlib.md5(sign_str.encode()).hexdigest().upper()


# ==================== 支付宝（真实接口框架） ====================
ALIPAY_CONFIG = {
    "app_id": "",           # TODO: 替换为你的支付宝 AppID
    "private_key": "",      # TODO: 替换为你的应用私钥
    "alipay_public_key": "",# TODO: 替换为支付宝公钥
    "notify_url": "",       # TODO: 替换为你的回调地址
}


def alipay_create_order(user_id: int, amount: float, tier: str) -> dict:
    """
    支付宝 - 创建支付订单
    需要先申请支付宝商户，填写 ALIPAY_CONFIG
    文档：https://opendocs.alipay.com/open/203/105285
    """
    if not ALIPAY_CONFIG["app_id"]:
        return {"error": "支付宝未配置，请填写 ALIPAY_CONFIG"}

    # TODO: 调用支付宝统一下单 API
    # 参考代码结构：
    # from alipay import AliPay
    # alipay = AliPay(
    #     appid=ALIPAY_CONFIG["app_id"],
    #     app_notify_url=ALIPAY_CONFIG["notify_url"],
    #     app_private_key_string=ALIPAY_CONFIG["private_key"],
    #     alipay_public_key_string=ALIPAY_CONFIG["alipay_public_key"],
    #     sign_type="RSA2",
    # )
    # order_string = alipay.api_alipay_trade_page_pay(
    #     out_trade_no=f"ORDER_{user_id}_{int(time.time())}",
    #     total_amount=amount,
    #     subject=f"电商利润分析工具 {tier.upper()} 会员",
    # )
    # return {"pay_url": f"https://openapi.alipay.com/gateway.do?{order_string}"}

    return {"status": "pending", "message": "支付宝接口待配置"}


# ==================== 通用升级函数 ====================
def process_upgrade(user_id: int, tier: str = "pro", amount: float = 9.9,
                    method: str = "mock") -> tuple:
    """
    统一升级入口
    method: "mock" | "wechat" | "alipay"
    """
    if method == "mock":
        return mock_pay(user_id, tier, amount)
    elif method == "wechat":
        result = wechat_create_order(user_id, amount, tier)
        if "error" in result:
            return False, result["error"]
        return True, "请扫码支付"
    elif method == "alipay":
        result = alipay_create_order(user_id, amount, tier)
        if "error" in result:
            return False, result["error"]
        return True, "跳转支付宝支付"
    else:
        return False, "不支持的支付方式"


def get_payment_history(user_id: int) -> list:
    """获取用户支付历史"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    records = conn.execute(
        "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in records]

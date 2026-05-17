"""
支付升级页面 - Upgrade to Pro
"""
import streamlit as st
import payment
import auth

st.set_page_config(page_title="升级 Pro", page_icon="⭐", layout="centered")

# 检查登录
if "user" not in st.session_state or st.session_state.user is None:
    st.error("请先登录")
    st.markdown("[→ 返回登录页](/)")
    st.stop()

user = st.session_state.user

st.markdown("""
<div style="text-align:center; padding:1rem 0;">
    <span style="font-size:3rem;">⭐</span>
    <h1>升级到 Pro</h1>
    <p style="color:#64748B;">解锁全部功能，无限次分析</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================== 套餐对比 ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="border:1px solid #E2E8F0; border-radius:12px; padding:1.5rem; text-align:center;">
        <h3>👤 免费版</h3>
        <p style="color:#64748B;">当前</p>
        <hr>
        <p>📊 每月 3 次分析</p>
        <p>📈 基础图表</p>
        <p>📥 CSV 导出</p>
        <p>🛒 单平台</p>
        <p style="color:#94A3B8;">—</p>
        <p style="color:#94A3B8;">—</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="border:2px solid #2563EB; border-radius:12px; padding:1.5rem; text-align:center; background:#F8FAFC;">
        <h3>⭐ Pro 版</h3>
        <h1 style="color:#2563EB;">¥9.9<span style="font-size:1rem;">/月</span></h1>
        <hr>
        <p>📊 无限次分析</p>
        <p>📈 高级图表 + 导出</p>
        <p>📥 Excel + CSV 导出</p>
        <p>🛒 全平台支持</p>
        <p>📋 分析历史记录</p>
        <p>💬 优先客服支持</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==================== 当前会员状态 ====================
if user["tier"] == "pro":
    st.success("🎉 你已经是 Pro 会员！")

    # 显示支付历史
    records = payment.get_payment_history(user["id"])
    if records:
        st.markdown("### 📋 支付记录")
        for r in records:
            status_icon = "✅" if r["status"] == "completed" else "⏳"
            st.markdown(
                f"{status_icon} {r['tier'].upper()} · "
                f"¥{r['amount']} · "
                f"{r['created_at'][:10]}"
            )
else:
    st.markdown("### 💳 选择支付方式")

    pay_method = st.radio(
        "支付方式",
        ["模拟支付（测试用）", "微信支付（即将上线）", "支付宝（即将上线）"],
        horizontal=True,
    )

    st.markdown("---")

    # 支付按钮
    amount = 9.9

    if pay_method == "模拟支付（测试用）":
        st.info("💡 这是测试模式，点击即升级，不会真实扣款")
        if st.button("🔓 确认升级 (¥9.9/月)", type="primary", use_container_width=True):
            with st.spinner("处理中..."):
                ok, msg = payment.process_upgrade(user["id"], "pro", amount, "mock")
                if ok:
                    st.session_state.user = auth.get_user_by_id(user["id"])
                    st.success(msg)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)

    elif pay_method == "微信支付（即将上线）":
        st.warning("微信支付需要商户号，正在接入中")
        st.markdown("""
        ### 微信支付接入步骤（开发者参考）
        1. 注册微信商户平台 https://pay.weixin.qq.com
        2. 获取 AppID、商户号、API密钥
        3. 填写 `payment.py` 中的 `WECHAT_CONFIG`
        4. 配置支付回调地址
        """)

    elif pay_method == "支付宝（即将上线）":
        st.warning("支付宝需要商户认证，正在接入中")
        st.markdown("""
        ### 支付宝接入步骤（开发者参考）
        1. 注册支付宝开放平台 https://open.alipay.com
        2. 创建应用获取 AppID
        3. 生成 RSA2 密钥对
        4. 填写 `payment.py` 中的 `ALIPAY_CONFIG`
        """)

st.divider()
st.markdown("[← 返回主页](/)")

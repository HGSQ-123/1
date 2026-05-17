"""
电商利润分析工具 - E-commerce Profit Analyzer
SaaS 模式，支持多平台订单分析
免费版：每月 3 次 | Pro版：每月 9.9 无限次
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
import auth
import platforms

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="电商利润分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS 样式 ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white !important; margin: 0; font-size: 2rem; }
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #E2E8F0;
        transition: all 0.2s;
    }
    .feature-card:hover {
        border-color: #2563EB;
        box-shadow: 0 4px 16px rgba(37,99,235,0.1);
    }
    .tier-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tier-free { background: #DBEAFE; color: #2563EB; }
    .tier-pro { background: #DCFCE7; color: #16A34A; }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)


# ==================== 会话初始化 ====================
if "user" not in st.session_state:
    st.session_state.user = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <span style="font-size:2rem;">📊</span>
        <h3 style="margin:0;">电商利润分析</h3>
        <p style="color:#64748B; font-size:0.85rem;">让数据告诉你答案</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ---------- 未登录 ----------
    if st.session_state.user is None:
        if not st.session_state.show_register:
            st.markdown("### 🔐 登录")
            login_user = st.text_input("用户名", key="login_user")
            login_pass = st.text_input("密码", type="password", key="login_pass")

            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.button("登录", use_container_width=True, type="primary")
            with col_b:
                reg_btn = st.button("注册新账号", use_container_width=True)

            if login_btn:
                user, msg = auth.login_user(login_user, login_pass)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error(msg)

            if reg_btn:
                st.session_state.show_register = True
                st.rerun()
        else:
            st.markdown("### 📝 注册")
            reg_user = st.text_input("用户名 (3位以上)", key="reg_user")
            reg_email = st.text_input("邮箱 (选填)", key="reg_email")
            reg_pass = st.text_input("密码 (6位以上)", type="password", key="reg_pass")
            reg_pass2 = st.text_input("确认密码", type="password", key="reg_pass2")

            col_c, col_d = st.columns(2)
            with col_c:
                reg_submit = st.button("提交注册", use_container_width=True, type="primary")
            with col_d:
                back_btn = st.button("返回登录", use_container_width=True)

            if reg_submit:
                if reg_pass != reg_pass2:
                    st.error("两次密码不一致")
                else:
                    ok, msg = auth.register_user(reg_user, reg_pass, reg_email)
                    if ok:
                        st.success(msg + " 请登录")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(msg)

            if back_btn:
                st.session_state.show_register = False
                st.rerun()

    # ---------- 已登录 ----------
    else:
        user = st.session_state.user
        tier_emoji = "⭐" if user["tier"] == "pro" else "👤"
        tier_class = "tier-pro" if user["tier"] == "pro" else "tier-free"

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:8px 0;">
            <span style="font-size:2rem;">{tier_emoji}</span>
            <div>
                <strong>{user['username']}</strong>
                <br>
                <span class="tier-badge {tier_class}">
                    {'Pro 会员' if user['tier'] == 'pro' else '免费版'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if user["tier"] == "free":
            used = auth.get_monthly_usage(user["id"])
            remaining = max(0, 3 - used)
            st.progress(used / 3, text=f"本月已用 {used}/3 次")
            if remaining == 0:
                st.warning("本月次数已用完")

        st.divider()
        st.markdown("### 📁 上传数据")

        platform_list = list(platforms.PLATFORM_PRESETS.keys())
        selected_platform = st.selectbox(
            "选择来源平台",
            platform_list,
            format_func=lambda x: f"{platforms.PLATFORM_PRESETS[x]['icon']} {x}",
        )
        st.caption(platforms.PLATFORM_PRESETS[selected_platform]["notes"])

        uploaded_file = st.file_uploader(
            "选择订单文件",
            type=["csv", "xlsx", "xls"],
            help="支持淘宝/拼多多/抖音/京东等平台导出的订单文件",
        )

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.divider()
    st.markdown("### 💰 升级 Pro")
    st.markdown("""
    ✅ 无限次分析 | ✅ 多平台 | ✅ 历史记录
    **每月 9.9**
    """)

    if st.session_state.user and st.session_state.user["tier"] == "free":
        if st.button("🔓 立即升级", use_container_width=True, type="primary"):
            st.switch_page("pages/1_💎_支付升级.py")

    st.divider()
    st.caption(" 2026 电商利润分析工具")


# ==================== 主界面 ====================
if st.session_state.user is None:
    # 欢迎页
    st.markdown("""
    <div class="main-header">
        <h1>📊 电商利润分析工具</h1>
        <p style="margin:0.5rem 0 0 0; opacity:0.9;">
            上传订单，秒出利润报告
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🌟 为什么选择我们？")
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        st.markdown('<div class="feature-card"><span style="font-size:2rem;">🚀</span><h4>秒级分析</h4><p style="color:#64748B;font-size:0.85rem;">上传即出结果</p></div>', unsafe_allow_html=True)
    with fc2:
        st.markdown('<div class="feature-card"><span style="font-size:2rem;">🛒</span><h4>多平台</h4><p style="color:#64748B;font-size:0.85rem;">淘宝/拼多多/抖音/京东</p></div>', unsafe_allow_html=True)
    with fc3:
        st.markdown('<div class="feature-card"><span style="font-size:2rem;">📈</span><h4>可视化</h4><p style="color:#64748B;font-size:0.85rem;">直观图表</p></div>', unsafe_allow_html=True)
    with fc4:
        st.markdown('<div class="feature-card"><span style="font-size:2rem;">📥</span><h4>一键导出</h4><p style="color:#64748B;font-size:0.85rem;">Excel报告</p></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 💎 定价方案")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("""
        <div style="border:1px solid #E2E8F0; border-radius:12px; padding:2rem; text-align:center;">
            <h3>🆓 免费版</h3>
            <h1 style="color:#2563EB;">Free</h1>
            <hr>
            <p>✅ 每月 3 次分析</p>
            <p>✅ 基础图表</p>
            <p>✅ CSV 导出</p>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown("""
        <div style="border:2px solid #2563EB; border-radius:12px; padding:2rem; text-align:center; background:#F8FAFC;">
            <h3>⭐ Pro 版</h3>
            <h1 style="color:#2563EB;">¥9.9/月</h1>
            <hr>
            <p>✅ 无限次分析</p>
            <p>✅ 全平台支持</p>
            <p>✅ Excel 报告</p>
            <p>✅ 历史记录</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 3 步开始")
    st.markdown("1. 👈 **左侧注册** 2. 📤 **上传文件** 3. 📊 **查看结果**")

elif uploaded_file is None:
    # 已登录但未上传
    st.markdown("""
    <div class="main-header">
        <h1>📊 电商利润分析工具</h1>
        <p style="margin:0.5rem 0 0 0; opacity:0.9;">准备就绪，请上传订单数据</p>
    </div>
    """, unsafe_allow_html=True)
    st.info(f"👈 请在左侧选择平台并上传订单文件")
    st.markdown(f"当前平台：**{platforms.PLATFORM_PRESETS[selected_platform]['icon']} {selected_platform}**")

else:
    # ==================== 主分析流程 ====================
    try:
        can, usage_msg = auth.can_analyze(st.session_state.user)
        if not can:
            st.error(usage_msg)
            st.markdown("### 💡 升级 Pro 即可无限使用")
            st.stop()

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = [c.strip() for c in df.columns]
        col_map = platforms.auto_detect_columns_with_platform(
            df.columns.tolist(), selected_platform
        )

        if len(col_map) < 5:
            st.warning("部分列名未能自动识别，请手动指定：")
            all_cols = df.columns.tolist()
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                date_col = st.selectbox("📅 日期", all_cols, key="date")
            with c2:
                product_col = st.selectbox("🏷️ 产品", all_cols, key="product")
            with c3:
                price_col = st.selectbox("💰 售价", all_cols, key="price")
            with c4:
                cost_col = st.selectbox("📦 成本", all_cols, key="cost")
            with c5:
                qty_col = st.selectbox("🔢 数量", all_cols, key="qty")
            col_map = {
                "date": date_col, "product": product_col,
                "price": price_col, "cost": cost_col, "qty": qty_col,
            }

        date_col = col_map["date"]
        product_col = col_map["product"]
        price_col = col_map["price"]
        cost_col = col_map["cost"]
        qty_col = col_map["qty"]

        df["销售额"] = df[price_col] * df[qty_col]
        df["总成本"] = df[cost_col] * df[qty_col]
        df["利润"] = df["销售额"] - df["总成本"]
        df["利润率"] = (df["利润"] / df["销售额"] * 100).round(2)
        df[date_col] = pd.to_datetime(df[date_col])

        auth.record_usage(st.session_state.user["id"], "analysis", uploaded_file.name)

        # ==================== KPI ====================
        total_revenue = df["销售额"].sum()
        total_cost = df["总成本"].sum()
        total_profit = df["利润"].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

        st.markdown(f"""
        <div class="main-header" style="padding:1.2rem 1.5rem;">
            <p style="margin:0; opacity:0.8; font-size:0.85rem;">
                📋 分析结果 · {selected_platform}
            </p>
            <p style="margin:0; font-size:1.2rem; font-weight:600;">
                净利润 ¥{total_profit:,.2f}
                <span style="font-size:0.9rem; opacity:0.8;"> 利润率 {profit_margin:.1f}%</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
        with kpi1:
            st.metric("📦 订单数", f"{len(df):,}")
        with kpi2:
            st.metric("🏷️ 产品数", df[product_col].nunique())
        with kpi3:
            st.metric("💰 总营收", f"¥{total_revenue:,.2f}")
        with kpi4:
            st.metric("📦 总成本", f"¥{total_cost:,.2f}")
        with kpi5:
            st.metric("🎯 净利润", f"¥{total_profit:,.2f}", delta=f"{profit_margin:.1f}%")
        with kpi6:
            st.metric("📊 利润率", f"{profit_margin:.2f}%")

        st.divider()

        # ==================== 产品分析 ====================
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("### 🏆 产品利润排名")

            product_summary = (
                df.groupby(product_col)
                .agg(
                    销售额=("销售额", "sum"),
                    总成本=("总成本", "sum"),
                    利润=("利润", "sum"),
                    销量=(qty_col, "sum"),
                )
                .reset_index()
            )
            product_summary["利润率"] = (
                product_summary["利润"] / product_summary["销售额"] * 100
            ).round(2)
            product_summary = product_summary.sort_values("利润", ascending=False)

            fig_bar = px.bar(
                product_summary,
                x="利润", y=product_col, orientation="h",
                color="利润",
                color_continuous_scale=["#EF4444", "#E2E8F0", "#10B981"],
                title="各产品利润对比", text="利润",
            )
            fig_bar.update_traces(texttemplate="¥%{text:,.0f}", textposition="outside")
            fig_bar.update_layout(height=400, coloraxis_showscale=False)
            st.plotly_chart(fig_bar, width="stretch")

            st.markdown("### 📋 产品明细")
            display_df = product_summary.copy()
            display_df["销售额"] = display_df["销售额"].apply(lambda x: f"¥{x:,.2f}")
            display_df["总成本"] = display_df["总成本"].apply(lambda x: f"¥{x:,.2f}")
            display_df["利润"] = display_df["利润"].apply(lambda x: f"¥{x:,.2f}")
            display_df["利润率"] = display_df["利润率"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(display_df, width="stretch", hide_index=True)

        with col_right:
            st.markdown("### 🔴 亏损预警")
            loss_products = product_summary[product_summary["利润"] < 0]
            if len(loss_products) > 0:
                for _, row in loss_products.iterrows():
                    st.error(
                        f" **{row[product_col]}**\n\n"
                        f"亏损 ¥{abs(row['利润']):,.2f} | 销量 {row['销量']} 件"
                    )
            else:
                st.success(" 所有产品都在盈利！")

            st.divider()
            st.markdown("### 🥧 销售额占比")
            fig_pie = px.pie(
                product_summary, values="销售额", names=product_col,
                hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, width="stretch")

            st.markdown("### 📊 利润率分布")
            profit_products = product_summary[product_summary["利润率"] > 0]
            if len(profit_products) > 0:
                fig_hist = px.histogram(
                    profit_products, x="利润率", nbins=10,
                    title="各产品利润率分布",
                    color_discrete_sequence=["#2563EB"],
                )
                fig_hist.update_layout(height=300)
                st.plotly_chart(fig_hist, width="stretch")

        st.divider()

        # ==================== 趋势分析 ====================
        st.markdown("### 📈 每日趋势")
        daily_summary = (
            df.groupby(date_col)
            .agg(销售额=("销售额", "sum"), 利润=("利润", "sum"))
            .reset_index()
            .sort_values(date_col)
        )

        tab1, tab2 = st.tabs(["📈 销售额趋势", "📉 利润趋势"])
        with tab1:
            fig_sales = px.area(
                daily_summary, x=date_col, y="销售额",
                title="每日销售额变化",
                color_discrete_sequence=["#2563EB"],
            )
            fig_sales.update_layout(height=400)
            st.plotly_chart(fig_sales, width="stretch")

        with tab2:
            fig_profit = px.line(
                daily_summary, x=date_col, y="利润",
                markers=True, title="每日利润变化",
                color_discrete_sequence=["#10B981"],
            )
            fig_profit.add_hline(
                y=0, line_dash="dash", line_color="#EF4444", opacity=0.5,
                annotation_text="盈亏平衡线",
            )
            fig_profit.update_layout(height=400)
            st.plotly_chart(fig_profit, width="stretch")

        st.divider()

        with st.expander("🔍 查看原始数据"):
            st.dataframe(df, width="stretch")

        st.divider()

        # ==================== 导出 ====================
        st.markdown("### 📥 导出报告")
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                product_summary.to_excel(writer, sheet_name="产品利润汇总", index=False)
                daily_summary.to_excel(writer, sheet_name="每日趋势", index=False)
                df.to_excel(writer, sheet_name="原始数据", index=False)
            st.download_button(
                label="📥 下载 Excel 报告",
                data=output.getvalue(),
                file_name=f"电商利润分析_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with col_btn2:
            csv_data = product_summary.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 下载产品汇总 CSV",
                data=csv_data,
                file_name=f"产品利润汇总_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"❌ 数据解析出错：{e}")
        st.markdown("请检查：文件格式是否正确、是否包含必要列（日期/产品/售价/成本/数量）")

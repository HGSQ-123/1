"""
管理后台 - Admin Panel
仅管理员可访问
"""
import streamlit as st
import sqlite3
import os
import auth

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

st.set_page_config(page_title="管理后台", page_icon="🔧", layout="wide")

# 管理员密码（生产环境请改用更安全的方式）
ADMIN_PASSWORD = "admin123"

# 检查管理员登录
if "admin_authed" not in st.session_state:
    st.session_state.admin_authed = False

st.markdown("""
<div style="text-align:center; padding:1rem 0;">
    <span style="font-size:2rem;">🔧</span>
    <h2>管理后台</h2>
</div>
""", unsafe_allow_html=True)

if not st.session_state.admin_authed:
    admin_pwd = st.text_input("管理员密码", type="password")
    if st.button("进入后台", type="primary"):
        if admin_pwd == ADMIN_PASSWORD:
            st.session_state.admin_authed = True
            st.rerun()
        else:
            st.error("密码错误")
    st.markdown("[← 返回主页](/)")
    st.stop()

# ==================== 管理员功能 ====================
tab1, tab2, tab3, tab4 = st.tabs(["👥 用户管理", "💰 支付记录", "📊 使用统计", "⚙️ 设置"])

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# ---------- Tab 1: 用户管理 ----------
with tab1:
    st.markdown("### 👥 用户列表")
    users = conn.execute(
        "SELECT id, username, email, tier, created_at, last_login FROM users ORDER BY created_at DESC"
    ).fetchall()

    if users:
        user_data = []
        for u in users:
            user_data.append({
                "ID": u["id"],
                "用户名": u["username"],
                "邮箱": u["email"] or "-",
                "会员等级": u["tier"],
                "注册时间": u["created_at"][:10] if u["created_at"] else "-",
                "最后登录": u["last_login"][:10] if u["last_login"] else "-",
            })

        import pandas as pd
        df = pd.DataFrame(user_data)
        st.dataframe(df, width="stretch", hide_index=True)

        st.markdown("---")
        st.markdown("### 🔄 手动调整会员等级")

        col_id, col_tier = st.columns(2)
        with col_id:
            target_id = st.number_input("用户 ID", min_value=1, step=1)
        with col_tier:
            new_tier = st.selectbox("新等级", ["free", "pro", "enterprise"])

        if st.button("确认修改", type="primary"):
            conn.execute("UPDATE users SET tier = ? WHERE id = ?", (new_tier, target_id))
            conn.commit()
            st.success(f"用户 #{target_id} 已更新为 {new_tier}")
            st.rerun()
    else:
        st.info("暂无用户")

# ---------- Tab 2: 支付记录 ----------
with tab2:
    st.markdown("### 💰 支付记录")
    payments = conn.execute(
        """SELECT p.id, u.username, p.amount, p.tier, p.status, p.created_at
           FROM payments p
           JOIN users u ON p.user_id = u.id
           ORDER BY p.created_at DESC"""
    ).fetchall()

    if payments:
        pay_data = []
        total_revenue = 0
        for p in payments:
            if p["status"] == "completed":
                total_revenue += p["amount"]
            pay_data.append({
                "ID": p["id"],
                "用户": p["username"],
                "金额": f"¥{p['amount']:.2f}",
                "等级": p["tier"],
                "状态": p["status"],
                "时间": p["created_at"],
            })

        import pandas as pd
        st.dataframe(pd.DataFrame(pay_data), width="stretch", hide_index=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("总支付笔数", len(payments))
        with col_r2:
            st.metric("总收入", f"¥{total_revenue:.2f}")
    else:
        st.info("暂无支付记录")

# ---------- Tab 3: 使用统计 ----------
with tab3:
    st.markdown("### 📊 使用统计")

    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    pro_users = conn.execute("SELECT COUNT(*) FROM users WHERE tier = 'pro'").fetchone()[0]
    free_users = conn.execute("SELECT COUNT(*) FROM users WHERE tier = 'free'").fetchone()[0]
    total_analyses = conn.execute("SELECT COUNT(*) FROM usage_log WHERE action='analysis'").fetchone()[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("总用户", total_users)
    with c2:
        st.metric("Pro 会员", pro_users)
    with c3:
        st.metric("免费用户", free_users)
    with c4:
        st.metric("总分析次数", total_analyses)

    # 最近使用记录
    st.markdown("### 📋 最近分析记录")
    logs = conn.execute(
        """SELECT ul.id, u.username, ul.file_name, ul.created_at
           FROM usage_log ul
           JOIN users u ON ul.user_id = u.id
           ORDER BY ul.created_at DESC
           LIMIT 20"""
    ).fetchall()

    if logs:
        log_data = []
        for l in logs:
            log_data.append({
                "用户": l["username"],
                "文件名": l["file_name"],
                "时间": l["created_at"],
            })
        import pandas as pd
        st.dataframe(pd.DataFrame(log_data), width="stretch", hide_index=True)

# ---------- Tab 4: 设置 ----------
with tab4:
    st.markdown("### ⚙️ 系统设置")

    st.info(f"数据库位置：`{DB_PATH}`")

    if st.button("🗑️ 清除缓存", type="secondary"):
        st.cache_data.clear()
        st.success("缓存已清除")

    with st.expander("⚠️ 危险操作"):
        if st.button("清空使用记录（不可恢复）", type="secondary"):
            conn.execute("DELETE FROM usage_log")
            conn.commit()
            st.warning("使用记录已清空")

conn.close()

st.divider()
st.markdown("[← 返回主页](/)")

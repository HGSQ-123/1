"""
用户认证模块 - User Authentication
使用 SQLite 存储用户数据，支持注册/登录/会员管理
"""
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            tier TEXT DEFAULT 'free',       -- free / pro / enterprise
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            file_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL,
            tier TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, email: str = "") -> tuple:
    """
    注册用户
    返回: (success: bool, message: str)
    """
    if len(username) < 3:
        return False, "用户名至少 3 个字符"
    if len(password) < 6:
        return False, "密码至少 6 个字符"

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, hash_password(password), email),
        )
        conn.commit()
        return True, "注册成功！"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"
    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple:
    """
    登录验证
    返回: (user_dict or None, message: str)
    """
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password)),
    ).fetchone()

    if user:
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user["id"],),
        )
        conn.commit()
        conn.close()
        return dict(user), "登录成功！"
    conn.close()
    return None, "用户名或密码错误"


def get_user_by_id(user_id: int) -> dict:
    """根据 ID 获取用户信息"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_monthly_usage(user_id: int) -> int:
    """获取本月使用次数"""
    conn = get_db()
    count = conn.execute(
        """SELECT COUNT(*) FROM usage_log
           WHERE user_id = ?
           AND created_at >= date('now', 'start of month')""",
        (user_id,),
    ).fetchone()[0]
    conn.close()
    return count


def record_usage(user_id: int, action: str, file_name: str = ""):
    """记录使用日志"""
    conn = get_db()
    conn.execute(
        "INSERT INTO usage_log (user_id, action, file_name) VALUES (?, ?, ?)",
        (user_id, action, file_name),
    )
    conn.commit()
    conn.close()


def can_analyze(user: dict) -> tuple:
    """
    检查用户是否可以分析
    免费用户每月 3 次
    返回: (can: bool, message: str)
    """
    if user["tier"] == "free":
        used = get_monthly_usage(user["id"])
        limit = 3
        if used >= limit:
            return False, f"免费版每月 {limit} 次已用完，升级 Pro 无限使用！"
        return True, f"本月剩余 {limit - used} 次"
    return True, "Pro 用户，无限使用！"


def upgrade_user(user_id: int, tier: str = "pro") -> tuple:
    """
    升级用户会员等级
    返回: (success: bool, message: str)
    """
    valid_tiers = ["free", "pro", "enterprise"]
    if tier not in valid_tiers:
        return False, f"无效等级，可选：{', '.join(valid_tiers)}"

    conn = get_db()
    try:
        conn.execute("UPDATE users SET tier = ? WHERE id = ?", (tier, user_id))
        conn.commit()
        return True, f"已升级为 {tier.upper()} 会员"
    except Exception as e:
        return False, f"升级失败：{e}"
    finally:
        conn.close()


def downgrade_user(user_id: int) -> tuple:
    """
    降级为免费用户
    返回: (success: bool, message: str)
    """
    return upgrade_user(user_id, "free")


def get_all_users() -> list:
    """获取所有用户列表（管理用）"""
    conn = get_db()
    users = conn.execute(
        "SELECT id, username, email, tier, created_at, last_login FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(u) for u in users]


def get_user_stats() -> dict:
    """获取用户统计"""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    pro = conn.execute("SELECT COUNT(*) FROM users WHERE tier='pro'").fetchone()[0]
    free = conn.execute("SELECT COUNT(*) FROM users WHERE tier='free'").fetchone()[0]
    analyses = conn.execute("SELECT COUNT(*) FROM usage_log WHERE action='analysis'").fetchone()[0]
    conn.close()
    return {
        "total_users": total,
        "pro_users": pro,
        "free_users": free,
        "total_analyses": analyses,
    }


# 初始化数据库
init_db()

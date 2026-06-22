import streamlit as st
import json
import os
from datetime import datetime, date

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Smart-Hub Hồng Phát",
    layout="wide",
    page_icon="🏭"
)

DB_FILE = "smart_hub_db.json"

ROLE_LABELS = {
    "1_creator": "👑 CREATOR",
    "2_owner": "💼 BOSS",
    "3_admin": "🛠️ ADMIN",
    "4_staff": "👁️ STAFF"
}

# =========================
# UTILS
# =========================
def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": st.session_state.users,
            "kho_hang": st.session_state.kho_hang
        }, f, ensure_ascii=False, indent=4)


def remove_vietnamese(text):
    if not text:
        return ""
    s = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    r = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    return text.translate(str.maketrans(s, r)).lower()


# =========================
# INIT DB
# =========================
if not os.path.exists(DB_FILE):
    default = {
        "users": {
            "admin": {
                "name": "Admin",
                "password": "123",
                "active": True,
                "role": "1_creator"
            }
        },
        "kho_hang": [
            {
                "ten": "CHOCOMONT BANH GAU",
                "ma_vach": "1111",
                "ngay_sx": "2026-01-01",
                "ngay_hh": "2026-06-30",
                "vi_tri": "Khu A - Ke 01"
            }
        ]
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(default, f, ensure_ascii=False, indent=4)


if "users" not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        st.session_state.users = data["users"]
        st.session_state.kho_hang = data["kho_hang"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None


# =========================
# LOGIN / REGISTER
# =========================
if not st.session_state.logged_in:

    st.title("🏭 SMART-HUB HỒNG PHÁT")

    col1, col2 = st.columns(2)

    # LOGIN
    with col1:
        st.subheader("Đăng nhập")

        u = st.text_input("User", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            if u in st.session_state.users:
                if st.session_state.users[u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else:
                    st.error("Sai mật khẩu")
            else:
                st.error("User không tồn tại")

    # REGISTER
    with col2:
        st.subheader("Đăng ký")

        ru = st.text_input("User mới", key="reg_user")
        rn = st.text_input("Tên", key="reg_name")
        rp = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register", key="reg_btn"):
            if ru in st.session_state.users:
                st.error("User đã tồn tại")
            else:
                st.session_state.users[ru] = {
                    "name": rn,
                    "password": rp,
                    "active": True,
                    "role": "4_staff"
                }
                save_data()
                st.success("Tạo tài khoản thành công")


# =========================
# DASHBOARD
# =========================
else:

    user = st.session_state.users[st.session_state.current_user]

    st.title(f"🏭 Smart-Hub - {user['name']}")

    if st.button("Logout", key="logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.markdown("---")

    # =========================
    # SEARCH (GOOGLE STYLE FIXED)
    # =========================
    st.subheader("🔍 Smart Search")

    search = st.text_input("Tìm hàng / mã vạch", key="search_main")

    search_clean = remove_vietnamese(search)

    result_high = []
    result_low = []

    for item in st.session_state.kho_hang:

        name = remove_vietnamese(item["ten"])
        code = item["ma_vach"].lower()

        if search_clean == "":
            result_high.append(item)
            continue

        prefix_name = name.startswith(search_clean)
        prefix_word = any(w.startswith(search_clean) for w in name.split())
        prefix_code = code.startswith(search_clean)
        contain = search_clean in name

        if prefix_name or prefix_word or prefix_code:
            result_high.insert(0, item)
        elif contain:
            result_low.append(item)

    final = result_high + result_low

    st.info(f"🔎 {len(final)} kết quả")

    for item in final[:30]:
        st.markdown(f"**📦 {item['ten']}**")
        st.write(f"📍 {item['vi_tri']}")
        st.write(f"🏷️ {item['ma_vach']}")
        st.write(f"📅 {item['ngay_hh']}")
        st.divider()

    # =========================
    # ADMIN PANEL
    # =========================
    if user["role"] in ["1_creator", "2_owner", "3_admin"]:

        st.markdown("## ⚙️ Admin Panel")

        col1, col2, col3 = st.columns(3)

        with col1:
            name = st.text_input("Tên hàng", key="add_name")
        with col2:
            code = st.text_input("Mã

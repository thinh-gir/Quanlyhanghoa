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

DB_FILE = "dulieu_kho_hongphat_smarthub.json"

ROLE_LABELS = {
    "1_creator": "👑 CREATOR",
    "2_owner": "💼 BOSS",
    "3_admin": "🛠️ ADMIN",
    "4_staff": "👁️ STAFF"
}

# =========================
# UTIL
# =========================
def luu_du_lieu():
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
# INIT DATA
# =========================
if not os.path.exists(DB_FILE):
    default_data = {
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
                "vi_tri": "Khu A"
            }
        ]
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(default_data, f, ensure_ascii=False, indent=4)

if "users" not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        st.session_state.users = data["users"]
        st.session_state.kho_hang = data["kho_hang"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# =========================
# LOGIN
# =========================
if not st.session_state.logged_in:

    st.title("🏭 SMART-HUB HỒNG PHÁT")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Đăng nhập")

        u = st.text_input("User")
        p = st.text_input("Pass", type="password")

        if st.button("Login"):
            if u in st.session_state.users:
                if st.session_state.users[u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else:
                    st.error("Sai mật khẩu")
            else:
                st.error("Không tồn tại user")

    with col2:
        st.subheader("Đăng ký")

        ru = st.text_input("User mới")
        rn = st.text_input("Tên")
        rp = st.text_input("Pass mới", type="password")

        if st.button("Register"):
            if ru in st.session_state.users:
                st.error("Đã tồn tại")
            else:
                st.session_state.users[ru] = {
                    "name": rn,
                    "password": rp,
                    "active": True,
                    "role": "4_staff"
                }
                luu_du_lieu()
                st.success("OK")

# =========================
# DASHBOARD
# =========================
else:

    user = st.session_state.users[st.session_state.current_user]

    st.title(f"🏭 Smart-Hub - {user['name']}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.markdown("---")

    # =========================
    # SMART SEARCH (GOOGLE STYLE)
    # =========================
    st.markdown("### 🔍 Smart Search")

    search = st.text_input("Tìm sản phẩm / mã vạch")

    search_clean = remove_vietnamese(search)

    result_top = []
    result_mid = []

    for item in st.session_state.kho_hang:

        name_clean = remove_vietnamese(item["ten"])
        code = item["ma_vach"].lower()

        if search_clean == "":
            result_top.append(item)
            continue

        match_start = any(
            w.startswith(search_clean)
            for w in name_clean.split()
        )

        match_code = code.startswith(search_clean)
        match_contain = search_clean in name_clean

        if match_start or match_code:
            result_top.append(item)
        elif match_contain:
            result_mid.append(item)

    results = result_top + result_mid

    st.info(f"Tìm thấy {len(results)} sản phẩm")

    for item in results[:20]:

        st.write(f"📦 {item['ten']}")
        st.write(f"📍 {item['vi_tri']}")
        st.write(f"🏷️ {item['ma_vach']}")
        st.write("---")

    # =========================
    # ADMIN PANEL
    # =========================
    if user["role"] in ["1_creator", "2_owner", "3_admin"]:

        st.markdown("### ⚙️ Admin Panel")

        name = st.text_input("Tên hàng")
        code = st.text_input("Mã vạch")
        loc = st.text_input("Vị trí")

        if st.button("Thêm hàng"):
            st.session_state.kho_hang.append({
                "ten": name.upper(),
                "ma_vach": code,
                "ngay_sx": str(date.today()),
                "ngay_hh": str(date.today()),
                "vi_tri": loc
            })
            luu_du_lieu()
            st.success("Đã thêm")
            st.rerun()

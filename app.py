import streamlit as st
import json
import os
from datetime import date

# =========================
# SETUP
# =========================
st.set_page_config(page_title="Smart-Hub", layout="wide", page_icon="🏭")

DB_FILE = "smart_hub_safe.json"


# =========================
# SAFE UTIL
# =========================
def remove_vietnamese(text: str) -> str:
    if not text:
        return ""
    s = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    r = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    return text.translate(str.maketrans(s, r)).lower()


def safe_item(item: dict) -> dict:
    """Chống thiếu field -> không crash"""
    return {
        "ten": item.get("ten", "UNKNOWN"),
        "ma_vach": item.get("ma_vach", "0000"),
        "ngay_sx": item.get("ngay_sx", ""),
        "ngay_hh": item.get("ngay_hh", ""),
        "vi_tri": item.get("vi_tri", "N/A")
    }


def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": st.session_state.users,
            "kho_hang": st.session_state.kho_hang
        }, f, ensure_ascii=False, indent=4)


# =========================
# INIT DATA
# =========================
if not os.path.exists(DB_FILE):
    init = {
        "users": {
            "admin": {
                "name": "Admin",
                "password": "123",
                "role": "1_creator",
                "active": True
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
        json.dump(init, f, ensure_ascii=False, indent=4)


if "users" not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        st.session_state.users = data["users"]
        st.session_state.kho_hang = data["kho_hang"]

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = None


# =========================
# LOGIN
# =========================
if not st.session_state.login:

    st.title("🏭 SMART-HUB")

    col1, col2 = st.columns(2)

    with col1:
        u = st.text_input("User", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            if u in st.session_state.users:
                if st.session_state.users[u]["password"] == p:
                    st.session_state.login = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Sai mật khẩu")
            else:
                st.error("Không tồn tại user")

    with col2:
        nu = st.text_input("User mới", key="reg_user")
        np = st.text_input("Tên", key="reg_name")
        pw = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register", key="reg_btn"):
            if nu in st.session_state.users:
                st.error("User đã tồn tại")
            else:
                st.session_state.users[nu] = {
                    "name": np,
                    "password": pw,
                    "role": "4_staff",
                    "active": True
                }
                save_db()
                st.success("OK")


# =========================
# DASHBOARD
# =========================
else:

    user = st.session_state.users[st.session_state.user]

    st.title(f"🏭 Smart-Hub - {user['name']}")

    if st.button("Logout", key="logout"):
        st.session_state.login = False
        st.session_state.user = None
        st.rerun()

    st.markdown("---")

    # =========================
    # SEARCH SAFE
    # =========================
    st.subheader("🔍 Search")

    q = st.text_input("Tìm hàng", key="search")

    q_clean = remove_vietnamese(q)

    high = []
    low = []

    for raw in st.session_state.kho_hang:
        item = safe_item(raw)

        name = remove_vietnamese(item["ten"])
        code = str(item["ma_vach"]).lower()

        if q_clean == "":
            high.append(item)
            continue

        if name.startswith(q_clean) or code.startswith(q_clean):
            high.insert(0, item)
        elif q_clean in name:
            low.append(item)

    results = high + low

    st.info(f"Tìm thấy {len(results)} sản phẩm")

    for item in results[:30]:
        st.markdown(f"**📦 {item['ten']}**")
        st.write(f"📍 {item['vi_tri']}")
        st.write(f"🏷️ {item['ma_vach']}")
        st.write(f"📅 {item['ngay_hh']}")
        st.divider()

    # =========================
    # ADD SAFE
    # =========================
    st.subheader("➕ Thêm hàng")

    c1, c2, c3 = st.columns(3)

    with c1:
        name = st.text_input("Tên", key="add_name")
    with c2:
        code = st.text_input("Mã", key="add_code")
    with c3:
        loc = st.text_input("Vị trí", key="add_loc")

    if st.button("Add", key="add_btn"):
        if name and code and loc:
            st.session_state.kho_hang.append({
                "ten": name.upper(),
                "ma_vach": code,
                "ngay_sx": str(date.today()),
                "ngay_hh": str(date.today()),
                "vi_tri": loc
            })
            save_db()
            st.success("Đã thêm")
            st.rerun()
        else:
            st.error("Thiếu dữ liệu")

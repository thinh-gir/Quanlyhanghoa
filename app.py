import streamlit as st
import json
import os

# Cấu hình trang web tối giản
st.set_page_config(page_title="He thong Smart-Hub Hong Phat", layout="wide")

DB_FILE = "dulieu_kho_hongphat_smarthub.json"

def loai_bo_dau_tieng_viet(chuoi_chu):
    co_dau = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    khong_dau = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    bang_chuyen = str.maketrans(co_dau, khong_dau)
    return chuoi_chu.translate(bang_chuyen).lower()

# Khởi tạo dữ liệu gốc an toàn
if not os.path.exists(DB_FILE):
    du_lieu_goc = {
        "users": {"Zeroizerd": {"name": "Dong Sang Lap Zeroizerd", "password": "13723@", "active": True, "role": "1_creator"}},
        "kho_hang": [
            {"ten": "CHOCOMONT BANH GAU", "ma_vach": "1111", "vi_tri": "Khu A - Ke 01 - Tang 2", "ngay_hh": "2026-06-30"},
            {"ten": "CHAO CHONG DINH", "ma_vach": "2222", "vi_tri": "Khu A - Ke 02 - Tang 1", "ngay_hh": "2028-01-01"},
            {"ten": "BANH MI SUA", "ma_vach": "3333", "vi_tri": "Khu B - Ke 01 - Tang 1", "ngay_hh": "2026-08-15"}
        ]
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(du_lieu_goc, f, ensure_ascii=False, indent=4)

if 'users' not in st.session_state or 'kho_hang' not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        tep_du_lieu = json.load(f)
        st.session_state.users = tep_du_lieu.get("users", {})
        st.session_state.kho_hang = tep_du_lieu.get("kho_hang", [])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# GIAO DIỆN ĐĂNG NHẬP
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0088cc;'>HE THONG BAO MAT HONG PHAT</h2>", unsafe_allow_html=True)
    u_in = st.text_input("Ten tai khoan:", key="u_in").strip()
    p_in = st.text_input("Mat khau bao mat:", type="password", key="p_in")
    if st.button("DANG NHAP SYSTEM", type="primary", use_container_width=True):
        if u_in in st.session_state.users and st.session_state.users[u_in]["password"] == p_in:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Sai tai khoan hoac mat khau!")

# GIAO DIỆN CHÍNH (CHỈ GIỮ LẠI THANH TÌM KIẾM ĐỘNG ABC)
else:
    st.markdown("<h2 style='color: #0088cc; margin:0;'>SMART-HUB DIEU HANH - HONG PHAT</h2>", unsafe_allow_html=True)
    if st.button("DANG XUAT", type="secondary"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.markdown("---")
    st.markdown("### TIM KIEM THONG MINH (Go chu cai goi y rut xuong ngay lap tuc)")
    
    kho_sap_xep_abc = sorted(st.session_state.kho_hang, key=lambda x: x["ten"])
    options_tim_kiem = ["-- Go chu cai dau hoac chon san pham tai day --"]
    for sp in kho_sap_xep_abc:
        options_tim_kiem.append(f"Spham: {sp['ten'].upper()} [Ma vach: {sp['ma_vach']}]")
        
    chon_lua_goi_y = st.selectbox(
        "Nhaps chuot vao day va GO CHU CAI DAU de tim nhanh:",
        options=options_tim_kiem,
        index=0,
        key="hongphat_instant_search_selectbox"
    )
    
    if chon_lua_goi_y != "-- Go chu cai dau hoac chon san pham tai day --":
        mv_trich_xuat = chon_lua_goi_y.split("[Ma vach: ")[-1].replace("]", "").strip()
        for sp in st.session_state.kho_hang:
            if sp["ma_vach"] == mv_trich_xuat:
                st.markdown("---")
                st.info(f"Vi tri ke kho: {sp['vi_tri']}")
                st.write(f"Ten vat tu: {sp['ten'].upper()} | Ma vach: {sp['ma_vach']} | Han dung: {sp['ngay_hh']}")
                break

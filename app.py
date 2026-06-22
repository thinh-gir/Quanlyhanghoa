import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CAU HINH VA KHOI TAO HE THONG SMART-HUB HONG PHAT
# ==========================================
st.set_page_config(page_title="He thong Quan ly Smart-Hub Hong Phat", layout="wide")

DB_FILE = "dulieu_kho_hongphat_smarthub.json"

ROLE_LABELS = {
    "1_creator": "CREATOR (DONG SANG LAP)",
    "2_owner": "BOSS (CHU CHO)",
    "3_admin": "ADMIN (QUAN LY)",
    "4_staff": "STAFF (NHAN VIEN)"
}

def luu_du_lieu_he_thong():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": st.session_state.users, "kho_hang": st.session_state.kho_hang}, f, ensure_ascii=False, indent=4)

def loai_bo_dau_tieng_viet(chuoi_chu):
    co_dau = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    khong_dau = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    bang_chuyen = str.maketrans(co_dau, khong_dau)
    return chuoi_chu.translate(bang_chuyen).lower()

# Khai bao cac ham quan tri doc lap de chong loi le loi
def xu_ly_nhap_kho():
    st.markdown("### MANAGEMENT ZONE (Khu vur quan tri danh cho Ban Quan Ly)")
    st.markdown("#### Nhap them vat tu hang hoa moi")
    col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
    with col_a1:
        add_name = st.text_input("Ten hang hoa:", key="w_add_name").strip()
    with col_a2:
        add_barcode = st.text_input("Ma vach dinh danh:", key="w_add_bar").strip()
    with col_a3:
        add_nsx = st.date_input("Ngay san xuat:", value=date.today(), key="w_add_nsx").strftime("%Y-%m-%d")
    with col_a4:
        add_nhh = st.date_input("Han su dung:", value=date.today(), key="w_add_nhh").strftime("%Y-%m-%d")
    with col_a5:
        add_loc = st.text_input("Vi tri ke kho chi tiet:", key="w_add_loc").strip()
    
    if st.button("XAC NHAN GHI SO NHAP KHO", type="primary", use_container_width=True):
        if not add_name or not add_barcode or not add_loc:
            st.error("Vui long nhap day du thong tin!")
        elif any(x["ma_vach"] == add_barcode for x in st.session_state.kho_hang):
            st.error("Ma vach nay da ton tai san!")
        else:
            st.session_state.kho_hang.append({"ten": add_name.upper(), "ma_vach": add_barcode, "ngay_sx": add_nsx, "ngay_hh": add_nhh, "vi_tri": add_loc})
            luu_du_lieu_he_thong()
            st.success(f"Da cap nhat thanh con san pham {add_name.upper()}!")
            st.rerun()

def xu_ly_sua_xoa_kho():
    if not st.session_state.kho_hang:
        st.info("Hien kho Hong Phat chua luu tru hang hoa nao.")
        return
    st.markdown("#### Sua doi thong tin chi tiet / Xoa bo vat tu")
    ds_ten_kho = [f"{x['ten']} [Ma vach: {x['ma_vach']}]" for x in st.session_state.kho_hang]
    sp_chon_de_sua = st.selectbox("Chon san pham ban muon sua doi hoac xoa bo:", options=ds_ten_kho, key="sb_edit_product_flat")
    idx_sua = ds_ten_kho.index(sp_chon_de_sua)
    item_sua = st.session_state.kho_hang[idx_sua]
    
    e_name = st.text_input("Dieu chinh ten hang hoa moi:", value=item_sua["ten"], key="txt_edit_flat_name").strip()
    e_bar = st.text_input("Dieu chinh ma vach moi:", value=item_sua["ma_vach"], key="txt_edit_flat_bar").strip()
    e_loc = st.text_input("Dieu chinh vi tri ke hang moi:", value=item_sua["vi_tri"], key="txt_edit_flat_loc").strip()
    
    if st.button("XAC NHAN LUU THAY DOI VAT TU", type="primary", use_container_width=True):
        if not e_name or not e_bar or not e_loc:
            st.error("Khong duoc de trong thong tin!")
        else:
            st.session_state.kho_hang[idx_sua] = {"ten": e_name.upper(), "ma_vach": e_bar, "ngay_sx": item_sua["ngay_sx"], "ngay_hh": item_sua["ngay_hh"], "vi_tri": e_loc}
            luu_du_lieu_he_thong()
            st.success("Da ghi nhan luu thong tin!")
            st.rerun()
            
    if st.button("XOA VINH VIEN SAN PHAM NAY", use_container_width=True, key="btn_delete_flat_prod"):
        st.session_state.kho_hang.pop(idx_sua)
        luu_du_lieu_he_thong()
        st.success("Da go khoi kho!")
        st.rerun()

def xu_ly_duyet_nhan_su(role_now):
    tai_khoan_sua_duoc = [tk for tk, info in st.session_state.users.items() if tk != st.session_state.current_user and info["role"] != "1_creator"]
    if not tai_khoan_sua_duoc:
        st.info("He thong chua ghi nhan tai khoan cap duoi nao khac de phe duyet.")
        return
        
    st.markdown("#### Phe duyet kich hoat tai khoan & Cap chuc vu cho nhan su")
    tk_selected = st.selectbox("Chon tai khoan nhan su cap duoi can cau hinh:", options=tai_khoan_sua_duoc, key="sb_edit_user_flat")
    info_u = st.session_state.users[tk_selected]
    role_u = info_u["role"]
    
    hop_le = False
    if role_now == "1_creator": hop_le = True
    elif role_now == "2_owner" and role_u in ["3_admin", "4_staff"]: hop_le = True
    elif role_now == "3_admin" and role_u == "4_staff": hop_le = True
    
    if hop_le:
        new_act = st.checkbox(f"Kich hoat / Mo khoa quyen truy cap cho [{tk_selected}]", value=info_u["active"], key="chk_flat_user_act")
        giai_cap = {"STAFF (NHAN VIEN)": "4_staff"}
        if role_now in ["1_creator", "2_owner"]: giai_cap["ADMIN (QUAN LY)"] = "3_admin"
        if role_now == "1_creator": giai_cap["BOSS CHU CHO"] = "2_owner"
        lbl_now = [k for k, v in giai_cap.items() if v == role_u]
        idx_def = list(giai_cap.keys()).index(lbl_now) if lbl_now else 0
        new_r_label = st.selectbox(f"Chi dinh cap bac chuc vu moi cho [{tk_selected}]:", options=list(giai_cap.keys()), index=idx_def, key="sb_flat_user_role")
        
        if st.button(f"PHE DUYET CAU HINH TAI KHOAN [{tk_selected}]", type="primary", use_container_width=True):
            st.session_state.users[tk_selected]["active"] = new_act
            st.session_state.users[tk_selected]["role"] = giai_cap[new_r_label]
            luu_du_lieu_he_thong()
            st.success("Da phe duyet phan cap tai khoan thanh con!")
            st.rerun()

# Khoi tao du lieu goc tai day
if not os.path.exists(DB_FILE):
    du_lieu_goc = {
        "users": {"Zeroizerd": {"name": "Dong Sang Lap Zeroizerd", "password": "13723@", "active": True, "role": "1_creator"}},
        "kho_hang": [
            {"ten": "CHOCOMONT BANH GAU", "ma_vach": "1111", "ngay_sx": "2026-01-01", "ngay_hh": "2026-06-30", "vi_tri": "Khu A - Ke 01 - Tang 2"},
            {"ten": "CHAO CHONG DINH", "ma_vach": "2222", "ngay_sx": "2026-01-01", "ngay_hh": "2028-01-01", "vi_tri": "Khu A - Ke 02 - Tang 1"}
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
    st.session_state.current_user = None

# ==========================================
# 2. GIAO DIỆN ĐĂNG NHẬP
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0088cc;'>HE THONG BAO MAT SMART-HUB HONG PHAT</h2>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.subheader("DANG NHAP")
        u_in = st.text_input("Ten tai khoan:", key="u_in").strip()
        p_in = st.text_input("Mat khau bao mat:", type="password", key="p_in")
        if st.button("DANG NHAP SYSTEM", type="primary", use_container_width=True):
            if u_in in st.session_state.users:
                u_info = st.session_state.users[u_in]
                if u_info["password"] == p_in:
                    if u_info["active"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_in
                        st.rerun()
                    else: st.error("Tai khoan chua duoc kich hoat quyen!")
                else: st.error("Mat khau khong chi'nh xac!")
            else: st.error("Tai khoan khong ton tai!")
    with col_l2:
        st.subheader("DANG KY TAI KHOAN MOI")
        r_user = st.text_input("Ten dang nhap moi (viet lien):", key="r_user").strip()
        r_name = st.text_input("Ho va ten that nhan su:", key="r_name").strip()
        r_pass = st.text_input("Tao mat khau truy cap:", type="password", key="r_pass")
        if st.button("GUI YEU CAU DANG KY", use_container_width=True):
            if not r_user or not r_name or not r_pass: st.error("Vui long dien day du thong tin!")
            elif r_user in st.session_state.users: st.error("Ten tai khoan nay la da co nguoi su dung!")
            else:
                st.session_state.users[r_user] = {"name": r_name, "password": r_pass, "active": False, "role": "4_staff"}
                luu_du_lieu_he_thong()
                st.success("Dang ky thanh cong! Hay cho cap tren phe duyet.")

# ==========================================
# 3. DASHBOARD DIEU HANH CHINH THUC
# ==========================================
else:
    u_now = st.session_state.users[st.session_state.current_user]
    role_now = u_now["role"]
    col_hd1, col_hd2 = st.columns(2)
    with col_hd1:
        st.markdown("<h2 style='color: #0088cc; margin:0;'>SMART-HUB DIEU HANH - HONG PHAT</h2>", unsafe_allow_html=True)
        st.write(f"Nguoi truc: {u_now['name']} | Chuc vu: {ROLE_LABELS[role_now]}")
    with col_hd2:
        if st.button("DANG XUAT", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    st.markdown("---")
    
    # CANH BAO BAO QUAN SAN PHAM HET HAN
    co_canh_bao = False
    for item in st.session_state.kho_hang:
        try:

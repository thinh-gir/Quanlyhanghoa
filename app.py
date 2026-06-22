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

# ==========================================
# KHAI BAO CAC HAM CHUC NANG (FLAT-FUNCTIONS CHONG LOI LE LOI)
# ==========================================
def hien_thi_canh_bao_het_han():
    st.header("CANH BAO BAO QUAN SAN PHAM (DUOI 7 NGAY)")
    thoi_gian_thuc = datetime.now()
    co_canh_bao = False
    
    for item in st.session_state.kho_hang:
        try:
            ngay_hh_dt = datetime.strptime(item.get("ngay_hh", "2099-12-31"), "%Y-%m-%d")
            days_left = (ngay_hh_dt - thoi_gian_thuc).days + 1
            if days_left <= 7:
                co_canh_bao = True
                if days_left < 0:
                    st.error(f"CANH BAO - DA QUA HAN {abs(days_left)} NGAY: {item['ten'].upper()} | Ke: {item['vi_tri']}")
                else:
                    st.warning(f"CANH BAO - SAP HET HAN (Con {days_left} ngay): {item['ten'].upper()} | Ke: {item['vi_tri']}")
        except:
            pass
            
    if not co_canh_bao:
        st.success("He thong an toan. Tat ca vat lieu deu co han su dung an toan.")

def xu_ly_tim_kiem_thong_minh():
    st.markdown("### TIM KIEM THONG MINH (Go chu cai goi y rut xuong ngay lap tuc)")
    with st.popover("BAM VAO DAY DE GO CHU CAI / XEM GOI Y ABC", use_container_width=True):
        chu_cai_nhap = st.text_input("Go chu cai dau, ten hang hoac quet ma vach:", value="", key="inst_search").strip()
        chu_cai_clean = loai_bo_dau_tieng_viet(chu_cai_nhap)
        start_with = []
        contain_with = []
        for sp in st.session_state.kho_hang:
            t_clean = loai_bo_dau_tieng_viet(sp["ten"])
            m_clean = sp["ma_vach"].lower()
            if chu_cai_clean in t_clean or chu_cai_clean in m_clean:
                if t_clean.startswith(chu_cai_clean) or m_clean.startswith(chu_cai_clean):
                    start_with.append(sp)
                else:
                    contain_with.append(sp)
        start_with.sort(key=lambda x: x["ten"])
        contain_with.sort(key=lambda x: x["ten"])
        ket_qua_goi_y = start_with + contain_with
        if chu_cai_nhap:
            st.markdown(f"Goi y khop cho tu khoa '{chu_cai_nhap}':")
        else:
            st.markdown("Toan bo danh sach kho hang (Xep theo thu tu ABC):")
        for item_goi_y in ket_qua_goi_y:
            st.markdown(f"**Spham: {item_goi_y['ten'].upper()}**")
            st.markdown(f"Vi tri ke: {item_goi_y['vi_tri']} | Ma vach: {item_goi_y['ma_vach']} | HSD: {item_goi_y['ngay_hh']}")
            st.markdown("---")

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

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU GỐC HỆ THỐNG
# ==========================================
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
# 2. GIAO DIỆN ĐĂNG NHẬP TRỰC QUAN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0088cc;'>HE THONG BAO MAT SMART-HUB HONG PHAT</h2>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns(2)

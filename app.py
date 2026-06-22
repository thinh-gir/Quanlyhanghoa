import streamlit as st
import json
import os
from datetime import datetime, date

# 1. CẤU HÌNH & KHỞI TẠO HỆ THỐNG SMART-HUB HỒNG PHÁT
st.set_page_config(page_title="Hệ thống Quản lý Smart-Hub Hồng Phát", layout="wide", page_icon="🏭")

DB_FILE = "dulieu_kho_hongphat_smarthub.json"

ROLE_LABELS = {
    "1_creator": "👑 CREATOR (ĐỒNG SÁNG LẬP)",
    "2_owner": "💼 BOSS (CHỦ CHỢ)",
    "3_admin": "🛠️ ADMIN (QUẢN LÝ)",
    "4_staff": "👁️ STAFF (NHÂN VIÊN)"
}

def luu_du_lieu_he_thong():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": st.session_state.users, "kho_hang": st.session_state.kho_hang}, f, ensure_ascii=False, indent=4)

if not os.path.exists(DB_FILE):
    du_lieu_goc = {
        "users": {"Zeroizerd": {"name": "Đồng Sáng Lập Zeroizerd", "password": "13723@", "active": True, "role": "1_creator"}},
        "kho_hang": [
            {"ten": "CHOCOMONT BÁNH GẤU", "ma_vach": "1111", "ngay_sx": "2026-01-01", "ngay_hh": "2026-06-30", "vi_tri": "Khu A - Kệ 01 - Tầng 2"},
            {"ten": "CHẢO CHỐNG DÍNH", "ma_vach": "2222", "ngay_sx": "2026-01-01", "ngay_hh": "2028-01-01", "vi_tri": "Khu A - Kệ 02 - Tầng 1"}
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

# 2. GIAO DIỆN ĐĂNG NHẬP
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0088cc;'>🏭 HỆ THỐNG BẢO MẬT SMART-HUB HỒNG PHÁT</h2>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.subheader("🔑 ĐĂNG NHẬP HỆ THỐNG")
        u_in = st.text_input("Tên tài khoản:", key="u_in").strip()
        p_in = st.text_input("Mật khẩu bảo mật:", type="password", key="p_in")
        if st.button("ĐĂNG NHẬP", type="primary", use_container_width=True):
            if u_in in st.session_state.users:
                u_info = st.session_state.users[u_in]
                if u_info["password"] == p_in:
                    if u_info["active"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_in
                        st.rerun()
                    else: st.error("Tài khoản chưa được kích hoạt quyền!")
                else: st.error("Mật khẩu không chính xác!")
            else: st.error("Tài khoản không tồn tại!")
    with col_l2:
        st.subheader("📝 ĐĂNG KÝ TÀI KHOẢN MỚI")
        r_user = st.text_input("Tên đăng nhập mới (viết liền không dấu):", key="r_user").strip()
        r_name = st.text_input("Họ và tên thật của nhân sự:", key="r_name").strip()
        r_pass = st.text_input("Tạo mật khẩu truy cập:", type="password", key="r_pass")
        if st.button("GỬI YÊU CẦU ĐĂNG KÝ", use_container_width=True):
            if not r_user or not r_name or not r_pass: st.error("Vui lòng điền đầy đủ thông tin!")
            elif r_user in st.session_state.users: st.error("Tên tài khoản này đã có người sử dụng!")
            else:
                st.session_state.users[r_user] = {"name": r_name, "password": r_pass, "active": False, "role": "4_staff"}
                luu_du_lieu_he_thong()
                st.success("Đăng ký thành công! Hãy chờ cấp trên phê duyệt.")

# 3. DASHBOARD ĐIỀU HÀNH CHÍNH THỨC
else:
    u_now = st.session_state.users[st.session_state.current_user]
    role_now = u_now["role"]
    col_hd1, col_hd2 = st.columns(2)
    with col_hd1:
        st.markdown(f"<h1 style='color: #0088cc; margin:0;'>🏭 SMART-HUB ĐIỀU HÀNH — HỒNG PHÁT</h1>", unsafe_allow_html=True)
        st.write(f"👤 Trực ban: **{u_now['name']}** | Chức vụ hệ thống: `{ROLE_LABELS[role_now]}`")
    with col_hd2:
        if st.button("🚪 ĐĂNG XUẤT HỆ THỐNG", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    st.markdown("---")
    
    # CẢNH BÁO BẢO QUẢN SẢN PHẨM HẾT HẠN
    co_canh_bao = False
    for item in st.session_state.kho_hang:
        try:
            days_left = (datetime.strptime(item.get("ngay_hh", "2099-12-31"), "%Y-%m-%d") - datetime.now()).days + 1
            if days_left <= 7:
                co_canh_bao = True
                if days_left < 0: st.error(f"🚨 **💥 ĐÃ QUÁ HẠN {abs(days_left)} NGÀY**: {item['ten'].upper()} | Mã vạch: {item['ma_vach']} | Vị trí: {item['vi_tri']}")
                else: st.warning(f"⚠️ **⏳ SẮP HẾT HẠN (Còn {days_left} ngày)**: {item['ten'].upper()} | Mã vạch: {item['ma_vach']} | Vị trí: {item['vi_tri']}")
        except: pass
    if not co_canh_bao: st.success("✅ Toàn bộ vật liệu lưu kho đều nằm trong hạn sử dụng an toàn.")
    st.markdown("---")
    
    # CHỨC NĂNG SMART-SEARCH GÕ CHỮ CÁI RA GỢI Ý TỨ THÌ (NO ENTER)
    st.markdown("### 🔍 SMART SUGGESTIONS SEARCH (Gõ chữ cái gợi ý rớt xuống ngay lập tức)")
    kho_sap_xep_abc = sorted(st.session_state.kho_hang, key=lambda x: x["ten"])
    options_tim_kiem = ["-- Gõ chữ cái đầu hoặc chọn sản phẩm tại đây --"]
    for sp in kho_sap_xep_abc: options_tim_kiem.append(f"🛒 {sp['ten'].upper()} [Mã vạch: {sp['ma_vach']}]")
    chon_lua_goi_y = st.selectbox("Nhấp chuột vào đây và GÕ CHỮ CÁI ĐẦU để tìm nhanh:", options=options_tim_kiem, index=0, key="hongphat_instant_search_selectbox")
    if chon_lua_goi_y != "-- Gõ chữ cái đầu hoặc chọn sản phẩm tại đây --":
        mv_trich_xuat = chon_lua_goi_y.split("[Mã vạch: ")[-1].replace("]", "").strip()
        for sp in st.session_state.kho_hang:
            if sp["ma_vach"] == mv_trich_xuat:
                st.markdown("---")
                st.info(f"📍 **ĐỊNH VỊ VỊ TRÍ KỆ HÀNG HỒNG PHÁT:** {sp['vi_tri']}\n\n📦 **Vật tư:** {sp['ten'].upper()} | 🆔 **Mã vạch:** `{sp['ma_vach']}` | 📅 **Hạn sử dụng:** {sp['ngay_hh']}")
                break
    st.markdown("---")

    # KHU VỰC THAO TÁC CỦA QUẢN LÝ (THÊM / SỬA / XÓA)
    if role_now in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("### ⚙️ MANAGEMENT ZONE (Khu vực quản trị dành cho Ban Quản Lý Chợ)")
        st.markdown("#### ➕ Nhập thêm vật tư hàng hóa mới")
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
        with col_a1: add_name = st.text_input("Tên hàng hóa:", key="w_add_name").strip()
        with col_a2: add_barcode = st.text_input("Mã vạch định danh:", key="w_add_bar").strip()
        with col_a3: add_nsx = st.date_input("Ngày sản xuất:", value=date.today(), key="w_add_nsx").strftime("%Y-%m-%d")
        with col_a4: add_nhh = st.date_input("Hạn sử dụng:", value=date.today(), key="w_add_nhh").strftime("%Y-%m-%d")
        with col_a5: add_loc = st.text_input("Vị trí kệ kho chi tiết:", key="w_add_loc").strip()
        if st.button("➕ XÁC NHẬN GHI SỔ NHẬP KHO", type="primary", use_container_width=True):
            if not add_name or not add_barcode or not add_loc: st.error("Vui lòng nhập đầy đủ thông tin!")
            elif any(x["ma_vach"] == add_barcode for x in st.session_state.kho_hang): st.error("Mã vạch này đã tồn tại sẵn!")
            else:
                st.session_state.kho_hang.append({"ten": add_name.upper(), "ma_vach": add_barcode, "ngay_sx": add_nsx, "ngay_hh": add_nhh, "vi_tri": add_loc})
                luu_du_lieu_he_thong()
                st.success(f"Đã cập nhật thành công sản phẩm {add_name.upper()}!")
                st.rerun()
        st.markdown("---")
        
        st.markdown("#### ✏️ Sửa đổi thông tin chi tiết / Xóa bỏ vật tư")
        if st.session_state.kho_hang:
            for idx, item in enumerate(st.session_state.kho_hang):
                col_e1, col_e2, col_e3, col_btn1, col_btn2 = st.columns(5)
                with col_e1: e_name = st.text_input(f"Tên hàng #{idx+1}", value=item["ten"], key=f"we_name_{idx}").strip()
                with col_e2: e_bar = st.text_input(f"Mã vạch #{idx+1}", value=item["ma_vach"], key=f"we_bar_{idx}").strip()
                with col_e3: e_loc = st.text_input(f"Vị trí kệ #{idx+1}", value=item["vi_tri"], key=f"we_loc_{idx}").strip()
                with col_btn1:
                    if st.button("LƯU", key=f"w_save_btn_{idx}", use_container_width=True):
                        if not e_name or not e_bar or not e_loc: st.error("Không được bỏ trống dữ liệu!")
                        else:
                            st.session_state.kho_hang[idx] = {"ten": e_name.upper(), "ma_vach": e_bar, "ngay_sx": item["ngay_sx"], "ngay_hh": item["ngay_hh"], "vi_tri": e_loc}
                            luu_du_lieu_he_thong()
                            st.success("Đã ghi nhận lưu!"); st.rerun()
                with col_btn2:
                    if st.button("XÓA", key=f"w_del_btn_{idx}", use_container_width=True):
                        st.session_state.kho_hang.pop(idx); luu_du_lieu_he_thong(); st.success("Đã gỡ khỏi kho!"); st.rerun()
        else: st.info("Hiện kho Hồng Phát chưa lưu trữ hàng hóa nào.")
        st.markdown("---")
        
        st.markdown("#### 👥 Phê duyệt kích hoạt tài khoản & Cấp chức vụ cho nhân sự")
        for tk, info in list(st.session_state.users.items()):
            if tk != st.session_state.current_user and info["role"] != "1_creator":
                hop_le = False
                if role_now == "1_creator": hop_le = True
                elif role_now == "2_owner" and info["role"] in ["3_admin", "4_staff"]: hop_le = True
                elif role_now == "3_admin" and info["role"] == "4_staff": hop_le = True
                if hop_le:
                    col_u1, col_u2, col_u3, col_u4 = st.columns(4)

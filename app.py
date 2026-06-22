import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH & KHỞI TẠO HỆ THỐNG SMART-HUB
# ==========================================
st.set_page_config(page_title="Walmart Smart Inventory Hub - Hồng Phát", layout="wide", page_icon="🔵")

DB_FILE = "dulieu_kho_walmart_v1.json"

ROLE_LABELS = {
    "1_creator": "👑 CREATOR (ĐỒNG SÁNG LẬP)",
    "2_owner": "💼 BOSS (CHỦ CHỢ)",
    "3_admin": "🛠️ ADMIN (QUẢN LÝ)",
    "4_staff": "👁️ STAFF (NHÂN VIÊN)"
}

def luu_du_lieu_he_thong():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": st.session_state.users,
            "kho_hang": st.session_state.kho_hang
        }, f, ensure_ascii=False, indent=4)

def loai_bo_dau_tieng_viet(chuoi_chu):
    co_dau = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    khong_dau = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    bang_chuyen = str.maketrans(co_dau, khong_dau)
    return chuoi_chu.translate(bang_chuyen).lower()

if not os.path.exists(DB_FILE):
    du_lieu_goc = {
        "users": {
            "Zeroizerd": {"name": "Đồng Sáng Lập Zeroizerd", "password": "13723@", "active": True, "role": "1_creator"}
        },
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

# ==========================================
# 2. GIAO DIỆN ĐĂNG NHẬP THUẦN CHỨC NĂNG
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0071CE;'>🔵 WALMART SMART INVENTORY LOGIN</h2>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.subheader("🔑 ĐĂNG NHẬP")
        u_in = st.text_input("Username:", key="u_in").strip()
        p_in = st.text_input("Password:", type="password", key="p_in")
        if st.button("SIGN IN", type="primary", use_container_width=True):
            if u_in in st.session_state.users:
                u_info = st.session_state.users[u_in]
                if u_info["password"] == p_in:
                    if u_info["active"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_in
                        st.rerun()
                    else: st.error("Tài khoản chưa được kích hoạt!")
                else: st.error("Sai mật khẩu!")
            else: st.error("Tài khoản không tồn tại!")
            
    with col_l2:
        st.subheader("📝 ĐĂNG KÝ MỚI")
        r_user = st.text_input("Username mới (viết liền):", key="r_user").strip()
        r_name = st.text_input("Họ và tên thật:", key="r_name").strip()
        r_pass = st.text_input("Mật khẩu truy cập:", type="password", key="r_pass")
        if st.button("CREATE ACCOUNT", use_container_width=True):
            if not r_user or not r_name or not r_pass:
                st.error("Vui lòng điền đủ thông tin!")
            elif r_user in st.session_state.users:
                st.error("Tên tài khoản này đã tồn tại!")
            else:
                st.session_state.users[r_user] = {"name": r_name, "password": r_pass, "active": False, "role": "4_staff"}
                luu_du_lieu_he_thong()
                st.success("Đăng ký thành công! Hãy chờ cấp trên duyệt.")

# ==========================================
# 3. DASHBOARD QUẢN LÝ KHO WALMART CHÍNH THỨC
# ==========================================
else:
    u_now = st.session_state.users[st.session_state.current_user]
    role_now = u_now["role"]
    
    # Header phong cách Walmart
    col_hd1, col_hd2 = st.columns([4, 1])
    with col_hd1:
        st.markdown(f"<h1 style='color: #0071CE; margin:0;'>🔵 WALMART INVENTORY HUB — HỒNG PHÁT</h1>", unsafe_allow_html=True)
        st.write(f"👤 Người trực: **{u_now['name']}** | Chức vụ: `{ROLE_LABELS[role_now]}`")
    with col_hd2:
        if st.button("🚪 LOG OUT", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
            
    st.markdown("---")
    
    # BANNER 1: CẢNH BÁO SẢN PHẨM HẾT HẠN (DƯỚI 7 NGÀY)
    co_canh_bao = False
    for item in st.session_state.kho_hang:
        try:
            days_left = (datetime.strptime(item.get("ngay_hh", "2099-12-31"), "%Y-%m-%d") - datetime.now()).days + 1
            if days_left <= 7:
                co_canh_bao = True
                if days_left < 0:
                    st.error(f"🚨 **💥 ĐÃ QUÁ HẠN {abs(days_left)} NGÀY**: {item['ten'].upper()} | Mã vạch: {item['ma_vach']} | Vị trí: {item['vi_tri']}")
                else:
                    st.warning(f"⚠️ **⏳ SẮP HẾT HẠN (Còn {days_left} ngày)**: {item['ten'].upper()} | Mã vạch: {item['ma_vach']} | Vị trí: {item['vi_tri']}")
        except: pass
    if not co_canh_bao:
        st.success("✅ Toàn bộ vật liệu trong kho đều có hạn sử dụng an toàn.")

    st.markdown("---")
    
    # BANNER 2: THANH TÌM KIẾM SMART SEARCH TRÊN CÙNG
    st.markdown("### 🔍 QUICK SEARCH (Tìm kiếm thông minh)")
    q_search = st.text_input("Gõ chữ cái, từ khóa, quét mã vạch để định vị nhanh sản phẩm:", key="walmart_search_bar").strip()
    
    items_filtered = []
    q_clean = loai_bo_dau_tieng_viet(q_search)
    for sp in st.session_state.kho_hang:
        if q_clean in loai_bo_dau_tieng_viet(sp["ten"]) or q_clean in sp["ma_vach"].lower():
            items_filtered.append(sp)

    # Hiển thị kết quả tìm kiếm dạng bảng Thẻ trực quan
    if q_search:
        st.markdown(f"💡 *Kết quả lọc nhanh cho từ khóa '{q_search}':*")
        for res in items_filtered:
            st.info(f"📍 **VỊ TRÍ KỆ HÀNG:** {res['vi_tri']} \n\n 📦 **Tên vật tư:** {res['ten'].upper()} | 🆔 **Mã vạch:** `{res['ma_vach']}` | 📅 **HSD:** {res['ngay_hh']}")
        st.markdown("---")

    # BANNER 3: KHU VỰC THAO TÁC CỦA QUẢN LÝ (THÊM / SỬA / XÓA)
    if role_now in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("### ⚙️ MANAGEMENT ZONE (Khu vực quản trị dành cho Admin trở lên)")
        
        # CHỨC NĂNG: NHẬP VẬT TƯ MỚI (Dạng thanh ngang tối giản)
        st.markdown("#### ➕ Nhập thêm vật tư mới")
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns([2, 1, 1, 1, 2])
        with col_a1: add_name = st.text_input("Tên sản phẩm:", key="w_add_name").strip()
        with col_a2: add_barcode = st.text_input("Mã vạch:", key="w_add_bar").strip()
        with col_a3: add_nsx = st.date_input("Ngày SX:", value=date.today(), key="w_add_nsx").strftime("%Y-%m-%d")
        with col_a4: add_nhh = st.date_input("Ngày HH:", value=date.today(), key="w_add_nhh").strftime("%Y-%m-%d")
        with col_a5: add_loc = st.text_input("Vị trí chi tiết trên kệ:", key="w_add_loc").strip()
        
        if st.button("➕ XÁC NHẬN NHẬP KHO", type="primary", use_container_width=True):
            if not add_name or not add_barcode or not add_loc:
                st.error("Vui lòng nhập đủ thông tin bắt buộc (Tên, Mã vạch, Vị trí)!")
            elif any(x["ma_vach"] == add_barcode for x in st.session_state.kho_hang):
                st.error("Mã vạch này đã tồn tại!")
            else:
                st.session_state.kho_hang.append({"ten": add_name.upper(), "ma_vach": add_barcode, "ngay_sx": add_nsx, "ngay_hh": add_nhh, "vi_tri": add_loc})
                luu_du_lieu_he_thong()
                st.success(f"Đã thêm sản phẩm {add_name.upper()}!")
                st.rerun()

        st.markdown("---")
        
        # CHỨC NĂNG: BẢNG CHỈNH SỬA / XÓA SẢN PHẨM TRỰC TIẾP
        st.markdown("#### ✏️ Sửa / Xóa dữ liệu kho")
        if st.session_state.kho_hang:
            for idx, item in enumerate(st.session_state.kho_hang):
                col_e1, col_e2, col_e3, col_btn1, col_btn2 = st.columns([2, 1, 2, 1, 1])
                with col_e1: e_name = st.text_input(f"Tên hàng #{idx+1}", value=item["ten"], key=f"we_name_{idx}").strip()
                with col_e2: e_bar = st.text_input(f"Mã vạch #{idx+1}", value=item["ma_vach"], key=f"we_bar_{idx}").strip()
                with col_e3: e_loc = st.text_input(f"Vị trí kệ #{idx+1}", value=item["vi_tri"], key=f"we_loc_{idx}").strip()
                
                with col_btn1:
                    if st.button("💾 LƯU", key=f"w_save_btn_{idx}", use_container_width=True):
                        if not e_name or not e_bar or not e_loc: st.error("Không bỏ trống thông tin!")
                        else:
                            st.session_state.kho_hang[idx] = {"ten": e_name.upper(), "ma_vach": e_bar, "ngay_sx": item["ngay_sx"], "ngay_hh": item["ngay_hh"], "vi_tri": e_loc}
                            luu_du_lieu_he_thong()
                            st.success("Đã lưu!")
                            st.rerun()
                with col_btn2:
                    if st.button("🗑️ XÓA", key=f"w_del_btn_{idx}", use_container_width=True):
                        st.session_state.kho_hang.pop(idx)
                        luu_du_lieu_he_thong()
                        st.success("Đã xóa!")
                        st.rerun()
        else: st.info("Kho hiện đang trống.")

        st.markdown("---")
        

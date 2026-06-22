import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH & KHỞI TẠO HỆ THỐNG SMART-HUB
# ==========================================
st.set_page_config(page_title="Walmart Smart Inventory Hub - Hồng Phát", layout="wide", page_icon="🔵")

DB_FILE = "dulieu_kho_walmart_v2.json"

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
            {"ten": "CHẢO CHỐNG DÍNH", "ma_vach": "2222", "ngay_sx": "2026-01-01", "ngay_hh": "2028-01-01", "vi_tri": "Khu A - Kệ 02 - Tầng 1"},
            {"ten": "BÁNH MÌ SỮA", "ma_vach": "3333", "ngay_sx": "2026-01-01", "ngay_hh": "2026-02-01", "vi_tri": "Khu B - Kệ 01 - Tầng 1"}
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
    
    col_hd1, col_hd2 = st.columns()
    with col_hd1:
        st.markdown(f"<h1 style='color: #0071CE; margin:0;'>🔵 WALMART INVENTORY HUB — HỒNG PHÁT</h1>", unsafe_allow_html=True)
        st.write(f"👤 Người trực: **{u_now['name']}** | Chức vụ: `{ROLE_LABELS[role_now]}`")
    with col_hd2:
        if st.button("🚪 LOG OUT", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
            
    st.markdown("---")
    
    # CẢNH BÁO SẢN PHẨM HẾT HẠN
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
    
    # ==========================================
    # CHỨC NĂNG NÂNG CẤP: GỢI Ý SEARCH GOOGLE / WALMART
    # ==========================================
    st.markdown("### 🔍 SMART AUTO-COMPLETE SEARCH (Gợi ý tìm kiếm thông minh ABC)")
    
    # Ô nhập từ khóa chữ cái
    q_search = st.text_input("Gõ từ khóa hoặc quét mã vạch (Hệ thống tự xếp lịch gợi ý theo bảng chữ cái):", key="walmart_smart_search").strip()
    q_clean = loai_bo_dau_tieng_viet(q_search)

    # Thuật toán phân tách và sắp xếp gợi ý theo bảng chữ cái A-Z
    start_with_query = []
    contain_query = []

    for sp in st.session_state.kho_hang:
        ten_clean = loai_bo_dau_tieng_viet(sp["ten"])
        ma_vach_clean = sp["ma_vach"].lower()
        
        if q_clean in ten_clean or q_clean in ma_vach_clean:
            # Nếu tên hoặc mã vạch BẮT ĐẦU bằng từ khóa gõ vào (Ví dụ gõ 'c' ra 'CHOCOMONT') -> Ưu tiên xếp lên đầu
            if ten_clean.startswith(q_clean) or ma_vach_clean.startswith(q_clean):
                start_with_query.append(sp)
            else:
                contain_query.append(sp)

    # Sắp xếp từng nhóm độc lập theo bảng chữ cái từ A-Z dựa theo tên sản phẩm
    start_with_query.sort(key=lambda x: x["ten"])
    contain_query.sort(key=lambda x: x["ten"])

    # Gom hai nhóm lại thành danh sách gợi ý hoàn chỉnh (Ưu tiên từ bắt đầu -> từ chứa bên trong)
    danh_sach_goi_y = start_with_query + contain_query

    # Đưa danh sách gợi ý vào Selectbox giống như thanh hiển thị Dropdown gợi ý dưới ô Search Walmart
    options_goi_y = ["-- Chọn từ danh sách gợi ý kết quả bên dưới --"]
    for idx, item in enumerate(danh_sach_goi_y):
        options_goi_y.append(f"🛒 {item['ten'].upper()} [Mã vạch: {item['ma_vach']}]")

    if q_search:
        st.markdown(f"✨ *Danh sách gợi ý khớp với từ khóa '**{q_search}**' (Đã xếp theo ABC):*")
        lua_chon_goi_y = st.selectbox("Bấm vào đây để chọn nhanh kết quả gợi ý:", options=options_goi_y, index=0, key="sb_smart_dropdown")
        
        if lua_chon_goi_y != "-- Chọn từ danh sách gợi ý kết quả bên dưới --":
            mv_tim = lua_chon_goi_y.split("[Mã vạch: ")[-1].replace("]", "").strip()
            for sp in st.session_state.kho_hang:
                if sp["ma_vach"] == mv_tim:
                    st.info(f"📍 **ĐỊNH VỊ VỊ TRÍ KỆ KHO:** {sp['vi_tri']}\n\n📦 **Sản phẩm:** {sp['ten'].upper()} | 🆔 **Mã vạch:** `{sp['ma_vach']}` | 📅 **HSD:** {sp['ngay_hh']}")
                    break
    else:
        st.info("💡 Mẹo: Chỉ cần gõ chữ cái đầu (ví dụ: c, ch, b), hệ thống sẽ tự hiển thị gợi ý thông minh lập tức.")

    st.markdown("---")

    # KHU VỰC THAO TÁC CỦA QUẢN LÝ (THÊM / SỬA / XÓA)
    if role_now in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("### ⚙️ MANAGEMENT ZONE (Khu vực quản trị dành cho Admin trở lên)")
        
        # CHỨC NĂNG: NHẬP VẬT TƯ MỚI
        st.markdown("#### ➕ Nhập thêm vật tư mới")
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns()
        with col_a1: add_name = st.text_input("Tên sản phẩm:", key="w_add_name").strip()
        with col_a2: add_barcode = st.text_input("Mã vạch:", key="w_add_bar").strip()
        with col_a3: add_nsx = st.date_input("Ngày SX:", value=date.today(), key="w_add_nsx").strftime("%Y-%m-%d")
        with col_a4: add_nhh = st.date_input("Ngày HH:", value=date.today(), key="w_add_nhh").strftime("%Y-%m-%d")
        with col_a5: add_loc = st.text_input("Vị trí chi tiết trên kệ:", key="w_add_loc").strip()
        
        if st.button("➕ XÁC NHẬN NHẬP KHO", type="primary", use_container_width=True):
            if not add_name or not add_barcode or not add_loc:
                st.error("Vui lòng nhập đủ thông tin bắt buộc!")
            elif any(x["ma_vach"] == add_barcode for x in st.session_state.kho_hang):
                st.error("Mã vạch này đã tồn tại!")
            else:
                st.session_state.kho_hang.append({"ten": add_name.upper(), "ma_vach": add_barcode, "ngay_sx": add_nsx, "ngay_hh": add_nhh, "vi_tri": add_loc})
                luu_du_lieu_he_thong()
                st.success(f"Đã thêm sản phẩm {add_name.upper()}!")

import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH & KHỞI TẠO HỆ THỐNG SMART-HUB HỒNG PHÁT
# ==========================================
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

# Khởi tạo bộ nhớ tạm để giữ sản phẩm được click chọn từ thanh gợi ý search
if 'selected_product_mv' not in st.session_state:
    st.session_state.selected_product_mv = None

# ==========================================
# 2. GIAO DIỆN ĐĂNG NHẬP THUẦN CHỨC NĂNG
# ==========================================
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
                    else: st.error("Tài khoản chưa được kích hoạt quyền truy cập!")
                else: st.error("Mật khẩu không chính xác!")
            else: st.error("Tài khoản không tồn tại trên hệ thống!")
            
    with col_l2:
        st.subheader("📝 ĐĂNG KÝ TÀI KHOẢN MỚI")
        r_user = st.text_input("Tên đăng nhập mới (viết liền không dấu):", key="r_user").strip()
        r_name = st.text_input("Họ và tên thật của nhân sự:", key="r_name").strip()
        r_pass = st.text_input("Tạo mật khẩu truy cập:", type="password", key="r_pass")
        if st.button("GỬI YÊU CẦU ĐĂNG KÝ", use_container_width=True):
            if not r_user or not r_name or not r_pass:
                st.error("Vui lòng điền đầy đủ thông tin bắt buộc!")
            elif r_user in st.session_state.users:
                st.error("Tên tài khoản này đã có người sử dụng!")
            else:
                st.session_state.users[r_user] = {"name": r_name, "password": r_pass, "active": False, "role": "4_staff"}
                luu_du_lieu_he_thong()
                st.success("Đăng ký thành công! Hãy liên hệ cấp trên phê duyệt kích hoạt.")

# ==========================================
# 3. DASHBOARD ĐIỀU HÀNH SMART-HUB HỒNG PHÁT CHÍNH THỨC
# ==========================================
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
            st.session_state.selected_product_mv = None
            st.rerun()
            
    st.markdown("---")
    
    # CẢNH BÁO BẢO QUẢN SẢN PHẨM HẾT HẠN (DƯỚI 7 NGÀY)
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
        st.success("✅ Toàn bộ vật liệu lưu kho đều nằm trong hạn sử dụng an toàn.")

    st.markdown("---")
    
    # ==========================================
    # CHỨC NĂNG GỢI Ý SEARCH GOOGLE ĐỘNG (DƯỚI DẠNG THẺ TAGS ABC)
    # ==========================================
    st.markdown("### 🔍 SEARCH SUGGESTIONS (Gợi ý tìm kiếm thông minh xếp lịch ABC)")
    q_search = st.text_input("Gõ chữ cái đầu hoặc quét mã vạch (Hệ thống tự rớt gợi ý chữ cái đầu lên trước):", key="hongphat_smart_search").strip()
    q_clean = loai_bo_dau_tieng_viet(q_search)

    if q_search:
        start_with_query = []
        contain_query = []

        for sp in st.session_state.kho_hang:
            ten_clean = loai_bo_dau_tieng_viet(sp["ten"])
            ma_vach_clean = sp["ma_vach"].lower()
            
            if q_clean in ten_clean or q_clean in ma_vach_clean:
                # Nếu từ khóa khớp ngay chữ cái đầu -> ưu tiên nhóm 1
                if ten_clean.startswith(q_clean) or ma_vach_clean.startswith(q_clean):
                    start_with_query.append(sp)
                else:
                    contain_query.append(sp)

        # Sắp xếp danh sách tự động theo bảng chữ cái ABC
        start_with_query.sort(key=lambda x: x["ten"])
        contain_query.sort(key=lambda x: x["ten"])
        danh_sach_goi_y = start_with_query + contain_query

        if danh_sach_goi_y:
            st.markdown("👇 *Bấm chọn một trong các từ khóa gợi ý bên dưới để xem vị trí định vị:*")
            
            # Tạo các nút bấm gợi ý động nằm ngang giống thanh gợi ý Google Search
            cols_tags = st.columns(min(len(danh_sach_goi_y), 6))
            for i, item in enumerate(danh_sach_goi_y[:6]): # Giới hạn hiển thị tối đa 6 gợi ý tốt nhất
                with cols_tags[i % 6]:
                    if st.button(f"🔍 {item['ten'].upper()}", key=f"tag_btn_{item['ma_vach']}"):
                        st.session_state.selected_product_mv = item['ma_vach']
        else:
            st.error("❌ Không tìm thấy sản phẩm nào khớp với chữ cái bạn vừa nhập.")

    # Hiển thị thông tin định vị chi tiết khi sếp click vào thẻ gợi ý hoặc tìm ra sản phẩm duy nhất
    if st.session_state.selected_product_mv:
        for sp in st.session_state.kho_hang:
            if sp["ma_vach"] == st.session_state.selected_product_mv:
                st.markdown("---")
                st.info(f"📍 **ĐỊNH VỊ VỊ TRÍ KỆ HÀNG HỒNG PHÁT:** {sp['vi_tri']}\n\n📦 **Vật tư:** {sp['ten'].upper()} | 🆔 **Mã vạch:** `{sp['ma_vach']}` | 📅 **Hạn sử dụng:** {sp['ngay_hh']}")
                break
    else:
        st.info("💡 Mẹo gợi ý: Gõ một vài chữ cái đầu (ví dụ: c, ch, b), hệ thống tự xếp danh sách ABC rớt xuống cho sếp chọn cực nhanh.")

    st.markdown("---")

    # KHU VỰC THAO TÁC CỦA QUẢN LÝ (THÊM / SỬA / XÓA)
    if role_now in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("### ⚙️ MANAGEMENT ZONE (Khu vực quản trị dành cho Ban Quản Lý Chợ)")
        
        # CHỨC NĂNG: NHẬP VẬT TƯ MỚI
        st.markdown("#### ➕ Nhập thêm vật tư hàng hóa mới")
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
        with col_a1: add_name = st.text_input("Tên hàng hóa:", key="w_add_name").strip()
        with col_a2: add_barcode = st.text_input("Mã vạch định danh:", key="w_add_bar").strip()
        with col_a3: add_nsx = st.date_input("Ngày sản xuất:", value=date.today(), key="w_add_nsx").strftime("%Y-%m-%d")
        with col_a4: add_nhh = st.date_input("Hạn sử dụng:", value=date.today(), key="w_add_nhh").strftime("%Y-%m-%d")
        with col_a5: add_loc = st.text_input("Vị trí kệ kho chi tiết:", key="w_add_loc").strip()
        
        if st.button("➕ XÁC NHẬN GHI SỔ NHẬP KHO", type="primary", use_container_width=True):

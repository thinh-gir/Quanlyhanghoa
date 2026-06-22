import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH TRANG WEB & KHỞI TẠO BẢO MẬT
# ==========================================
st.set_page_config(page_title="Hệ thống Quản lý Chợ Hồng Phát", layout="wide", page_icon="🏭")

DB_FILE = "dulieu_kho_hongphat_v4.json"

ROLE_LABELS = {
    "1_creator": "👑 ĐỒNG SÁNG LẬP DUY NHẤT",
    "2_owner": "💼 BOSS CHỦ CHỢ (OWNER)",
    "3_admin": "🛠️ QUẢN LÝ (ADMIN)",
    "4_staff": "👁️ NHÂN VIÊN (STAFF)"
}

def luu_du_lieu_he_thong():
    """Ghi đè đồng bộ dữ liệu từ bộ nhớ tạm vào tệp tin lưu trữ dữ liệu JSON"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": st.session_state.users,
            "kho_hang": st.session_state.kho_hang
        }, f, ensure_ascii=False, indent=4)

def loai_bo_dau_tieng_viet(chuoi_chu):
    """Hàm bổ trợ giúp tìm kiếm thông minh không cần gõ dấu"""
    co_dau = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    khong_dau = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    bang_chuyen = str.maketrans(co_dau, khong_dau)
    return chuoi_chu.translate(bang_chuyen).lower()

# Khởi tạo cơ sở dữ liệu gốc nếu chạy lần đầu tiên
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

# Nạp dữ liệu vào bộ nhớ đệm Session State của Streamlit
if 'users' not in st.session_state or 'kho_hang' not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        tep_du_lieu = json.load(f)
        st.session_state.users = tep_du_lieu.get("users", {})
        st.session_state.kho_hang = tep_du_lieu.get("kho_hang", [])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# ==========================================
# 2. GIAO DIỆN HỆ THỐNG TRƯỚC ĐĂNG NHẬP
# ==========================================
if not st.session_state.logged_in:
    st.title("🔒 HỆ THỐNG BẢO MẬT CHỢ HỒNG PHÁT")
    tab_dang_nhap, tab_dang_ky = st.tabs(["🔑 Đăng nhập hệ thống", "📝 Đăng ký tài khoản mới"])
    
    with tab_dang_nhap:
        user_input = st.text_input("Tên tài khoản truy cập:", key="nhap_user").strip()
        pass_input = st.text_input("Mật khẩu bảo mật:", type="password", key="nhap_pass")
        
        if st.button("Đăng nhập vào hệ thống", type="primary", use_container_width=True):
            if user_input in st.session_state.users:
                thong_tin = st.session_state.users[user_input]
                if thong_tin["password"] == pass_input:
                    if thong_tin["active"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input
                        st.success("🎉 Đăng nhập thành công vào hệ thống Chợ Hồng Phát!")
                        st.rerun()
                    else:
                        st.error("🚨 Tài khoản này chưa được kích hoạt hoặc đang bị khóa bởi cấp trên!")
                else:
                    st.error("❌ Mật khẩu nhập vào chưa chính xác!")
            else:
                st.error("❌ Tài khoản này không tồn tại trên hệ thống dữ liệu!")
                
    with tab_dang_ky:
        st.info("💡 Tài khoản đăng ký tự do mặc định sẽ xếp ở cấp bậc Nhân viên (Staff) và cần cấp trên xét duyệt để mở khóa.")
        reg_user = st.text_input("Tạo tên tài khoản (Viết liền không dấu):", key="tao_user").strip()
        reg_name = st.text_input("Nhập họ và tên thật:", key="tao_ten").strip()
        reg_pass = st.text_input("Tạo mật khẩu đăng nhập:", type="password", key="tao_pass")
        
        if st.button("Gửi yêu cầu đăng ký tài khoản", use_container_width=True):
            if not reg_user or not reg_name or not reg_pass:
                st.error("❌ Vui lòng cung cấp đầy đủ thông tin, không được bỏ trống!")
            elif reg_user in st.session_state.users:
                st.error("❌ Tên tài khoản này đã được sử dụng, vui lòng chọn tên khác!")
            else:
                st.session_state.users[reg_user] = {
                    "name": reg_name, 
                    "password": reg_pass, 
                    "active": False, 
                    "role": "4_staff"
                }
                luu_du_lieu_he_thong()
                st.success("🎉 Đăng ký thành công! Hãy báo cho cấp trên trực ban mở khóa tài khoản cho bạn.")

# ==========================================
# 3. GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP THÀNH CÔNG
# ==========================================
else:
    user_truc = st.session_state.users[st.session_state.current_user]
    cap_bac_hien_tai = user_truc["role"]
    
    # Cấu hình thanh chức năng Sidebar bên trái màn hình
    st.sidebar.title("🏭 CHỢ HỒNG PHÁT")
    st.sidebar.markdown(f"👤 Trực ban: **{user_truc['name']}**")
    st.sidebar.markdown(f"🎖️ Quyền hạn: `{ROLE_LABELS[cap_bac_hien_tai]}`")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Đăng xuất khỏi hệ thống", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.title("🏭 HỆ THỐNG TRỰC BAN & ĐỊNH VỊ VẬT LIỆU")
    st.markdown("---")
    
    # CHỨC NĂNG CHUNG 1: KIỂM TRA TỰ ĐỘNG HẠN SỬ DỤNG
    st.header("⏳ CẢNH BÁO BẢO QUẢN SẢN PHẨM (DƯỚI 7 NGÀY)")
    thoi_gian_thuc = datetime.now()
    co_canh_bao = False
    
    for hang in st.session_state.kho_hang:
        try:
            ngay_het_han_dt = datetime.strptime(hang.get("ngay_hh", "2099-12-31"), "%Y-%m-%d")
            tinh_toan_ngay = (ngay_het_han_dt - thoi_gian_thuc).days + 1
            
            if tinh_toan_ngay <= 7:
                co_canh_bao = True
                ten_hang_hoa = hang['ten'].upper()
                vi_tri_kho = hang.get('vi_tri', 'Chưa rõ vị trí')
                
                if tinh_toan_ngay < 0:
                    st.error(f"🚨 **{ten_hang_hoa}** - **ĐÃ QUÁ HẠN {abs(tinh_toan_ngay)} NGÀY!** 📍 Vị trí: {vi_tri_kho}")
                else:
                    st.warning(f"⚠️ **{ten_hang_hoa}** - Sắp hết hạn (Còn lại **{tinh_toan_ngay} ngày**). 📍 Vị trí: {vi_tri_kho}")
        except Exception:
            pass
            
    if not co_canh_bao:
        st.success("✅ Hệ thống an toàn. Không phát hiện sản phẩm nào sắp hết hạn trong kho.")
        
    st.markdown("---")

    # CHỨC NĂNG CHUNG 2: TÌM KIẾM THÔNG MINH KHÔNG DẤU & CHỮ CÁI
    st.header("🔍 BỘ ĐỊNH VỊ VỊ TRÍ HÀNG HÓA THÔNG MINH")
    o_tim_kiem = st.text_input("Gõ chữ cái, tên sản phẩm (có dấu/không dấu) hoặc quét mã vạch:", "").strip()
    
    danh_sach_loc_duoc = []
    tu_khoa_xu_ly = loai_bo_dau_tieng_viet(o_tim_kiem)
    
    for sp in st.session_state.kho_hang:
        ten_xu_ly = loai_bo_dau_tieng_viet(sp["ten"])
        ma_vach_xu_ly = sp["ma_vach"].lower()
        if tu_khoa_xu_ly in ten_xu_ly or tu_khoa_xu_ly in ma_vach_xu_ly:
            danh_sach_loc_duoc.append(sp)
            
    if o_tim_kiem:
        st.write(f"💡 Cơ chế thông minh lọc được **{len(danh_sach_loc_duoc)}** kết quả phù hợp:")

    if danh_sach_loc_duoc:
        hop_lua_chon = ["-- Bấm vào đây để xem chi tiết vị trí định vị --"]
        for i, san_pham in enumerate(danh_sach_loc_duoc):
            hop_lua_chon.append(f"{i+1}. {san_pham['ten'].upper()} [Mã vạch: {san_pham['ma_vach']}]")
            
        chon_san_pham = st.selectbox("Lựa chọn sản phẩm cần định vị vị trí:", options=hop_lua_chon, index=0)
        
        if chon_san_pham != "-- Bấm vào đây để xem chi tiết vị trí định vị --":
            mv_trich_xuat = chon_san_pham.split("[Mã vạch: ")[-1].replace("]", "").strip()
            for hang_hoa in st.session_state.kho_hang:
                if hang_hoa["ma_vach"] == mv_trich_xuat:
                    st.info(f"📍 **VỊ TRÍ CHÍNH XÁC TRÊN KỆ:** {hang_hoa.get('vi_tri', 'Chưa xác định')}")
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        st.write(f"📦 **Tên vật tư:** {hang_hoa['ten'].upper()}")
                        st.write(f"🆔 **Mã vạch sản phẩm:** `{hang_hoa['ma_vach']}`")
                    with col_h2:
                        st.write(f"📅 **Ngày sản xuất kho:** {hang_hoa.get('ngay_sx', 'Chưa rõ')}")
                        st.write(f"📅 **Hạn sử dụng kho:** {hang_hoa.get('ngay_hh', 'Chưa rõ')}")
                    break
    else:
        st.error("❌ Không tìm thấy sản phẩm nào trùng khớp với từ khóa tìm kiếm của bạn.")

    # ==========================================
    # 4. TRUNG TÂM QUẢN TRỊ PHÂN CẤP BẢO MẬT TUYỆT ĐỐI
    # ==========================================
    if cap_bac_hien_tai in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("---")
        st.header("⚙️ TRUNG TÂM ĐIỀU HÀNH BẢO MẬT & PHÂN QUYỀN CHỢ HỒNG PHÁT")
        
        tab_nhan_su, tab_them_hang, tab_sua_hang = st.tabs([
            "👥 Phê duyệt & Quản lý Giai cấp Nhân sự", 
            "📦 Nhập thêm vật tư mới", 
            "✏️ Chỉnh sửa thông tin / Xóa bỏ vật tư"
        ])
        
        # --- TAB 1: PHÊ DUYỆT TÀI KHOẢN ---
        with tab_nhan_su:
            st.subheader("Bảng danh sách nhân sự hiện thời")
            bang_hien_thi = []
            for tk, thong_tin_tk in st.session_state.users.items():
                bang_hien_thi.append({
                    "Tài khoản hệ thống": tk,

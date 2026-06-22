import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH TRANG WEB & KHỞI TẠO BẢO MẬT
# ==========================================
st.set_page_config(page_title="Hệ thống Quản lý Chợ Hồng Phát", layout="wide", page_icon="🏭")

DB_FILE = "dulieu_kho_hongphat_v6.json"

ROLE_LABELS = {
    "1_creator": "👑 ĐỒNG SÁNG LẬP DUY NHẤT",
    "2_owner": "💼 BOSS CHỦ CHỢ (OWNER)",
    "3_admin": "🛠️ QUẢN LÝ (ADMIN)",
    "4_staff": "👁️ NHÂN VIÊN (STAFF)"
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
# 2. GIAO DIỆN HỆ THỐNG TRƯỚC ĐĂNG NHẬP
# ==========================================
if not st.session_state.logged_in:
    st.title("🔒 HỆ THỐNG BẢO MẬT CHỢ HỒNG PHÁT")
    
    giao_dien_auth = st.radio("CHỌN THAO TÁC THỰC HIỆN:", ["🔑 Đăng nhập hệ thống", "📝 Đăng ký tài khoản mới"], horizontal=True)
    
    if giao_dien_auth == "🔑 Đăng nhập hệ thống":
        user_input = st.text_input("Tên tài khoản truy cập:", key="nhap_user").strip()
        pass_input = st.text_input("Mật khẩu bảo mật:", type="password", key="nhap_pass")
        
        if st.button("Đăng nhập vào hệ thống", type="primary", use_container_width=True):
            if user_input in st.session_state.users:
                thong_tin = st.session_state.users[user_input]
                if thong_tin["password"] == pass_input:
                    if thong_tin["active"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input
                        st.success("🎉 Đăng nhập thành công!")
                        st.rerun()
                    else:
                        st.error("🚨 Tài khoản này chưa được kích hoạt hoặc đang bị khóa quyền!")
                else:
                    st.error("❌ Mật khẩu nhập vào chưa chính xác!")
            else:
                st.error("❌ Tài khoản này không tồn tại trên hệ thống dữ liệu!")
                
    else:
        st.info("💡 Tài khoản đăng ký tự do mặc định sẽ xếp ở cấp bậc Nhân viên (Staff) và cần cấp trên xét duyệt.")
        reg_user = st.text_input("Tạo tên tài khoản (Viết liền không dấu):", key="tao_user").strip()
        reg_name = st.text_input("Nhập họ và tên thật:", key="tao_ten").strip()
        reg_pass = st.text_input("Tạo mật khẩu đăng nhập:", type="password", key="tao_pass")
        
        if st.button("Gửi yêu cầu đăng ký tài khoản", use_container_width=True):
            if not reg_user or not reg_name or not reg_pass:
                st.error("❌ Vui lòng cung cấp đầy đủ thông tin, không được bỏ trống!")
            elif reg_user in st.session_state.users:
                st.error("❌ Tên tài khoản này đã được sử dụng!")
            else:
                st.session_state.users[reg_user] = {"name": reg_name, "password": reg_pass, "active": False, "role": "4_staff"}
                luu_du_lieu_he_thong()
                st.success("🎉 Đăng ký thành công! Hãy báo cho cấp trên mở khóa tài khoản cho bạn.")

# ==========================================
# 3. GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP THÀNH CÔNG
# ==========================================
else:
    user_truc = st.session_state.users[st.session_state.current_user]
    cap_bac_hien_tai = user_truc["role"]
    
    st.sidebar.title("🏭 CHỢ HỒNG PHÁT")
    st.sidebar.markdown(f"👤 Trực ban: **{user_truc['name']}**")
    st.sidebar.markdown(f"🎖️ Quyền hạn: `{ROLE_LABELS[cap_bac_hien_tai]}`")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Đăng xuất khỏi hệ thống", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.title("🏭 HỆ THỐNG TRỰC BAN CHỢ HỒNG PHÁT")
    st.markdown("---")
    
    # CHỨC NĂNG CHUNG 1: CẢNH BÁO HẠN SỬ DỤNG
    st.header("⏳ CẢNH BÁO BẢO QUẢN SẢN PHẨM (DƯỚI 7 NGÀY)")
    thoi_gian_thuc = datetime.now()
    co_canh_bao = False
    
    for hang in st.session_state.kho_hang:
        try:
            ngay_het_han_dt = datetime.strptime(hang.get("ngay_hh", "2099-12-31"), "%Y-%m-%d")
            tinh_toan_ngay = (ngay_het_han_dt - thoi_gian_thuc).days + 1
            if tinh_toan_ngay <= 7:
                co_canh_bao = True
                if tinh_toan_ngay < 0:
                    st.error(f"🚨 **{hang['ten'].upper()}** - **ĐÃ QUÁ HẠN {abs(tinh_toan_ngay)} NGÀY!** 📍 Kệ: {hang.get('vi_tri', 'Chưa rõ')}")
                else:
                    st.warning(f"⚠️ **{hang['ten'].upper()}** - Còn lại **{tinh_toan_ngay} ngày**. 📍 Kệ: {hang.get('vi_tri', 'Chưa rõ')}")
        except:
            pass
            
    if not co_canh_bao:
        st.success("✅ Hệ thống an toàn. Không phát hiện sản phẩm nào sắp hết hạn.")
        
    st.markdown("---")

    # CHỨC NĂNG CHUNG 2: TRA CỨU KHÔNG DẤU VÀ CHỮ CÁI
    st.header("🔍 BỘ ĐỊNH VỊ VỊ TRÍ HÀNG HÓA THÔNG MINH")
    o_tim_kiem = st.text_input("Gõ chữ cái, tên sản phẩm (có dấu/không dấu) hoặc quét mã vạch:", key="txt_search_box").strip()
    
    danh_sach_loc_duoc = []
    tu_khoa_xu_ly = loai_bo_dau_tieng_viet(o_tim_kiem)
    
    for sp in st.session_state.kho_hang:
        if tu_khoa_xu_ly in loai_bo_dau_tieng_viet(sp["ten"]) or tu_khoa_xu_ly in sp["ma_vach"].lower():
            danh_sach_loc_duoc.append(sp)
            
    if danh_sach_loc_duoc:
        hop_lua_chon = ["-- Chọn sản phẩm cần định vị vị trí --"]
        for san_pham in danh_sach_loc_duoc:
            hop_lua_chon.append(f"{san_pham['ten'].upper()} | Mã vạch: {san_pham['ma_vach']}")
            
        chon_san_pham = st.selectbox("Kết quả bộ lọc thông minh:", options=hop_lua_chon, index=0, key="sb_search_result")
        
        if chon_san_pham != "-- Chọn sản phẩm cần định vị vị trí --":
            mv_trich_xuat = chon_san_pham.split("| Mã vạch: ")[-1].strip()
            for hang_hoa in st.session_state.kho_hang:
                if hang_hoa["ma_vach"] == mv_trich_xuat:
                    st.info(f"📍 **VỊ TRÍ CHÍNH XÁC TRÊN KỆ:** {hang_hoa.get('vi_tri', 'Chưa xác định')}")
                    st.write(f"📦 **Tên vật tư:** {hang_hoa['ten'].upper()} | 🆔 **Mã vạch:** `{hang_hoa['ma_vach']}`")
                    st.write(f"📅 **NSX:** {hang_hoa.get('ngay_sx', 'Chưa rõ')} | **HSD:** {hang_hoa.get('ngay_hh', 'Chưa rõ')}")
                    break
    else:
        st.error("❌ Không tìm thấy sản phẩm nào phù hợp.")

    # ==========================================
    # 4. TRUNG TÂM QUẢN TRỊ PHÂN CẤP (CHỈ ADMIN TRỞ LÊN MỚI THẤY)
    # ==========================================
    if cap_bac_hien_tai in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("---")
        st.header("⚙️ TRUNG TÂM ĐIỀU HÀNH BẢO MẬT CHỢ HỒNG PHÁT")
        
        # CHỨC NĂNG QUẢN LÝ NHÂN SỰ
        st.subheader("👥 Phê duyệt & Quản lý Tài khoản Cấp dưới")
        tai_khoan_hop_le = [u for u in st.session_state.users.keys() if u != st.session_state.current_user and st.session_state.users[u]["role"] != "1_creator"]
        
        if tai_khoan_hop_le:
            tk_duoc_chon = st.selectbox("Chọn tài khoản nhân sự cần xử lý quyền:", options=tai_khoan_hop_le, key="sb_manage_staff")
            thong_tin_sua = st.session_state.users[tk_duoc_chon]
            role_sua = thong_tin_sua["role"]
            
            quyen_duyet = False
            if cap_bac_hien_tai == "1_creator": quyen_duyet = True
            elif cap_bac_hien_tai == "2_owner" and role_sua in ["3_admin", "4_staff"]: quyen_duyet = True
            elif cap_bac_hien_tai == "3_admin" and role_sua == "4_staff": quyen_duyet = True
                
            if quyen_duyet:
                chuyen_trang_thai = st.checkbox("Cho phép tài khoản này hoạt động đăng nhập", value=thong_tin_sua["active"], key=f"chk_active_{tk_duoc_chon}")
                giai_cap_cho_phep = {"👁️ Nhân viên (STAFF)": "4_staff"}
                if cap_bac_hien_tai in ["1_creator", "2_owner"]: giai_cap_cho_phep["🛠️ Quản lý (ADMIN)"] = "3_admin"
                if cap_bac_hien_tai == "1_creator": giai_cap_cho_phep["💼 BOSS CHỦ CHỢ (OWNER)"] = "2_owner"
                
                ten_nhan_hien_tai = [k for k, v in giai_cap_cho_phep.items() if v == role_sua]
                vi_tri_mac_dinh = list(giai_cap_cho_phep.keys()).index(ten_nhan_hien_tai) if ten_nhan_hien_tai else 0

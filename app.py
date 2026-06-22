import streamlit as st
import json
import os
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & CƠ SỞ DỮ LIỆU
# ==========================================
st.set_page_config(page_title="Hệ thống Quản lý Chợ Hồng Phát", layout="wide")

DB_FILE = "dulieu_kho_hongphat_v3.json"

ROLE_LABELS = {
    "1_creator": "👑 ĐỒNG SÁNG LẬP DUY NHẤT",
    "2_owner": "💼 BOSS CHỦ CHỢ (OWNER)",
    "3_admin": "🛠️ QUẢN LÝ (ADMIN)",
    "4_staff": "👁️ NHÂN VIÊN (STAFF)"
}

def luu_du_lieu():
    """Ghi đè dữ liệu hiện tại trong session_state vào file JSON cứng"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "users": st.session_state.users,
            "kho_hang": st.session_state.kho_hang
        }, f, ensure_ascii=False, indent=4)

# Khởi tạo file dữ liệu gốc nếu chưa tồn tại
if not os.path.exists(DB_FILE):
    initial_data = {
        "users": {
            "Zeroizerd": {
                "name": "Đồng Sáng Lập Zeroizerd", 
                "password": "13723@", 
                "active": True, 
                "role": "1_creator"
            }
        },
        "kho_hang": [
            {"ten": "CHOCOMONT BÁNH GẤU", "ma_vach": "1111", "ngay_sx": "2026-01-01", "ngay_hh": "2026-06-30", "vi_tri": "Khu A - Kệ 01 - Tầng 2"},
            {"ten": "CHẢO CHỐNG DÍNH", "ma_vach": "2222", "ngay_sx": "2026-01-01", "ngay_hh": "2028-01-01", "vi_tri": "Khu A - Kệ 02 - Tầng 1"}
        ]
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=4)

# Nạp dữ liệu vào bộ nhớ đệm Session State
if 'users' not in st.session_state or 'kho_hang' not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        st.session_state.users = data.get("users", {})
        st.session_state.kho_hang = data.get("kho_hang", [])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# ==========================================
# 2. GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if not st.session_state.logged_in:
    st.title("🔒 HỆ THỐNG BẢO MẬT CHỢ HỒNG PHÁT")
    tab_login, tab_register = st.tabs(["🔑 Đăng nhập hệ thống", "📝 Đăng ký tài khoản mới"])
    
    with tab_login:
        username_input = st.text_input("Tài khoản:", key="login_user").strip()
        password_input = st.text_input("Mật khẩu:", type="password", key="login_pass")
        
        if st.button("Đăng nhập", key="btn_login", type="primary"):
            if username_input in st.session_state.users:
                user_info = st.session_state.users[username_input]
                if user_info["password"] == password_input:
                    if user_info["active"]:
                        st.session_state.logged_in = True
                        st.session_state.current_user = username_input
                        st.success("Đăng nhập thành công!")
                        st.rerun()
                    else:
                        st.error("🚨 Tài khoản này chưa được kích hoạt hoặc đang bị khóa quyền!")
                else:
                    st.error("❌ Sai mật khẩu!")
            else:
                st.error("❌ Tài khoản không tồn tại trên hệ thống!")
                
    with tab_register:
        st.info("💡 Tài khoản đăng ký mới mặc định sẽ ở cấp Nhân viên và cần cấp trên có thẩm quyền duyệt.")
        reg_username = st.text_input("Tên đăng nhập mới (Viết liền, không dấu):", key="reg_user").strip()
        reg_name = st.text_input("Họ và tên thật của bạn:", key="reg_name").strip()
        reg_password = st.text_input("Đặt mật khẩu truy cập:", type="password", key="reg_pass")
        
        if st.button("Gửi yêu cầu đăng ký", key="btn_reg"):
            if not reg_username or not reg_name or not reg_password:
                st.error("❌ Vui lòng điền đầy đủ thông tin!")
            elif reg_username in st.session_state.users:
                st.error("❌ Tên tài khoản này đã tồn tại!")
            else:
                st.session_state.users[reg_username] = {
                    "name": reg_name, 
                    "password": reg_password, 
                    "active": False, 
                    "role": "4_staff"
                }
                luu_du_lieu()
                st.success("🎉 Gửi yêu cầu thành công! Vui lòng liên hệ cấp trên để kích hoạt tài khoản.")

# ==========================================
# 3. GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP
# ==========================================
else:
    user_now = st.session_state.users[st.session_state.current_user]
    role_now = user_now["role"]
    
    # Thanh điều hướng Sidebar
    st.sidebar.title("MENU HỆ THỐNG")
    st.sidebar.write(f"👤 Trực ban: **{user_now['name']}**")
    st.sidebar.write(f"🎖️ Chức vụ: `{ROLE_LABELS[role_now]}`")
    
    if st.sidebar.button("🚪 Đăng xuất hệ thống", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.title("🏭 HỆ THỐNG QUẢN LÝ KHO CHỢ HỒNG PHÁT")
    st.markdown("---")
    
    # ------------------------------------------
    # CHỨC NĂNG 1: CẢNH BÁO HẠN SỬ DỤNG VẬT LIỆU
    # ------------------------------------------
    st.header("⏳ CẢNH BÁO HẠN SỬ DỤNG (DƯỚI 7 NGÀY)")
    ngay_hien_tai = datetime.now()
    co_hang_can_chu_y = False
    
    for item in st.session_state.kho_hang:
        try:
            ngay_hh = datetime.strptime(item.get("ngay_hh", "2099-12-31"), "%Y-%m-%d")
            so_ngay = (ngay_hh - ngay_hien_tai).days + 1
            
            if so_ngay <= 7:
                co_hang_can_chu_y = True
                ten_in_hoa = item['ten'].upper()
                vi_tri_hang = item.get('vi_tri', 'Chưa xác định')
                
                if so_ngay < 0:
                    st.error(f"🚨 **{ten_in_hoa}** - **HẾT HẠN QUÁ {abs(so_ngay)} NGÀY!** 📍 Vị trí: {vi_tri_hang}")
                else:
                    st.warning(f"⚠️ **{ten_in_hoa}** - Sắp hết hạn (Còn **{so_ngay} ngày**). 📍 Vị trí: {vi_tri_hang}")
        except Exception:
            pass
            
    if not co_hang_can_chu_y:
        st.success("✅ Toàn bộ vật liệu trong kho đều có hạn sử dụng an toàn trên 7 ngày.")
        
    st.markdown("---")

    # ------------------------------------------
    # CHỨC NĂNG 2: TÌM KIẾM THÔNG MINH THEO CHỮ CÁI
    # ------------------------------------------
    st.header("🔍 TRA CỨU ĐỊNH VỊ VỊ TRÍ VẬT LIỆU THÔNG MINH")
    
    # Ô nhập chữ cái tự động lọc nhanh dữ liệu bên dưới
    tu_khoa = st.text_input("Gõ chữ cái bất kỳ hoặc Quét mã vạch để tìm nhanh:", "").strip().lower()
    
    # Lọc danh sách sản phẩm khớp với từ khóa (Fuzzy filter)
    items_phu_hop = []
    for item in st.session_state.kho_hang:
        if tu_khoa in item["ten"].lower() or tu_khoa in item["ma_vach"].lower():
            items_phu_hop.append(item)
            
    if tu_khoa:
        st.write(f"💡 Tìm thấy **{len(items_phu_hop)}** vật liệu khớp với từ khóa của bạn:")
    
    if items_phu_hop:
        # Tạo danh sách hiển thị cho hộp selectbox từ các item đã lọc được
        danh_sach_selectbox = ["-- Bấm vào đây để xem kết quả lọc chi tiết --"]
        for idx, item in enumerate(items_phu_hop):
            danh_sach_selectbox.append(f"{idx+1}. {item['ten'].upper()} | Mã vạch: {item['ma_vach']}")
            
        lua_chon = st.selectbox("Kết quả lọc thông minh:", options=danh_sach_selectbox, index=0)
        
        if lua_chon != "-- Bấm vào đây để xem kết quả lọc chi tiết --":
            # Trích xuất mã vạch để hiển thị thông tin chính xác
            ma_vach_can_tim = lua_chon.split("| Mã vạch: ")[-1].strip()
            for item in st.session_state.kho_hang:
                if item["ma_vach"] == ma_vach_can_tim:
                    st.info(f"📍 **VỊ TRÍ ĐỊNH VỊ CHI TIẾT:** {item.get('vi_tri', 'Chưa rõ')}")
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        st.write(f"🔹 **Tên sản phẩm:** {item['ten'].upper()}")
                        st.write(f"🔹 **Mã vạch định danh:** `{item['ma_vach']}`")
                    with col_i2:
                        st.write(f"📅 **Ngày sản xuất:** {item.get('ngay_sx', 'Chưa rõ')}")
                        st.write(f"📅 **Hạn sử dụng:** {item.get('ngay_hh', 'Chưa rõ')}")
                    break
    else:
        st.error("❌ Không tìm thấy sản phẩm nào khớp với chữ cái/mã vạch bạn vừa gõ.")

    # ==========================================
    # 4. KHU VỰC QUẢN TRỊ PHÂN TẦNG NGHIÊM NGẶT
    # ==========================================
    if role_now in ["1_creator", "2_owner", "3_admin"]:
        st.markdown("---")
        st.header("⚙️ TRUNG TÂM ĐIỀU HÀNH BẢO MẬT & PHÂN QUYỀN")
        
        tab_ns, tab_kho_them, tab_kho_sua = st.tabs([
            "👥 Quản lý Nhân sự & Phê duyệt", 
            "📦 Thêm vật liệu Mới", 
            "✏️ Sửa / Xóa vật liệu Hiện tại"
        ])
        
        # --- TAB 1: PHÊ DUYỆT NHÂN SỰ (Creator quản 3 cấp, Boss quản 2 cấp, Admin quản 1 cấp) ---
        with tab_ns:
            st.subheader("Bảng trạng thái nhân sự hiện tại")
            ds_nhan_su = []
            for k, v in st.session_state.users.items():
                ds_nhan_su.append({
                    "Tài khoản": k,
                    "Họ tên": v["name"],
                    "Quyền hạn hệ thống": ROLE_LABELS[v["role"]],
                    "Trạng thái": "🟢 Hoạt động" if v["active"] else "🔴 Đang Khóa/Chờ duyệt"
                })
            st.table(ds_nhan_su)
            
            st.markdown("---")
            st.subheader("Cập nhật quyền & Phê duyệt tài khoản mới")
            
            ds_cho_sua = [
                u for u in st.session_state.users.keys() 
                if u != st.session_state.current_user and st.session_state.users[u]["role"] != "1_creator"

import streamlit as st
from datetime import datetime

# ตั้งค่าหน้าเว็บให้รองรับ Responsive ทุกขนาดจอ (มือถือและ PC)
st.set_page_config(
    hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    page_title="Library Book Borrowing System",
    page_icon="📚",
    layout="centered"
)

st.title("📚 ระบบยืมสมุดและคำนวณค่าปรับเกินเวลา")
st.write("ระบบจัดการห้องสมุด ตรวจสอบสถานะหนังสือ และคำนวณค่าปรับอัตโนมัติ")

# 1. DATABASE & NESTED LIST (เก็บข้อมูลหนังสือ และประวัติการยืม)
if "books_db" not in st.session_state:
    # Nested List: [รหัสหนังสือ, ชื่อหนังสือ, หมวดหมู่, จำนวนคงเหลือ]
    st.session_state.books_db = [
        ["B001", "Python Programming Guide", "Technology", 3],
        ["B002", "Data Science Essentials", "Technology", 2],
        ["B003", "History of Chiang Mai", "History", 5],
        ["B004", "English Grammar in Use", "Education", 1]
    ]

if "borrow_records" not in st.session_state:
    # Nested List: [ชื่อผู้ยืม, รหัสหนังสือ, ชื่อหนังสือ, จำนวนวันที่ยืมจริง, กำหนด (วัน)]
    st.session_state.borrow_records = []

# เมนูหลักทาง Sidebar (Selection Structure จุดที่ 1)
menu = st.sidebar.selectbox("เลือกเมนูการทำงาน", [
    "1. ตรวจสอบหนังสือและยืม",
    "2. คืนหนังสือและคำนวณค่าปรับ",
    "3. รายการประวัติการยืมทั้งหมด"
])

# ==========================================
# 2. USER-DEFINED FUNCTIONS (อย่างน้อย 3 ฟังก์ชัน)
# ==========================================

def check_book_stock(book_id, db):
    """ฟังก์ชันที่ 1: ตรวจสอบว่าหนังสือรหัสนี้มีคงเหลือให้ยืมหรือไม่"""
    # Repetition Structure จุดที่ 1: วนลูปค้นหาหนังสือใน Database
    for book in db:
        if book[0].lower() == book_id.lower():
            if book[3] > 0:
                return True, book[1] # คืนค่าสถานะและชื่อหนังสือ
            else:
                return False, "หนังสือหมดชั่วคราว"
    return False, "ไม่พบรหัสหนังสือนี้ในระบบ"


def calculate_fine(actual_days, due_days):
    """ฟังก์ชันที่ 2: คำนวณค่าปรับกรณีคืนเกินกำหนด (วันละ 5 บาท)"""
    fine_per_day = 5.0
    # Selection Structure จุดที่ 2: ตรวจสอบว่าคืนเกินกำหนดหรือไม่
    if actual_days > due_days:
        late_days = actual_days - due_days
        total_fine = late_days * fine_per_day
        return late_days, total_fine
    else:
        return 0, 0.0


def display_total_records(records):
    """ฟังก์ชันที่ 3: คำนวณและสรุปจำนวนรายการยืมทั้งหมดในระบบ"""
    total = 0
    # Repetition Structure จุดที่ 2: วนลูปนับจำนวนรายการ
    for r in records:
        total += 1
    return total


# ==========================================
# 3. MAIN PROGRAM & LOGIC
# ==========================================

if menu == "1. ตรวจสอบหนังสือและยืม":
    st.header("📖 ค้นหาและทำรายการยืมหนังสือ")
    
    st.subheader("รายการหนังสือในห้องสมุด:")
    # Repetition Structure จุดที่ 3: วนลูปแสดงข้อมูลหนังสือทั้งหมดในรูปแบบตารางย่อย
    for b in st.session_state.books_db:
        st.info(f"รหัส: **{b[0]}** | ชื่อ: **{b[1]}** | หมวดหมู่: {b[2]} | คงเหลือ: `{b[3]} เล่ม`")

    with st.form("borrow_form"):
        st.write("---")
        borrower_name = st.text_input("ชื่อผู้ยืมหนังสือ:")
        selected_id = st.text_input("กรอกรหัสหนังสือที่ต้องการยืม (เช่น B001):")
        borrow_days = st.number_input("จำนวนวันที่ต้องการยืม (กำหนดคืนภายใน 7 วัน):", min_value=1, max_value=1000000, value=7)
        
        submit_borrow = st.form_submit_button("ยืนยันการยืมหนังสือ")
        
        if submit_borrow:
            # Selection Structure จุดที่ 3: ตรวจสอบความถูกต้องของข้อมูลที่กรอก
            if borrower_name.strip() == "" or selected_id.strip() == "":
                st.error("กรุณากรอกชื่อผู้ยืมและรหัสหนังสือให้ครบถ้วน")
            else:
                is_available, book_name = check_book_stock(selected_id, st.session_state.books_db)
                if is_available:
                    # ตัดสต็อกหนังสือใน Nested List
                    for book in st.session_state.books_db:
                        if book[0].lower() == selected_id.lower():
                            book[3] -= 1
                    
                    # บันทึกลงประวัติการยืม
                    st.session_state.borrow_records.append([borrower_name, selected_id.upper(), book_name, borrow_days, 7])
                    st.success(f"ยืมหนังสือ '{book_name}' สำเร็จ! (กำหนดคืนภายใน {borrow_days} วัน)")
                else:
                    st.error(f"ไม่สามารถยืมได้: {book_name}")

elif menu == "2. คืนหนังสือและคำนวณค่าปรับ":
    st.header("🔄 คืนหนังสือและคำนวณค่าปรับเกินเวลา")
    st.write("อัตราค่าปรับ: คืนเกินกำหนดปรับวันละ 5 บาท")

    if len(st.session_state.borrow_records) == 0:
        st.warning("ยังไม่มีรายการยืมหนังสือในระบบ")
    else:
        with st.form("return_form"):
            # ดึงรายชื่อผู้ที่กำลังยืมอยู่มาทำ Dropdown
            borrower_list = [r[0] + " (" + r[2] + ")" for r in st.session_state.borrow_records]
            selected_record = st.selectbox("เลือกรายการที่ต้องการคืน:", borrower_list)
            
            actual_return_days = st.number_input("จำนวนวันที่ผู้ใช้ถือครองหนังสือจริง (วัน):", min_value=1, max_value=1000000, value=7)
            
            submit_return = st.form_submit_button("คำนวณและคืนหนังสือ")
            
            if submit_return:
                # ค้นหาข้อมูลรายการที่เลือก
                idx_to_return = borrower_list.index(selected_record)
                record_data = st.session_state.borrow_records[idx_to_return]
                
                due_limit = record_data[4] # กำหนดมาตรฐาน 7 วัน
                late_days, fine_amount = calculate_fine(actual_return_days, due_limit)
                
                st.write("---")
                st.write(f"ผู้ยืม: **{record_data[0]}**")
                st.write(f"หนังสือ: **{record_data[2]}**")
                
                if late_days > 0:
                    st.error(f"⚠️ คืนเกินกำหนด {late_days} วัน! ต้องชำระค่าปรับเป็นเงิน **{fine_amount:.2f} บาท**")
                else:
                    st.success("🎉 คืนตรงเวลา ไม่มีค่าปรับครับ!")
                
                # คืนสต็อกหนังสือกลับเข้าคลัง
                for book in st.session_state.books_db:
                    if book[0] == record_data[1]:
                        book[3] += 1
                
                # ลบออกจากรายการยืมปัจจุบัน
                st.session_state.borrow_records.pop(idx_to_return)

elif menu == "3. รายการประวัติการยืมทั้งหมด":
    st.header("📊 สรุปรายการยืมหนังสือในระบบปัจจุบัน")
    
    total_active = display_total_records(st.session_state.borrow_records)
    st.metric(label="จำนวนรายการที่กำลังยืมอยู่ทั้งหมด", value=f"{total_active} รายการ")
    
    if total_active > 0:
        st.write("---")
        for idx, rec in enumerate(st.session_state.borrow_records, 1):
            st.write(f"{idx}. คุณ **{rec[0]}** ยืมหนังสือ *{rec[2]}* (รหัส: {rec[1]}) - กำหนดคืนใน {rec[3]} วัน")
    else:
        st.info("ขณะนี้ไม่มีผู้ยืมหนังสือ")

import streamlit as st
import os
import json
import io
import time
from reflection_core import (
    source_part, parse_holidays, validate_weeks, lesson_date,
    format_topic_for_form, render_document,
)
from docxtpl import DocxTemplate
from google import genai
from google.genai import types

# กำหนดรหัสผ่านสำหรับปลดล็อกระบบ
SYSTEM_PASSCODE = os.environ.get("SYSTEM_PASSCODE", "1234")

st.set_page_config(
    page_title="ระบบบันทึกหลังการสอน อาชีวศึกษา",
    page_icon="🐣",
    layout="wide",
)

# สไตล์หน้าจอหลัก
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700&display=swap');
:root {
    --ink: #18324a;
    --muted: #64788a;
    --line: #dbe5ea;
    --surface: #ffffff;
    --canvas: #f3f7f8;
    --teal: #087f8c;
    --teal-dark: #05616b;
    --teal-soft: #e5f4f3;
}
html, body, [data-testid="stAppViewContainer"], input, button, textarea, label, h1, h2, h3, p {
    font-family: 'Noto Sans Thai', sans-serif !important;
}
body, [data-testid="stAppViewContainer"] {background-color:var(--canvas); color:var(--ink);
    background-image:linear-gradient(rgba(8,127,140,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(8,127,140,.035) 1px, transparent 1px);
    background-size:36px 36px;}
.block-container {max-width:1400px; padding-top:1.5rem; padding-bottom:2.5rem;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stToolbar"] {visibility:hidden;}
.main-header {background:#123f4b; color:white; padding:2.1rem 2.35rem; border-radius:12px;
    margin-bottom:1.8rem; border-left:6px solid #55c5bb; position:relative; overflow:hidden;
    box-shadow:0 12px 30px rgba(24,50,74,.10);}
.main-header:after {content:""; position:absolute; right:-70px; top:-130px; width:300px; height:300px;
    border:1px solid rgba(150,235,222,.28); transform:rotate(35deg); pointer-events:none;}
.main-header h1 {color:white !important; font-size:clamp(1.55rem,2.4vw,2.25rem); line-height:1.45; font-weight:700; margin:0 0 .45rem; position:relative; z-index:1;}
.login-header h1 {font-size:clamp(1.86rem,2.88vw,2.7rem);}
.login-header h1 {text-align:center;}
.centered-header h1 {text-align:center;}
.main-header p {color:#c9e9e5 !important; font-size:15px; line-height:1.8; margin:0; position:relative; z-index:1;}
.eyebrow {color:#91e0d5; font-size:11px; letter-spacing:1.8px; font-weight:700; margin-bottom:.55rem;}
h2, h3 {color:var(--ink) !important; font-size:1.08rem !important; line-height:1.6 !important; letter-spacing:0 !important;}
[data-testid="stSidebar"] {background:var(--surface); border-right:1px solid var(--line);}
[data-testid="stSidebar"] > div:first-child {padding-top:1.25rem;}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {margin-top:.7rem;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:10px; border-color:var(--line);}
[data-testid="stFileUploader"] {background:var(--surface); border:1px solid var(--line); padding:12px; border-radius:10px;}
[data-testid="stFileUploaderDropzone"] {background:#f8fbfb; border:1px dashed #b8d8d7; border-radius:8px;}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {font-size:15px; border-color:#cbd9df; border-radius:8px; background:#fff;}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {border-color:var(--teal); box-shadow:0 0 0 1px var(--teal);}
[data-testid="stTextInput"]:has(input[aria-label="กรอกรหัสเข้าใช้งาน :"]) label {font-size:20.4px !important; font-weight:600;}
[data-testid="stTextInput"]:has(input[aria-label="กรอกรหัสเข้าใช้งาน :"]) input {font-size:21.6px !important; min-height:48px;}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {border-color:#cbd9df; border-radius:8px;}
.stButton > button[kind="primary"], .stDownloadButton > button {background:var(--teal); color:white; border:0; min-height:46px; border-radius:8px; font-weight:600; box-shadow:0 5px 12px rgba(8,127,140,.16);}
.stButton > button {min-height:42px; border-radius:8px; border-color:#cbd9df; color:var(--ink); font-weight:500;}
.stButton > button:hover {border-color:var(--teal); color:var(--teal-dark);}
.stButton > button[kind="primary"]:hover {background:var(--teal-dark); color:white;}
.badge-tag {display:inline-block; background:var(--teal-soft); color:var(--teal-dark); padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600; margin-bottom:1rem;}
.footer-box {text-align:center; padding:20px 12px; margin-top:2rem; border-top:1px solid var(--line); color:var(--muted); font-size:12px; line-height:1.9;}
.footer-badge {color:var(--teal-dark); font-size:11px; font-weight:700; letter-spacing:1px;}
[data-testid="stMetric"] {background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:14px 18px; box-shadow:0 5px 16px rgba(24,50,74,.04);}
[data-testid="stMetricLabel"] {color:var(--muted);}
[data-testid="stMetricValue"] {color:var(--ink); font-size:1.35rem;}
[data-testid="stAlert"] {border-radius:8px;}
.api-panel h3 {margin:0 0 .35rem !important;}
.top-panel-title {text-align:center; color:var(--ink); font-size:1.08rem; font-weight:700; line-height:1.6; margin-bottom:.35rem;}
.section-heading {display:flex; align-items:center; gap:.55rem; margin:0 0 1rem; padding:.65rem .85rem;
    background:linear-gradient(90deg, #e5f4f3 0%, rgba(229,244,243,.28) 72%, transparent 100%);
    border-left:4px solid var(--teal); border-bottom:1px solid #cce5e2; border-radius:0 6px 6px 0;
    color:var(--teal-dark); font-size:1.08rem; font-weight:700; line-height:1.6;}
.api-panel-caption {color:var(--muted); font-size:12px; line-height:1.7; margin-bottom:.5rem;}
.workflow-strip {height:100%; padding:1.1rem 1.25rem; background:#eaf5f4; border:1px solid #cce5e2; border-radius:10px;}
.workflow-strip strong {display:block; color:var(--teal-dark); font-size:14px; margin-bottom:.35rem;}
.workflow-strip span {color:var(--muted); font-size:13px; line-height:1.8;}
.api-loading {position:fixed; right:24px; bottom:24px; z-index:9999; display:flex; align-items:center; gap:10px;
    padding:10px 14px; background:#ffffff; color:var(--ink); border:1px solid var(--line); border-radius:10px;
    box-shadow:0 8px 24px rgba(24,50,74,.16); font-size:13px; font-weight:600;}
.api-loading-icon {width:18px; height:18px; border:3px solid #c9e9e5; border-top-color:var(--teal);
    border-radius:50%; animation:api-spin .8s linear infinite;}
.api-loading-dots {display:inline-flex; gap:3px; margin-left:-5px;}
.api-loading-dots span {width:3px; height:3px; background:var(--teal); border-radius:50%; animation:api-pulse 1s infinite ease-in-out;}
.api-loading-dots span:nth-child(2) {animation-delay:.15s;}
.api-loading-dots span:nth-child(3) {animation-delay:.3s;}
@keyframes api-spin {to {transform:rotate(360deg);}}
@keyframes api-pulse {0%, 80%, 100% {opacity:.25; transform:translateY(0);} 40% {opacity:1; transform:translateY(-2px);}}
@media(max-width:640px) {.block-container {padding:1rem .8rem 2rem;} .main-header {padding:1.5rem 1.25rem;} .main-header h1 {font-size:1.5rem;} .login-header h1 {font-size:1.8rem;} .main-header p {font-size:14px;} }
</style>
""", unsafe_allow_html=True)

# ระบบตรวจสอบรหัสผ่านปลดล็อก
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="main-header login-header">
        <h1>บันทึกหลังการสอน<br/>ผู้ช่วย AI สำหรับครูอาชีวศึกษา</h1>
        <p style="text-align:center;">.............................................</p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        
      
        pass_input = st.text_input("กรอกรหัสเข้าใช้งาน :", type="password", placeholder="..............")
        if st.button("เข้าสู่ระบบ →", use_container_width=True, type="primary"):
            if pass_input == SYSTEM_PASSCODE:
                st.session_state.authenticated = True
                st.success("✅  กำลังเข้าสู่ระบบ...")
                st.rerun()
            else:
                st.error("❌ รหัสผ่านไม่ถูกต้อง กรุณาติดต่อเจ้าของระบบ")


        st.markdown("""
        <div class="footer-box" style="margin-top: 20px;">
            <div class="footer-badge">🛡️ PROPRIETARY SOFTWARE</div><br/>
             พัฒนาโดย <b>นายวัชรพงษ์ สุขแช่ม</b> ครู วิทยาลัยเทคนิคจันทบุรี
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ข้อมูลปฏิทินและแผนกวิชา
THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
DAY_NAMES = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
DEPARTMENT_OPTIONS = [
    "เทคโนโลยีสารสนเทศ",
    "เทคโนโลยีธุรกิจดิจิทัล",
    "อื่นๆ (ระบุเอง)"
]
DEFAULT_TEACHER_NAME = " "
DEFAULT_DEPARTMENT = "เทคโนโลยีสารสนเทศ"

st.markdown("""
<div class="main-header centered-header">
    <h1>จัดทำบันทึกหลังการสอน</h1>
    <p style="text-align:center;">แนบโครงการสอน กำหนดตารางเรียน แล้วสร้างร่างบันทึกในแบบฟอร์ม Word </p>
</div>
""", unsafe_allow_html=True)

top_api, top_workflow = st.columns(2, gap="large")
with top_api:
    with st.container(border=True):
        st.markdown('<div class="api-panel">', unsafe_allow_html=True)
        st.markdown('<div class="top-panel-title">🔑 Gemini API Key</div>', unsafe_allow_html=True)
        st.markdown('<div class="api-panel-caption" style="text-align:center;">ใส่ API Key แล้วกด บันทึก ก่อนสร้างเอกสาร</div>', unsafe_allow_html=True)
        api_key_input = st.text_input(
            "API Key", type="password", placeholder="วาง API Key ของคุณ",
            label_visibility="collapsed", key="gemini_api_key"
        )
        if st.button("บันทึก", key="confirm_api_key", use_container_width=True):
            confirmed_api_key = api_key_input.strip()
            if not confirmed_api_key:
                st.warning("กรุณาใส่ API Key")
            else:
                st.session_state.confirmed_gemini_api_key = confirmed_api_key
                st.success("บันทึก API Key แล้ว")
        st.markdown('<a href="https://aistudio.google.com/apikey" target="_blank">กดเพื่อรับ Gemini API Key </a></div>', unsafe_allow_html=True)

with top_workflow:
    with st.container(border=True):
        st.markdown('<div class="api-panel">', unsafe_allow_html=True)
        st.markdown('<div class="top-panel-title">😾 ข้อมูลครูผู้สอน</div>', unsafe_allow_html=True)
        teacher_name = st.text_input("ชื่อ-สกุลครูผู้สอน (ตัวอย่าง นายรักเรียน เขียนดี):", value=DEFAULT_TEACHER_NAME)
        dept_choice = st.selectbox(
            "สาขาวิชา / แผนกวิชา:",
            DEPARTMENT_OPTIONS,
            index=DEPARTMENT_OPTIONS.index(DEFAULT_DEPARTMENT)
        )
        if dept_choice == "อื่นๆ (ระบุเอง)":
            department = st.text_input("ระบุสาขาวิชาของคุณ:", value="")
        else:
            department = dept_choice
        st.markdown('</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="section-heading">📚 แบบฟอร์มและโครงการสอน</div>', unsafe_allow_html=True)
    tpl_file = st.file_uploader("📄 แนบแบบฟอร์มวิทยาลัย (template.docx):", type=["docx"])
    uploaded_file = st.file_uploader("📚 แนบไฟล์โครงการสอน (PDF, Word, TXT, รูปภาพ):", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

with col2:
    st.markdown('<div class="section-heading">เลือกระดับชั้น (คำนวณวันหยุดอัตโนมัติตามปฏิทิน)</div>', unsafe_allow_html=True)
    c_deg, c_yr = st.columns(2)
    with c_deg:
        degree = st.selectbox("ระดับ:", ["ปวช.", "ปวส."])
    with c_yr:
        if degree == "ปวช.":
            year_num = st.selectbox("ชั้นปี:", ["1", "2", "3"])
            target_weeks = 18
        else:
            year_num = st.selectbox("ชั้นปี:", ["1", "2"])
            target_weeks = 15

    class_level = f"{degree} {year_num}"
    st.markdown(f"ระดับ: **{class_level}** | สาขา: **{department}** | กำหนดอัตโนมัติ: **{target_weeks} สัปดาห์**")
    st.markdown('<div class="section-heading">🗓️ ตารางสอน</div>', unsafe_allow_html=True)
    slots_count = st.selectbox(
        "จำนวนวันสอนใน 1 สัปดาห์ :",
        options=[1, 2, 3, 4],
        format_func=lambda x: f"สอน {x} วัน / สัปดาห์",
        index=0
    )

    slots_info = []
    default_days = [0, 1, 2, 3]
    time_options = [f"{hour:02d}.30" for hour in range(8, 18)]
    default_times = [("15.30", "16.30"), ("08.30", "10.30"), ("10.30", "12.30"), ("13.30", "15.30")]

    for i in range(slots_count):
        st.markdown(f"**💻 รายละเอียด {i+1}:**")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            d_val = st.selectbox(f"วัน ( {i+1}):", DAY_NAMES, index=default_days[i % len(default_days)], key=f"day_slot_{i}")
        with sc2:
            default_start, default_end = default_times[i]
            start_time = st.selectbox(
                f"เวลาเริ่มต้น ( {i+1}):", time_options[:-1],
                index=time_options.index(default_start), key=f"start_time_slot_{i}"
            )
        with sc3:
            end_options = time_options[time_options.index(start_time) + 1:]
            end_key = f"end_time_slot_{i}"
            if st.session_state.get(end_key) not in end_options:
                st.session_state[end_key] = default_end if default_end in end_options else end_options[0]
            end_time = st.selectbox(
                f"เวลาสิ้นสุด ( {i+1}):", end_options, key=end_key
            )
        t_val = f"{start_time}-{end_time} น."
        slots_info.append({"day": d_val, "time": t_val})

    start_date = st.date_input(
        "📅 วันที่เริ่มรอบสัปดาห์ที่ 1:",
        format="DD/MM/YYYY",
    )
    st.caption(
        f"วันที่เลือก: {start_date.day:02d}/{start_date.month:02d}/{start_date.year + 543}"
    )

    st.caption("แต่ละสัปดาห์นับ 7 วันจากวันที่นี้ คาบแรกจะไม่อยู่ก่อนวันเริ่มต้น")
    holiday_text = "8:ตรงกับวันหยุดนักขัตฤกษ์ตามประกาศสถานศึกษา"

def format_thai_date(dt):
    d = dt.day
    m = THAI_MONTHS[dt.month]
    y = dt.year + 543
    day_name = DAY_NAMES[dt.weekday()]
    return f"{day_name} {d} {m} {y}"

action_left, action_center, action_right = st.columns([1, 2, 1])
with action_center:
    st.markdown('<div style="text-align:center;">AI ช่วยจัดทำร่างจากโครงการสอน</div>', unsafe_allow_html=True)
    generate_clicked = st.button(
        f"สร้างร่างบันทึก {target_weeks} สัปดาห์ →",
        use_container_width=True,
        type="primary"
    )

if generate_clicked:
    st.session_state.pop("generated_document", None)
    api_key = st.session_state.get("confirmed_gemini_api_key", "")
    if not api_key:
        st.warning("⚠️ กรุณากรอก Gemini API Key แล้วกด บันทึก ที่แถบด้านซ้ายก่อนเริ่มใช้งาน")
        st.stop()
    if not tpl_file:
        st.warning("⚠️ กรุณาแนบไฟล์ template.docx ของวิทยาลัย")
        st.stop()
    if not uploaded_file:
        st.warning("⚠️ กรุณาแนบไฟล์โครงการสอน")
        st.stop()
    if not department.strip():
        st.warning("⚠️ กรุณาระบุสาขาวิชา/แผนกวิชา")
        st.stop()

    progress_bar = st.progress(0)
    status_text = st.empty()
    loading_popup = st.empty()
    loading_popup.markdown("""
    <div class="api-loading" role="status" aria-label="กำลังประมวลผล">
        <span class="api-loading-icon"></span>
        <span>กำลังประมวลผล</span>
        <span class="api-loading-dots"><span></span><span></span><span></span></span>
    </div>
    """, unsafe_allow_html=True)

    try:
        status_text.text("🤖 กำลังส่งข้อมูลให้ Gemini AI วิเคราะห์โครงการสอนตามหลักวิชาการอาชีวศึกษา...")
        client = genai.Client(api_key=api_key)
        holidays = parse_holidays(holiday_text, target_weeks)
        if not teacher_name.strip():
            raise ValueError("กรุณากรอกชื่อครูผู้สอน")
        attachment = source_part(uploaded_file.name, uploaded_file.getvalue())
        template_check = DocxTemplate(io.BytesIO(tpl_file.getvalue()))
        if not template_check.get_undeclared_template_variables():
            raise ValueError("ไม่พบช่องแทนค่าในแบบฟอร์ม Word กรุณาตรวจสอบ template.docx")

        prompt = f"""
         คุณคือผู้เชี่ยวชาญด้านหลักสูตรและการจัดการเรียนรู้อาชีวศึกษา (สอศ.)
        จงวิเคราะห์เนื้อหาโครงการสอนที่แนบมานี้ เพื่อจัดทำ "บันทึกหลังการจัดการเรียนรู้" ระดับชั้น {class_level}
        ให้ครบถ้วนตั้งแต่สัปดาห์ที่ 1 ถึงสัปดาห์ที่ {target_weeks} (รวม {target_weeks} สัปดาห์พอดี ห้ามขาด)
        ข้อมูลวันหยุด/งดสอน: {holiday_text}

        เกณฑ์การเขียนเชิงวิชาการที่เข้มข้น สมบูรณ์ และมีมิติ (ความยาวพอเหมาะ ไม่สั้นเกินไปและไม่ล้นหน้า):
        1. topic: ระบุชื่อหน่วยการเรียนรู้และหัวข้อการเรียนรู้แบบกระชับ ไม่เกิน 3 บรรทัด
        2. student_eval: ประเมินผลการเรียนรู้ของผู้เรียนอย่างเป็นรูปธรรม แยกมิติ K-P-A:
           - ด้านความรู้ (K): ผู้เรียนมีความรู้ความเข้าใจในเนื้อหาผ่านเกณฑ์การประเมิน
           - ด้านทักษะ/กระบวนการ (P): ผู้เรียนสามารถฝึกปฏิบัติงาน/ใบงานได้ถูกต้องตามขั้นตอน
           - ด้านคุณลักษณะ (A): ผู้เรียนมีวินัย ความรับผิดชอบ และความตรงต่อเวลา
           - สรุปตัวเลข: "มีผู้เรียนผ่านเกณฑ์การประเมินร้อยละ 85 ขึ้นไป (หรือสอดคล้องกับแต่ละสัปดาห์)"
        3. teacher_eval: ผลการสอนของครู เน้นการจัดการเรียนรู้เชิงรุก (Active Learning):
           - ระบุเทคนิคการสอน เช่น การจัดการเรียนรู้โดยใช้ปัญหาเป็นฐาน (Problem-based Learning), การสาธิตร่วมกับฝึกปฏิบัติ (Demonstration & Practice), การใช้เทคโนโลยีเป็นฐาน
           - สื่อและนวัตกรรม: ระบุสื่อการสอน สื่อดิจิทัล ใบความรู้ ใบงานที่ใช้จริง
           - การวัดและประเมินผล: ประเมินตามสภาพจริงผ่านแบบสังเกตพฤติกรรมและแบบประเมินผลงาน
        4. problem_solution: ปัญหา อุปสรรค และแนวทางแก้ไขตามวงรอบคุณภาพ (PDCA):
           - ปัญหา: ระบุปัญหาจริง เช่น ผู้เรียนบางคนยังขาดทักษะพื้นฐาน หรือสับสนขั้นตอนปฏิบัติ
           - แนวทางแก้ไข: ระบุการสอนเสริม (Coaching) รายบุคคล, การจัดกลุ่มเพื่อนช่วยเพื่อน, มอบหมายใบงานซ่อมเสริมเพื่อพัฒนาสมรรถนะ

        ส่งออกเป็น Pure JSON โครงสร้างนี้เท่านั้น:
        {{
            "code": "รหัสวิชา",
            "subject": "ชื่อวิชา",
            "weeks": [
                {{
                    "week": 1,
                    "topic": "ชื่อหน่วยและเรื่องที่จัดการเรียนรู้",
                    "is_holiday": false,
                    "off_reason": "-",
                    "student_eval": "ข้อความประเมินผู้เรียนครบ K P A และร้อยละที่ผ่าน",
                    "teacher_eval": "ข้อความการสอนเชิงรุก Active Learning สื่อ และการประเมิน",
                    "problem_solution": "ข้อความปัญหาและแนวทางแก้ไขเชิงรูปธรรม"
                }}
            ]
        }}
        ห้ามใส่เครื่องหมาย markdown block ส่งเฉพาะ Pure JSON เท่านั้น
      
        """

        models_to_try = [
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite"
        ]
        response = None
        last_error = None

        for target_m in models_to_try:
            status_text.markdown(
                f'<div style="text-align:center;">⏳⏳ กำลังประมวลผลด้วยโมเดล {target_m}... 🐱🐱🐱🐱🐱🐱🐱 </div>',
                unsafe_allow_html=True,
            )
            try:
                response = client.models.generate_content(
                    model=target_m,
                    contents=[
                        attachment,
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.25
                    )
                )
                if response and response.text:
                    break
            except Exception as err:
                last_error = err
                time.sleep(1)

        if not response or not response.text:
            raise Exception(f"ไม่สามารถเชื่อมต่อโมเดลได้: {last_error}")

        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        data = json.loads(clean_text)
        course_code = data.get("code", "วิชา")
        course_name = data.get("subject", "โครงการสอน")

        final_weeks = validate_weeks(data, target_weeks, holidays)
        tpl_bytes = tpl_file.getvalue()
        contexts = []
        total_count = len(final_weeks)
        day_map = {name: idx for idx, name in enumerate(DAY_NAMES)}

        for idx, w in enumerate(final_weeks):
            progress_bar.progress(int(((idx + 1) / total_count) * 100))
            status_text.text(f"📝 กำลังลงข้อมูลสัปดาห์ที่ {w.get('week')} ในแบบฟอร์มวิทยาลัย...")

            week_num = w.get("week", idx + 1)

            date_lines = []
            time_lines = []
            seen_days = set()
            for slot in slots_info:
                if not slot["day"]:
                    time_lines.append("")
                    continue
                t_wday = day_map.get(slot["day"], 0)
                dt_slot = lesson_date(start_date, week_num, t_wday)
                if slot["day"] not in seen_days:
                    date_lines.append(format_thai_date(dt_slot))
                seen_days.add(slot["day"])
                time_lines.append(f"เวลา {slot['time']}")

            date_display = "\n".join(date_lines)
            time_display = "\n".join(time_lines)

            is_hol = w.get("is_holiday", False)
            context_w = {
                "code": course_code,
                "subject": course_name,
                "week": week_num,
                "date": date_display,
                "date_display": date_display,
                "time": time_display,
                "time_display": time_display,
                "topic": format_topic_for_form(w.get("topic")),
                "level": class_level,
                "department": department,
                "check_on": "☑" if not is_hol else "☐",
                "check_off": "☑" if is_hol else "☐",
                "off_reason": w.get("off_reason", "-") if is_hol else "-",
                "student_eval": w.get("student_eval"),
                "teacher_eval": w.get("teacher_eval"),
                "problem_solution": w.get("problem_solution"),
            }

            contexts.append({"teacher_name": teacher_name, "w": context_w, **context_w})

        output_bytes = render_document(tpl_bytes, contexts)
        st.session_state.generated_document = {
            "content": output_bytes,
            "name": f"บันทึกหลังการสอน_{class_level.replace(' ', '')}_{target_weeks}สัปดาห์.docx",
            "weeks": target_weeks,
        }
        progress_bar.progress(100)
        status_text.empty()
        loading_popup.empty()

    except Exception as e:
        status_text.empty()
        loading_popup.empty()
        st.error(f"สร้างเอกสารไม่สำเร็จ: {str(e).replace(api_key, '[hidden]')}")

if "generated_document" in st.session_state:
    result = st.session_state.generated_document
    with action_center:
        st.markdown(
            f'<div style="text-align:center;">สร้างร่างบันทึกครบ {result["weeks"]} สัปดาห์แล้ว กรุณาตรวจเนื้อหาและการแบ่งหน้าใน Word</div>',
            unsafe_allow_html=True
        )
        st.download_button(
            "ดาวน์โหลดบันทึก Word ↓",
            data=result["content"],
            file_name=result["name"],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

# กล่องข้อมูลลิขสิทธิ์และผู้พัฒนาระบบด้านล่างสุด
st.markdown("""
<div class="footer-box">



</div>
""", unsafe_allow_html=True)

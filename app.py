import streamlit as st
from groq import Groq 
import pypdf
from fpdf import FPDF

st.set_page_config(page_title="Vetly AI", page_icon="🎯", layout="wide")
st.title("🎯 Vetly AI")
st.subheader("منظومة التقييم الفني المتقدم وتوليد أدلة المقابلات التنفيذية")

try:
    client = Groq(api_key=st.secrets["API_e"])
except Exception as e:
    st.error("خطأ تكتيكي: المتغير السري API_e غير معرف في الـ Secrets!")
    st.stop()

def extract_text_from_pdf(pdf_file):
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except:
        return ""

def generate_pdf_report(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    pdf.set_font("Helvetica", size=12)
    
    lines = report_text.split('\n')
    for line in lines:
        # استبدال الإيموجي أو الرموز الغريبة لضمان عدم تعطل دالة fpdf
        clean_line = line.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_line)
        pdf.ln(2)
        
    return pdf.output(dest='S')

st.sidebar.header("🛠️ معايير تقييم المقابلة")
job_description = st.sidebar.text_area("وصف متطلبات الوظيفة المستهدفة (Job Description):", 
                                       placeholder="أدخل المهام والخبرات المطلوبة للوظيفة هنا...")

num_questions = st.sidebar.slider("عدد الأسئلة المطلوبة لكل مرشح:", min_value=1, max_value=10, value=3)
difficulty_level = st.sidebar.selectbox("مستوى عمق الأسئلة الفنية:", 
                                         ["تقييم أساسي ومتدرج", "تقييم متوسط لكشف الفهم", "تقييم متقدم وعميق جداً"])

if "cv_count" not in st.session_state:
    st.session_state.cv_count = 1

st.write("### 👥 السير الذاتية للمرشحين المستهدفين")
candidates_data = []

for i in range(st.session_state.cv_count):
    col1, col2 = st.columns(2)
    with col1:
        c_name = st.text_input(f"اسم المرشح #{i+1}", value=f"مرشح {i+1}", key=f"name_{i}")
    with col2:
        c_file = st.file_uploader(f"ارفع ملف الـ PDF للمرشح #{i+1}", type=["pdf"], key=f"file_{i}")
    candidates_data.append({"name": c_name, "file": c_file})
    st.divider()

if st.button("➕ إضافة مرشح آخر للمقابلة المتقاطعة"):
    st.session_state.cv_count += 1
    st.rerun()

if st.button("🔥 هندسة دليل المقابلة التنفيذي"):
    if not job_description:
        st.warning("الرجاء إدخال وصف الوظيفة أولاً في اللوحة الجانبية.")
    else:
        full_report_content = "VETLY AI - EXECUTIVE INTERVIEW GUIDE\n=================================\n\n"
        
        system_instruction = """
        أنت مستشار توظيف تقني أول ومسؤول الفرز الفني في كبرى مجموعات الاستثمار العالمية. مهمتك هي تحليل السيرة الذاتية بدقة ومقارنتها بالوظيفة، واستخراج أسئلة فنية عميقة ومباغتة (Structural Interview Questions) لكشف عمق المعرفة الحقيقية للمرشح وتحديد ما إذا كان يملك خبرة عملية فعلية أم مجرد معلومات سطحية.
        اجعل أسلوب الصياغة احترافياً، صارماً، وخالياً تماماً من الألفاظ الطفولية أو الكلمات الهزلية مثل 'فخ'. قدم السؤال الفني متبوعاً مباشرة بالإجابة النموذجية القاطعة المختصرة التي تثبت كفاءة المرشح.
        """
        
        for person in candidates_data:
            if person["file"] is not None:
                with st.spinner(f"جاري فرز الـ PDF وهندسة التقارير لـ {person['name']}..."):
                    cv_text = extract_text_from_pdf(person["file"])
                    
                    if not cv_text:
                        st.error(f"فشل استخراج النص من ملف {person['name']}.")
                        continue
                    
                    user_instruction = f"""
                    قم بتوليد عدد ({num_questions}) أسئلة فنية متقدمة بمستوى ({difficulty_level}).
                    
                    المرشح: {person['name']}
                    السيرة الذاتية المستخرجة: {cv_text}
                    متطلبات الوظيفة: {job_description}
                    
                    التنسيق المطلق للمخرجات (باللغة العربية الاحترافية):
                    Candidate: [اسم المرشح]
                    Question [الرقم]: [نص السؤال الفني المتقدم]
                    Model Answer: [الرد التقني الحاسم المتوقع]
                    """
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1
                    )
                    
                    result_text = chat_completion.choices[0].message.content
                    st.info(result_text)
                    full_report_content += result_text + "\n\n"
                    
        st.success("تم توليد التقييم الفني بنجاح!")
        
        st.write("#### 📥 تحميل دليل المقابلة الرسمي")
        try:
            pdf_data = generate_pdf_report(full_report_content)
            st.download_button(
                label="📥 تحميل مستند التقييم بصيغة PDF",
                data=pdf_data,
                file_name="Vetly_Interview_Guide.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error("حدث خطأ أثناء إعداد ملف الـ PDF، يرجى مراجعة تنسيق النصوص المخرجة.")

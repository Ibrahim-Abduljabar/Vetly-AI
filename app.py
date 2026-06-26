import streamlit as st
from groq import Groq 
import pypdf

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
        st.write("### 🎯 دليل الأسئلة المخفية الجاهز للمدير:")
        
        system_instruction = """
        أنت مستشار توظيف تقني أول ومسؤول الفرز الفني في كبرى الشركات العالمية. مهمتك هي تحليل السيرة الذاتية بدقة ومقارنتها بالوظيفة، واستخراج أسئلة فنية عميقة ومباغتة لكشف عمق المعرفة الحقيقية للمرشح وتحديد ما إذا كان يملك خبرة عملية فعلية أم مجرد معلومات سطحية.
        اجعل أسلوب الصياغة احترافياً، صارماً، وبنبرة عسكرية تقنية جادة باللغة العربية.
        قدم السؤال الفني متبوعاً مباشرة بالإجابة النموذجية القاطعة المختصرة التي تثبت كفاءة المرشح.
        """
        
        for person in candidates_data:
            if person["file"] is not None:
                with st.spinner(f"جاري فرز الـ PDF وهندسة التقارير لـ {person['name']}..."):
                    cv_text = extract_text_from_pdf(person["file"])
                    
                    if not cv_text:
                        st.error(f"فشل استخراج النص من ملف {person['name']}.")
                        continue
                    
                    user_instruction = f"""
                    قم بتوليد عدد ({num_questions}) أسئلة فنية متقدمة بمستوى ({difficulty_level}) للمرشح ({person['name']}).
                    بناءً على السيرة الذاتية المستخرجة من الـ PDF: {cv_text}
                    ومتطلبات الوظيفة: {job_description}
                    
                    التنسيق الصارم للمخرجات باللغة العربية (ابدأ باسم المرشح):
                    👤 اسم المرشح: [اسم المرشح]
                    
                    ❓ السؤال [الرقم]: [نص السؤال الفني المتقدم والمباغت]
                    💡 الإجابة النموذجية المتوقعة: [الجواب التقني الحاسم وعميق]
                    """
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1
                    )
                    
                    st.info(chat_completion.choices[0].message.content)
                    
        st.success("تم توليد التقييم الفني بنجاح! الأداة مفتوحة لك مجاناً بالكامل.")

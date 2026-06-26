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
        أنت مستشار توظيف تقني أول ومسؤول الفرز الفني في كبرى الشركات العالمية. مهمتك هي تحليل السيرة الذاتية بدقة ومقارنتها بالوظيفة، واستخراج أسئلة فنية عميقة ومباغتة لكشف خبرة المرشح الحقيقية.
        يجب أن تصيغ مخرجاتك مباشرة ككود HTML منسق ومقفل بالكامل يحتوي على تصميم بطاقة تدعم اللغة العربية من اليمين إلى اليسار (RTL).
        
        استخدم هذا الهيكل تماماً لكل مرشح واطبعه ككود HTML جاهز دون كتابة أي كلمات ترحيبية خارجه:
        <div style="background-color: #f8f9fa; border-right: 5px solid #007bff; padding: 20px; border-radius: 5px; margin-bottom: 25px; direction: rtl; text-align: right; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
           <h3 style="color: #007bff; font-size: 22px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #dee2e6; padding-bottom: 5px;">👤 المرشح: [اسم المرشح]</h3>
           
           <div style="background-color: #ffffff; padding: 12px; border-radius: 4px; margin-bottom: 10px; border: 1px solid #e9ecef;">
               <p style="font-weight: bold; color: #212529; margin-bottom: 5px; font-size: 16px;">❓ السؤال [الرقم]: [نص السؤال الفني المتقدم]</p>
               <p style="color: #28a745; font-weight: 500; font-size: 15px; font-style: italic;">💡 الإجابة النموذجية المتوقعة: [الرد التقني الحاسم وعميق]</p>
           </div>
        </div>
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
                    
                    تذكر: صغ المخرجات بكود الـ HTML المنسق المذكور في النظام تماماً، ولا تكتب أي نصوص أخرى خارج وسوم الـ HTML.
                    """
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1
                    )
                    
                    html_content = chat_completion.choices[0].message.content
                    st.markdown(html_content, unsafe_allow_html=True)
                    
        st.success("تم توليد التقييم الفني بنجاح! يمكنك الآن الضغط على (Ctrl + P) لطباعة الدليل أو حفظه كـ PDF من متصفحك مباشرة بشكل منسق!")

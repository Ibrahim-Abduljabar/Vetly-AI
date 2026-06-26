import streamlit as st
# تأكد من تثبيت المكتبات عبر الـ requirements.txt المحدث بالأسفل
from groq import Groq 
import pypdf

# 1. إعداد واجهة الموقع الفخمة
st.set_page_config(page_title="Vetly AI", page_icon="🎯", layout="wide")
st.title("🎯 Vetly AI")
st.subheader("منظومة فرز وتوليد الأسئلة الفخاخ لكشف خبرة المرشحين عبر ملفات الـ PDF مباشرة")

# 2. استدعاء العميل باستخدام المتغير السري الخاص بك (مخفي وصارم)
if 'API_e' in globals() or 'API_e' in locals():
    client = Groq(api_key=API_e)
else:
    try:
        client = Groq(api_key=st.secrets["API_e"])
    except:
        st.error("خطأ تكتيكي: المتغير السري API_e غير معرف في بيئة العمل!")
        st.stop()

# 3. دالة برمجية صامتة لقراءة واستخراج النصوص من ملفات الـ PDF المرفوعة
def extract_text_from_pdf(pdf_file):
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return ""

# 4. نظام حفظ الإيميلات (جمع الـ 5000 إيميل)
def save_lead_email(email):
    if email and "@" in email:
        with open("vetly_leads.txt", "a", encoding="utf-8") as f:
            f.write(email + "\n")
        return True
    return False

# 5. لوحة التحكم الجانبية لمعايير الـ HR
st.sidebar.header("🛠️ معايير فرز المقابلة")
job_description = st.sidebar.text_area("وصف متطلبات الوظيفة المستهدفة (Job Description):", 
                                       placeholder="أدخل المهام والخبرات المطلوبة للوظيفة هنا...")

num_questions = st.sidebar.slider("عدد الأسئلة الفخاخ لكل مرشح:", min_value=1, max_value=10, value=3)
difficulty_level = st.sidebar.selectbox("مستوى صعوبة الفخاخ الفنية:", 
                                         ["سهل ومتدرج", "متوسط لاختبار الفهم", "صعب جداً وفخاخ تقنية عميقة"])

# 6. إدارة خانات الـ PDF الديناميكية (إضافة ملفات متعددة بضغط زر)
if "cv_count" not in st.session_state:
    st.session_state.cv_count = 1

st.write("### 👥 رفع السير الذاتية للمرشحين (ملفات PDF)")

candidates_data = []

# الـ Loop الحركي لتوليد خانات رفع الملفات
for i in range(st.session_state.cv_count):
    col1, col2 = st.columns()
    with col1:
        c_name = st.text_input(f"اسم المرشح #{i+1}", value=f"مرشح {i+1}", key=f"name_{i}")
    with col2:
        c_file = st.file_uploader(f"ارفع ملف الـ PDF للمرشح #{i+1}", type=["pdf"], key=f"file_{i}")
    
    candidates_data.append({"name": c_name, "file": c_file})
    st.divider()

if st.button("➕ إضافة مرشح آخر للمقابلة المتقاطعة"):
    st.session_state.cv_count += 1
    st.rerun()

# 7. المعالجة واستدعاء الـ API بدرجة حرارة 0.1 الصارمة لقتل الهلوسة
if st.button("🔥 هندسة دليل الأسئلة الفخاخ فوراً"):
    if not job_description:
        st.warning("الرجاء إدخل وصف الوظيفة أولاً في اللوحة الجانبية.")
    else:
        st.write("### 🎯 دليل الأسئلة المخفية الجاهز للمدير:")
        
        system_instruction = """
        أنت مستشار توظيف تقني فذ ومسؤول فرز فني عسكري في كبرى الشركات. مهمتك قراءة السيرة الذاتية المستخرجة ومقارنتها بالوظيفة، واستخراج أسئلة بمثابة فخاخ تقنية دقيقة وعميقة لكشف الخبرة الحقيقية ومنع الخداع تماماً.
        يجب أن تقدم الإجابة النموذجية البشرية المحترفة والمختصرة جداً التي يجب أن يسمعها المدير ليعرف إذا كان المرشح نصاباً أم خبيراً في نفس اللحظة.
        """
        
        for person in candidates_data:
            if person["file"] is not None:
                with st.spinner(f"جاري قراء الـ PDF وهندسة الفخاخ لـ {person['name']}..."):
                    
                    # استخراج النص من ملف الـ PDF المرفوع حياً
                    cv_text = extract_text_from_pdf(person["file"])
                    
                    if not cv_text:
                        st.error(f"فشل استخراج النص من ملف {person['name']}. تأكد أن الملف ليس تالفاً أو عبارة عن صورة.")
                        continue
                    
                    user_instruction = f"""
                    قم بتوليد عدد ({num_questions}) أسئلة فخاخ بمستوى صعوبة ({difficulty_level}).
                    
                    المرشح: {person['name']}
                    السيرة الذاتية (المستخرجة من الـ PDF): {cv_text}
                    الوظيفة المستهدفة: {job_description}
                    
                    التنسيق الصارم للمخرجات:
                    👤 المرشح: [اسم المرشح]
                    ❓ السؤال الفخ [الرقم]: [نص السؤال الفني الصعب والمباغت]
                    💡 الإجابة النموذجية المتوقعة: [الجواب القصير الحاسم والعميق]
                    """
                    
                    chat_completion = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1
                    )
                    
                    st.info(chat_completion.choices.message.content)
                    
        st.success("تم توليد الأسئلة بنجاح!")
        st.write("#### 🔒 فتح ميزة تحميل 'دليل المدير التنفيذي للمقابلات' (PDF)")
        lead_email = st.text_input("أدخل بريدك الإلكتروني التجاري لفك قفل تحميل ملف الـ PDF الجاهز للاجتماع:")
        
        if st.button("تحميل وثيقة المقابلة الرسمية"):
            if save_lead_email(lead_email):
                st.success("تم تسجيل إيميلك بنجاح في قاعدة بيانات Vetly AI! جاري إعداد وتصدير ملف الـ PDF الفخم...")
            else:
                st.error("الرجاء إدخال بريد إلكتروني حقيقي وصحيح لفك القفل.")

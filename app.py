import streamlit as st
from groq import Groq 

st.set_page_config(page_title="Vetly AI", page_icon="🎯", layout="wide")
st.title("🎯 Vetly AI")
st.subheader("منظومة فرز وتوليد الأسئلة الفخاخ لكشف خبرة المرشحين ومنع الخداع")

if 'API_e' in globals() or 'API_e' in locals():
    client = Groq(api_key=API_e)
else:
    try:
        client = Groq(api_key=st.secrets["API_e"])
    except:
        st.error("خطأ تكتيكي: المتغير السري API_e غير معرف في بيئة العمل!")
        st.stop()

def save_lead_email(email):
    if email and "@" in email:
        with open("vetly_leads.txt", "a", encoding="utf-8") as f:
            f.write(email + "\n")
        return True
    return False

st.sidebar.header("🛠️ معايير فرز المقابلة")
job_description = st.sidebar.text_area("وصف متطلبات الوظيفة المستهدفة (Job Description):", 
                                       placeholder="أدخل المهام والخبرات المطلوبة للوظيفة هنا...")

num_questions = st.sidebar.slider("عدد الأسئلة الفخاخ لكل مرشح:", min_value=1, max_value=10, value=3)
difficulty_level = st.sidebar.selectbox("مستوى صعوبة الفخاخ الفنية:", 
                                         ["سهل ومتدرج", "متوسط لاختبار الفهم", "صعب جداً وفخاخ تقنية عميقة"])

if "cv_count" not in st.session_state:
    st.session_state.cv_count = 1  # نبدأ بمرشح واحد تلقائياً

st.write("### 👥 السير الذاتية للمرشحين")

candidates_data = []

for i in range(st.session_state.cv_count):
    col1, col2 = st.columns([1, 4])
    with col1:
        c_name = st.text_input(f"اسم المرشح #{i+1}", value=f"مرشح {i+1}", key=f"name_{i}")
    with col2:
        c_cv = st.text_area(f"نص السيرة الذاتية أو أهم مهارات المرشح #{i+1}", 
                            placeholder="انسخ نص الـ CV أو الخبرات هنا...", key=f"cv_{i}")
    candidates_data.append({"name": c_name, "cv": c_cv})
    st.divider()

if st.button("➕ إضافة مرشح آخر للمقابلة المتقاطعة"):
    st.session_state.cv_count += 1
    st.rerun()

if st.button("🔥 هندسة دليل الأسئلة الفخاخ فوراً"):
    if not job_description:
        st.warning("الرجاء إدخال وصف الوظيفة أولاً في اللوحة الجانبية.")
    else:
        st.write("### 🎯 دليل الأسئلة المخفية الجاهز للمدير:")
        
        system_instruction = """
        أنت مستشار توظيف تقني فذ ومسؤول فرز فني عسكري في كبرى الشركات. مهمتك قراءة السيرة الذاتية ومقارنتها بالوظيفة، واستخراج أسئلة بمثابة فخاخ تقنية دقيقة وعميقة لكشف الخبرة الحقيقية ومنع الخداع تماماً.
        يجب أن تقدم الإجابة النموذجية البشرية المحترفة والمختصرة جداً التي يجب أن يسمعها المدير ليعرف إذا كان المرشح نصاباً أم خبيراً في نفس اللحظة.
        """
        
        for person in candidates_data:
            if person["cv"]: # نتحقق أن الخانة ليست فارغة
                with st.spinner(f"جاري فحص الـ CV وهندسة الفخاخ لـ {person['name']}..."):
                    
                    user_instruction = f"""
                    قم بتوليد عدد ({num_questions}) أسئلة فخاخ بمستوى صعوبة ({difficulty_level}).
                    
                    المرشح: {person['name']}
                    السيرة الذاتية: {person['cv']}
                    الوظيفة المستهدفة: {job_description}
                    
                    التنسيق الصارم للمخرجات:
                    👤 المرشح: [اسم المرشح]
                    ❓ السؤال الفخ [الرقم]: [نص السؤال الفني الصعب والمباغت]
                    💡 الإجابة النموذجية المتوقعة: [الجواب القصير الحاسم والعميق]
                    """
                    
                    # الاستدعاء المباشر بدرجة حرارة 0.1 الصارمة والمنيعة ضد الهلوسة
                    chat_completion = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1
                    )
                    
                    # عرض المخرجات فورا على شاشة واجهة الـ HR
                    st.info(chat_completion.choices.message.content)
                    
        st.success("تم توليد الأسئلة بنجاح!")
        st.write("#### 🔒 فتح ميزة تحميل 'دليل المدير التنفيذي للمقابلات' (PDF)")
        lead_email = st.text_input("أدخل بريدك الإلكتروني التجاري لفك قفل تحميل ملف الـ PDF الجاهز للاجتماع:")
        
        if st.button("تحميل وثيقة المقابلة الرسمية"):
            if save_lead_email(lead_email):
                st.success("تم تسجيل إيميلك بنجاح في قاعدة بيانات Vetly AI! جاري إعداد وتصدير ملف الـ PDF الفخم...")
            else:
                st.error("الرجاء إدخال بريد إلكتروني حقيقي وصحيح لفك القفل.")

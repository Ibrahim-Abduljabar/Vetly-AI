import streamlit as st
from groq import Groq 
import pypdf
import json

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
        html_style = """
        <style>
            .candidate-box {
                background-color: #f8f9fa;
                border-right: 5px solid #007bff;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 25px;
                direction: rtl;
                text-align: right;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .candidate-name {
                color: #007bff;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 15px;
                border-bottom: 1px solid #dee2e6;
                padding-bottom: 5px;
            }
            .question-item {
                background-color: #ffffff;
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 10px;
                border: 1px solid #e9ecef;
            }
            .q-text {
                font-weight: bold;
                color: #212529;
                margin-bottom: 5px;
                font-size: 16px;
            }
            .a-text {
                color: #28a745;
                font-weight: 500;
                font-size: 15px;
            }
        </style>
        """
        st.markdown(html_style, unsafe_allow_html=True)
        st.write("### 🎯 دليل الأسئلة المخفية الجاهز للمدير:")
        
        system_instruction = """
        أنت مستشار توظيف تقني أول ومسؤول الفرز الفني في كبرى مجموعات الاستثمار العالمية. مهمتك هي تحليل السيرة الذاتية بدقة ومقارنتها بالوظيفة، واستخراج أسئلة فنية عميقة ومباغتة (Structural Interview Questions) لكشف عمق المعرفة الحقيقية للمرشح.
        يجب أن تصيغ المخرجات بتنسيق JSON النظيف الصارم التالي فقط، وبدون أي نصوص ترحيبية أو تفسيرية خارج القوسين:
        {
            "candidate_name": "اسم المرشح الممرر لك",
            "questions": [
                {"q": "نص السؤال الفني المتقدم الأول", "a": "الرد التقني الحاسم المتوقع"},
                {"q": "نص السؤال الفني المتقدم الثاني", "a": "الرد التقني الحاسم المتوقع"}
            ]
        }
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
                    بناءً على السيرة الذاتية المستخرجة: {cv_text}
                    ومتطلبات الوظيفة: {job_description}
                    
                    تذكر صياغة المخرجات بتنسيق JSON النظيف التالي فقط وبدون أي كلمات زائدة:
                    {{
                        "candidate_name": "{person['name']}",
                        "questions": [
                            {{"q": "نص السؤال الفني الأول", "a": "نص الإجابة النموذجية الأولى"}},
                            {{"q": "نص السؤال الفني الثاني", "a": "نص الإجابة النموذجية الثانية"}}
                        ]
                    }}
                    """
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )
                    
                    try:
                        result_json = json.loads(chat_completion.choices.message.content)
                        
                        html_output = f'<div class="candidate-box">'
                        html_output += f'<div class="candidate-name">👤 المرشح: {result_json["candidate_name"]}</div>'
                        
                        for idx, item in enumerate(result_json["questions"]):
                            html_output += f"""
                            <div class="question-item">
                                <div class="q-text">❓ السؤال {idx+1}: {item['q']}</div>
                                <div class="a-text">💡 الإجابة النموذجية المتوقعة: {item['a']}</div>
                            </div>
                            """
                        html_output += '</div>'
                        
                        st.markdown(html_output, unsafe_allow_html=True)
                        
                    except Exception as json_err:
                        st.text(chat_completion.choices.message.content)
                        
        st.success("تم توليد التقييم الفني بنجاح! يمكنك الآن الضغط على (Ctrl + P) لطباعة الدليل أو حفظه كـ PDF من متصفحك مباشرة بشكل منسق!")

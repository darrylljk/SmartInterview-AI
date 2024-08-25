import streamlit as st
from openai import OpenAI
import openai
import fitz  # PyMuPDF
from docx import Document
from dotenv import load_dotenv
import os
import time

api_key = st.secrets["OPENAI_API_KEY"]

# uncomment below if running local, store api key in .env file
# load_dotenv()
# api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=api_key
)
model = "gpt-4o-mini"

def read_file(file):
    # Determine file type
    if file.type == "application/pdf":
        return read_pdf(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    else:
        return file.read().decode('utf-8')

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def read_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_requirements(text):
    """
    Extract the key skills, qualifications, and responsibilities from the job description.
    """
    prompt = f"""
    Extract the key skills, qualifications, and responsibilities from the following job description:

    {text}

    Provide a summary of the key requirements.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts key skills, qualifications, and responsibilities from the job description"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0
    )

    return response.choices[0].message.content.strip()

def analyze_text(text):
    """
    Analyze the text to extract skills, qualifications, and experience from the candidate's CV.
    """
    prompt = f"""
    Analyze the following text from a candidate's CV and extract key skills, qualifications, and experiences:

    {text}

    Provide a summary of the candidate's skills and experiences.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant that analyzes the text to extract skills, qualifications, and experience from the candidate CV'},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0
    )

    return response.choices[0].message.content.strip()

def evaluate_candidate_fit(requirements, cv_analysis):
    """
    Evaluate the candidate's fit for the role based on the job requirements and their CV.
    """
    prompt = f"""
    Based on the following job requirements and candidate CV analysis, assess the candidate’s fit for the role:

    Job Requirements:
    {requirements}

    Candidate CV Analysis:
    {cv_analysis}

    Provide a suitability score on a scale of 1 to 10, and explain the assessment.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant that evaluates the candidate fit for the role based on the job requirements and their CV'},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0
    )

    return response.choices[0].message.content.strip()

def generate_interview_questions(jd, cv, categories):
    categories_str = ', '.join(categories)

    prompt = f"""
    Job Description:
    {jd}
    
    Candidate CV:
    {cv}
    
    You are a seasoned interviewer tasked with creating insightful and relevant interview questions.
    Your goal is to assess the candidate's fit for the role based on the job description and their CV.
    Focus on evaluating both technical skills and cultural fit.
    
    Generate a comprehensive list of interview questions that:
    1. Probe the candidate's experience and skills as described in their CV.
    2. Assess the candidate's ability to perform the key responsibilities and requirements in the job description.
    3. Evaluate the candidate's problem-solving abilities, critical thinking, and adaptability.
    4. Explore the candidate's fit with the company culture and values.
    5. Understand the candidate's motivation and long-term career goals.
    6. Gauge the candidate's ability to work within a team and manage conflicts.
    7. Address any potential concerns or "elephants in the room," such as long periods of unemployment, short tenures at previous jobs, or any other anomalies in their employment history.

    Focus on the following categories: {categories_str}

    Each category should contain 4-5 questions.
    In each category, there should be 1-2 questions directed at the candidate's experiences in his CV.

    Output the questions in the following format:

    Category A
    - question 1
    - question 2
    - question 3
    - question 4

    Category B
    - question 1
    - question 2
    - question 3
    - question 4
    - question 5

    List of Interview Questions:
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates interview questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0
    )

    return response.choices[0].message.content.strip()

def main():
    st.set_page_config(page_title="SmartInterview AI", page_icon="🚀")
    st.title("SmartInterview AI")
    st.write("""
        🚀 Welcome to SmartInterview AI 🚀
        
        This tool is designed to revolutionize your interview preparation process (for interviewers and interviewees alike). 
        Simply upload a Job Description (JD) and a Candidate's CV, and SmartInterview AI will generate a comprehensive
        set of tailored interview questions.
        
        These questions will help you dive deep into the candidate's experience,
        skills, and potential fit for your organization, making your interview process more effective and insightful.
        
        Select the question types you want to focus on, and let SmartInterview AI handle the rest. 
    """)

    with st.sidebar:
        st.header("Settings")
        jd_file = st.file_uploader("Upload Job Description (JD) File", type=['pdf', 'txt', 'docx'])
        cv_file = st.file_uploader("Upload Candidate CV File", type=['pdf', 'txt', 'docx'])
        categories = st.multiselect(
            "Select Question Types to Focus On",
            options=["Technical Skills", "Business Acumen", "Cultural Fit", "Problem-Solving", "Career Goals", "Teamwork", "Conflict Management", "CV Anomalies"],
            default=["Technical Skills", "Business Acumen", "Cultural Fit", "Problem-Solving", "Career Goals", "Teamwork", "Conflict Management", "CV Anomalies"]
        )

    if st.button("Generate Interview Questions"):
        if jd_file is None or cv_file is None:
            st.warning("Missing files. Please ensure both the Job Description and Candidate CV files are uploaded.")
        else:
            jd = read_file(jd_file)
            cv = read_file(cv_file)

            jd_requirements = extract_requirements(jd)
            cv_analysis = analyze_text(cv)

            suitability_score = evaluate_candidate_fit(jd_requirements, cv_analysis)

            with st.spinner('Generating questions...'):
                progress_bar = st.progress(0)

                for percent_complete in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(percent_complete + 1)

                questions = generate_interview_questions(jd, cv, categories)
            
            st.subheader("Generated Interview Questions:")
            st.write(questions)
            st.download_button(label="Download Questions as TXT", data=questions, file_name="interview_questions.txt", mime="text/plain")

            st.subheader('Candidate Suitability Assessment:')
            st.write(suitability_score)


if __name__ == "__main__":
    main()

from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import fitz
import re

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Extract text using PyMuPDF
def extract_text_from_pdf(uploaded_file):
    try:
        uploaded_file.seek(0)
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in doc])
        return text if text.strip() else "No text found in PDF."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# Prepare image for Gemini
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        uploaded_file.seek(0)
        images = pdf2image.convert_from_bytes(
    uploaded_file.read(), 
    poppler_path=r"C:\Users\raksh\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
)

        first_page = images[0]

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_data = base64.b64encode(img_byte_arr.getvalue()).decode()

        return [{"mime_type": "image/jpeg", "data": img_data}]
    else:
        raise FileNotFoundError("No file uploaded")

# Extract Name, Email, Phone, LinkedIn
def extract_resume_details(text):
    details = {
        "Name": "Name Not found",
        "Email ID": "Email ID Not found",
        "Phone Number": "Phone Number Not found",
        "LinkedIn": "LinkedIn Not found"
    }

    lines = text.split("\n")
    if lines:
        details["Name"] = lines[0].strip()

    # Phone
    phone_match = re.findall(r"(?:\+?91[-\s]?)?\d{3}[-\s]?\d{3}[-\s]?\d{4}", text)
    if phone_match:
        phone = phone_match[0].replace(' ', '').replace('-', '')
        details["Phone Number"] = phone

    # Email
    email_match = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        details["Email ID"] = email_match[0]

    # LinkedIn
    linkedin_match = re.findall(r'\S*linkedin\S*', text)
    if linkedin_match:
        url = linkedin_match[0]
        if 'www.' not in url:
            url = 'www.' + url
        if 'http://' in url:
            url = 'https://' + url[7:]
        if 'https://' not in url:
            url = 'https://' + url
        details["LinkedIn"] = url

    return details

# Gemini Response Generator
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

# Job roles and descriptions
job_and_desc = {
    "Data Analyst": """
        Collect, clean, and analyze large datasets to extract insights. Develop reports, dashboards, and visualizations using tools like Power BI, Tableau, or Excel. Perform statistical analysis and predictive modeling using Python or R.
        Work with SQL databases to query and manipulate data. Identify trends and patterns to support business decision-making. Collaborate with stakeholders to understand data requirements.
    """,
    "HR Manager": """
        Oversee recruitment, hiring, and onboarding processes. Develop and implement HR policies and procedures. Manage employee relations, conflict resolution, and workplace culture.
        Conduct performance evaluations and training programs. Ensure compliance with labor laws and company regulations. Maintain employee records and handle payroll administration.
    """,
    "Web Developer": """
        Design, develop, and maintain websites using HTML, CSS, JavaScript, and frameworks like React or Angular. Optimize web applications for performance, speed, and scalability. Ensure website responsiveness across different devices and browsers.
        Develop backend functionality using Node.js, Django, or other frameworks. Work with databases like MySQL, PostgreSQL, or MongoDB. Troubleshoot and debug web applications.
    """,
    "App Developer": """
        Design and develop mobile applications for iOS and Android platforms. Work with programming languages such as Swift, Kotlin, Flutter, or React Native. Optimize app performance and responsiveness.
        Integrate third-party APIs and services. Conduct testing and debugging to ensure app stability. Collaborate with UI/UX designers to improve user experience.
    """
}

# Streamlit UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("📄 ATS Resume Analyzer")

selected_role = st.selectbox("Select the Position Applied For:", list(job_and_desc.keys()))
st.write(f"You selected: **{selected_role}**")

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully")
    text = extract_text_from_pdf(uploaded_file)

    if text.startswith("Error"):
        st.error(text)
    else:
        details = extract_resume_details(text)

        st.markdown("---")
        st.write(f"👤 **Name:** {details['Name']}")
        st.write(f"📧 **Email ID:** {details['Email ID']}")
        st.write(f"📞 **Phone Number:** {details['Phone Number']}")
        st.write(f"🔗 **LinkedIn:** {details['LinkedIn']}")

input_prompt1 = """
You are an experienced Technical HR Manager. Review the resume against the job description.
Evaluate the candidate's profile. Highlight strengths and weaknesses with respect to the job requirements.
"""

input_prompt2 = """
You're an ATS scanner. Match the resume against the job description.
Return: 
1. Percentage match
2. Missing keywords
3. Final comments on alignment
"""

input_text = job_and_desc.get(selected_role)

if st.button("📋 Tell Me About the Resume"):
    if uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("📌 Evaluation Result:")
        st.write(response)
    else:
        st.warning("Please upload a resume.")

if st.button("📊 Percentage Match"):
    if uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt2, pdf_content, input_text)
        st.subheader("📌 Match Percentage and Analysis:")
        st.write(response)
    else:
        st.warning("Please upload a resume.")

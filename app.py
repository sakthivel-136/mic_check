import streamlit as st
from fpdf import FPDF
from pygments import highlight
from pygments.lexers import PythonLexer, CLexer, JavaLexer
from pygments.formatters import HtmlFormatter
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib
import os
import tempfile

# ---------------------- Convert Code to PDF -----------------------
def code_to_pdf(code, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    for line in code.split('\n'):
        pdf.multi_cell(0, 5, line)
    pdf.output(output_path)

# ---------------------- Detect Language by File Extension -----------------------
def detect_language(file_name):
    if file_name.endswith('.py'):
        return 'python'
    elif file_name.endswith('.c'):
        return 'c'
    elif file_name.endswith('.java'):
        return 'java'
    elif file_name.endswith('.ipynb'):
        return 'json'  # Optional: handle via nbconvert later
    else:
        return 'text'

# ---------------------- Email Sender -----------------------
def send_email_with_attachment(receiver_email, subject, body, attachments):
    sender_email = "kamarajengg.edu.in@gmail.com"
    password = "qwerty12345"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for file_path in attachments:
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# ---------------------- Streamlit UI -----------------------
st.title("📄 Code File to PDF & Email Sender")

uploaded_files = st.file_uploader("📤 Upload your code files (.py, .c, .java, .ipynb)", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)
user_email = st.text_input("📧 Enter your email to receive PDFs")

if st.button("Convert & Send"):
    if uploaded_files and user_email:
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []

        for uploaded_file in uploaded_files:
            try:
                code = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                lang = detect_language(uploaded_file.name)
                pdf_path = os.path.join(temp_dir, uploaded_file.name + ".pdf")
                code_to_pdf(code, pdf_path)
                pdf_paths.append(pdf_path)
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {e}")

        if send_email_with_attachment(user_email, "Your Code PDFs", "Attached are your converted code PDFs.", pdf_paths):
            st.success("✅ Email sent successfully!")
        else:
            st.error("❌ Failed to send email.")
    else:
        st.warning("Please upload at least one file and enter your email.")

    

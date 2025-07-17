import streamlit as st
from fpdf import FPDF
import subprocess
import os
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib
import pdfkit
# ---------------------- Convert Code Files to PDF (wrapped lines) -----------------------
def code_to_pdf(code, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    for line in code.split('\n'):
        while len(line) > 100:
            pdf.cell(0, 5, line[:100], ln=True)
            line = line[100:]
        pdf.cell(0, 5, line, ln=True)
    pdf.output(output_path)

# ---------------------- Convert .ipynb to PDF using nbconvert -----------------------
def notebook_to_pdf(ipynb_path, output_pdf_path):
    try:
        html_path = output_pdf_path.replace(".pdf", ".html")
        subprocess.run([
    "jupyter", "nbconvert", "--to", "html",
    "--output", html_path,
    ipynb_path
], check=True)

pdfkit.from_file(html_path, output_pdf_path)

        return True
    except Exception as e:
        st.error(f"Failed to convert notebook: {e}")
        return False

# ---------------------- Email Sender -----------------------
def send_email_with_attachment(receiver_email, subject, body, attachments):
    sender_email = "kamarajengg.edu.in@gmail.com"
    password = "vwvcwsfffbrvumzh"

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
        st.error(f"Email send failed: {e}")
        return False

# ---------------------- Streamlit UI -----------------------
st.title("📄 Code to PDF & Email (with .ipynb Support)")

uploaded_files = st.file_uploader("📤 Upload your files (.py, .c, .java, .ipynb)", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)
user_email = st.text_input("📧 Enter your email to receive the PDFs")

if st.button("Convert & Send"):
    if uploaded_files and user_email:
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []

        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            file_path = os.path.join(temp_dir, filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            output_pdf_path = os.path.join(temp_dir, filename + ".pdf")

            if filename.endswith(".ipynb"):
                st.info(f"Converting notebook: {filename}")
                if notebook_to_pdf(file_path, output_pdf_path.replace(".pdf", "")):
                    pdf_paths.append(output_pdf_path)
            else:
                try:
                    code = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                    code_to_pdf(code, output_pdf_path)
                    pdf_paths.append(output_pdf_path)
                except Exception as e:
                    st.error(f"Error converting {filename}: {e}")

        if not pdf_paths:
            st.error("❌ No valid PDFs to send.")
        elif send_email_with_attachment(user_email, "Your Converted PDFs", "Here are your files.", pdf_paths):
            st.success("✅ Email sent successfully!")
        else:
            st.error("❌ Email failed.")
    else:
        st.warning("Please upload at least one file and enter your email.")

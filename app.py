import streamlit as st
from fpdf import FPDF
import os
import tempfile
import json
import zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

# ---------------------- Convert Code/Text to PDF -----------------------
def code_to_pdf(text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    for line in text.split('\n'):
        while len(line) > 100:
            pdf.cell(0, 5, line[:100], ln=True)
            line = line[100:]
        pdf.cell(0, 5, line, ln=True)
    pdf.output(output_path)

# ---------------------- Extract Code from .ipynb -----------------------
def notebook_to_text(ipynb_path):
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)

        extracted_code = []
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "code":
                extracted_code.append("".join(cell.get("source", [])))
                extracted_code.append("\n")

        return "\n".join(extracted_code) if extracted_code else "[No code cells found]"
    except Exception as e:
        return f"Failed to parse notebook: {e}"

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
        st.error(f"❌ Email send failed: {e}")
        return False

# ---------------------- Streamlit UI -----------------------
st.title("📄 Code/Notebook to PDF Converter")

uploaded_files = st.file_uploader("📤 Upload your files (.py, .c, .java, .ipynb)", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)

delivery_option = st.radio("📤 How would you like to receive your PDFs?", ["Download", "Email"])
user_email = st.text_input("📧 Enter your email (required only if you choose Email)") if delivery_option == "Email" else None

if st.button("Convert & Process"):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one file.")
    elif delivery_option == "Email" and not user_email:
        st.warning("⚠️ Please enter your email address to receive the files.")
    else:
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []

        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            file_path = os.path.join(temp_dir, filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            output_pdf_path = os.path.join(temp_dir, filename + ".pdf")

            try:
                if filename.endswith(".ipynb"):
                    st.info(f"🔄 Converting notebook: {filename}")
                    extracted_text = notebook_to_text(file_path)
                    code_to_pdf(extracted_text, output_pdf_path)
                else:
                    code = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                    code_to_pdf(code, output_pdf_path)

                pdf_paths.append(output_pdf_path)
            except Exception as e:
                st.error(f"❌ Error converting {filename}: {e}")

        if not pdf_paths:
            st.error("❌ No valid PDFs to process.")
        else:
            if delivery_option == "Email":
                if send_email_with_attachment(user_email, "Your Converted PDFs", "Here are your files.", pdf_paths):
                    st.success("✅ Email sent successfully!")
            else:
                # Zip and offer download
                zip_path = os.path.join(temp_dir, "converted_files.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for pdf in pdf_paths:
                        zipf.write(pdf, arcname=os.path.basename(pdf))

                with open(zip_path, "rb") as f:
                    st.download_button("📥 Download All PDFs as ZIP", f, file_name="converted_pdfs.zip")

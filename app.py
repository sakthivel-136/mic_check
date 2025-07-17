import streamlit as st
from fpdf import FPDF
import os
import tempfile
import json
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

# ---------------------- PDF Generator (Emoji Safe) ----------------------
def code_to_pdf(text, output_path):
    pdf = FPDF()
    font_path = "DejaVuSans.ttf"
    pdf.add_font("Unicode", "", font_path, uni=True)
    pdf.add_page()
    pdf.set_font("Unicode", size=10)

    for line in text.split('\n'):
        while len(line) > 100:
            pdf.cell(0, 5, line[:100], ln=True)
            line = line[100:]
        pdf.cell(0, 5, line, ln=True)
    pdf.output(output_path)

# ---------------------- Convert .ipynb to Code Text ----------------------
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

# ---------------------- Email Function ----------------------
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

# ---------------------- UI Setup ----------------------
st.set_page_config(page_title="Team 2 PDF Converter", page_icon="🧾", layout="centered")

# Inject moving banner and styles
st.markdown("""
<style>
@keyframes slide {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}
.banner {
  background: linear-gradient(to right, #a1c4fd, #c2e9fb);
  padding: 10px;
  overflow: hidden;
  white-space: nowrap;
  font-weight: bold;
  color: #000;
  border-radius: 10px;
  margin-bottom: 20px;
}
.banner span {
  display: inline-block;
  padding-left: 100%;
  animation: slide 10s linear infinite;
}
.upload-box {
  border: 2px dashed #aaa;
  padding: 20px;
  border-radius: 12px;
  background-color: #f9f9f9;
}
</style>
<div class="banner">
  <span>👨‍💻 Team 2 - Sakthi | Priya | John | Aravind 🚀</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; color:#2E86C1;">📄 Code/Notebook to PDF Converter</h2>', unsafe_allow_html=True)

# Upload UI
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_files = st.file_uploader("📤 Upload your files (.py, .c, .java, .ipynb)", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

# Delivery method
delivery_option = st.radio("📤 How would you like to receive your PDFs?", ["📥 Download", "📧 Email"])
user_email = st.text_input("📧 Enter your email (only needed if you choose Email)") if "Email" in delivery_option else None

# Process
if st.button("🚀 Convert Now"):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one file.")
    elif delivery_option == "📧 Email" and not user_email:
        st.warning("⚠️ Please enter your email address.")
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
                    text = notebook_to_text(file_path)
                else:
                    text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                code_to_pdf(text, output_pdf_path)
                pdf_paths.append(output_pdf_path)
                st.success(f"✅ Converted: {filename}")
                with open(output_pdf_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download {filename}.pdf",
                        data=f,
                        file_name=filename + ".pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error converting {filename}: {e}")

        if delivery_option == "📧 Email" and pdf_paths:
            if send_email_with_attachment(user_email, "Your Converted PDFs", "Here are your PDFs 🎉", pdf_paths):
                st.success("📧 Email sent successfully!")

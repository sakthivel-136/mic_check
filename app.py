import streamlit as st
from fpdf import FPDF
import os
import tempfile
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

# ---------------------- Hugging Face Summarizer ----------------------
def summarize_code_hf(code):
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/codet5-base"
    HF_TOKEN = "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"  # Hardcoded as requested

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": code,
        "parameters": {"max_length": 60, "do_sample": False},
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0]['summary_text']
        else:
            return "[⚠️ Summary error]"
    except Exception as e:
        return f"[❌ AI Summary failed: {e}]"

# ---------------------- PDF Writer ----------------------
def code_to_pdf(text, output_path):
    pdf = FPDF()
    font_path = "DejaVuSans.ttf"  # Unicode font
    pdf.add_font("Unicode", "", font_path, uni=True)
    pdf.add_page()
    pdf.set_font("Unicode", size=10)

    summary = summarize_code_hf(text)
    pdf.set_text_color(0, 0, 180)
    pdf.multi_cell(0, 5, f"🔍 AI Summary:\n{summary}")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    for line in text.split('\n'):
        while len(line) > 100:
            pdf.cell(0, 5, line[:100], ln=True)
            line = line[100:]
        pdf.cell(0, 5, line, ln=True)
    pdf.output(output_path)

# ---------------------- Notebook to Code Extractor ----------------------
def notebook_to_text(ipynb_path):
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        extracted_code = []
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "code":
                extracted_code.append("".join(cell.get("source", [])))
        return "\n".join(extracted_code) if extracted_code else "[No code cells found]"
    except Exception as e:
        return f"[❌ Failed to parse notebook: {e}]"

# ---------------------- Email PDF Attachment ----------------------
def send_email_with_attachment(receiver_email, subject, body, attachments):
    sender_email = "kamarajengg.edu.in@gmail.com"
    password = "vwvcwsfffbrvumzh"  # Use app password

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
        st.error(f"❌ Email failed: {e}")
        return False

# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="Team 2 Code to PDF AI", page_icon="🧾")

# UI Styles + Banner
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

st.markdown('<h2 style="text-align:center; color:#2E86C1;">📄 AI Code Summarizer & PDF Export</h2>', unsafe_allow_html=True)

# File Upload
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_files = st.file_uploader("📤 Upload .py / .c / .java / .ipynb files", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

# Option
delivery_option = st.radio("📤 How do you want your PDFs?", ["📥 Download", "📧 Email"])
user_email = st.text_input("📧 Enter your email") if "Email" in delivery_option else None

# Process Button
if st.button("🚀 Convert & Generate PDFs"):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one file.")
    elif delivery_option == "📧 Email" and not user_email:
        st.warning("⚠️ Please enter your email.")
    else:
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []

        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            output_pdf = os.path.join(temp_dir, filename + ".pdf")

            try:
                if filename.endswith(".ipynb"):
                    code = notebook_to_text(file_path)
                else:
                    code = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                code_to_pdf(code, output_pdf)
                pdf_paths.append(output_pdf)

                st.success(f"✅ Converted: {filename}")
                with open(output_pdf, "rb") as f:
                    st.download_button(
                        f"📥 Download {filename}.pdf", f, file_name=filename + ".pdf", mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error converting {filename}: {e}")

        if delivery_option == "📧 Email" and pdf_paths:
            if send_email_with_attachment(user_email, "Your Converted PDFs", "Here are your AI-powered PDFs 🎯", pdf_paths):
                st.success("📧 Email sent successfully!")

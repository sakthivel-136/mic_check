import streamlit as st
from fpdf import FPDF
import os
import tempfile
import json
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer, PythonLexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

# ------------------ Detect best lexer ------------------
def detect_lexer(filename, code):
    try:
        return get_lexer_for_filename(filename, code)
    except:
        try:
            return guess_lexer(code)
        except:
            return PythonLexer()

# ------------------ Get code statistics ------------------
def get_code_stats(code):
    lines = code.splitlines()
    return {
        "Total Lines": len(lines),
        "Blank Lines": sum(1 for l in lines if not l.strip()),
        "Comment Lines": sum(1 for l in lines if l.strip().startswith("#") or l.strip().startswith("//")),
        "Function Definitions": sum(1 for l in lines if any(k in l for k in ['def ', 'void ', 'function ']))
    }

# ------------------ PDF Generator ------------------
def code_to_pdf(filename, code, output_path):
    stats = get_code_stats(code)
    pdf = FPDF()
    font_path = "DejaVuSans.ttf"
    pdf.add_font("Unicode", "", font_path, uni=True)
    pdf.set_font("Unicode", size=9)
    pdf.add_page()

    # Add stats
    pdf.set_text_color(0, 0, 180)
    pdf.cell(0, 6, "📊 Code Statistics:", ln=True)
    pdf.set_text_color(0, 0, 0)
    for k, v in stats.items():
        pdf.cell(0, 6, f"- {k}: {v}", ln=True)
    pdf.ln(4)

    # Highlight code
    lexer = detect_lexer(filename, code)
    formatter = HtmlFormatter(style="colorful", noclasses=True)
    highlighted_html = highlight(code, lexer, formatter)
    soup = BeautifulSoup(highlighted_html, "html.parser")
    clean_text = soup.get_text()

    for line in clean_text.splitlines():
        while len(line) > 100:
            pdf.cell(0, 5, line[:100], ln=True)
            line = line[100:]
        pdf.cell(0, 5, line, ln=True)

    pdf.output(output_path)

# ------------------ Extract from Notebook ------------------
def notebook_to_text(ipynb_path):
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        return "\n".join("".join(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == "code")
    except Exception as e:
        return f"[Error parsing notebook: {e}]"

# ------------------ Email Sender ------------------
def send_email(receiver_email, files):
    sender_email = "kamarajengg.edu.in@gmail.com"
    password = "vwvcwsfffbrvumzh"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Your converted PDFs from Streamlit App"
    msg.attach(MIMEText("Please find your converted PDF files attached.", "plain"))

    for file_path in files:
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

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Code to PDF - Email or Download", page_icon="📄")
st.title("📄 Code to PDF Converter with Stats & Highlighting")
st.markdown("✅ Upload `.py`, `.c`, `.java`, or `.ipynb` files. Choose to download or receive via email.")

uploaded_files = st.file_uploader("📤 Upload code files", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)

choice = st.radio("📤 Choose output method", ["📥 Download", "📧 Email"])
email = st.text_input("📧 Enter your email") if choice == "📧 Email" else None

if st.button("🚀 Convert Now"):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one file.")
    elif choice == "📧 Email" and not email:
        st.warning("⚠️ Please enter your email address.")
    else:
        temp_dir = tempfile.mkdtemp()
        pdf_paths = []

        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            file_path = os.path.join(temp_dir, filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            if filename.endswith(".ipynb"):
                code = notebook_to_text(file_path)
            else:
                code = uploaded_file.getvalue().decode("utf-8", errors="ignore")

            pdf_output = os.path.join(temp_dir, filename + ".pdf")
            code_to_pdf(filename, code, pdf_output)
            pdf_paths.append(pdf_output)

        if choice == "📧 Email":
            if send_email(email, pdf_paths):
                st.success("✅ Email sent successfully!")
        else:
            for path in pdf_paths:
                with open(path, "rb") as f:
                    st.download_button(
                        f"📥 Download {os.path.basename(path)}", f,
                        file_name=os.path.basename(path), mime="application/pdf"
                    )

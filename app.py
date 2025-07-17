import streamlit as st
from fpdf import FPDF
import os
import tempfile
import json
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, CLexer, JavaLexer

# ---------------------- Code Statistics ----------------------
def get_code_stats(code):
    lines = code.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for l in lines if not l.strip())
    comment_lines = sum(1 for l in lines if l.strip().startswith("#") or l.strip().startswith("//"))
    function_defs = sum(1 for l in lines if "def " in l or "function " in l or "void " in l)
    
    return {
        "Total Lines": total_lines,
        "Blank Lines": blank_lines,
        "Comment Lines": comment_lines,
        "Function Definitions": function_defs,
    }

# ---------------------- PDF Generator with Syntax Highlighting ----------------------
def code_to_pdf(code, output_path):
    stats = get_code_stats(code)

    pdf = FPDF()
    font_path = "DejaVuSans.ttf"
    pdf.add_font("Unicode", "", font_path, uni=True)
    pdf.set_font("Unicode", size=10)
    pdf.add_page()

    # 📊 Print statistics
    pdf.set_text_color(0, 0, 255)
    pdf.multi_cell(0, 8, "📊 Code Statistics:")
    pdf.set_text_color(0, 0, 0)
    for key, value in stats.items():
        pdf.multi_cell(0, 8, f"- {key}: {value}")
    pdf.ln(4)

    # 🖍️ Syntax Highlighting
    try:
        lexer = guess_lexer(code)
    except:
        lexer = PythonLexer()

    formatter = HtmlFormatter(style="colorful", noclasses=True)
    highlighted_code = highlight(code, lexer, formatter)

    # Remove HTML tags to render as plain text in PDF
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(highlighted_code, "html.parser")
    stripped_code = soup.get_text()

    for line in stripped_code.splitlines():
        while len(line) > 100:
            pdf.cell(0, 5, line[:100], ln=True)
            line = line[100:]
        pdf.cell(0, 5, line, ln=True)

    pdf.output(output_path)

# ---------------------- Notebook Extractor ----------------------
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

# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="Code to PDF (with Stats + Highlighting)", page_icon="📄")
st.title("📄 Code to PDF Converter with AI-Like Stats")
st.markdown("### Upload `.py`, `.c`, `.java`, or `.ipynb` files to convert to PDF with line statistics and syntax highlighting.")

uploaded_files = st.file_uploader("📤 Upload your code files", type=["py", "c", "java", "ipynb"], accept_multiple_files=True)

if st.button("🚀 Convert to PDF"):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one code file.")
    else:
        temp_dir = tempfile.mkdtemp()
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
                st.success(f"✅ Converted: {filename}")
                with open(output_pdf, "rb") as f:
                    st.download_button(
                        f"📥 Download {filename}.pdf", f, file_name=filename + ".pdf", mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Failed to convert {filename}: {e}")

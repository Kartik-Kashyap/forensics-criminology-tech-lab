from fpdf import FPDF

def create_pdf(case_data, analysis_text, graph_image_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"FORENSIC EVIDENCE REPORT: {case_data['case_id']}", ln=True, align='C')
    
    # Sub-header
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, f"Submitted to: {case_data['court_name']} | Judge: {case_data['judge_name']}", ln=True, align='C')
    
    # Evidence Body (The AI Text)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, analysis_text)
    
    # Graph (Save the Plotly chart as an image first, then insert)
    # pdf.image(graph_image_path, x=10, y=100, w=190)
    
    return pdf.output(dest='S').encode('latin-1')
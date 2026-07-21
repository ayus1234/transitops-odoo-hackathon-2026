from fpdf import FPDF
import io
from typing import List, Dict, Any

class TransitOpsPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'TransitOps Enterprise ERP', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_table(title: str, headers: List[str], data: List[List[Any]]) -> bytes:
    pdf = TransitOpsPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, title, ln=1, align='L')
    pdf.ln(5)
    
    # Calculate column widths
    col_widths = [190 / len(headers)] * len(headers)
    
    # Headers
    pdf.set_font("helvetica", 'B', 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), border=1, align='C')
    pdf.ln()
    
    # Rows
    pdf.set_font("helvetica", '', 9)
    for row in data:
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], 10, str(item), border=1, align='C')
        pdf.ln()
        
    return bytes(pdf.output())

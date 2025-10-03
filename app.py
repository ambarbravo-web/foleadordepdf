
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
import os

# Función que crea el encabezado (overlay)
def overlay_encabezado(width, height, folio, bloque_izq,
                       margen=36, font="Helvetica", fs=6, line_gap=8):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))

    x_left = margen
    x_right = width - margen
    y = height - margen

    c.setFont(font, fs)
    for line in bloque_izq.split("\n"):
        c.drawString(x_left, y, line)
        y -= line_gap

    y_right = height - margen
    right_lines = [
        f"Folio: {folio:08d}",
        "Representante Legal:",
        "Medina Herrera Pablo",
        "R.U.T.: 7.037.581-8",
    ]
    for line in right_lines:
        c.drawRightString(x_right, y_right, line)
        y_right -= line_gap

    c.save()
    buf.seek(0)
    return buf

# Función para foliar PDF
def foliar_pdf(input_pdf, folio_inicial, bloque_izq):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    folio = folio_inicial
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        overlay_buf = overlay_encabezado(width, height, folio, bloque_izq)
        overlay_reader = PdfReader(overlay_buf)
        page.merge_page(overlay_reader.pages[0])

        writer.add_page(page)
        folio += 1

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# Interfaz Streamlit
st.set_page_config(page_title="Foleador de PDFs", layout="centered")
st.title("📄 Foleador de PDFs")

st.write("Sube un PDF, escribe los datos y se generará un nuevo archivo con folio por página.")

archivo_pdf = st.file_uploader("📎 Sube tu PDF", type=["pdf"])

folio_inicial = st.number_input("🔢 Folio inicial", min_value=1, value=24920)

bloque_izq = st.text_area("🏢 Texto del bloque izquierdo (empresa, dirección, etc.)",
"""Emilio Vaisse Spa
Sociedades de inversión y rentistas de capitales mobiliarios
Presidente Riesco 5561 Oficina 601
Las Condes, Santiago
R.U.T.: 76.311.477-5""")

if st.button("✅ Foliar PDF"):
    if archivo_pdf is None:
        st.warning("Por favor sube un archivo PDF.")
    elif not bloque_izq.strip():
        st.warning("Por favor escribe el bloque izquierdo.")
    else:
        resultado = foliar_pdf(archivo_pdf, folio_inicial, bloque_izq)
        st.success("✅ PDF foliado correctamente.")
        st.download_button("📥 Descargar PDF Foliado", data=resultado, file_name="foliado.pdf")

from docx import Document
from docx.shared import Inches
from typing import Dict, Any
import io

# Almacenamiento en memoria para gráficos y conclusiones
report_artifacts: Dict[str, Any] = {
    "plots": {},
    "summary": "No se han generado conclusiones todavía."
}

def clear_report_artifacts():
    """Limpia los artefactos del informe anterior."""
    report_artifacts["plots"].clear()
    report_artifacts["summary"] = "No se han generado conclusiones todavía."
    print("Artefactos de informe limpiados.")

def add_plot(name: str, plot_bytes: io.BytesIO):
    """Guarda un gráfico en memoria para el informe."""
    report_artifacts["plots"][name] = plot_bytes
    print(f"Gráfico '{name}' guardado para el informe.")

def set_summary(text: str):
    """Guarda el texto de resumen/conclusiones para el informe."""
    report_artifacts["summary"] = text
    print("Resumen del informe guardado.")


def generate_report() -> io.BytesIO:
    """
    Genera un informe de Word (.docx) con los artefactos guardados.
    """
    document = Document()
    document.add_heading('Informe Analítico Profesional Automático (IAIP)', 0)

    p = document.add_paragraph('Este informe ha sido generado automáticamente por el Sistema de Analítica de Datos Inteligente (SADI). ')
    p.add_run('Resume los hallazgos clave, visualizaciones y conclusiones del análisis realizado.').italic = True

    document.add_heading('1. Resumen y Conclusiones', level=1)
    document.add_paragraph(report_artifacts["summary"])

    document.add_heading('2. Visualizaciones Clave', level=1)

    if not report_artifacts["plots"]:
        document.add_paragraph("No se generaron gráficos durante este análisis.")
    else:
        for name, plot_bytes in report_artifacts["plots"].items():
            try:
                document.add_heading(f'Gráfico: {name.replace("_", " ").title()}', level=2)
                # El buffer debe ser reseteado al principio antes de leerlo
                plot_bytes.seek(0)
                document.add_picture(plot_bytes, width=Inches(6.0))
            except Exception as e:
                document.add_paragraph(f"No se pudo renderizar el gráfico '{name}'. Error: {e}")

    # Guardar el documento en un buffer en memoria
    doc_buffer = io.BytesIO()
    document.save(doc_buffer)
    doc_buffer.seek(0)

    return doc_buffer

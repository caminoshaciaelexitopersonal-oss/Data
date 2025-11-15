import zipfile
import io
import os
from typing import List, Dict, Any

def export_code_blocks_to_zip(steps: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Toma una lista de pasos de ejecución (del logger) y los compila en un
    archivo ZIP en memoria.

    Cada paso se guarda como un archivo .py numerado.

    :param steps: La lista de pasos, donde cada paso es un diccionario
                  con al menos una clave 'codigo' y 'descripcion'.
    :return: Un objeto BytesIO que contiene el archivo zip.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Añadir un archivo README
        readme_content = "Código Fuente Generado por SADI\n=================================\n\n"
        readme_content += "Este archivo ZIP contiene los fragmentos de código Python generados y ejecutados por el agente de IA durante el análisis.\n\n"
        readme_content += "Los archivos están numerados en el orden de ejecución.\n"
        zf.writestr("README.md", readme_content)

        # Añadir cada paso como un archivo .py
        for i, step in enumerate(steps):
            code = step.get("codigo", "# No se encontró código para este paso.")
            description = step.get("descripcion", "Sin descripción.")

            # Limpiar la descripción para usarla como parte del nombre del archivo
            # (versión simplificada, se podría mejorar con regex)
            safe_desc = "".join(c for c in description if c.isalnum() or c in (' ', '_')).rstrip()
            safe_desc = safe_desc.replace(' ', '_').lower()

            filename = f"{i+1:02d}_{safe_desc}.py"

            # Crear el contenido del archivo .py con comentarios
            file_content = f'"""\nPaso {i+1}: {description}\n"""\n\n'
            file_content += code

            zf.writestr(os.path.join("codigo_ejecutado", filename), file_content)

    # Rebobinar el buffer para que pueda ser leído desde el principio
    zip_buffer.seek(0)
    return zip_buffer

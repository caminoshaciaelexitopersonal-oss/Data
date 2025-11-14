import zipfile
import tarfile
import io
from typing import Dict

def decompress_files(filename: str, file_content: bytes) -> Dict[str, bytes]:
    """
    Descomprime un archivo ZIP o TAR.GZ en memoria.

    :param filename: El nombre del archivo original, para determinar el tipo de compresión.
    :param file_content: El contenido del archivo comprimido en bytes.
    :return: Un diccionario donde las claves son los nombres de los archivos extraídos
             y los valores son su contenido en bytes.
    :raises: ValueError si el tipo de archivo no está soportado.
    """
    extracted_files = {}

    if filename.lower().endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(file_content)) as zf:
            for name in zf.namelist():
                # Omitir directorios o archivos __MACOSX
                if not name.endswith('/') and '__MACOSX' not in name:
                    extracted_files[name] = zf.read(name)

    elif filename.lower().endswith(('.tar.gz', '.tgz')):
        with tarfile.open(fileobj=io.BytesIO(file_content), mode='r:gz') as tf:
            for member in tf.getmembers():
                if member.isfile():
                    f = tf.extractfile(member)
                    if f:
                        extracted_files[member.name] = f.read()

    else:
        raise ValueError(f"Tipo de archivo comprimido no soportado: {filename}")

    return extracted_files

from PyPDF2 import PdfReader, PdfWriter  # Para manejar archivos PDF
import os, fitz, re
from readpdf import get_data_user, get_user_data_by_OCR_METHOD
    
def limpiar_nombre_archivo(ruta_archivo, prefijo="", sufijo=""):
    """
    Modifica el nombre de un archivo:
    1. Elimina el patrón '_page_XX' del nombre
    2. Agrega un prefijo (opcional)
    3. Agrega un sufijo (opcional)
    
    Parámetros:
        ruta_archivo (str): Ruta completa del archivo
        prefijo (str): Texto para agregar al inicio del nombre
        sufijo (str): Texto para agregar antes de la extensión
    
    Retorna:
        str: Nueva ruta del archivo
    """
    try:
        # Obtenemos el directorio y el nombre del archivo
        directorio = os.path.dirname(ruta_archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        
        # Separamos el nombre y la extensión
        nombre_base, extension = os.path.splitext(nombre_archivo)
        
        # Eliminamos el patrón '_page_XX' usando expresiones regulares
        # El patrón busca '_page_' seguido de cualquier número de dígitos
        nombre_limpio = re.sub(r'_page_\d+', '', nombre_base)
        
        # Creamos el nuevo nombre con el prefijo y sufijo
        nuevo_nombre = f"{prefijo}{nombre_limpio}{sufijo}{extension}"
        
        # Construimos la nueva ruta completa
        nueva_ruta = os.path.join(directorio, nuevo_nombre)
        
        # Renombramos el archivo
        os.rename(ruta_archivo, nueva_ruta)
        print(f"Archivo modificado exitosamente:")
        print(f"Original: {nombre_archivo}")
        print(f"Nuevo: {nuevo_nombre}")
        
        return nueva_ruta
        
    except Exception as e:
        print(f"Error al modificar el archivo: {str(e)}")
        return None

def create_folder(path):
    # Obtenemos el directorio del script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio base: {base_dir}")
    
    # Construimos la ruta completa
    full_path = os.path.join(base_dir, path)
    print(f"Ruta completa a crear: {full_path}")
    
    try:
        os.makedirs(full_path, exist_ok=True)
        print(f"Carpeta creada exitosamente en: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error al crear la carpeta: {str(e)}")
        return None

def split_pdf_pages(input_pdf, output_certificates_path):
    """
    Divide un archivo PDF en páginas individuales y las guarda en un directorio específico.
    
    Parámetros:
    input_pdf (str): Ruta al archivo PDF que queremos dividir
    output_dir (str): Directorio donde se guardarán las páginas separadas
    """
    archivos_creados = []    
    pdf_name = os.path.basename(input_pdf)
    
    # Obtenemos el nombre sin la extensión .pdf
    pdf_name_without_extension = os.path.splitext(pdf_name)[0]
    print ('certificado', pdf_name_without_extension)

    path_folder = create_folder(f"certificates-split/{pdf_name_without_extension}")

    # Abrimos y leemos el PDF original
    reader = PdfReader(open(input_pdf, "rb"))
    
    # Obtenemos el número total de páginas
    total_pages = len(reader.pages)
    print(f"Total páginas: {total_pages}")
    
    # Procesamos cada página del PDF
    for page_num in range(total_pages):
        # Creamos un nuevo documento PDF para cada página
        writer = PdfWriter()
        
        # Extraemos la página actual
        current_page = reader.pages[page_num]
        
        # Añadimos la página al nuevo documento
        writer.add_page(current_page)
        
        # Construimos el nombre del archivo de salida
        output_pdf = os.path.join(path_folder, f"certificate_{pdf_name_without_extension}_page_{str(page_num+1)}.pdf")
        
        # Guardamos la página como un nuevo archivo PDF
        with open(output_pdf, "wb") as output:
            writer.write(output)
        
        archivos_creados.append(output_pdf)
        # Informamos al usuario que se ha creado el archivo
        print(f"Creado archivo: {output_pdf}")
    
    return archivos_creados

def process_pdf_directory(input_directory):
    """
    Procesa todos los archivos PDF en un directorio específico.
    
    Parámetros:
    input_directory (str): Ruta al directorio que contiene los archivos PDF a procesar
    """
    # Verificamos que el directorio existe
    if not os.path.exists(input_directory):
        print(f"El directorio {input_directory} no existe")
        return
    
    # Obtenemos la lista de todos los archivos en el directorio
    files = os.listdir(input_directory)
    
    # Filtramos solo los archivos PDF
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No se encontraron archivos PDF en {input_directory}")
        return
    
    print(f"Se encontraron {len(pdf_files)} archivos PDF para procesar")
    
    # Procesamos cada archivo PDF
    for pdf_file in pdf_files:
        # Construimos la ruta completa al archivo PDF
        pdf_path = os.path.join(input_directory, pdf_file)
        print(f"\nProcesando: {pdf_file}")
        
        try:
            # Utilizamos tu función existente para procesar cada PDF
            output_certificates_path = os.path.join(os.path.dirname(__file__), "certificates-split")
            certificates = split_pdf_pages(pdf_path, output_certificates_path)
            # print(f"Archivos creados: {archivos_creados}")

            for split_certificate in certificates:
                certificado_user = {
                    "name": None,
                    "cc": None
                }

                print(f"path", split_certificate)
                datos_usuario = get_data_user(split_certificate)

                if datos_usuario is None:
                    print('OCR function ******************************** ')
                    data_user_OCR = get_user_data_by_OCR_METHOD(split_certificate)
                    print(f"Datos extraídos por OCR: {data_user_OCR}")
                    # Obtenemos los datos del usuario
                    certificado_user['name'] = data_user_OCR.nombre
                    certificado_user['cc'] = data_user_OCR.identificacion
                else:                    
                    certificado_user['name'] = datos_usuario.get("name")
                    certificado_user['cc'] = datos_usuario.get("cc")
                
                prefijo = f"{certificado_user['cc']}_{certificado_user['name']}_"
        
                print('metadata PDF found',prefijo)
                
                # # Renombramos el archivo y actualizamos la ruta
                nueva_ruta = limpiar_nombre_archivo(split_certificate, prefijo=prefijo, sufijo="_done")
                
                # Actualizamos la ruta original con la nueva para la siguiente iteración
                if nueva_ruta:
                    split_certificate = nueva_ruta
                print(f"Datos extraídos de {split_certificate}:", datos_usuario)

        except Exception as e:
            print(f"Error procesando {pdf_file}: {str(e)}")

if __name__ == "__main__":
    output_certificates_path = os.path.join(os.path.dirname(__file__), "certificates-split")
    pdf_directory = "./certificates-raw"
    archivos_creados = process_pdf_directory(pdf_directory)

    # ruta_archivo = "/home/desarrollo/Pictures/split-certificates/processed-certificates/Formación continua en anestesia y mantemiento del paciente trasplantado/nuevo_documentooks.pdf"
    # nuevo_nombre = "nuevo_documentooks"
    
    # nueva_ruta = limpiar_nombre_archivo(
    #         ruta_archivo=ruta_archivo,
    #         prefijo="processed_",
    #         sufijo="_done"
    #     )
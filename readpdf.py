import fitz
import re
import pytesseract
from PIL import Image
import io, time
from PyPDF2 import PdfReader, PdfWriter  # Para manejar archivos PDF
from ia import  get_inference_for_pdf_open_ai

def get_data_user(pdf_path):
    certificado = {
        "name": None,
        "cc": None
    }
    # Abrimos y leemos el PDF
    reader = PdfReader(pdf_path)
    # Obtenemos el texto de la primera página
    text = reader.pages[0].extract_text()
    if not text:
        return None 
   
    print(text)
    lineas = text.split('\n')
    # Buscamos las líneas que contienen el nombre y CC
    for i, linea in enumerate(lineas):
        if 'CC' in linea:
            # El nombre está en la línea anterior
            nombre = lineas[i-1].strip()
            
            cc = linea.replace('CC', '')  # Quita 'CC'
            cc = cc.replace('.', '')      # Quita puntos
            cc = cc.strip()               # Quita espacios al inicio y final
            certificado["name"] = nombre
            certificado["cc"] = cc
    
    if certificado["name"] is None or certificado["cc"] is None:
        print("No se pudieron obtener los datos del certificado.")
        return None
    
    return certificado

def get_user_data_by_OCR_METHOD(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        try:
            # Convertimos la página a imagen
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Aumentamos la resolución
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # Realizamos OCR
            text = pytesseract.image_to_string(img)
            # print (text)
            time.sleep(0.1)
            user_data = get_inference_for_pdf_open_ai(text)
            return user_data
        except Exception as e:
            print(f"Error en el procesamiento del pdf usando OCR: {str(e)}")
            return None
    doc.close()

if __name__ == "__main__":
    pdf_path = "/home/desarrollo/Pictures/split-certificates/certificates-raw/SALVACORAZONES FCI JULIO 17-23.pdf"
    user_data = {}
    try:
        user_data_m = get_data_user(pdf_path)
        print("User data", user_data_m)
        
                
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
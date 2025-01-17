# from google import genai
# from google.genai import types
from openai import OpenAI
from typing import Optional, Dict, Any
import json
class InferenceError(Exception):
    """Clase personalizada para errores de inferencia"""
    pass

class ResponseParsingError(Exception):
    """Clase personalizada para errores de parsing de respuesta"""
    pass

class CertificateInfo:
    """Clase para almacenar la información extraída del certificado"""
    def __init__(self, nombre: Optional[str], identificacion: Optional[str]):
        self.nombre = nombre
        self.identificacion = identificacion

    def __str__(self):
        return f"CertificateInfo(nombre='{self.nombre}', identificacion='{self.identificacion}')"
    
gemini_key = ''

# client = genai.Client(api_key=gemini_key)
client_open_ai = OpenAI(api_key='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')

prompt="Tu tarea es extraer información específica de certificados de cursos y capacitaciones. Instrucciones: 1. Lee cuidadosamente el texto del certificado proporcionado 2. Identifica el nombre completo de la persona certificada 3. Identifica el número de identificación (puede estar precedido por C.C., Cédula, DNI, etc.) 4. Devuelve la información en formato JSON con las siguientes claves: - 'nombre': nombre completo de la persona - 'identificacion': número de identificación (solo números, sin prefijos) Si algún campo no se encuentra, devuelve null para ese campo. Ejemplo de entrada: CERTIFICA A: JUAN CARLOS PEREZ MARTINEZ C.C. 79845632 Por su asistencia... Ejemplo de salida: { 'nombre': 'JUAN CARLOS PEREZ MARTINEZ', 'identificacion': '79845632' } El contendo es diverso si no puedes inferir que se certifica con un nombre como CERTIFICA A: JUAN CARLOS PEREZ MARTINEZ devuelve null ya que no todos los nombres son validos ya que pueden ser el nombre de la intitucion o el nombre del certificado o quien firma pero queremos obtener a quien se otorga y si tiene , el nombre quitala A partir de ahora, procesa el siguiente texto y devuelve solo el JSON:"

def parse_inference_response(response_text: str) -> CertificateInfo:
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise ResponseParsingError("No se encontró una estructura JSON válida en la respuesta")
        
        json_str = response_text[start_idx:end_idx + 1]
        
        data = json.loads(json_str)
        
        if not isinstance(data, dict):
            raise ResponseParsingError("La respuesta no es un objeto JSON válido")
        
        if 'nombre' not in data:
            raise ResponseParsingError("Falta el campo 'nombre' en la respuesta")
        
        return CertificateInfo(
            nombre=data.get('nombre'),
            identificacion=data.get('identificacion')
        )
    
    except json.JSONDecodeError as e:
        print(f"Texto recibido: {response_text}")
        print(f"Intento de JSON: {json_str if 'json_str' in locals() else 'No se pudo extraer JSON'}")
        raise ResponseParsingError(f"Error al decodificar JSON: {str(e)}")
    except Exception as e:
        raise ResponseParsingError(f"Error inesperado al procesar la respuesta: {str(e)}")

# def get_inference_for_pdf(content_certificate):
#     try:
#         response = client.models.generate_content(
#             model='gemini-2.0-flash-exp',
#             contents=content_certificate,
#             config=types.GenerateContentConfig(
#                 system_instruction= "Tu tarea es extraer información específica de certificados de cursos y capacitaciones. Instrucciones: 1. Lee cuidadosamente el texto del certificado proporcionado 2. Identifica el nombre completo de la persona certificada 3. Identifica el número de identificación (puede estar precedido por C.C., Cédula, DNI, etc.) 4. Devuelve la información en formato JSON con las siguientes claves: - 'nombre': nombre completo de la persona - 'identificacion': número de identificación (solo números, sin prefijos) Si algún campo no se encuentra, devuelve null para ese campo. Ejemplo de entrada: CERTIFICA A: JUAN CARLOS PEREZ MARTINEZ C.C. 79845632 Por su asistencia... Ejemplo de salida: { 'nombre': 'JUAN CARLOS PEREZ MARTINEZ', 'identificacion': '79845632' } El contendo es diverso si no puedes inferir que se certifica con un nombre como CERTIFICA A: JUAN CARLOS PEREZ MARTINEZ devuelve null ya que no todos los nombres son validos ya que pueden ser el nombre de la intitucion o el nombre del certificado o quien firma pero queremos obtener a quien se otorga, A partir de ahora, procesa el siguiente texto y devuelve solo el JSON:",
#                 temperature= 0.3,
#             ),
#         )
#         # Validamos la respuesta
#         if not response.text:
#             raise InferenceError("La API no devolvió ninguna respuesta")

#         # Procesamos la respuesta
#         certificate_info = parse_inference_response(response.text)
#         return certificate_info
#     except Exception as e:
#         print(f"Error inesperado en la API: {str(e)}")
#         return None

def get_inference_for_pdf_open_ai(content_certificate):
    # full_message = f"{prompt}\n\nAnaliza el siguiente texto:\n{content_certificate}"
    try:
        completion = client_open_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            store=True,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content_certificate}
            ],
            temperature=0.3 
        )
        # Extraemos la respuesta del modelo
        response_text = completion.choices[0].message.content

        # Validamos que tengamos una respuesta
        if not response_text:
            raise Exception("La API no devolvió ninguna respuesta")
            
        # Procesamos la respuesta usando la misma función que teníamos
        certificate_info = parse_inference_response(response_text)
        print(f"Información extraída: {certificate_info}")
        return certificate_info
    except Exception as e:
        print(f"Error inesperado en la API de OpenAI: {str(e)}")
        return None

# Ejemplo de uso con un PDF que contiene el texto del certificado

if __name__ == "__main__":
    content_pdf="Texto extraído por OCR: i laCardio FUNDACION CARDIOINFANTIL — INSTITUTO DE CARDIOLOGIA HOSPITAL SIMULADO “CAMILO CABRERA” CERTIFICA A: MANUEL ANTONIO GARCIA LOPEZ C.C. 79980864 Por su asistencia y aprobacion del curso: REANIMACION CARDIOPULMONAR BASICA SALVACORAZONES DEA Realizado en la ciudad de Bogota El dia 17 de Julio de 2023 Con una intensidad de 20 Horas En calidad de: PROVEEDOR Curso Oficial que sigue los lineamientos establecidos por la American Heart Association JAIME FERNANDEZ SARMIENTO M.D. Director Hospital Simulado “Camilo Cabrera”"
    inference = get_inference_for_pdf_open_ai(content_pdf)
    print (inference)
# firmar_sri_py.py
import os
from lxml import etree
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.backends import default_backend
from signxml import XMLSigner, methods

def firmar_xml_python(ruta_xml_entrada, ruta_firma_p12, password_p12, ruta_xml_salida):
    """
    Firma un XML usando un archivo .p12 y lo guarda en la ruta de salida.
    Reemplaza la funcionalidad de Node.js.
    """
    print(f"🔐 Iniciando firma digital nativa en Python para: {ruta_xml_entrada}")

    # 1. Cargar el archivo .p12
    try:
        with open(ruta_firma_p12, "rb") as f:
            p12_data = f.read()
        
        # Convertir password a bytes si es string
        if isinstance(password_p12, str):
            password_bytes = password_p12.encode('utf-8')
        else:
            password_bytes = password_p12
            
        private_key, certificate, additional_certificates = load_key_and_certificates(
            p12_data,
            password_bytes,
            backend=default_backend()
        )
        print("✅ Certificado y clave privada cargados correctamente.")

    except Exception as e:
        return {"status": "error", "mensaje": f"Error leyendo firma P12: {str(e)}"}

    # 2. Cargar el XML a firmar
    try:
        with open(ruta_xml_entrada, "rb") as f:
            xml_data = f.read()
        root = etree.fromstring(xml_data)
    except Exception as e:
        return {"status": "error", "mensaje": f"Error leyendo XML de entrada: {str(e)}"}

    # 3. Configurar y Ejecutar la Firma (XAdES-BES básica para SRI)
    try:
        # El SRI requiere que la firma esté 'enveloped' (dentro del mismo XML)
        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha256", # El SRI suele usar SHA1, aunque SHA256 es más moderno
            digest_algorithm="sha256",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        )

        # Firmamos
        signed_root = signer.sign(
            root,
            key=private_key,
            cert=[certificate]
        )

        # Convertir a string y guardar
        signed_xml_str = etree.tostring(signed_root, encoding='UTF-8', xml_declaration=True)
        
        with open(ruta_xml_salida, "wb") as f:
            f.write(signed_xml_str)
            
        print(f"✅ XML firmado guardado en: {ruta_xml_salida}")
        return {"status": "ok", "ruta_firmada": ruta_xml_salida}

    except Exception as e:
        return {"status": "error", "mensaje": f"Error durante el proceso de firma: {str(e)}"}

# Bloque para probarlo solo (sin correr toda la app)
if __name__ == "__main__":
    # 1. Asegúrate de que esta carpeta exista
    if not os.path.exists("FIRMADOS"):
        os.makedirs("FIRMADOS")

    # 2. Datos de prueba (Asegúrate de que sean los correctos)
    xml_prueba = "GENERADOS/factura_prueba.xml"
    p12_prueba = "CERTIFICADOS/LUIS SAENZ Luis2025.p12" # <--- ¡REVISA QUE ESTE NOMBRE SEA EL CORRECTO!
    pass_prueba = "Luis2025"               # <--- ¡REVISA TU CONTRASEÑA!

    # 3. Ejecutar y MOSTRAR RESULTADO
    if os.path.exists(xml_prueba) and os.path.exists(p12_prueba):
        # Guardamos la respuesta en una variable
        resultado = firmar_xml_python(xml_prueba, p12_prueba, pass_prueba, "FIRMADOS/prueba_exitosa.xml")
        
        # Imprimimos lo que pasó
        print("\n--- RESULTADO FINAL ---")
        print(resultado) 
    else:
        print("⚠️ FALTAN INGREDIENTES:")
        if not os.path.exists(xml_prueba): print(f" - No encuentro el XML: {xml_prueba}")
        if not os.path.exists(p12_prueba): print(f" - No encuentro la firma: {p12_prueba}")
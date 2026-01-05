# -*- coding: utf-8 -*-
from zeep import Client, Settings
from zeep.transports import Transport
from lxml import etree
import os
import sys
from datetime import datetime
from zeep.helpers import serialize_object
import json

def enviar_al_sri(xml_firmado_path, ambiente="2", timeout=30):
    """Envía XML al SRI con manejo robusto de errores"""
    try:
        # Validación estricta
        if not os.path.isfile(xml_firmado_path):
            raise FileNotFoundError(f"Archivo no encontrado: {xml_firmado_path}")
            
        if ambiente not in ("1", "2"):
            raise ValueError("Ambiente debe ser '1' (pruebas) o '2' (producción)")
            
        # Configuración WSDL
        if ambiente == "1":
            wsdl_url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
        else:
            wsdl_url = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
        
        # Configurar cliente Zeep robusto
        print(f"🔍 Enviando a ambiente: {ambiente} → WSDL: {wsdl_url}")
        settings = Settings(
            strict=False,
            xml_huge_tree=True,
            extra_http_headers={'Connection': 'keep-alive'}
        )
        
        transport = Transport(
            timeout=timeout,
            operation_timeout=timeout
        )

        client = Client(wsdl_url, settings=settings, transport=transport)

        # Leer y validar XML
        with open(xml_firmado_path, 'rb') as f:
            xml_data = f.read()
        
        try:
            etree.fromstring(xml_data)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML mal formado: {str(e)}")

        # Intento de envío
        response = client.service.validarComprobante(xml_data)

        # Procesamiento de respuesta
        estado = getattr(response, 'estado', 'DESCONOCIDO')
        mensajes = []
        clave_registrada = False
        if hasattr(response, 'comprobantes') and response.comprobantes:
            for comp in response.comprobantes.comprobante:
                if hasattr(comp, 'mensajes') and comp.mensajes:
                    for msg in comp.mensajes.mensaje:
                        texto = getattr(msg, 'mensaje', '').upper()
                        if "CLAVE ACCESO REGISTRADA" in texto:
                            clave_registrada = True
        
                        identificador = getattr(msg, 'identificador', '')
                        mensaje_principal = getattr(msg, 'mensaje', '')
                        detalle = getattr(msg, 'informacionAdicional', '')
                        if detalle:
                            mensaje_completo = f"{identificador}: {mensaje_principal} - {detalle}"
                        else:
                            mensaje_completo = f"{identificador}: {mensaje_principal}"
                        mensajes.append(mensaje_completo)

        mensaje = " | ".join(mensajes) if mensajes else estado

        # Devolver resultado
        return (estado, mensaje, clave_registrada)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR en línea {exc_tb.tb_lineno}: {str(e)}")
        return ("ERROR", str(e), None)
    
    
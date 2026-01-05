# backend/Generador_de_XML_a_Excel.py
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import os
import re

# Importamos tu nuevo firmador de Python (asegúrate que firmar_sri_py.py esté en la misma carpeta)
from firmar_sri_py import firmar_xml_python

def generar_factura(row, output_dir):
    try:
        factura_raw = str(row['FACTURA']).strip()
        num_match = re.search(r'\d+', factura_raw)

        if not num_match:
            raise ValueError(f"FACTURA inválida en fila: '{factura_raw}'")

        num_factura = re.sub(r'\D', '', factura_raw)[-9:].zfill(9)
        cliente = row.get('CLIENTE') or row.get('MARCACION')
        tallos = float(row['TALLOS'])
        precio_unitario = float(row['PU']) 
        fob = float(row['FOB']) 
        descuento = float(row['DESCUENTO'])
        
        if isinstance(row['FECHA FACTURA'], str):
            fecha_emision = datetime.strptime(row['FECHA FACTURA'], "%d/%m/%Y")
        else:
            fecha_emision = row['FECHA FACTURA']

        fecha_str = fecha_emision.strftime("%d%m%Y")
        fecha_emision_formatted = fecha_emision.strftime("%d/%m/%Y")
        
        info_texto = row["INFO ADICIONAL"] if pd.notna(row["INFO ADICIONAL"]) else " "

        def format_price(number):
            s = f"{number:.6f}"
            if '.' in s:
                s = s.rstrip('0').rstrip('.')
            return s
        
        formatted = format_price(precio_unitario)
        
        # --- BLOQUE DE CLAVE DE ACCESO ---
        # NOTA: Aquí deberías usar el RUC real de la fila o config, puse uno fijo por compatibilidad con el código
        ruc_emisor = "1714208806001" 
        ambiente = "1"
        serie = "002002"
        codigo_num = "43762667"
        
        clave_incompleta = (fecha_str + "01" + ruc_emisor + ambiente + serie + num_factura + codigo_num + "1")

        def calcular_digito_verificador(clave_sin_digito):
            digits = clave_sin_digito[::-1]
            suma = 0
            factor = 2
            for i in range(len(digits)):
                suma += int(digits[i]) * factor
                factor = 2 if factor == 7 else factor + 1
            dv = 11 - (suma % 11)
            return 1 if dv == 10 else 0 if dv == 11 else dv
            
        digito_verificador = calcular_digito_verificador(clave_incompleta)
        clave_acceso = clave_incompleta + str(digito_verificador)

        # Crear XML
        factura = ET.Element("factura", id="comprobante", version="1.1.0")
        
        info_trib = ET.SubElement(factura, "infoTributaria")
        ET.SubElement(info_trib, "ambiente").text = ambiente
        ET.SubElement(info_trib, "tipoEmision").text = "1"
        ET.SubElement(info_trib, "razonSocial").text = "SAENZ SAENZ LUIS RAMIRO"
        ET.SubElement(info_trib, "nombreComercial").text = "SAENZ SAENZ LUIS RAMIRO"
        ET.SubElement(info_trib, "ruc").text = ruc_emisor
        ET.SubElement(info_trib, "claveAcceso").text = clave_acceso       
        ET.SubElement(info_trib, "codDoc").text = "01"
        ET.SubElement(info_trib, "estab").text = serie[:3]
        ET.SubElement(info_trib, "ptoEmi").text = serie[3:]
        ET.SubElement(info_trib, "secuencial").text = num_factura
        ET.SubElement(info_trib, "dirMatriz").text = "PICHINCHA / PEDRO MONCAYO / TOCACHI / PRINCIPAL SN Y PANAMERICANA"

        info_fact = ET.SubElement(factura, "infoFactura")
        ET.SubElement(info_fact, "fechaEmision").text = fecha_emision_formatted
        ET.SubElement(info_fact, "dirEstablecimiento").text = "PICHINCHA / PEDRO MONCAYO / TOCACHI / PRINCIPAL SN Y PANAMERICANA EXPORTADOR HABITUAL DE BIENES"
        ET.SubElement(info_fact, "obligadoContabilidad").text = "NO"
        ET.SubElement(info_fact, "comercioExterior").text = "EXPORTADOR"
        ET.SubElement(info_fact, "incoTermFactura").text = "FOB"
        ET.SubElement(info_fact, "lugarIncoTerm").text = "QUITO"
        ET.SubElement(info_fact, "paisOrigen").text = "593"
        ET.SubElement(info_fact, "puertoEmbarque").text = "QUITO"
        ET.SubElement(info_fact, "puertoDestino").text = str(row['DESTINO'])
        ET.SubElement(info_fact, "tipoIdentificacionComprador").text = "08"
        ET.SubElement(info_fact, "razonSocialComprador").text = str(cliente)
        ET.SubElement(info_fact, "identificacionComprador").text = str(int(row['IDENTIFICACION DEL COMPRADOR']))
        ET.SubElement(info_fact, "totalSinImpuestos").text = f"{fob:.2f}"
        ET.SubElement(info_fact, "incoTermTotalSinImpuestos").text = "FOB"
        ET.SubElement(info_fact, "totalDescuento").text = f"{descuento:.2f}"

        total_con_impuestos = ET.SubElement(info_fact, "totalConImpuestos")
        total_impuesto = ET.SubElement(total_con_impuestos, "totalImpuesto")
        ET.SubElement(total_impuesto, "codigo").text = "2"
        ET.SubElement(total_impuesto, "codigoPorcentaje").text = "0"
        ET.SubElement(total_impuesto, "baseImponible").text = f"{fob:.2f}"
        ET.SubElement(total_impuesto, "tarifa").text = "0.00"
        ET.SubElement(total_impuesto, "valor").text = "0.00"
        
        ET.SubElement(info_fact, "propina").text = "0.00"
        ET.SubElement(info_fact, "importeTotal").text = f"{fob:.2f}"
        ET.SubElement(info_fact, "moneda").text = "DOLAR"
        
        pagos = ET.SubElement(info_fact, "pagos")
        pago = ET.SubElement(pagos, "pago")
        ET.SubElement(pago, "formaPago").text = "20"
        ET.SubElement(pago, "total").text = f"{fob:.2f}"

        detalles = ET.SubElement(factura, "detalles")
        detalle = ET.SubElement(detalles, "detalle")
        ET.SubElement(detalle, "codigoPrincipal").text = "0001"
        ET.SubElement(detalle, "codigoAuxiliar").text = "0001"
        ET.SubElement(detalle, "descripcion").text = "ROSAS"
        ET.SubElement(detalle, "cantidad").text = f"{tallos:.2f}"
        ET.SubElement(detalle, "precioUnitario").text = formatted
        ET.SubElement(detalle, "descuento").text = f"{descuento:.2f}"
        ET.SubElement(detalle, "precioTotalSinImpuesto").text = f"{fob:.2f}"
        
        detalles_adicionales = ET.SubElement(detalle, "detallesAdicionales")
        ET.SubElement(detalles_adicionales, "detAdicional", nombre="TALLOS", valor="TALLOS")
        ET.SubElement(detalles_adicionales, "detAdicional", nombre="USHTS 06031100000", valor="USHTS")
        
        impuestos = ET.SubElement(detalle, "impuestos")
        impuesto = ET.SubElement(impuestos, "impuesto")
        ET.SubElement(impuesto, "codigo").text = "2"
        ET.SubElement(impuesto, "codigoPorcentaje").text = "0"
        ET.SubElement(impuesto, "tarifa").text = "0.00"
        ET.SubElement(impuesto, "baseImponible").text = f"{fob:.2f}"
        ET.SubElement(impuesto, "valor").text = "0.00"
        
        info_adicional = ET.SubElement(factura, "infoAdicional")
        ET.SubElement(info_adicional, "campoAdicional", nombre="  ").text = info_texto

        # Guardar XML
        tree = ET.ElementTree(factura)
        ET.indent(tree, space="\t", level=0)
        xml_str = ET.tostring(factura, encoding="unicode")
        
        # Hacks de formato SRI
        xml_str = xml_str.replace('<puertoEmbarque>', '\t<puertoEmbarque>').replace('<puertoDestino>', '\t<puertoDestino>')
        xml_str = xml_str.replace(' />', '/>').replace('<paisOrigen>\n\t', '<paisOrigen>')
        
        archivo_salida = os.path.join(output_dir, f"{clave_acceso}.xml")
        with open(archivo_salida, 'w', encoding='UTF-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            f.write(xml_str)
        
        return archivo_salida
        
    except Exception as e:
        print(f"Error generando XML: {str(e)}")
        return None

def procesar_excel_web(dataframe, carpeta_generados, carpeta_firmados, ruta_p12, clave_p12):
    """
    Función maestra para la web:
    1. Recibe el DataFrame del Excel subido.
    2. Genera los XMLs.
    3. Los firma automáticamente con Python.
    4. Devuelve una lista de lo que hizo.
    """
    reporte = []
    
    for index, row in dataframe.iterrows():
        try:
            if pd.notna(row.get('FACTURA')):
                # 1. Generar
                xml_generado = generar_factura(row, carpeta_generados)
                
                if xml_generado:
                    # 2. Firmar (Usando tu script de Python, NO Node.js)
                    nombre_archivo = os.path.basename(xml_generado)
                    ruta_salida_firmado = os.path.join(carpeta_firmados, nombre_archivo.replace(".xml", "_firmado.xml"))
                    
                    resultado_firma = firmar_xml_python(xml_generado, ruta_p12, clave_p12, ruta_salida_firmado)
                    
                    if resultado_firma["status"] == "ok":
                        reporte.append({
                            "factura": str(row['FACTURA']),
                            "estado": "OK",
                            "archivo": nombre_archivo,
                            "mensaje": "Generado y Firmado"
                        })
                    else:
                        reporte.append({
                            "factura": str(row['FACTURA']),
                            "estado": "ERROR FIRMA",
                            "mensaje": resultado_firma["mensaje"]
                        })
                else:
                    reporte.append({"factura": str(row['FACTURA']), "estado": "ERROR GENERACION", "mensaje": "Fallo al crear XML"})
        except Exception as e:
             reporte.append({"factura": f"Fila {index}", "estado": "ERROR CRITICO", "mensaje": str(e)})
             
    return reporte
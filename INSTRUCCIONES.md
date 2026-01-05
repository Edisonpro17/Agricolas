**PROGRAMA PARA EXPORTAR EXCEL A XML Y AUTORIZAR XML**
--- 

PASOS QUE HICE PARA MIGRAR A WEB EL PROYECTO CLI DE AGRICOLAS.

crear un pequeño server independiente del cli para la correcta ejecución y apropiado funcionamiento.

Primer punto de vista:
Complicación del programador Jeremy al querer utilizar python y node.js dentro de su backend puesto que esto es costoso y propenso a errores. Al hacerlo 100% Python, el despliegue será sencillo y robusto.


Cambio:
Actualmente su flujo es: Python (genera) → Node.js (firma) → Python (envía). Vamos a cambiarlo a: Python (genera) → Python (firma) → Python (envía).


SHA1 es una tecnología vieja y ya no es segura, el SRI de Ecuador acepta SHA256, que es más moderno y seguro. Así que la solución es actualizar tu código para usar el estándar nuevo.


Utilizaré como motor web a FastAPI y para correr nuestro servidor Uvicorn. Por cierto para mantener python puro utilizaré python-multipart que es una librería que le permite al usuario subir sus archivos que es lo que buscamos, más específicamente los Excel.

Organicé las carpetas para nuestro backend para poner a prueba el mismo y tener un backend funcional para la web.
Ahora me centrare en la lógica del botón de subida de archivos para que el cliente pueda tener facilidad de uso, ya que la lógica esta centrada solamente en CLI.


Ahora lo mas importante, eh estado en duda, en cuestión del uso de frameworks para la parte visual (Frontend). Por términos de tiempo y acortamiento de complejidad eh optado el uso de HTML puro con estilos tipo Tailwind CSS para nuestro frontend. Y en caso de ser necesario mejoras o escalabilidad del programa, veré prudente el uso de frameworks tomando como segunda alternativa "React".



si Subir archivo y poner contra
si Inventario
aun no Facturacion manual
si BDD

Seguridad:
Encriptacion de contraseñas dentro de BDD. Credenciales escondidas en .env. Cooldown de 30 min. Por inactividad para mayor protección. Cooldown de 1 min. por cada 5 intentos de ingreso de contraseña para evitar que una máquina pruebe 10,000 contraseñas por segundo. Creación de un script para el cambio de usuarios  y claves administrativas (Las cuales serán cambiadas para cada dominio independiente de cada agrícola).

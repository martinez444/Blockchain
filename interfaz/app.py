# --------------------------
# !Certificación SSL omitida
# --------------------------

from flask import Flask, request, jsonify, render_template
import hashlib
from web3 import Web3, HTTPProvider
import ssl
import requests
from datetime import datetime
import urllib3
import os
import json
import pytz # Para la zona horaria UTC
import socket # Para obtener la IP del servidor

# --------------------------
# Parchear verificación SSL
# --------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
old_request = requests.Session.request

def unsafe_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return old_request(self, method, url, **kwargs)

requests.Session.request = unsafe_request

# --------------------------
# Configuración
# 
# Esta parte debería estar en un archivo de configuración separado, para así aumentar la seguridad y la mantenibilidad del código.
# --------------------------
PRIVATE_KEY = "45d89b438b406209ddd40b383365452532c0ff8a20216e4da5d0c108ac438a1b" # Clave privada de la billetera usada para pagar las transacciones
ADDRESS = "0x5115A56d10046aD49Ce8cC0B11A8a496945E5716" # Dirección de la billetera
SEPOLIA_RPC = "https://eth-sepolia.g.alchemy.com/v2/2SAz6OP1qiVjFyDHYbrtbwJvdv1P_hwe" # Nodo blockchain de Sepolia (Alchemy)

# Instancias de conexión
w3 = Web3(HTTPProvider(SEPOLIA_RPC)) # Instancia de conexión al nodo blockchain
cuenta = w3.eth.account.from_key(PRIVATE_KEY) # Instancia de la cuenta a partir de la clave privada

# Flask
app = Flask(__name__)

# Ubicación del archivo de log
log_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_dir, "log.txt")

# Hash de archivo en formato SHA-256
def hash_archivo(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

# Guardar en el fichero de log
def create_Log(fecha, operacion, nArchivo, hLocal, hRecibido, tx_Hash, resultado, msg, usuario, ipUsuario, ipCliente):
    log = fecha + "~" + operacion + "~" + nArchivo  + "~" + hLocal + "~" + hRecibido + "~" + tx_Hash + "~" + resultado + "~" + msg + "~" + usuario + "~" + ipUsuario + "~" + ipCliente
    with open(log_path, "a") as f:
        f.write(log + "\n")

def get_client_ip():
    """Obtiene la IP real del cliente, incluso si hay un proxy entre medias."""
    # Si hay cabeceras 'X-Forwarded-For', usa la primera IP listada (IP original del cliente)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        # Sin proxy, la IP viene directamente de remote_addr
        ip = request.remote_addr
    return ip

def leer_txt_como_tabla(ruta_archivo):
    tabla = []
    with open(ruta_archivo, encoding='utf-8') as f:
        for linea in f:
            celdas = linea.strip().split('~')
            if celdas:  # Ignorar líneas vacías
                tabla.append(celdas)
    return tabla

# Página principal
@app.route("/")
def index():
    datos = leer_txt_como_tabla("C:/Users/david.benllochpenin/Desktop/blockchain/interfaz/log.txt")  # Cambia el nombre si es necesario
    return render_template("index.html", tabla=datos)

# Endpoint para subir el hash de un archivo a la blockchain
@app.route("/subir", methods=["POST"])
def subir():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['file']
    filepath = os.path.abspath(file.filename)
    file.save(filepath)
    nombre_archivo = os.path.basename(filepath) # Se obtiene el nombre del archivo a partir de la ruta
    
    client_ip = get_client_ip()
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    fecha_hora = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    hash_hex = ""
    try:
        
        hash_hex = hash_archivo(filepath)
        nonce = w3.eth.get_transaction_count(cuenta.address, 'pending') # Número de transacción; se recupera el número de transacciones realizadas, incluyendo las pendientes
        tx = {
            "nonce": nonce,
            "to": ADDRESS, # Destinatario de la transacción (en este caso nos la enviamos a nosotros mismos)
            "value": 0, # Cantidad transferida (En ETH)
            "gas": 25000, # Máxima cantidad de "trabajo" que se puede usar en una transacción 
            "gasPrice": w3.to_wei("50", "gwei"),
            "data": w3.to_bytes(hexstr=hash_hex), # Datos adicionales de la transacción (en este caso el hash del archivo convertido a bytes)
            "chainId": 11155111 # ID de la red Sepolia
        }
        signed_tx = cuenta.sign_transaction(tx) # Se firma la transacción
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) # Se envía la transacción firmada a la red y se guarda el hash de la transacción
        tx_hash_str = w3.to_hex(tx_hash) # El hash de la transacción se convierte a string hexadecimal

        
        """
        # Guardar en subidas.json
        try:
            with open("subidas.json", "r", encoding="utf-8") as f:
                historial = json.load(f)
        except FileNotFoundError:
            historial = []

        historial.append({
            "fecha_hora": fecha_hora,
            "tx_hash": tx_hash_str,
            "ruta_archivo": filepath
        })

        with open("subidas.json", "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
        """
        create_Log(fecha_hora, "UPLOAD", nombre_archivo, hash_hex, "", tx_hash_str, "OK", "Archivo subido correctamente", "Usuario", server_ip, client_ip) # Guardar en el log
        #Mensaje que se printea en la consola
        return jsonify({
            "hash_archivo": hash_hex,
            "tx_hash": tx_hash_str,
            "etherscan_url": f"https://sepolia.etherscan.io/tx/{tx_hash_str}"# URL para ver la transacción en Etherscan (Puede tardar bastante en aparecer)
        })

    except Exception as e:
        create_Log(fecha_hora, "upload", filepath, hash_hex, "", "", "ERROR", str(e), "Usuario", server_ip, client_ip) # Guardar en el log
        return jsonify({"error": str(e)}), 500

# Ruta para bajar el hash de un archivo a raiz del hash de una transacción y compararlo con el hash del archivo local (que puede haber sido modificado o no)
@app.route("/bajar", methods=["POST"])
def bajar():
    fecha_hora = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    client_ip = get_client_ip()
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    hash_local = ""
    hash_enviado = ""
    tx_hash = ""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                "tx_hash": request.form.get("tx_hash"),
                "ruta_archivo": request.form.get("ruta_archivo")
            }

        tx_hash = data.get("tx_hash")
        ruta_archivo = data.get("ruta_archivo")
        nombre_archivo = os.path.basename(ruta_archivo) # Se obtiene el nombre del archivo a partir de la ruta
        if not tx_hash or not ruta_archivo:
            return jsonify({"error": "Se debe proporcionar tx_hash y ruta_archivo"}), 400

        tx = w3.eth.get_transaction(tx_hash) # Se obtiene la transacción a partir del hash de transacción que hemos indicado
        hash_enviado = tx['input'].hex() # Se obtiene el hash del archivo a partir de la transacción (en este caso, el hash del archivo se encuentra en el campo "input" de la transacción)
        hash_local = hash_archivo(ruta_archivo) # Se saca el hash del archivo local

        mensaje = "El archivo es autentico. Los hashes coinciden." if hash_enviado == hash_local else "El archivo no coincide. Los hashes son diferentes." # Se compara el hash del archivo local
        """
        # Se guardan los datos en el archivo verificaciones.json
        verificacion = {
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ruta_archivo": ruta_archivo,
            "hash_local": hash_local,
            "tx_hash": tx_hash,
            "hash_enviado": hash_enviado,
            "resultado": mensaje
        }

        try:
            with open("verificaciones.json", "r", encoding="utf-8") as f:
                historial = json.load(f)
        except FileNotFoundError:
            historial = []

        historial.append(verificacion)

        with open("verificaciones.json", "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
        """
        
        
        create_Log(fecha_hora, "DOWNLOAD", nombre_archivo, hash_local, hash_enviado, tx_hash, "OK", mensaje, "Usuario", server_ip, client_ip) # Guardar en el log
        # Mensaje que se printea en consola
        return jsonify({
            "mensaje": mensaje,
            "hash_local": hash_local,
            "hash_enviado": hash_enviado
        })

    except Exception as e:
        create_Log(fecha_hora, "download", ruta_archivo, hash_local, hash_enviado, tx_hash, "ERROR", str(e), "Usuario", server_ip, client_ip) # Guardar en el log
        return jsonify({"error": "Error al procesar la transacción: " + str(e)}), 500
"""---"""   
@app.route("/comprobar", methods=["POST"])
def comprobar():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                "tx_hash": request.form.get("tx_hash")
            }

        tx_hash = data.get("tx_hash")
        if not tx_hash:
            return jsonify({"error": "Se debe proporcionar tx_hash"}), 400

        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            estado = "confirmada" if receipt["status"] == 1 else "fallida"
            bloque = receipt["blockNumber"]
            return jsonify({
                "estado": estado,
                "bloque": bloque,
                "etherscan_url": f"https://sepolia.etherscan.io/tx/{tx_hash}"
            })
        except Exception:
            return jsonify({"estado": "pendiente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""---"""
# Iniciar servidor
if __name__ == "__main__":
    time = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    create_Log(time, "SERVER", "", "", "", "", "OK", "Servidor iniciado", "Usuario", server_ip, "")
    app.run(port=6000)
    create_Log(datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"), "SERVER", "", "", "","","OK", "Servidor detenido", "Usuario", server_ip, "")

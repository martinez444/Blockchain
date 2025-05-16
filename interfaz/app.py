from flask import Flask, request, jsonify, render_template
# from hashlib import sha256 (unused import)
from web3 import Web3, HTTPProvider
# import ssl (unused import)
# import requests (unused import)
from datetime import datetime

# import urllib3 (unused import)
import os
# import json (unused import)
import pytz  # For UTC timezone handling
import socket  # To get the server's IP address
import functions as f  # Custom module with utility functions

f.parch_SSL()  # Patch SSL verification issues (defined in functions.py)

# --------------------------
# Configuration
# --------------------------
# Note: In production, this configuration should be moved to a secure config file or environment variables.

PRIVATE_KEY = "45d89b438b406209ddd40b383365452532c0ff8a20216e4da5d0c108ac438a1b"  # Wallet private key to sign transactions
ADDRESS = "0x5115A56d10046aD49Ce8cC0B11A8a496945E5716"  # Wallet address used for sending transactions
SEPOLIA_RPC = "https://eth-sepolia.g.alchemy.com/v2/2SAz6OP1qiVjFyDHYbrtbwJvdv1P_hwe"  # RPC URL of the Sepolia testnet via Alchemy

# Web3 instance setup
w3 = Web3(HTTPProvider(SEPOLIA_RPC))  # Connect to Ethereum node
cuenta = w3.eth.account.from_key(PRIVATE_KEY)  # Load account from private key

# Flask application setup
app = Flask(__name__)

# --------------------------
# Home route - Index page
# --------------------------
@app.route("/")
def index():
    # Read the log file and convert it to a 2D table (list of lists)
    # The function leer_txt_como_tabla() reads a .txt log and returns it as a table
    datos = f.leer_txt_como_tabla(f.log_path)

    # Render the index.html template with the log data
    return render_template("index.html", datos=datos)


# --------------------------
# Upload endpoint - Send file hash to blockchain
# --------------------------
@app.route("/subir", methods=["POST"])
def subir():
    """
    Upload endpoint for sending the SHA-256 hash of a file to the blockchain.

    Expects:
    - 'file': File field in a multipart/form-data POST request.

    Returns:
    - JSON containing:
    - hash_archivo: SHA-256 hash of the file
    - tx_hash: Blockchain transaction hash
    - etherscan_url: Link to view transaction on Etherscan
    - tiempo_segundos: Time taken to send the transaction
    """
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['file']
    filepath = os.path.abspath(file.filename)
    nombre_archivo = os.path.basename(filepath)  # Extract just the filename
    
    client_ip = f.getClientIp()
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    hash_hex = ""
    try:
        # Read file contents
        contenido = file.read()
        file.seek(0)  # Reset pointer
        hash_hex = f.hash_archivo(contenido)  # Generate SHA-256 hash

        # Start timing the blockchain transaction
        start_time = datetime.now()

        # Prepare Ethereum transaction
        nonce = w3.eth.get_transaction_count(cuenta.address, 'pending')  # Get current transaction count for nonce
        tx = {
            "nonce": nonce,
            "to": ADDRESS,  # Sending to self
            "value": 0,  # No ETH transfer
            "gas": 25000,
            "gasPrice": w3.to_wei("50", "gwei"),
            "data": w3.to_bytes(hexstr=hash_hex),  # Hash as hex bytes in data field
            "chainId": 11155111  # Sepolia chain ID
        }
        signed_tx = cuenta.sign_transaction(tx)  # Sign transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Send signed transaction
        tx_hash_str = w3.to_hex(tx_hash)  # Convert tx hash to string

        # Stop timing
        end_time = datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()

        # Format duration as HH:MM:SS.MS
        milliseconds = int((duration_seconds - int(duration_seconds)) * 1000)
        seconds = int(duration_seconds)
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

        # Save the uploaded file locally
        file.save(filepath)

        # Log the upload
        f.create_Log("UPLOAD", nombre_archivo, hash_hex, "", tx_hash_str, "OK", "Archivo subido correctamente", "Usuario", duracion=formatted_duration)

        # Return response
        return jsonify({
            "hash_archivo": hash_hex,
            "tx_hash": tx_hash_str,
            "etherscan_url": f"https://sepolia.etherscan.io/tx/{tx_hash_str}",
            "tiempo_segundos": formatted_duration
        })

    except Exception as e:
        # Log error if something goes wrong
        f.create_Log("UPLOAD", filepath, hash_hex, "", "", "ERROR", str(e), "Usuario", duracion="ERROR")
        return jsonify({"error": str(e)}), 500


# --------------------------
# Download endpoint - Verify file hash from blockchain
# --------------------------
@app.route("/bajar", methods=["POST"])
def bajar():
    """
    Endpoint for downloading and verifying a file's hash against the hash stored on blockchain.

    Expects:
    - 'tx_hash': Transaction hash (string)
    - 'archivo': File to verify (uploaded via HTML form)

    Returns:
    - JSON containing:
    - mensaje: "OK" if hashes match, "KO" if not
    - hash_local: Hash of the uploaded file
    - hash_enviado: Hash from blockchain transaction
    """
    hash_local = ""
    hash_enviado = ""
    tx_hash = ""
    nombre_archivo = ""

    try:
        # Only accept HTML form (not JSON)
        if request.is_json:
            return jsonify({"error": "Este endpoint solo acepta archivos vía formulario HTML"}), 400

        # Get form data
        tx_hash = request.form.get("tx_hash")
        archivo = request.files.get("archivo")
        if not archivo or not tx_hash:
            return jsonify({"error": "Debes proporcionar tx_hash y un archivo"}), 400

        nombre_archivo = archivo.filename
        archivo.seek(0)
        contenido = archivo.read()

        # Check for empty file
        if len(contenido) == 0:
            return jsonify({"error": "El archivo está vacío"}), 400

        # Compute local hash
        hash_local = f.hash_archivo(contenido)

        # Get hash from blockchain transaction input data
        tx = w3.eth.get_transaction(tx_hash)
        hash_enviado = tx['input'].hex()
        hash_enviado_clean = hash_enviado.replace("0x", "").lower()
        hash_local = hash_local.lower()

        # Compare hashes
        mensaje = "OK" if hash_enviado_clean == hash_local else "KO"

        # Log the verification
        f.create_Log("DOWNLOAD", nombre_archivo, hash_local, hash_enviado_clean, tx_hash, "OK", mensaje, "Usuario")

        # Return result
        return jsonify({
            "mensaje": mensaje,
            "hash_local": hash_local,
            "hash_enviado": hash_enviado_clean
        })

    except Exception as e:
        # Log error
        f.create_Log("DOWNLOAD", nombre_archivo, hash_local, hash_enviado, tx_hash, "ERROR", str(e), "Usuario")
        return jsonify({"error": "Error al procesar la transacción: " + str(e)}), 500


# --------------------------
# Start Flask server
# --------------------------
if __name__ == "__main__":
    time = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)

    # Log that the server was started
    f.create_Log("SERVER", "", "", "", "", "OK", "Servidor iniciado", "Usuario")

    app.run(debug=True, port=5000)

    # Log that the server was stopped
    f.create_Log("SERVER", "", "", "", "", "OK", "Servidor detenido", "Usuario")
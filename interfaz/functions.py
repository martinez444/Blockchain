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





# Parchear verificación SSL
def parch_SSL():
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    old_request = requests.Session.request
    
    def unsafe_request(self, method, url, **kwargs):
        kwargs['verify'] = False
        return old_request(self, method, url, **kwargs)
    
    requests.Session.request = unsafe_request
 
# Hash de archivo en formato SHA-256   
def hash_archivo(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

# Ubicación del archivo de log
log_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_dir, "log.txt")

# Crea el archivo de log
def create_Log(operacion, nArchivo, hLocal, hRecibido, txHash, resultado, msg, usuario):
    fecha = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    serverIP = getServerIp()
    if operacion == "SERVER":
        clientIP = ""
    else:
        clientIP = getClientIp()
    log = fecha + "~" + operacion + "~" + nArchivo + "~" + hLocal + "~" + hRecibido + "~" + txHash + "~" + resultado + "~" + msg + "~" + usuario + "~" + serverIP + "~" + clientIP 
    
    with open(log_path, 'a') as log_file:
        log_file.write(log + '\n')  
        
# Recibir la IP del cliente
def getClientIp():
    if request.headers.getlist("X-Forwarded-For"):
        # Si hay cabeceras 'X-Forwarded-For', usa la primera IP listada (IP original del cliente)
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        # Sin proxy, la IP viene directamente de remote_addr
        ip = request.remote_addr
    
    return ip

# Función para obtener la IP del servidor
def getServerIp():
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    return server_ip

# Función para convertir un archivo en tabla y pasarsela al HTML
def leer_txt_como_tabla(ruta_archivo):
    tabla = []
    with open(ruta_archivo, encoding='utf-8') as f:
        for linea in f:
            celdas = linea.strip().split('~')
            if celdas:  # Ignorar líneas vacías
                tabla.append(celdas)

    cols_elim = [7, 6, 4, 1]
    for fila in tabla:
        for i in cols_elim:
            if i < len(fila):  # Por si alguna fila es más corta
                del fila[i]
    
    return tabla

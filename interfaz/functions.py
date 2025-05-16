from flask import Flask, request, jsonify, render_template
import hashlib
from web3 import Web3, HTTPProvider
import ssl
import requests
from datetime import datetime
import urllib3
import os
import json
import pytz # For UTC timezone
import socket # To get the server IP

# Patch SSL verification
def parch_SSL():
    """
    Patches SSL verification of HTTPS requests.
    This is because the Alchemy test server does not have a valid SSL certificate.
    """
    
    # Disables the InsecureRequestWarning warning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Replaces the requests session request method with a version that does not verify SSL certificates
    old_request = requests.Session.request
    
    def unsafe_request(self, method, url, **kwargs):
        # Disables SSL certificate verification
        kwargs['verify'] = False
        # Calls the original request method with the modified parameters
        return old_request(self, method, url, **kwargs)
    
    # Replaces the requests session request method with the patched version
    requests.Session.request = unsafe_request

# File hash in SHA-256 format   
def hash_archivo(contenido_bytes):
    """
    Converts file content in bytes to a SHA-256 hash.
    
    Parameters:
    contenido_bytes (bytes): File content in bytes.
    
    Returns:
    str: SHA-256 hash represented as a hexadecimal string.
    """
    # Creates an empty SHA-256 hash object
    hash_object = hashlib.sha256()
    
    # Updates the hash object with the file content in bytes
    hash_object.update(contenido_bytes)
    
    # Returns the SHA-256 hash represented as a hexadecimal string
    return hash_object.hexdigest()

def hash_bajada(file_storage):
    # Read the contents of the file from the file storage object
    contenido = file_storage.read()
    
    # Compute the SHA-256 hash of the file contents
    # hashlib.sha256() creates a new SHA-256 hash object
    # .hexdigest() returns the hash as a hexadecimal string
    return hashlib.sha256(contenido).hexdigest()

# Log file location
log_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_dir, "log.txt")

# Creates the log file
def create_Log(operacion, nArchivo, hLocal, hRecibido, txHash, resultado, msg, usuario, duracion=""):
    """
    Logs an entry in the log file.

    Parameters:
    operacion (str): Type of operation (upload, download, server).
    nArchivo (str): File name.
    hLocal (str): Hash of the file on the local server.
    hRecibido (str): Hash of the file received from the client.
    txHash (str): Transaction hash on the blockchain.
    resultado (str): Operation result (OK, ERROR).
    msg (str): Additional message for the log.
    usuario (str): User who performed the operation.
    duracion (str): Time taken by the operation (optional).
    """
    
    # Gets the current date and time in UTC format
    fecha = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    # Gets the server IP
    serverIP = getServerIp()
    
    # If operation is "SERVER", do not log client IP
    if operacion == "SERVER":
        clientIP = ""
    else:
        # Gets the client IP
        clientIP = getClientIp()
    
    # Constructs the log entry
    log = fecha + "~" + operacion + "~" + nArchivo + "~" + hLocal + "~" + hRecibido + "~" + txHash + "~" + resultado + "~" + msg + "~" + usuario + "~" + serverIP + "~" + clientIP + "~" + duracion
    
    # Opens the log file in append mode and writes the entry
    with open(log_path, 'a') as log_file:
        log_file.write(log + '\n')
        
# Receive client IP
def getClientIp():
    """
    Gets the IP of the client making the request.

    The IP can come in two ways:
    1. If the proxy passes the original client IP in the HTTP header 'X-Forwarded-For',
    the first IP listed is used.
    2. If there is no proxy, the IP is obtained directly from the request's 'remote_addr' property.
    """

    # Checks if the request has the 'X-Forwarded-For' header
    if request.headers.getlist("X-Forwarded-For"):
        # If 'X-Forwarded-For' headers exist, extracts the first IP listed
        # which is the original client IP
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        # Without proxy, IP comes directly from remote_addr
        ip = request.remote_addr
    
    # Returns the client IP
    return ip

# Function to get the server IP
def getServerIp():
    """
    Gets the IP of the server where this application is running.

    First, it obtains the server's hostname using the socket library's
    gethostname() function. Then, it uses gethostbyname() to get the IP associated with the hostname.
    """

    # Gets the server hostname
    hostname = socket.gethostname()

    # Gets the IP associated with the hostname
    server_ip = socket.gethostbyname(hostname)

    # Returns the server IP
    return server_ip

# Function to convert a file into a table and pass it to the HTML
def leer_txt_como_tabla(ruta_archivo):
    # Reads a text file and returns an in-memory table.
    # The table is represented as a list of lists, where each sublist
    # represents a table row and contains cell values
    # separated by '~'. The first column is ignored and rows
    # without at least one cell with content are removed.

    tabla = []  # The table to return
    with open(ruta_archivo, encoding='utf-8', errors='replace') as f:
        # Opens the file in read mode and UTF-8 encoding with read errors
        # replaced by '?'
        for linea in f:
            # Iterates over each line of the file
            celdas = linea.strip().split('~')
            # Converts each line into a list of cells separated by '~'
            # and strips leading and trailing whitespace
            if celdas:  # Ignores empty lines
                tabla.append(celdas)

    # Removes columns that should not be displayed in the table
    cols_elim = [11, 7, 6, 4, 1]
    cols_elim = sorted(cols_elim, reverse=True)

    # Creates a filtered table that only contains rows that meet
    # certain conditions
    tabla_filtrada = []

    for fila in tabla:
        # Iterates over each row of the original table
        if len(fila) > 1 and fila[1] == "UPLOAD" and fila[6] == "OK":
            # If the row has at least two cells, the second cell is "UPLOAD"
            # and the sixth cell is "OK", it is added to the filtered table
            nueva_fila = fila[:]  # Copy to avoid modifying the original
            for i in cols_elim:
                # Removes columns that should not be displayed
                if i < len(nueva_fila):
                    del nueva_fila[i]
            tabla_filtrada.append(nueva_fila)

    # Replaces the original table with the filtered table
    tabla = tabla_filtrada

    # Returns the filtered table
    return tabla

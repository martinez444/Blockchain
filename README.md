web3
requests
flasks

Primero hay que iniciar el servidor ejecutando app.py, luego, en otra ventana de la terminal se pueden ejecutar los comandos

ejemplo subir: (corregir rutas)
curl -F "file=@C:\Users\stephanyanahi.martin\Prueba-Blockchain\requirements" http://localhost:5000/subir

ejemplo comparar: (corregir rutas)

curl -d "tx_hash=0xe9a3c3aed209d645b9974b8beac31805e8538d3fe4a2af00f7c3099ddecb7782" -d "ruta_archivo=C:\\Users\\stephanyanahi.martin\\Prueba-Blockchain\\requirements" "http://localhost:5000/bajar"

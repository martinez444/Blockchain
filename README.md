web3
requests
flasks
pytz

# How to use the server

1. First, start the server by running `app.py`:

# Terminal

python app.py

# 2. Then, open another terminal window to run the commands.

Example to upload a file
Remember to correct the file path according to your system.

curl -F "file=@C:\Users\stephanyanahi.martin\Prueba-Blockchain\requirements" http://localhost:5000/subir

# Example to compare a file with a hash in the blockchain

Remember to correct the file path and the hash according to your case

curl -d "tx_hash=0xe9a3c3aed209d645b9974b8beac31805e8538d3fe4a2af00f7c3099ddecb7782" -d "ruta_archivo=C:\\Users\\stephanyanahi.martin\\Prueba-Blockchain\\requirements" "http://localhost:5000/bajar"

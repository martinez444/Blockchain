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

To check if a file has been modified over time, open the visual interface by accessing http://localhost:5000/

from flask import Flask, render_template

app = Flask(__name__)

def leer_txt_como_tabla(ruta_archivo):
    tabla = []
    with open(ruta_archivo, encoding='utf-8') as f:
        for linea in f:
            celdas = linea.strip().split('~')
            if celdas:  # Ignorar líneas vacías
                tabla.append(celdas)
    return tabla

@app.route("/")
def index():
    datos = leer_txt_como_tabla("C:/Users/david.benllochpenin/Desktop/blockchain/interfaz/log.txt")  # Cambia el nombre si es necesario
    return render_template("index.html", tabla=datos)

if __name__ == "__main__":
    app.run(debug=True)

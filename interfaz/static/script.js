
function copiarContenido(boton) {
    // Encuentra el párrafo hermano que contiene el texto a copiar
    const celda = boton.parentElement.querySelector('.hash-content');
    const texto = celda.innerText;

    navigator.clipboard.writeText(texto)
        .then(() => {
            // Opcional: cambia el ícono o muestra un feedback temporal
            boton.innerHTML = '<i class="fa-solid fa-check"></i>';
            setTimeout(() => {
                boton.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
            }, 1500);
        })
        .catch(err => alert("Error al copiar: " + err));
}

function filtrarTabla() {
    const input = document.getElementById("buscador");
    const filtro = input.value.toLowerCase();
    const filas = document.querySelectorAll("table tbody tr");

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll("td");
        let textoFila = Array.from(celdas).map(td => td.textContent.toLowerCase()).join(" ");

        if (textoFila.includes(filtro)) {
            fila.style.display = "";
        } else {
            fila.style.display = "none";
        }
    });
}

function filtrarPorFecha() {
    const desde = document.getElementById("fechaInicio").value;
    const hasta = document.getElementById("fechaFin").value;
    const filas = document.querySelectorAll("table tbody tr");

    filas.forEach(fila => {
        const celdaFecha = fila.querySelector("td"); // asume que la fecha está en la primera celda
        if (!celdaFecha) return;

        const textoFecha = celdaFecha.textContent.trim();
        const fecha = new Date(textoFecha); // conviértelo a objeto Date

        const fechaDesde = desde ? new Date(desde) : null;
        const fechaHasta = hasta ? new Date(hasta) : null;

        let visible = true;

        if (fechaDesde && fecha < fechaDesde) visible = false;
        if (fechaHasta && fecha > fechaHasta) visible = false;

        fila.style.display = visible ? "" : "none";
    });
}


document.addEventListener("DOMContentLoaded", function () {
    llenarSelectsIP();
});

function llenarSelectsIP() {
    const filas = document.querySelectorAll("table tbody tr");
    const servidorSet = new Set();
    const clienteSet = new Set();

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll("td");
        const ipServidor = celdas[celdas.length - 3]?.textContent.trim();
        const ipCliente = celdas[celdas.length - 2]?.textContent.trim();
        if (ipServidor) servidorSet.add(ipServidor);
        if (ipCliente) clienteSet.add(ipCliente);
    });

    const selectServidor = document.getElementById("ipServidor");
    const selectCliente = document.getElementById("ipCliente");

    servidorSet.forEach(ip => {
        const option = document.createElement("option");
        option.value = ip;
        option.textContent = ip;
        selectServidor.appendChild(option);
    });

    clienteSet.forEach(ip => {
        const option = document.createElement("option");
        option.value = ip;
        option.textContent = ip;
        selectCliente.appendChild(option);
    });
}

function filtrarPorIPs() {
    const ipServidorFiltro = document.getElementById("ipServidor").value;
    const ipClienteFiltro = document.getElementById("ipCliente").value;
    const filas = document.querySelectorAll("table tbody tr");

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll("td");
        const ipServidor = celdas[celdas.length - 3]?.textContent.trim();
        const ipCliente = celdas[celdas.length - 2]?.textContent.trim();

        let visible = true;

        if (ipServidorFiltro && ipServidor !== ipServidorFiltro) visible = false;
        if (ipClienteFiltro && ipCliente !== ipClienteFiltro) visible = false;

        fila.style.display = visible ? "" : "none";
    });


}

function limpiarFiltros() {
    // Limpiar inputs
    document.getElementById("fechaInicio").value = "";
    document.getElementById("fechaFin").value = "";
    document.getElementById("ipServidor").value = "";
    document.getElementById("ipCliente").value = "";
    document.getElementById("buscador").value = "";

    // Mostrar todas las filas
    const filas = document.querySelectorAll("table tbody tr");
    filas.forEach(fila => {
        fila.style.display = "";
    });
}

function mostrarFormulario(txHash) {
    document.getElementById("txHash").value = txHash;
    document.getElementById("modalFormulario").style.display = "block";

    const form = document.getElementById("modalFormulario");
    document.getElementById("txHash").value = txHash;
    form.style.display = "flex";
    form.style.justifyContent = "center";
    form.style.alignItems = "center";
    form.style.flexDirection = "column";

}

function cerrarFormulario() {
    document.getElementById("modalFormulario").style.display = "none";
}

function enviarFormulario() {
    const form = document.getElementById("formComparar");
    const archivoInput = document.getElementById("rutaArchivo");
    const txHashInput = document.getElementById("txHash");


    const resSubmit = document.getElementById("res-submit");
    const cerrar = document.getElementById("cerrar");

    // Validar que se ha proporcionado un tx_hash (opcional si lo estás cargando dinámicamente)
    if (!txHashInput.value) {
        alert("No se ha proporcionado un hash de transacción.");
        return false;
    }

    const formData = new FormData();
    formData.append("archivo", archivoInput.files[0]);
    formData.append("tx_hash", txHashInput.value);

    resSubmit.innerHTML = ""; // Limpiar el contenedor de resultados
    fetch("/bajar", {
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            const resImg = document.createElement("img");
            const resTxt = document.createElement("p");
            resImg.classList.add("fade-in");
            resTxt.classList.add("fade-in", "reslt-message");
            const resSubmit = document.getElementById("res-submit");
            resSubmit.appendChild(resTxt);
            resSubmit.appendChild(resImg);
            if (data.mensaje) {
                if (data.mensaje == "OK") {
                    resTxt.classList.add("green");
                    resTxt.innerText = "¡Los hashes coinciden!";
                    resImg.src = "../static/tick.webp";
                }
                else if (data.mensaje === "KO") {
                    resTxt.classList.add("red");
                    resTxt.innerText = "¡Los hashes no coinciden!"
                    resImg.src = "../static/cruz.webp";
                }
                else {
                    alert(data.mensaje);
                    resSubmit.innerHTML = "";
                    resTxt.innerText = ""
                    resImg.style.opacity = 0
                }
            } else if (data.error) {
                alert("Error: " + data.error);
                resSubmit.innerHTML = "";
                resTxt.innerText = ""
                resImg.style.opacity = 0
            } else {
                alert("Respuesta inesperada del servidor.");
            }

            // Vacía el input de archivo
            archivoInput.value = "";

            cerrar.addEventListener("click", () => {
                resTxt.remove();
                resImg.remove();
            });
        })
        .catch(error => {
            console.error("Error en la solicitud:", error);
            alert("Error al conectar con la API");
        });

    return false; // Evita el envío tradicional del formulario
}
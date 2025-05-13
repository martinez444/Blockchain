function enviarFormulario() {
            const form = document.getElementById("formComparar");
            const formData = new FormData(form);
            const fileInput = document.getElementById("rutaArchivo");
            const txHashInput = document.getElementById("txHash");
            const resSubmit = document.getElementById("res-submit");
            const cerrar = document.getElementById("cerrar");
            formData.append("archivo", fileInput.files[0]);
            formData.append("tx_hash", txHashInput.value);
            // Limpia cualquier imagen previa
            resSubmit.innerHTML = "";
 
            // Validar que se ha proporcionado un tx_hash (opcional si lo estás cargando dinámicamente)
            if (!txHashInput.value) {
                alert("No se ha proporcionado un hash de transacción.");
                return false;
            }
            
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
                    resSubmit.appendChild(resTxt);
                    resSubmit.appendChild(resImg);
                   
                    if (data.mensaje) {
                        if (data.mensaje === "OK") {
                            resTxt.classList.add("green");
                            resTxt.innerText = "¡Los hashes coinciden!";
                            resImg.src = "../static/Sujeto.png";
                        } else if (data.mensaje === "KO") {
                            resTxt.classList.add("red");
                            resTxt.innerText = "¡Los hashes no coinciden!"
                            resImg.src = "../static/tralalero.jpg";
                        } else {
                            alert(data.mensaje);
                        }
                    } else if (data.error) {
                        alert("Error: " + data.error);
                    } else {
                        alert("Respuesta inesperada del servidor.");
                    }
 
                    // Vacía el input de archivo
                    fileInput.value = "";
 
                    // Después de 5 segundos, añade animación de salida y elimina la imagen
                    setTimeout(() => {
                        resImg.classList.remove("fade-in");
                        resTxt.classList.remove("fade-in");
                        // resImg.classList.add("fade-out");
                        // resTxt.classList.add("fade-out");
 
                        cerrar.addEventListener("click", () => {
                            resTxt.remove();
                            resImg.remove();
                        });
                    }, 3000);
                })
                .catch(error => {
                    console.error("Error en la solicitud:", error);
                    alert("Error al conectar con la API");
                });
 
            return false; // Evita el envío tradicional del formulario
        }
// This function is responsible for copying the content of a cell to the system clipboard
// when the "Copy" button inside the cell is clicked.
function copiarContenido(boton) {
  // Finds the cell containing the text to copy (the button has a sibling
  // which is a paragraph with class "hash-content")
  const celda = boton.parentElement.querySelector(".hash-content");

  // Extracts the text from the cell to copy it
  const texto = celda.innerText;

  // Uses the Clipboard API to write the text to the system clipboard
  navigator.clipboard
    .writeText(texto)
    .then(() => {
      // Optional: changes the button icon to show temporary feedback
      // (a green tick <i class="fa-solid fa-check"></i>) to indicate the text has been copied.
      // After 1.5 seconds, it reverts the button to its original state.
      boton.innerHTML = '<i class="fa-solid fa-check"></i>';
      setTimeout(() => {
        boton.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
      }, 1500);
    })
    .catch((err) => alert("Error copying: " + err));
}

function filtrarTabla() {
  // Gets the search input by its ID and converts its value to lowercase for case-insensitive search
  const input = document.getElementById("buscador");
  const filtro = input.value.toLowerCase();

  // Selects all the table rows inside the tbody
  const filas = document.querySelectorAll("table tbody tr");

  // Loops through each row to apply the filter
  filas.forEach((fila) => {
    // Selects all the cells (td) of the current row
    const celdas = fila.querySelectorAll("td");

    // Converts each cell's content to lowercase text, then combines into a single string
    let textoFila = Array.from(celdas)
      .map((td) => td.textContent.toLowerCase()) // Converts text to lowercase
      .join(" "); // Joins all texts with a space to form a single string

    // Checks if the row text includes the filter string
    if (textoFila.includes(filtro)) {
      // If it includes the filter, shows the row
      fila.style.display = "";
    } else {
      // Otherwise, hides the row
      fila.style.display = "none";
    }
  });
}

/**
 * Filters table rows based on a date range.
 *
 * Takes the start and end date input values, and hides the rows
 * whose date is not within the specified range.
 *
 * The function iterates over each table row and checks if its date
 * (assumed in the first column) is within the specified range. If not, hides the row.
 */
function filtrarPorFecha() {
  // Gets the values of the start and end date inputs
  const desde = document.getElementById("fechaInicio").value;
  const hasta = document.getElementById("fechaFin").value;

  // Gets all the rows of the table
  const filas = document.querySelectorAll("table tbody tr");

  // Iterates over each row and applies the filter
  filas.forEach((fila) => {
    // Finds the cell that contains the date (assumed to be in the first column)
    const celdaFecha = fila.querySelector("td");
    if (!celdaFecha) return; // If there's no cell, skip the row

    // Converts the cell's text to a Date object
    const textoFecha = celdaFecha.textContent.trim();
    const fecha = new Date(textoFecha);

    // Converts the input values to Date objects (if not empty)
    const fechaDesde = desde ? new Date(desde) : null;
    const fechaHasta = hasta ? new Date(hasta) : null;

    // Determines if the row should be visible or not
    let visible = true;

    // If there's a start date and the row's date is earlier, hide the row
    if (fechaDesde && fecha < fechaDesde) {
      visible = false;
    }

    // If there's an end date and the row's date is later, hide the row
    if (fechaHasta && fecha > fechaHasta) {
      visible = false;
    }

    // Shows or hides the row as needed
    fila.style.display = visible ? "" : "none";
  });
}

document.addEventListener("DOMContentLoaded", function () {
  llenarSelectsIP();
});

/**
 * Fills the server and client IP selects with the unique IP addresses found in the table.
 *
 * The function iterates over each row in the table, extracts the server and client IPs from the
 * corresponding cells, and adds them to sets to avoid duplicates. Then, it iterates over the sets and
 * creates options for each IP address in the corresponding select elements.
 */
function llenarSelectsIP() {
  // Gets all the table rows
  const filas = document.querySelectorAll("table tbody tr");

  // Creates sets to store server and client IP addresses
  const servidorSet = new Set(); // Set to store server IPs
  const clienteSet = new Set(); // Set to store client IPs

  // Iterates over each row to extract server and client IPs
  filas.forEach((fila) => {
    const celdas = fila.querySelectorAll("td");
    const ipServidor = celdas[celdas.length - 3]?.textContent.trim(); // Extracts server IP
    const ipCliente = celdas[celdas.length - 2]?.textContent.trim(); // Extracts client IP

    // If there's a server IP, add it to the set
    if (ipServidor) servidorSet.add(ipServidor);
    // If there's a client IP, add it to the set
    if (ipCliente) clienteSet.add(ipCliente);
  });

  // Gets the select elements for server and client IP filters
  const selectServidor = document.getElementById("ipServidor");
  const selectCliente = document.getElementById("ipCliente");

  // Iterates over the sets of IPs and creates options for each
  servidorSet.forEach((ip) => {
    const option = document.createElement("option");
    option.value = ip;
    option.textContent = ip;
    selectServidor.appendChild(option);
  });

  clienteSet.forEach((ip) => {
    const option = document.createElement("option");
    option.value = ip;
    option.textContent = ip;
    selectCliente.appendChild(option);
  });
}

/**
 * Filters table rows based on the selected server and client IP values.
 *
 * Iterates over each row in the table, extracts the server and client IPs from the
 * corresponding cells, and checks if each selected value matches the extracted IP.
 * If not, the row is hidden.
 */
function filtrarPorIPs() {
  const ipServidorFiltro = document.getElementById("ipServidor").value;
  const ipClienteFiltro = document.getElementById("ipCliente").value;

  const filas = document.querySelectorAll("table tbody tr");

  filas.forEach((fila) => {
    const celdas = fila.querySelectorAll("td");

    const ipServidor = celdas[celdas.length - 3]?.textContent.trim();
    const ipCliente = celdas[celdas.length - 2]?.textContent.trim();

    let visible = true;

    if (ipServidorFiltro && ipServidor !== ipServidorFiltro) {
      visible = false;
    }

    if (ipClienteFiltro && ipCliente !== ipClienteFiltro) {
      visible = false;
    }

    fila.style.display = visible ? "" : "none";
  });
}

/**
 * Clears all table filters and shows all rows.
 *
 * Iterates over each filter input and resets its value to an empty string.
 * Then iterates over each row in the table and sets its display style to empty,
 * making all rows visible.
 */
function limpiarFiltros() {
  const fechaInicio = document.getElementById("fechaInicio");
  const fechaFin = document.getElementById("fechaFin");
  fechaInicio.value = "";
  fechaFin.value = "";

  const ipServidor = document.getElementById("ipServidor");
  const ipCliente = document.getElementById("ipCliente");
  ipServidor.value = "";
  ipCliente.value = "";

  const buscador = document.getElementById("buscador");
  buscador.value = "";

  document.getElementById("fechaInicio").value = "";
  document.getElementById("fechaFin").value = "";
  document.getElementById("ipServidor").value = "";
  document.getElementById("ipCliente").value = "";
  document.getElementById("buscador").value = "";

  const filas = document.querySelectorAll("table tbody tr");
  filas.forEach((fila) => {
    fila.style.display = "";
  });
}

function mostrarFormulario(txHash) {
  // Set the value of the hidden input field with the transaction hash
  document.getElementById("txHash").value = txHash;

  // Get the modal element by its ID
  const form = document.getElementById("modalFormulario");

  // Set the display property to "block" to make the modal visible
  form.style.display = "block";

  // Center the modal content using flexbox properties
  form.style.justifyContent = "center"; // Align content vertically to the center
  form.style.alignItems = "center"; // Align content horizontally to the center
  form.style.flexDirection = "column"; // Set the direction of flex items to column
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

  // Validate that a tx_hash has been provided (optional if loaded dynamically)
  if (!txHashInput.value) {
    alert("No transaction hash provided.");
    return false;
  }

  const formData = new FormData();
  formData.append("archivo", archivoInput.files[0]);
  formData.append("tx_hash", txHashInput.value);

  resSubmit.innerHTML = "";
  fetch("/bajar", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
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
          resTxt.innerText = "Hashes match!";
          resImg.src = "../static/tick.webp";
        } else if (data.mensaje === "KO") {
          resTxt.classList.add("red");
          resTxt.innerText = "Hashes do not match!";
          resImg.src = "../static/cruz.webp";
        } else {
          alert(data.mensaje);
          resSubmit.innerHTML = "";
          resTxt.innerText = "";
          resImg.style.opacity = 0;
        }
      } else if (data.error) {
        alert("Error: " + data.error);
        resSubmit.innerHTML = "";
        resTxt.innerText = "";
        resImg.style.opacity = 0;
      } else {
        alert("Unexpected server response.");
      }

      archivoInput.value = "";

      cerrar.addEventListener("click", () => {
        resTxt.remove();
        resImg.remove();
      });
    })
    .catch((error) => {
      console.error("Request error:", error);
      alert("Error connecting to the API");
    });

  return false; // Prevent traditional form submission
}

function setOrigenFormulario(origen) {
    // Guardar el origen en sessionStorage
    sessionStorage.setItem("origenFormulario", origen);
    console.log(`Origen establecido a: ${origen}`);
}

function getOrigenFormulario() {
    // Recuperar el origen desde sessionStorage
    return sessionStorage.getItem("origenFormulario") || "index"; // Valor predeterminado: "index"
}

// Log para verificar que el script se carga
console.log("Origen.js cargado");

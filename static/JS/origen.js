function setOrigenFormulario(origen) {
    sessionStorage.setItem("origenFormulario", origen);
    console.log(`Origen establecido a: ${origen}`);
}

function getOrigenFormulario() {
    return sessionStorage.getItem("origenFormulario") || "index";
}

function adjustReturnLink(linkId) {
    const volverEnlace = document.getElementById(linkId);
    if (!volverEnlace) {
        console.error(`No se encontró un elemento con el ID: ${linkId}`);
        return;
    }

    // Ajustar según el origen
    const origenFormulario = getOrigenFormulario();
    if (origenFormulario === "gestion_usuarios") {
        volverEnlace.href = "/gestion-usuarios";
    } else {
        // Obtener los parámetros del servidor
        const username = document.body.getAttribute("data-username");
        const nivelAcceso = document.body.getAttribute("data-nivel-acceso");

        if (username && nivelAcceso) {
            volverEnlace.href = `/index?username=${encodeURIComponent(username)}&nivel_acceso=${encodeURIComponent(nivelAcceso)}`;
        } else {
            console.warn("No se encontraron los datos de username o nivel_acceso. Redirigiendo a /index.");
            volverEnlace.href = "/index"; // Redirige sin parámetros si faltan datos
        }
    }

    console.log(`Enlace de 'Volver' ajustado a: ${volverEnlace.href}`);
}

// Log para verificar que el script se carga
console.log("Origen.js cargado");

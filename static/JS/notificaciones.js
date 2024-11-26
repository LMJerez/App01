document.addEventListener("DOMContentLoaded", () => {
    const usuarioId = document.body.dataset.usuarioId; // ID del usuario desde el atributo data-usuario-id    
    if (!usuarioId) return; // Salir si no hay usuario
    console.log("---> Entrando a notificaciones usuario", usuarioId);

    // Cargar mensajes desde el servidor
    fetch(`/mensajes/${usuarioId}`)
        .then(response => response.json())
        .then(mensajes => {
            if (mensajes.length > 0) {
                mensajes.forEach(mensaje => {
                    console.log(`Mostrando mensaje: ${mensaje.asunto}`); // Depuración
                    if (typeof mostrarMensaje === "function") {
                        mostrarMensaje(mensaje.asunto, mensaje.mensaje, mensaje.fecha_envio);
                    } else {
                        console.error("mostrarMensaje no está definida.");
                    }
                });
            }
        })
        .catch(error => console.error("Error al cargar mensajes:", error));
});

/**
 * Muestra un mensaje en un <dialog> flotante no modal.
 * @param {string} asunto - Asunto del mensaje.
 * @param {string} texto - Contenido del mensaje.
 * @param {string} fechaEnvio - Fecha de envío del mensaje.
 */
function mostrarMensaje(asunto, texto, fechaEnvio) {
    const dialog = document.createElement("dialog");
    dialog.classList.add("mensaje-dialog");
    dialog.innerHTML = `
        <h3>${asunto}</h3>
        <p><strong>Enviado:</strong> ${new Date(fechaEnvio).toLocaleString()}</p>
        <p>${texto}</p>
        <button onclick="this.parentElement.close()">Cerrar</button>
    `;
    document.body.appendChild(dialog);
    dialog.show();
}
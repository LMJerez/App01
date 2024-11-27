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
    dialog.classList.add("mensaje");
    dialog.innerHTML = `
        <img src="/static/images/logos/logo-msg.png" alt="Mensaje">
        <h2>Mensaje</h2>        
        <h3>Asunto: ${asunto}</h3>        
        <p>${texto}</p>
        <p>Fecha: ${new Date(fechaEnvio).toLocaleString()}</p>        
        <button class="close-dialog">Cerrar</button>        
    `;
    document.body.appendChild(dialog);    
    // Mostrar el diálogo
    dialog.show();
    // Añadir el evento al botón de cierre
    dialog.querySelector(".close-dialog").addEventListener("click", () => {
        dialog.close(); // Cierra el diálogo
        dialog.remove(); // Elimina el diálogo del DOM
    });
}


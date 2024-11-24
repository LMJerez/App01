// Variable para almacenar el ID seleccionado (específica del toolbar)
let toolbarSelectedId = null;

/**
 * Función para redirigir a la página de edición del usuario seleccionado.
 */
function editUser() {
    toolbarSelectedId = getSelectedId(); // Obtener el ID seleccionado desde tabla_interactiva.js
    if (!toolbarSelectedId) {
        alert("Por favor, selecciona un usuario de la tabla haciendo click sobre su ID.");
        return;
    }
    // Redirigir a la página de edición
    window.location.href = `/actualizar/datos-usuario/${toolbarSelectedId}`;
    console.log(`ID seleccionado para editar: ${toolbarSelectedId}`);
}

/**
 * Actualiza el nivel de acceso del usuario seleccionado.
 */
function updateAccessLevel() {
    const AccessLevelSelectedId = TableManager.getSelectedId(); // Obtener el ID seleccionado
    if (!AccessLevelSelectedId) {
        alert("Por favor, selecciona un usuario de la tabla haciendo clic sobre su ID.");
        return;
    }

    // Solicitar el nuevo nivel de acceso
    const newAccessLevel = prompt("Ingrese el nuevo nivel de acceso (1: Básico, 2: Intermedio, 3: Avanzado):");
    if (!newAccessLevel || !["1", "2", "3"].includes(newAccessLevel)) {
        alert("El nivel de acceso ingresado no es válido. Por favor, ingrese 1, 2 o 3.");
        return;
    }

    // Enviar la solicitud al servidor
    fetch(`/actualizar-nivel-acceso/${AccessLevelSelectedId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ nivel_acceso: parseInt(newAccessLevel) }),
    })
        .then(response => {
            if (response.ok) {
                alert("Nivel de acceso actualizado correctamente.");
                window.location.reload(); // Recargar la página para reflejar el cambio
            } else {
                alert("Error al actualizar el nivel de acceso. Inténtelo de nuevo.");
            }
        })
        .catch(error => {
            console.error("Error al actualizar el nivel de acceso:", error);
            alert("Ocurrió un error inesperado. Verifique la consola para más detalles.");
        });
}

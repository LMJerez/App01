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

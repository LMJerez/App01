let selectedId = null; // Variable global para almacenar el ID seleccionado

/**
 * Alterna la selección de una celda y desmarca las demás.
 * @param {HTMLElement} element - La celda seleccionada.
 */
function toggleSelection(element) {
    // Desmarcar todas las celdas con clase "id"
    document.querySelectorAll('.id').forEach(cell => {
        cell.classList.remove('selected');
    });

    // Marcar la celda actual y actualizar el ID seleccionado
    element.classList.add('selected');
    selectedId = element.textContent.trim(); // Guardar el ID seleccionado
    console.log(`ID seleccionado: ${selectedId}`); // Mostrar el ID en la consola
}

/**
 * Devuelve el ID actualmente seleccionado.
 * @returns {string|null} El ID seleccionado o null si no hay selección.
 */
function getSelectedId() {
    return selectedId;
}

// - Usar el ID Seleccionado en Otras Funcionalidades -

// Obtener el ID seleccionado y usarlo en una acción
document.getElementById("mi-boton").addEventListener("click", () => {
    const idSeleccionado = getSelectedId();
    if (idSeleccionado) {
        alert(`ID seleccionado: ${idSeleccionado}`);
        // Aquí puedes agregar lógica adicional como enviar el ID al servidor
    } else {
        alert("Por favor, selecciona un ID antes de continuar.");
    }
});
const TableManager = (() => {
    let selectedId = null; // Variable privada para almacenar el ID seleccionado

    /**
     * Alterna la selección de una celda y desmarca las demás.
     * @param {HTMLElement} element - La celda seleccionada.
     */
    function toggleSelection(element) {
        // Deseleccionar todas las celdas con clase "id"
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

    // Agregar manejadores de clic a las celdas con clase "id" al cargar la página
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll('table tbody .id').forEach(cell => {
            cell.addEventListener('click', () => toggleSelection(cell));
        });
    });

    // Exponer las funciones necesarias
    return {
        toggleSelection,
        getSelectedId,
    };
})();

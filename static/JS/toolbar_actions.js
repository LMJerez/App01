// Variable global para almacenar el ID seleccionado
let selectedId = null;

// Obtener el ID seleccionado desde el archivo `tabla_interactiva.js`
function getSelectedId() {
    return selectedId;
}

// Función para manejar la selección de filas de la tabla
function toggleSelection(row) {
    // Deseleccionar previamente seleccionados
    const previouslySelected = document.querySelector('.selected');
    if (previouslySelected) {
        previouslySelected.classList.remove('selected');
    }

    // Seleccionar la nueva fila
    row.classList.add('selected');
    selectedId = row.dataset.id; // Asegúrate de que la fila tenga el atributo data-id con el ID del usuario
}

// Agregar manejadores de clic a las filas de la tabla
document.querySelectorAll('table tbody tr').forEach(row => {
    row.addEventListener('click', () => toggleSelection(row));
});

// Submenu gestion-usuario Actualizar/DAtos de usuario
function editUser() {
    const selectedId = getSelectedId(); // Obtener el ID seleccionado de la tabla
    if (!selectedId) {
        alert("Por favor, selecciona un usuario de la tabla.");
        return;
    }
    // Redirigir a la página de edición
    window.location.href = `/actualizar/datos-usuario/${selectedId}`;
}

/**
 * Redirige a la página de edición de usuario.
 */
function editUser() {
    const selectedId = TableManager.getSelectedId(); // Obtener el ID seleccionado desde TableManager
    if (!selectedId) {
        alert("Selecciona un usuario de la tabla haciendo clic sobre su ID.");
        return;
    }
    // Redirigir a la página de edición
    window.location.href = `/actualizar/datos-usuario/${selectedId}`;
    console.log(`ID seleccionado para editar: ${selectedId}`);
}

/**
 * Actualiza el nivel de acceso del usuario seleccionado utilizando un <dialog>.
 */
function updateAccessLevel() {
    const selectedId = TableManager.getSelectedId();
    if (!selectedId) {
        alert("Selecciona un usuario de la tabla haciendo clic sobre su ID.");
        return;
    }

    // Crear el diálogo dinámicamente
    const dialog = document.createElement("dialog");
    dialog.innerHTML = `
        <form method="dialog">
            <h3>Actualizar Nivel de Acceso</h3>
            <div>
                <p>Selecciona el nuevo nivel de acceso:</p>
                <select id="access-level-select" required>
                    <option value="1">1: Básico</option>
                    <option value="2">2: Intermedio</option>
                    <option value="3">3: Avanzado</option>
                </select>
            </div>
            <div class="form-buttons">                
                <button value="confirm">Confirmar</button>
                <button value="cancel" class="button naranja">Cancelar</button>
            </div>
        </form>
    `;
    document.body.appendChild(dialog);

    // Mostrar el diálogo
    dialog.showModal();

    // Manejar la acción de confirmar
    dialog.addEventListener("close", () => {
        if (dialog.returnValue === "confirm") {
            const newAccessLevel = document.getElementById("access-level-select").value;
            if (["1", "2", "3"].includes(newAccessLevel)) {
                // Llamar a la API para actualizar
                fetch(`/actualizar-nivel-acceso/${selectedId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ nivel_acceso: parseInt(newAccessLevel) }),
                })
                    .then(response => {
                        if (response.ok) {
                            //Actualizado volver
                            window.location.reload();
                        } else {
                            alert("Error al actualizar el nivel de acceso.");
                        }
                    })
                    .catch(error => {
                        console.error("Error al actualizar el nivel de acceso:", error);
                    });
            } else {
                alert("Nivel de acceso no válido.");
            }
        }
        // Eliminar el diálogo después de usarlo
        dialog.remove();
    });
}

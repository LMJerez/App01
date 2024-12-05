// --> Funciónes para Usuarios
function handleAction(action) {
    const selectedId = TableManager.getSelectedId(); // Obtener el ID seleccionado
    if (!selectedId) {
        alert("Por favor, selecciona un usuario primero.");
        return;
    }

    switch (action) {
        case 'update':
            window.location.href = `/actualizar/datos-usuario/${selectedId}`;
            break;

        case 'access':
            console.log(`Cambiando nivel de acceso para el usuario con ID ${selectedId}`);
            updateAccessLevel(selectedId);
            break;

        default:
            console.error(`Acción desconocida: ${action}`);
    }
}

/**
 * Redirige a la página de edición de usuario.
 */
function editUser() {
    const selectedId = TableManager.getSelectedId(); // Obtener el ID seleccionado desde TableManager
    if (!selectedId) {
        alert("Selecciona un usuario de la tabla haciendo clic sobre su ID.");
        return;
    }
    // Redirigir a la página de edición con el origen 'gestion_usuarios'
    const next = "gestion_usuarios";
    window.location.href = `/actualizar/datos-usuario/${selectedId}?next=${next}`;
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

/**
 * Redirigir al formulario de mensajes individuales según el usuario seleccionado.
 */
function messageToUser() {
    const userId = TableManager.getSelectedId();
    if (!userId) {
        alert("Selecciona un usuario de la tabla.");
        return;
    }
    window.location.href = `/enviar-mensaje/individual/${userId}`;
}

/**
 * Redirigir a la ruta notificacr usuarios sin datos.
 */
function notificarUsuariosSinDatos() {
    console.log("Verificando usuarios sin datos...");

    fetch("/notificar-usuarios-sin-datos", {
        method: "POST",
    })
        .then(response => response.json())
        .then(data => {
            const totalNotificaciones = data.usuarios_notificados || 0;
            alert(`Notificaciones enviadas correctamente: ${totalNotificaciones} usuarios notificados.`);
            console.log("Respuesta del servidor:", data);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ocurrió un error al enviar notificaciones.");
        });
}

// --> Funciónes para Cargos
function handleCargoAction(action) {
    const selectedCargoId = TableManager.getSelectedId(); // Obtener el ID del cargo seleccionado
    if (!selectedCargoId) {
        alert("Por favor, selecciona un cargo primero.");
        return;
    }

    switch (action) {
        case 'nuevo_cargo':
            window.location.href = `/editar/cargo/${selectedCargoId}`;
            break;
        
        case 'editar_cargo':
            window.location.href = `/editar/cargo/${selectedCargoId}`;
            break;

        case 'remover_cargo':
            showDeleteCargoDialog(selectedCargoId); // Mostrar el diálogo dinámico
            break;
    
        default:
            console.error(`Acción desconocida: ${action}`);
    }
}

// Mostrar el dialogo de confirmacion para remover cargo usuario
function showDeleteCargoDialog(cargoId) {
    // Crear el diálogo dinámicamente
    const dialog = document.createElement("dialog");
    dialog.innerHTML = `
        <form method="dialog">
            <h3>Confirmar Eliminación</h3>
            <div>
                <p>¿Estás seguro de que deseas remover el cargo con ID ${cargoId} para el usuario?</p>
                <p>¡Sera eliminado definitivamente!</p>
            </div>
            <div class="form-buttons">
                <button value="confirm">Eliminar</button>
                <button value="cancel" class="button naranja">Cancelar</button>
            </div>
        </form>
    `;
    document.body.appendChild(dialog);

    // Manejar la respuesta del diálogo
    dialog.addEventListener("close", () => {
        const response = dialog.returnValue;
        if (response === "confirm") {
            // Llamar a la función para eliminar el cargo
            removeCargo(cargoId);
        }
        dialog.remove(); // Eliminar el diálogo del DOM
    });

    // Mostrar el diálogo
    dialog.showModal();
}
 
async function removeCargo(cargoId) {
    try {
        const response = await fetch(`/api/remover-cargo/${cargoId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error al eliminar el cargo: ${errorData.error}`);
            return;
        }

        const result = await response.json();
        alert(result.message); // Mostrar mensaje de éxito
        console.log("Cargo eliminado:", cargoId);

        // Recargar los cargos del usuario seleccionado
        const usuarioId = TableManager.getSelectedId(); // ID del usuario seleccionado
        if (usuarioId) {
            cargarCargos(usuarioId) // Volver a cargar la tabla de cargos
                .then(() => {
                    // Simular el clic en la fila del usuario seleccionado
                    const filaUsuario = document.querySelector(`table#usuarios-tbody .id.selected`);
                    if (filaUsuario) {
                        filaUsuario.click(); // Activar el evento de clic en la fila seleccionada
                    }
                })
                .catch(error => {
                    console.error("Error al recargar los cargos:", error);
                });
        }
    } catch (error) {
        console.error("Error al eliminar el cargo:", error);
        alert("Ocurrió un error al intentar eliminar el cargo.");
    }
}

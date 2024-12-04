// Función para cargar la tabla de usuarios
async function cargarUsuarios() {
    try {
        const response = await fetch("/api/usuarios");
        if (!response.ok) {
            throw new Error(`Error en la solicitud: ${response.statusText}`);
        }

        const usuarios = await response.json();
        const tbody = document.getElementById("usuarios-tbody");
        tbody.innerHTML = ""; // Limpiar tabla

        usuarios.forEach(usuario => {
            const fila = document.createElement("tr");

            // Crear celdas
            fila.innerHTML = `
                <td class="id">${usuario.id}</td>
                <td>${usuario.username}</td>
                <td>${usuario.nivel_acceso}</td>
                <td>${usuario.telefono || 'N/A'}</td>
                <td>${usuario.correo || 'N/A'}</td>
                <td>${usuario.estado_contrasena}</td>
            `;

            // Agregar manejador de clic para seleccionar/deseleccionar fila
            fila.addEventListener("click", () => {
                // Deseleccionar cualquier fila previamente seleccionada
                document.querySelectorAll("tr.selected").forEach(row => row.classList.remove("selected"));

                // Marcar la fila actual como seleccionada
                fila.classList.add("selected");
                TableManager.toggleSelection(fila.querySelector(".id"));

                // Cargar cargos del usuario seleccionado
                const usuarioId = TableManager.getSelectedId();
                if (usuarioId) {
                    cargarCargos(usuarioId);
                }
            });

            // Agregar la fila al tbody
            tbody.appendChild(fila);
        });
    } catch (error) {
        console.error("Error cargando usuarios:", error);
    }
}

// Función para cargar la tabla de cargos
async function cargarCargos(usuarioId) {
    try {
        const response = await fetch(`/api/cargos/${usuarioId}`);
        if (!response.ok) {
            throw new Error(`Error al obtener cargos: ${response.statusText}`);
        }

        const cargos = await response.json();
        const tbody = document.getElementById("cargos-tbody");
        tbody.innerHTML = ""; // Limpiar la tabla de cargos

        cargos.forEach(cargo => {
            const fila = document.createElement("tr");

            // Crear celdas para la fila, incluyendo el ID del cargo
            fila.innerHTML = `
                <td class="id">${cargo.id}</td>
                <td>${cargo.cargo}</td>
                <td>${cargo.area}</td>
            `;

            // Agregar funcionalidad de selección
            fila.addEventListener("click", () => {
                if (fila.classList.contains("selected")) {
                    // Si la fila ya está seleccionada, deseleccionarla
                    fila.classList.remove("selected");
                    TableManager.clearSelection(); // Limpiar selección
                } else {
                    // Deseleccionar cualquier fila previamente seleccionada
                    document.querySelectorAll("#cargos-tbody tr.selected").forEach(row => row.classList.remove("selected"));
                    
                    // Marcar la fila actual como seleccionada
                    fila.classList.add("selected");
                    TableManager.toggleSelection(fila.querySelector(".id"));
                }
            });

            tbody.appendChild(fila);
        });
    } catch (error) {
        console.error("Error cargando los cargos:", error);
    }
}

// Cargar usuarios al cargar la página
document.addEventListener("DOMContentLoaded", cargarUsuarios);

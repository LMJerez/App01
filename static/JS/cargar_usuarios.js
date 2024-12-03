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
                if (fila.classList.contains("selected")) {
                    // Si ya está seleccionada, deseleccionar
                    fila.classList.remove("selected");
                    TableManager.clearSelection(); // Limpiar el ID seleccionado
                } else {
                    // Deseleccionar cualquier fila previamente seleccionada
                    document.querySelectorAll("tr.selected").forEach(row => row.classList.remove("selected"));
                    
                    // Marcar la fila actual como seleccionada
                    fila.classList.add("selected");
                    TableManager.toggleSelection(fila.querySelector(".id"));
                }
            });

            // Agregar la fila al tbody
            tbody.appendChild(fila);
        });
    } catch (error) {
        console.error("Error cargando usuarios:", error);
    }
}

document.addEventListener("DOMContentLoaded", cargarUsuarios);

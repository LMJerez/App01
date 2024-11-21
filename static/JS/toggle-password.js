document.addEventListener("DOMContentLoaded", () => {
    // Seleccionar el botón y el campo de contraseña
    const togglePasswordButton = document.getElementById('toggle-password');
    const passwordField = document.getElementById('password');

    // Verificar si los elementos existen en el DOM
    if (togglePasswordButton && passwordField) {
        togglePasswordButton.addEventListener('click', () => {
            // Alternar entre "text" y "password"
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                togglePasswordButton.textContent = 'Ocultar';
            } else {
                passwordField.type = 'password';
                togglePasswordButton.textContent = 'Mostrar';
            }
        });
    } else {
        console.error("No se encontró el botón o el campo de contraseña en el DOM.");
    }
});

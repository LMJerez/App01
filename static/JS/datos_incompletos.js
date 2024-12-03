document.addEventListener("DOMContentLoaded", () => {
    const datosIncompletos = JSON.parse(document.body.dataset.datosIncompletos); // Leer el atributo de datos
    const userId = document.body.dataset.userId; // Leer el ID de usuario

    if (datosIncompletos === "true") {
        const confirmacion = confirm("Debes actualizar tus datos. ¿Quieres cargar el formulario?");
        if (confirmacion) {
            window.location.href = `/actualizar/datos-usuario/${userId}`;
        }
    }
});

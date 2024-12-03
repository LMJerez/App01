const TableManager = (() => {
    let selectedId = null;

    function toggleSelection(element) {
        selectedId = element.textContent.trim(); // Actualizar el ID seleccionado
        console.log(`ID seleccionado: ${selectedId}`);
    }

    function getSelectedId() {
        return selectedId;
    }

    function clearSelection() {
        selectedId = null; // Limpiar el ID seleccionado
        console.log("Selección borrada.");
    }

    return {
        toggleSelection,
        getSelectedId,
        clearSelection,
    };
})();

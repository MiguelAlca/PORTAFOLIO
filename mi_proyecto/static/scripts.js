document.addEventListener("DOMContentLoaded", () => {
    const menuToggle = document.querySelector(".menu-toggle");
    const menu = document.querySelector(".menu");

    // Verifica si ambos elementos existen antes de agregar el evento
    if (menuToggle && menu) {
        menuToggle.addEventListener("click", (event) => {
            menu.classList.toggle("show"); // Alterna la clase "show" para mostrar/ocultar el menú
            event.stopPropagation(); // Evita que el clic en el botón cierre el menú inmediatamente
        });

        // Cierra el menú si se hace clic fuera de él
        document.addEventListener("click", (event) => {
            if (!menu.contains(event.target) && !menuToggle.contains(event.target)) {
                menu.classList.remove("show");
            }
        });
    } else {
        console.error("Error: Elementos '.menu-toggle' o '.menu' no encontrados en el DOM.");
    }
});

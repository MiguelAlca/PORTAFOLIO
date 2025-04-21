// Función para eliminar productos
document.querySelectorAll('.eliminar-btn').forEach(button => {
    button.addEventListener('click', function() {
        let confirmDelete = confirm("¿Estás seguro de que deseas eliminar este producto?");
        if (confirmDelete) {
            showLoading();
            let id = this.getAttribute('data-id');
            let cantidadInput = document.querySelector(`.cantidad-eliminar[data-id='${id}']`);
            let cantidad = cantidadInput.value || 0;

            fetch(`/productos/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cantidad: parseInt(cantidad) })
            })
            .then(response => {
                hideLoading();
                if (!response.ok) {
                    throw new Error('Error en la solicitud');
                }
                return response.json();
            })
            .then(data => {
                // Mostrar el mensaje en la página
                document.getElementById('texto-mensaje').textContent = data.mensaje;
                document.getElementById('total-eliminado').textContent = data.precio_reduccion.toFixed(2);
                document.getElementById('mensaje-eliminacion').style.display = 'block';

                // Recargar la página después de 3 segundos
                setTimeout(() => {
                    location.reload();
                }, 3000);
            })
            .catch(error => {
                hideLoading();
                alert("Error: " + error.message);
            });
        }
    });
});
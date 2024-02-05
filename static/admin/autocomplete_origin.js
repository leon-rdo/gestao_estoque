document.addEventListener('DOMContentLoaded', function () {
    const productUnitSelect = document.getElementById('id_product_unit');
    const originSelect = document.getElementById('id_origin');
    const destinationSelect = document.getElementById('id_destination');

    originSelect.readOnly = true;

    productUnitSelect.addEventListener('change', function () {
        const selectedProductUnit = this.value;

        fetch(`/get_product_location/${selectedProductUnit}`)
            .then(response => response.json())
            .then(data => {
                originSelect.value = data.location;
                checkOriginDestination();
            });
    });

    destinationSelect.addEventListener('change', function () {
        checkOriginDestination();
    });

    function checkOriginDestination() {
        if (originSelect.value === destinationSelect.value) {
            // Display an error message or take appropriate action
            alert("Origem e destino não podem ser iguais.");
            destinationSelect.value = '';
        }
    }
});
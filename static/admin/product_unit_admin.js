$(document).ready(function() {
    function toggleShelfField() {
        var locationText = $('#id_location option:selected').text();

        if (locationText.trim() === "Loja") {
            $('.field-shelf').show();
        } else {
            $('.field-shelf').hide();
        }
    }

    $('#id_location').change(function() {
        toggleShelfField();
    });


    toggleShelfField();
});

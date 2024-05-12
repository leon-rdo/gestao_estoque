$(document).ready(function() {
    // Função para mostrar ou ocultar o campo 'shelf' com base no valor selecionado no campo 'location'
    function toggleShelfField() {
        var locationText = $('#id_location option:selected').text();
        // Verifica se o texto selecionado do campo 'location' corresponde a "Loja"
        if (locationText.trim() === "Loja") {
            $('.field-shelf').show(); // Mostra o campo 'shelf' e seu elemento pai
        } else {
            $('.field-shelf').hide(); // Oculta o campo 'shelf' e seu elemento pai
        }
    }

    // Monitora as alterações no campo 'location'
    $('#id_location').change(function() {
        toggleShelfField();
    });

    // Executa a função ao carregar a página para garantir que o campo 'shelf' seja mostrado ou ocultado corretamente
    toggleShelfField();
});

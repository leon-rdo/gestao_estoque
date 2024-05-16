$(document).ready(function() {
    var isCreationMode = window.location.href.indexOf('/add/') !== -1;
    
    // Função para atualizar os campos dependendo da seleção
    function updateFields() {
        // Se o formulário não estiver em modo de criação, saia da função
        if (!isCreationMode) {
            return;
        }

        var locationSelected = $('#id_location option:selected').text().trim();
        var buildingSelected = $('#id_building').val();
        var roomSelected = $('#id_room').val();
        var hallSelected = $('#id_hall').val();
        var shelfSelected = $('#id_shelf').val(); // Adicionado aqui

        // Mostrar ou ocultar campos dependendo da localização selecionada
        if (locationSelected === "Loja") {
            $('.field-building').show();
        } else {
            $('.field-building').hide();
        }

        // Atualizar e mostrar o campo de salas se um prédio for selecionado
        if (buildingSelected) {
            $('.field-room').show();
            updateRooms(buildingSelected, roomSelected);
        } else {
            $('.field-room').hide();
        }

        // Atualizar e mostrar o campo de corredores se uma sala for selecionada
        if (roomSelected) {
            $('.field-hall').show();
            updateHalls(roomSelected, hallSelected);
        } else {
            $('.field-hall').hide();
        }

        // Atualizar e mostrar o campo de prateleiras se um corredor for selecionado
        if (hallSelected) {
            $('.field-shelf').show();
            updateShelves(hallSelected, shelfSelected);
        } else {
            $('.field-shelf').hide();
        }
    }

    // Função para buscar salas com base no prédio selecionado
    function updateRooms(buildingId, selectedRoom) {
        // Se a seleção de prédio estiver vazia, saia da função
        if (!buildingId) {
            return;
        }

        $.ajax({
            url: '/get-rooms/',
            data: {
                'building_id': buildingId
            },
            success: function(data) {
                $('#id_room').empty();
                $('#id_room').append($('<option>').text('---------').attr('value', ''));
                $.each(data, function(index, value) {
                    var option = $('<option>').text(value.name).attr('value', value.id);
                    if (value.id == selectedRoom) {
                        option.attr('selected', 'selected');
                    }
                    $('#id_room').append(option);
                });
            }
        });
    }

    // Função para buscar corredores com base na sala selecionada
    function updateHalls(roomId, selectedHall) {
        // Se a seleção de sala estiver vazia, saia da função
        if (!roomId) {
            return;
        }

        $.ajax({
            url: '/get-halls/',
            data: {
                'room_id': roomId
            },
            success: function(data) {
                $('#id_hall').empty();
                $('#id_hall').append($('<option>').text('---------').attr('value', ''));
                $.each(data, function(index, value) {
                    var option = $('<option>').text(value.name).attr('value', value.id);
                    if (value.id == selectedHall) {
                        option.attr('selected', 'selected');
                    }
                    $('#id_hall').append(option);
                });
            }
        });
    }

    // Função para buscar prateleiras com base no corredor selecionado
    function updateShelves(hallId, selectedShelf) {
        // Se a seleção de corredor estiver vazia, saia da função
        if (!hallId) {
            return;
        }

        $.ajax({
            url: '/get-shelves/',
            data: {
                'hall_id': hallId
            },
            success: function(data) {
                $('#id_shelf').empty();
                $('#id_shelf').append($('<option>').text('---------').attr('value', ''));
                $.each(data, function(index, value) {
                    var option = $('<option>').text(value.name).attr('value', value.id);
                    if (value.id == selectedShelf) {
                        option.attr('selected', 'selected');
                    }
                    $('#id_shelf').append(option);
                });
            }
        });
    }

    // Atualizar os campos quando ocorrer uma mudança nas seleções
    $('#id_location').change(function() {
        updateFields();
    });

    $('#id_building').change(function() {
        updateFields();
    });

    $('#id_room').change(function() {
        updateFields();
    });

    $('#id_hall').change(function() {
        updateFields();
    });

    // Inicializar os campos quando a página for carregada
    updateFields();
});

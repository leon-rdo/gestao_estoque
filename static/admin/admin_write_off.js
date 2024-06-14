$(document).ready(function() {
    var isCreationMode = window.location.href.indexOf('/add/') !== -1;
    
    
    function updateFields() {
        if (!isCreationMode) {
            $('.field-recomission_building').hide();
            $('.field-recomission_room').hide();
            $('.field-recomission_hall').hide();
            $('.field-recomission_shelf').hide();
            return;
        }

        var locationSelected = $('#id_recomission_storage_type option:selected').text().trim();
        var buildingSelected = $('#id_recomission_building').val();
        var roomSelected = $('#id_recomission_room').val();
        var hallSelected = $('#id_recomission_hall').val();
        var shelfSelected = $('#id_recomission_shelf').val(); 

        if (locationSelected === "Depósito") {
            $('.field-recomission_building').show();
        } else {
            $('.field-recomission_building').hide();
        }

        if (buildingSelected) {
            $('.field-recomission_room').show();
            updateRooms(buildingSelected, roomSelected);
        } else {
            $('.field-recomission_room').hide();
        }

        if (roomSelected) {
            $('.field-recomission_hall').show();
            updateHalls(roomSelected, hallSelected);
        } else {
            $('.field-recomission_hall').hide();
        }

        if (hallSelected) {
            $('.field-recomission_shelf').show();
            updateShelves(hallSelected, shelfSelected);
        } else {
            $('.field-recomission_shelf').hide();
        }
    }

    function updateRooms(buildingId, selectedRoom) {
        if (!buildingId) {
            return;
        }

        $.ajax({
            url: '/get-rooms/',
            data: {
                'building_id': buildingId
            },
            success: function(data) {
                $('#id_recomission_room').empty();
                $('#id_recomission_room').append($('<option>').text('---------').attr('value', ''));
                $.each(data, function(index, value) {
                    var option = $('<option>').text(value.name).attr('value', value.id);
                    if (value.id == selectedRoom) {
                        option.attr('selected', 'selected');
                    }
                    $('#id_recomission_room').append(option);
                });
            }
        });
    }

    function updateHalls(roomId, selectedHall) {
        if (!roomId) {
            return;
        }

        $.ajax({
            url: '/get-halls/',
            data: {
                'room_id': roomId
            },
            success: function(data) {
                $('#id_recomission_hall').empty();
                $('#id_recomission_hall').append($('<option>').text('---------').attr('value', ''));
                $.each(data, function(index, value) {
                    var option = $('<option>').text(value.name).attr('value', value.id);
                    if (value.id == selectedHall) {
                        option.attr('selected', 'selected');
                    }
                    $('#id_recomission_hall').append(option);
                });
            }
        });
    }

    function updateShelves(hallId, selectedShelf) {
        if (!hallId) {
            return;
        }

        $.ajax({
            url: '/get-shelves/',
            data: {
                'hall_id': hallId
            },
            success: function(data) {
                $('#id_recomission_shelf').empty();
                $('#id_recomission_shelf').append($('<option>').text('---------').attr('value', ''));
                $.each(data, function(index, value) {
                    var option = $('<option>').text(value.name).attr('value', value.id);
                    if (value.id == selectedShelf) {
                        option.attr('selected', 'selected');
                    }
                    $('#id_recomission_shelf').append(option);
                });
            }
        });
    }

    $('#id_recomission_storage_type').change(function() {
        updateFields();
    });

    $('#id_recomission_building').change(function() {
        updateFields();
    });

    $('#id_recomission_room').change(function() {
        updateFields();
    });

    $('#id_recomission_hall').change(function() {
        updateFields();
    });

    updateFields();  // Para a inicialização no carregamento da página

    // Função para atualizar os campos com base na unidade de produto selecionada
    function updateWriteOffFields() {
        var selectedProductUnit = $('#id_product_unit').val();
        
        if (selectedProductUnit) {
            $.ajax({
                url: '/get-write-off-status/' + selectedProductUnit + '/',
                method: 'GET',
                success: function(data) {
                    var writeOffStatus = data.write_off;
                    if (writeOffStatus === false) {
                        $('.field-storage_type').show();
                        $('.field-write_off_destination').show();
                        $('.field-recomission_storage_type').hide();
                    } else {
                        $('.field-storage_type').hide();
                        $('.field-write_off_destination').hide();
                        $('.field-recomission_storage_type').show();
                    }
                }
            });
        } else {
            $('.field-storage_type').hide();
            $('.field-write_off_destination').hide();
            $('.field-recomission_storage_type').hide();
            $('.field-recomission_building').hide();
            $('.field-recomission_room').hide();
            $('.field-recomission_hall').hide();
            $('.field-recomission_shelf').hide();
        }
    }

    $('#id_product_unit').change(function() {
        updateWriteOffFields();
    });

    updateWriteOffFields();  // Para a inicialização no carregamento da página
});

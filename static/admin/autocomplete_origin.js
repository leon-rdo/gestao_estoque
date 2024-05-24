$(document).ready(function() {
    $('#id_product_unit').change(function() {
        var selectedProductUnit = $(this).val();
        if (selectedProductUnit) {
            $.ajax({
                url: '/get-product-location-shelf/' + selectedProductUnit + '/',
                success: function(data) {
                    $('#id_origin_transfer_area').val(data.location).trigger('change');
                    $('#id_origin_shelf').val(data.shelf).trigger('change');
                }
            });
        }
    });
        var isCreationMode = window.location.href.indexOf('/add/') !== -1;
        console.log('aaaaaaa');
        function updateFields() {
            if (!isCreationMode) {
                return;
            }
    
            var locationSelected = $('#id_destination_transfer_area option:selected').text().trim();
            var buildingSelected = $('#id_destination_building').val();
            var roomSelected = $('#id_destination_room').val();
            var hallSelected = $('#id_destination_hall').val();
            var shelfSelected = $('#id_destination_shelf').val(); 
    
            if (locationSelected === "Loja") {
                $('.field-destination_building').show();
            } else {
                $('.field-destination_building').hide();
            }
    
            if (buildingSelected) {
                $('.field-destination_room').show();
                updateRooms(buildingSelected, roomSelected);
            } else {
                $('.field-destination_room').hide();
            }
    
            if (roomSelected) {
                $('.field-destination_hall').show();
                updateHalls(roomSelected, hallSelected);
            } else {
                $('.field-destination_hall').hide();
            }
    
            if (hallSelected) {
                $('.field-destination_shelf').show();
                updateShelves(hallSelected, shelfSelected);
            } else {
                $('.field-destination_shelf').hide();
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
                    $('#id_destination_room').empty();
                    $('#id_destination_room').append($('<option>').text('---------').attr('value', ''));
                    $.each(data, function(index, value) {
                        var option = $('<option>').text(value.name).attr('value', value.id);
                        if (value.id == selectedRoom) {
                            option.attr('selected', 'selected');
                        }
                        $('#id_destination_room').append(option);
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
                    $('#id_destination_hall').empty();
                    $('#id_destination_hall').append($('<option>').text('---------').attr('value', ''));
                    $.each(data, function(index, value) {
                        var option = $('<option>').text(value.name).attr('value', value.id);
                        if (value.id == selectedHall) {
                            option.attr('selected', 'selected');
                        }
                        $('#id_destination_hall').append(option);
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
                    $('#id_destination_shelf').empty();
                    $('#id_destination_shelf').append($('<option>').text('---------').attr('value', ''));
                    $.each(data, function(index, value) {
                        var option = $('<option>').text(value.name).attr('value', value.id);
                        if (value.id == selectedShelf) {
                            option.attr('selected', 'selected');
                        }
                        $('#id_destination_shelf').append(option);
                    });
                }
            });
        }
    
        $('#id_destination_transfer_area').change(function() {
            updateFields();
        });
    
        $('#id_destination_building').change(function() {
            updateFields();
        });
    
        $('#id_destination_room').change(function() {
            updateFields();
        });
    
        $('#id_destination_hall').change(function() {
            updateFields();
        });
    
        updateFields();
    });
    
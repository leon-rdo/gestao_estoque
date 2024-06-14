$(document).ready(function() {
    var isCreationMode = window.location.href.indexOf('/add/') !== -1;
    
    function updateFields() {
        if (!isCreationMode) {
            return;
        }

        var locationSelected = $('#id_location option:selected').text().trim();
        var buildingSelected = $('#id_building').val();
        var roomSelected = $('#id_room').val();
        var hallSelected = $('#id_hall').val();
        var shelfSelected = $('#id_shelf').val(); 

        if (locationSelected === "Depósito") {
            $('.field-building').show();
        } else {
            $('.field-building').hide();
        }

        if (buildingSelected) {
            $('.field-room').show();
            updateRooms(buildingSelected, roomSelected);
        } else {
            $('.field-room').hide();
        }

        if (roomSelected) {
            $('.field-hall').show();
            updateHalls(roomSelected, hallSelected);
        } else {
            $('.field-hall').hide();
        }

        if (hallSelected) {
            $('.field-shelf').show();
            updateShelves(hallSelected, shelfSelected);
        } else {
            $('.field-shelf').hide();
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

    updateFields();
});

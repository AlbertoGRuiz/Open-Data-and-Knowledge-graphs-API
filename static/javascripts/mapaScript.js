$(document).ready(function() {
    var map = L.map("map").setView([40.42, -3.7], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributor | " +
            "&copy; <a href='https://datos.madrid.es/portal/site/egob/menuitem.3efdb29b813ad8241e830cc2a8a409a0/?vgnextoid=108804d4aab90410VgnVCM100000171f5a0aRCRD&vgnextchannel=b4c412b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default'>Ayuntamiento de Madrid</a> source"
    }).addTo(map);

    map.invalidateSize();

    // Conjunto de capas para los marcadores
    var markersLayer = new L.LayerGroup().addTo(map);

    // Función de autocompletado
    $('#street-input').on('input', function() {
        var inputText = $(this).val().toLowerCase();

        // Hacer una solicitud al servidor para obtener resultados
        $.ajax({
            url: '/api/autocomplete/calle/' + inputText, 
            type: 'GET',
            dataType: 'json', // Especifica el tipo de datos como JSON
            success: function(data) {
                // Limpiar resultados anteriores
                var autocompleteResults = $('#autocomplete-results');
                autocompleteResults.empty();

                // Recorrer los nombres devueltos por el servidor y mostrarlos
                data.forEach(function(result) {
                    autocompleteResults.append('<div class="autocomplete-item">' + result + '</div>');
                });
            },
            error: function() {
                console.error('Error en la solicitud AJAX');
                var autocompleteResults = $('#autocomplete-results');
                autocompleteResults.empty();
            }
        });
    });

    // Manejar clic en resultado de autocompletado
    $('#autocomplete-results').on('click', '.autocomplete-item', function() {
        var selectedStreet = $(this).text();
        alert('Has seleccionado la calle: ' + selectedStreet);
        var loadingBar = $('#loading-bar');
        loadingBar.css('display', 'block');

        // Borrar marcadores anteriores
        markersLayer.clearLayers();

        // Hacer una solicitud al servidor para obtener resultados de locales
        $.ajax({
            url: '/api/search/locales/' + selectedStreet,
            type: 'GET',
            dataType: 'json', // Especifica el tipo de datos como JSON
            success: function(data) {
                // Recorrer los resultados devueltos por el servidor
                data.forEach(function(result) {

                    // Crear un marcador en el mapa con las coordenadas
                    var marker = L.marker([result.lat, result.long]).addTo(markersLayer);
                    var autocompleteResults = $('#autocomplete-results');
                    autocompleteResults.empty();
                    loadingBar.css('display', 'none');

                    // Mostrar la URL al hacer clic en el marcador
                    marker.on('click', function() {
                        $('#local-url').html('<a href="' + result.local + '" target="_blank">Ver más información</a>');
                    });
                    map.on('click', function() {
                        $('#local-url').empty(); // Borra la URL al hacer clic en otro lugar del mapa
                    });
                    $('#street-input').on('click', function() {
                        $('#local-url').empty(); // Borra la URL al hacer clic en otro lugar del mapa
                    });
                    map.setView(marker.getLatLng(), 15);
                });
            },
            error: function() {
                console.error('Error en la solicitud AJAX');
            }
        });
    });
});

$(document).ready(function() {
    var map = L.map("map").setView([40.42, -3.7], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributor | " +
            "&copy; <a href='https://datos.madrid.es/portal/site/egob/menuitem.3efdb29b813ad8241e830cc2a8a409a0/?vgnextoid=108804d4aab90410VgnVCM100000171f5a0aRCRD&vgnextchannel=b4c412b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default'>Ayuntamiento de Madrid</a> source"
    }).addTo(map);

    map.invalidateSize();

    // Conjunto de capas para los marcadores
    var markersLayer = new L.LayerGroup().addTo(map);

    // Array para almacenar las coordenadas de los marcadores
    var markerCoords = [];

    // Función de autocompletado
    $('#street-input').on('input', function() {
        var inputText = $(this).val().toLowerCase();

        var autocompleteResults = $('#autocomplete-select');
            autocompleteResults.empty();
            autocompleteResults.hide();
        if (inputText.trim() === "") {
            return;
        }

        // Hacer una solicitud al servidor para obtener resultados
        var loadingBar = $('#loading-bar');
        loadingBar.css('display', 'block');
        $.ajax({
            url: '/api/search/distrito/' + inputText, 
            type: 'GET',
            dataType: 'json', // Especifica el tipo de datos como JSON
            success: function(data) {

                // Crear un nuevo elemento select
                console.log(data)
                var select = $('<select class="autocomplete-select"></select>');
                var option = $('<option></option>');
                option.val('Selecciona un distrito');
                option.text('Selecciona un distrito');
                select.append(option);
            
                // Recorrer los nombres devueltos por el servidor y mostrarlos
                data.nombres.forEach(function(result) {
                    // Crear un nuevo elemento option
                    var option = $('<option></option>');
                    option.val(result);
                    option.text(result);
            
                    // Añadir el elemento option al elemento select
                    select.append(option);
                });
            
                // Establecer el HTML de autocompleteResults en el HTML del elemento select
                var autocompleteResults = $('#autocomplete-select');
                autocompleteResults.empty();
                autocompleteResults.append(select);
                autocompleteResults.show();
                $('#loading-bar').css('display', 'none');
            },
            error: function() {
                $('#loading-bar').css('display', 'none');
                console.error('Error en la solicitud AJAX');
                var autocompleteResults = $('#autocomplete-select');
                autocompleteResults.empty();
            }
        });
    });

    // Manejar clic en resultado de autocompletado
    $('#autocomplete-select').on('change', 'select', function() {
        var selectedStreet = $(this).find('option:selected').text();
        if("Selecciona un distrito" === selectedStreet){
            return;
        }
        alert('Has seleccionado el distrito: ' + selectedStreet);
        var loadingBar = $('#loading-bar');
        loadingBar.css('display', 'block');

        // Vaciar el array de coordenadas
        markerCoords = [];

        // Hacer una solicitud al servidor para obtener resultados de locales
        $.ajax({
            url: '/api/search/distrito/' + selectedStreet+ '/locales',
            type: 'GET',
            dataType: 'json', // Especifica el tipo de datos como JSON
            success: function(data) {
                // Recorrer los resultados devueltos por el servidor
                // Borrar marcadores anteriores
                markersLayer.clearLayers();
                data.locales.forEach(function(result) {
                    if(result.lat < 43.75 && result.lat > 27.75 && result.long < 4.75 && result.long > -18.75){
                        // Crear un marcador en el mapa con las coordenadas
                        var marker = L.marker([result.lat, result.long]).addTo(markersLayer);

                        marker.bindPopup(`
                            <strong>Local:</strong> ${result.rotulo} <br>
                            <strong>Situación:</strong> ${result.situacion} <br>
                            <strong>Lat, long:</strong> ${result.lat},${result.long} <br>
                            <strong>HoraApertura:</strong> ${result.horaApertura} horas <br>
                            <strong>HoraCierre:</strong> ${result.horaCierre} horas <br>
                            <strong>Terraza:</strong>
                            <ul>
                                <li><strong>sillas:</strong> ${result.sillas}</li>
                                <li><strong>mesas:</strong> ${result.mesas}</li>
                                <li><strong>superficie:</strong> ${result.superficie} m<sup>2</sup></li>
                            </ul>
                        `);
                        var autocompleteResults = $('#autocomplete-results');
                        autocompleteResults.empty();
                        // Añadir las coordenadas del marcador al array
                        markerCoords.push([parseFloat(result.lat), parseFloat(result.long)]);

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
                    }
                });

                // Calcular la media de las coordenadas de los marcadores
                var avgLat = markerCoords.reduce(function(sum, coord) {
                    return sum + coord[0];
                }, 0) / markerCoords.length;
                var avgLng = markerCoords.reduce(function(sum, coord) {
                    return sum + coord[1];
                }, 0) / markerCoords.length;
                // Centrar el mapa en la media de las coordenadas
                map.setView([avgLat, avgLng], 13);
                setTimeout(function() {
                    $('#loading-bar').css('display', 'none');
                    $('#correct-bar').css('display', 'block');
                    setTimeout(function() {
                        $('#correct-bar').css('display', 'none');
                    }, 5000);
                }, 2000);
                
            },
            error: function() {
                // Borrar marcadores anteriores
                markersLayer.clearLayers();
                console.error('Error en la solicitud AJAX');
            }
        });
    });
});

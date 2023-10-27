import requests
import pyproj
import warnings

# Desactivar advertencias FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Helios URL endpoint to make queries from the RDF
URL_HELIOS = "http://localhost:9000/api/sparql"


def completar_distrito(filtro, result):
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX madridonc: <http://madridalfresco.es/lcc/ontology/locales#>

    SELECT DISTINCT ?nombre
            WHERE {{
                ?dist rdf:type madridonc:Distrito.
                ?dist madridonc:nombreDistrito ?nombre.
                FILTER(CONTAINS(LCASE(?nombre), "{}")).
            }}
    """.format(str(filtro))

    params = {
        "query": query
    }

    response = requests.get(URL_HELIOS, params=params)

    if response.status_code == 200:
        data = response.json()
        nombres = [item['nombre']['value'].encode('latin-1').decode('utf-8') for item in data['results']['bindings']]
        print("Petición helios éxito")
        result['nombres'] = nombres
        return result
    else:
        # Si la solicitud no se completó con éxito, muestra el código de estado
        print(f"Error: Código de estado {response.status_code}")
        return result


def buscar_locales(filtro, result):
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX madridonc: <http://madridalfresco.es/lcc/ontology/locales#>
    SELECT DISTINCT ?local ?coordX ?coordY ?horaCierre ?horaApertura ?rotulo ?situacion ?mesas ?sillas ?superficie
        WHERE {{
            ?dist rdf:type madridonc:Distrito.
            ?dist madridonc:nombreDistrito ?nombreDelDistrito.
            ?local rdf:type madridonc:Local.
            ?local madridonc:perteneceADistrito ?dist;
                   madridonc:coordenadaX ?coordX;
                   madridonc:coordenadaY ?coordY;
                   madridonc:horaCierre ?horaCierre;
                   madridonc:horaApertura ?horaApertura;
                   madridonc:tieneTerraza ?terraza;
                   madridonc:rotulo ?rotulo;
                   madridonc:situacion ?situacion.
            ?terraza madridonc:mesas ?mesas;
                    madridonc:sillas ?sillas;
                    madridonc:superficie ?superficie.
            FILTER(LCASE(?nombreDelDistrito) = "{}").
        }}""".format(str(filtro).lower())

    params = {
        "query": query
    }

    response = requests.get(URL_HELIOS, params=params)

    if response.status_code == 200:
        # Muestra la respuesta JSON (si la API devuelve datos en formato JSON)
        data = response.json()

        for item in data['results']['bindings']:
            latitud, longitud = utm_to_latlon(item['coordX']['value'], item['coordY']['value'])
            local = {
                "local": item['local']['value'],
                "lat": str(latitud),
                "long": str(longitud),
                "horaCierre": item['horaCierre']['value'],
                "horaApertura": item['horaApertura']['value'],
                "rotulo": item['rotulo']['value'],
                "situacion": item['situacion']['value'],
                "mesas": item['mesas']['value'],
                "sillas": item['sillas']['value'],
                "superficie": item['superficie']['value']
            }
            result['locales'].append(local)
        print("Petición helios éxito")
        return result

    else:
        # Si la solicitud no se completó con éxito, muestra el código de estado
        print(f"Error: Código de estado {response.status_code}")
        return result


def utm_to_latlon(coord_x, coord_y, zona_utm=30, hemisferio='N'):
    # Define el sistema de coordenadas UTM y el sistema de coordenadas de latitud y longitud (WGS84)
    utm = pyproj.Proj(proj='utm', zone=zona_utm, ellps='WGS84', south=(hemisferio == 'S'))
    latlon = pyproj.Proj(proj='latlong', datum='WGS84')

    # Realiza la conversión
    longitud, latitud = pyproj.transform(utm, latlon, coord_x, coord_y)

    return latitud, longitud

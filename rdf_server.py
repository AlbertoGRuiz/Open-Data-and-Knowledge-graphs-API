from flask import Flask, render_template, jsonify, request
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
import os
import json
import pyproj
from rdflib.namespace import  XSD
from tqdm import tqdm
import warnings

# Desactivar advertencias FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
madridonc = Namespace("http://madridalfresco.es/lcc/ontology/locales#")
madridrec = Namespace ("http://madridalfresco.es/lcc/resource/")
def utm_to_latlon(coordX, coordY, zona_utm=30, hemisferio='N'):
    # Define el sistema de coordenadas UTM y el sistema de coordenadas de latitud y longitud (WGS84)
    utm = pyproj.Proj(proj='utm', zone=zona_utm, ellps='WGS84', south=(hemisferio == 'S'))
    latlon = pyproj.Proj(proj='latlong', datum='WGS84')

    # Realiza la conversión
    longitud, latitud = pyproj.transform(utm, latlon, coordX, coordY)

    return latitud, longitud
def transform_all_rdf_coordinates():
    # Consulta SPARQL para obtener todos los locales
    query = prepareQuery(
        f"""SELECT ?local ?coordX ?coordY
        WHERE {{
            ?local rdf:type madridonc:Local;
                  madridonc:coordenadaX ?coordX;
                  madridonc:coordenadaY ?coordY.
        }}""",
        initNs={"madridonc": madridonc}
    )

    # Realiza la consulta en el grafo
    resultados = g.query(query)

    # Recorre los resultados y transforma las coordenadas de cada local
    progress_bar = tqdm(total=len(resultados), desc="Cargando RDF")
    for row in resultados:
        local_uri = URIRef(str(row.local))
        coordX = float(row.coordX)
        coordY = float(row.coordY)

        latitud, longitud = utm_to_latlon(coordX, coordY)

        # Actualiza las coordenadas en el grafo para el local actual
        g.set((local_uri, madridonc.coordenadaX, Literal(latitud, datatype=XSD.float)))
        g.set((local_uri, madridonc.coordenadaY, Literal(longitud, datatype=XSD.float)))
        progress_bar.update(1)
    progress_bar.close()
    return "Coordenadas de todos los locales transformadas y actualizadas."
current_directory = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(current_directory,'templates'))

# Cargar el archivo RDF y hacer que 'g' sea global
archivo_rdf = os.path.join(current_directory,'files\\rdf_with_rules.ttl')  # Ruta al archivo RDF que deseas cargar
g = Graph()
g.parse(archivo_rdf, format='ttl')
transform_all_rdf_coordinates()

# Ruta para mostrar el mapa Leaflet y proporcionar datos RDF
@app.route('/')
def mostrar_mapa():
    return render_template("mapa.html")

# Punto final de API para obtener datos RDF en formato JSON
@app.route('/api/autocomplete/calle/<filtro>', methods=['GET'])
def autocomplete_calle(filtro):
    print(f"Buscando por calle {filtro}")
    query = prepareQuery(
        f"""SELECT DISTINCT ?nombre
        WHERE {{
            ?distr rdf:type madridonc:Distrito;
                   madridonc:nombreCalle ?nombre.
            FILTER(CONTAINS(LCASE(?nombre), "{filtro.lower()}"))
        }}""",
        initNs={"madridonc": madridonc}
    )
    
    resultados = g.query(query)
    nombres = [str(row.nombre) for row in resultados]
    nombres_json = json.dumps(nombres)
    return nombres_json

@app.route('/api/search/locales/<filtro>', methods=['GET'])
def search_locales(filtro):
    print(f"Buscando por calle {filtro}")
        # Primera consulta para obtener la URL del distrito
    query_dist = prepareQuery(
        f"""SELECT DISTINCT ?dist
        WHERE {{
            ?dist rdf:type madridonc:Distrito.
            ?dist madridonc:nombreCalle ?nombre.
            FILTER(LCASE(?nombre) = "{filtro.lower()}").
        }}""",
        initNs={"madridonc": madridonc, "madridrec": madridrec}
    )
    resultados_dist = g.query(query_dist)
    
    # Inicializa una variable para almacenar la URL del distrito
    url_distrito = None
    
    # Recorre los resultados de la primera consulta para obtener la URL del distrito
    for row in resultados_dist:
        url_distrito = str(row.dist)  # Asume que la URL del distrito es una cadena
    print(f"Buscando por distrito {url_distrito}")
    if url_distrito:
        # Segunda consulta utilizando la URL del distrito
        query_local = prepareQuery(
            f"""SELECT DISTINCT ?local ?coordX ?coordY
            WHERE {{
                <{url_distrito}> madridonc:nombreCalle ?nombre.
                FILTER(LCASE(?nombre) = "{filtro.lower()}").
                
                <{url_distrito}> rdf:type madridonc:Distrito.
                ?local rdf:type madridonc:Local.
            
                ?local madridonc:perteneceADistrito <{url_distrito}>;
                       madridonc:coordenadaX ?coordX;
                       madridonc:coordenadaY ?coordY.
                
            }}""",
            initNs={"madridonc": madridonc, "madridrec": madridrec}
        )
        resultados_local = g.query(query_local)
        resultados_estructurados = []
        for row in resultados_local:
            resultado = {
                "local": str(row.local),
                "lat": str(row.coordX),
                "long": str(row.coordY)
            }
            resultados_estructurados.append(resultado)
        resultados_json = json.dumps(resultados_estructurados)
        return resultados_json
    return json.dumps([])




if __name__ == '__main__':
    app.run(debug=True)

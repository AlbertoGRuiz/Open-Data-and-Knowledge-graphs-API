from api.route import core

from flask import Blueprint, render_template, request
from flasgger import swag_from
from http import HTTPStatus
from unidecode import unidecode

from api.schema.distrito_schema import DistritoSchema
from api.schema.locales_schema import LocalesSchema

home_api = Blueprint('api', __name__)
map = Blueprint('/', __name__)
DISTRITOS = core.completar_distrito("", {"nombres": []})


@map.route('/')
def mostrar_mapa():
    return render_template('mapa.html')


@home_api.route('/search/distrito/<filtro>', methods=['GET'])
@swag_from({
    'parameters': [{
        "name": "filtro",
        "in": "path",
        "description": "district to be filtered among districts",
        "type": "string",
        "required": False,
        "default": "hortaleza"
    }],
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'List of coincidences',
            'schema': DistritoSchema
        }
    }
})
def autocomplete_distrito(filtro):
    """
    Endpoint to analyze an email.

    ---
    """
    try:

        if 'filtro' in request.view_args.keys():
            if not str(request.view_args.get('filtro')) == '{filtro}':
                filtro = str(request.view_args.get('filtro'))
            else:
                filtro = ''
        else:
            filtro = ''

        if filtro == '':
            return DistritoSchema().dump({[]}), 200
        print("El filtro es {}".format(str(filtro)))

        result = {"nombres": []}

        if filtro == 'default':
            for distrito in DISTRITOS['nombres']:
                result['nombres'].append(distrito)
            return DistritoSchema().dump(result), 200

        for distrito in DISTRITOS['nombres']:
            if str(distrito.lower()).startswith(filtro.lower()) or unidecode(distrito.lower()).startswith(
                    filtro.lower()):
                result['nombres'].append(distrito)

        return DistritoSchema().dump(result), 200
    except Exception as e:
        print(str(e))


@home_api.route("/search/distrito/<filtro>/locales", methods=['GET'])
@swag_from({
    'parameters': [{
        "name": "filtro",
        "in": "path",
        "description": "restaurants to be filtered among a district",
        "type": "string",
        "required": False,
        "default": "madrid"
    }],
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'List of coincidences',
            'schema': LocalesSchema
        }
    }
})
def search_locales(filtro):
    """
    Endpoint to analyze an email.

    ---
    """
    try:
        if 'filtro' in request.view_args.keys():
            if not str(request.view_args.get('filtro')) == '{filtro}':
                filtro = str(request.view_args.get('filtro'))
            else:
                filtro = ''
        else:
            filtro = ''

        if filtro == '':
            return DistritoSchema().dump({[]}), 200

        print("El filtro es {}".format(str(filtro)))

        result = {"locales": []}

        result = core.buscar_locales(filtro, result)

        return LocalesSchema().dump(result), 200
    except Exception as e:
        print(str(e))

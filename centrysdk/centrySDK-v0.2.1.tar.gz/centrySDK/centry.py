import urllib.parse
import requests


class Centry:
    # Constructor de la clase SDK.
    #
    # @param [String] client_id Identificador de la aplicación. Es generado por
    # Centry.
    # @param [String] client_secret Clave secreta de la aplicación. Es generado
    # por Centry, debe ser conocido sólo por la aplicación y Centry. Los usuarios
    # no tienen que tener acceso a este dato.
    # @param [String] redirect_uri URL a la que Centry enviará el código de
    # autorización como parámetro GET cada vez que un usuario autorice a ésta a
    # acceder a sus datos. Si se usa la URI `urn:ietf:wg:oauth:2.0:oob`, entonces
    # el código de autorización se mostrará en pantalla y el usuario deberá
    # copiarlo y pegarlo donde la aplicación pueda leerlo.
    # @param [String] access_token (opcional) Último access_token del que se tiene
    # registro. Si se entrega, entonces no es necesario que el usuario tenga que
    # volver a autorizar la aplicacción.
    # @param [String] refresh_token (opcional) Último refresh_token del que se
    # tiene registro.
    # @return [Centry] una nueva instancia del SDK.
    def __init__(self, client_id, client_secret, redirect_uri, access_token=None, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.__PUBLIC_ENDPOINTS = [
            'oauth/token'
        ]

    ##
    # Genera la URL con la que le pediremos a un usuario que nos entregue los
    # permisos de lectura y/o escritura a los recursos que se indican en el
    # parámetro <code>scope</code>.
    #
    # @param [String] scope Es la concatenación con un espacio de separación (" ")
    # de todos los ámbitos a los que se solicita permiso. Estos pueden ser:
    # * *public* Para acceder a la información publica de Centry como marcas, categorías, colores, tallas, etc.
    # * *read_orders* Para leer información de pedidos
    # * *write_orders* Para manipular o eliminar pedidos
    # * *read_products* Para leer información de productos y variantes
    # * *write_products* Para manipular o eliminar productos y variantes
    # * *read_integration_config* Para leer información de configuraciones de integraciones
    # * *write_integration_config* Para manipular o eliminar configuraciones de integraciones
    # * *read_user* Para leer información de usuarios de la empresa
    # * *write_user* Para manilupar o eliminar usuarios de la empresa
    # * *read_webhook* Para leer información de webhooks
    # * *write_webhook* Para manilupar o eliminar webhooks
    # @return [String] URL para redirigir a los usuarios y solicitarles la
    # autorización de acceso.
    def authorization_url(self, scope):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope
        }
        return f"https://www.centry.cl/oauth/authorize?{urllib.parse.urlencode(params)}"

    ##
    # Método encargado de hacer todo tipo de solicitudes a Centry, desde
    # autorizaciones hasta manipulación de inventario.
    #
    # @param [String] endpoint Ruta o recurso de la API.
    # @param [symbol] method Indica el método HTTP a usar. Las opciones son:
    # * +:get+
    # * +:post+
    # * +:put+
    # * +:delete+
    # Como es una API REST, estos métodos suelen estar asociados a la lectura,
    # creación, edición y eliminacion de recursos.
    # @param [Hash] params (opcional) Llaves y valores que irán en la URL como
    # parámetros GET
    # @param [Hash] payload (opcional) Body del request. El SDK se
    # encargará de transformarlo en un JSON.
    # @return [Net::HTTPResponse] resultado del request.
    def request(self, endpoint, method, params=None, payload=None):
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        req = None
        uri = f"https://www.centry.cl/{endpoint}"
        header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if endpoint not in self.__PUBLIC_ENDPOINTS:
            header['Authorization'] = f"Bearer {self.access_token}"

        if method == 'get':
            req = requests.get(uri, params=params, headers=header)
        elif method == 'post':
            req = requests.post(uri, params=params, headers=header, json=payload)
        elif method == 'put':
            req = requests.put(uri, params=params, headers=header, json=payload)
        elif method == 'delete':
            req = requests.delete(uri, params=params, headers=header)
        return req

    # Atajo para generar requests GET
    #
    # @param [String] endpoint Ruta o recurso de la API.
    # @param [Hash] params (opcional) Llaves y valores que irán en la URL como
    # parámetros GET
    # @return [Hash]
    def get(self, endpoint, params=None):
        if params is None:
            params = {}
        return self.request(endpoint, 'get', params)

    # Atajo para generar requests POST
    #
    # @param [String] endpoint Ruta o recurso de la API.
    # @param [Hash] params (opcional) Llaves y valores que irán en la URL como
    # parámetros GET
    # @param [Hash] payload (opcional) Body del request. El SDK se
    # encargará de transformarlo en un JSON.
    def post(self, endpoint, params=None, payload=None):
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        return self.request(endpoint, 'post', params, payload)

    # Atajo para generar requests PUT
    #
    # @param [String] endpoint Ruta o recurso de la API.
    # @param [Hash] params (opcional) Llaves y valores que irán en la URL como
    # parámetros GET
    # @param [Hash] payload (opcional) Body del request. El SDK se
    # encargará de transformarlo en un JSON.
    def put(self, endpoint, params=None, payload=None):
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        return self.request(endpoint, 'put', params, payload)

    # Atajo para generar requests DELETE
    #
    # @param [String] endpoint Ruta o recurso de la API.
    # @param [Hash] params (opcional) Llaves y valores que irán en la URL como
    # parámetros GET
    def delete(self, endpoint, params=None):
        if params is None:
            params = {}
        return self.request(endpoint, 'delete', params)

    # Una vez que un usuario ha autorizado nuestra aplicación para que accceda a
    # su información, Centry genera un código de autorización con el cual podremos
    # solicitar el primer access_token y refresh_token. Éste método se encarga de
    # esta tarea por lo que se le debe entrecar el código de autorización como
    # parámetro.
    #
    # Se recomienda registrar estos tokens con algún mecanismo de persistencia
    # como una base de datos.
    #
    # @param [String] code Código de autorización generado por Centry depués de
    # que el usuario autorizó la aplicación.
    #
    # @see https://www.oauth.com/oauth2-servers/access-tokens/authorization-code-request/
    def authorize(self, code):
        return self.__grant('authorization_code', {'code': code})

    # Un access_token tiene una vigencia de 7200 segudos (2 horas) por lo que una
    # vez cumplido ese plazo es necesario solicitar un nuevo token usando como
    # llave el refresh_token que teníamos registrado. Este método se encarga de
    # hacer esta renovacion de tokens.
    #
    # Se recomienda registrar estos nuevos tokens con algún mecanismo de
    # persistencia como una base de datos.
    #
    # @see https://www.oauth.com/oauth2-servers/access-tokens/authorization-code-request/
    def refresh(self):
        return self.__grant('refresh_token', {'refresh_token': self.refresh_token})

    # Este mecanismo de autorización es utilizado en aplicaciones que requieren
    # acceso a sus propios recursos.
    #
    # @param [String] scope Es la concatenación con un espacio de separación (" ") de todos los ámbitos a
    # los que se solicita permiso. Estos pueden ser:
    # * *public* Para acceder a la información publica de Centry como marcas, categorías, colores, tallas, etc.
    # * *read_orders* Para leer información de pedidos
    # * *write_orders* Para manipular o eliminar pedidos
    # * *read_products* Para leer información de productos y variantes
    # * *write_products* Para manipular o eliminar productos y variantes
    # * *read_integration_config* Para leer información de configuraciones de integraciones
    # * *write_integration_config* Para manipular o eliminar configuraciones de integraciones
    # * *read_user* Para leer información de usuarios de la empresa
    # * *write_user* Para manilupar o eliminar usuarios de la empresa
    # * *read_webhook* Para leer información de webhooks
    # * *write_webhook* Para manilupar o eliminar webhooks
    #
    # @see https://www.oauth.com/oauth2-servers/access-tokens/client-credentials/
    def client_credentials(self, scope=None):
        s = {} if (scope is None) or (scope.strip() == '') else {'scope': scope.strip()}
        return self.__grant('client_credentials', s)

    # Endpoints de la API de Centry que no requieren de un access_token.
    def __grant(self, grant_type, extras):
        p = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': grant_type,
        }
        payload = {**p, **extras}
        response = self.post('oauth/token', {}, payload)
        assert (response.status_code == requests.codes.ok), response.json()
        body = response.json()
        if 'access_token' in body.keys():
            self.access_token = body['access_token']
        if 'refresh_token' in body.keys():
            self.refresh_token = body['refresh_token']
        if 'token_type' in body.keys():
            self.token_type = body['token_type']
        if 'scope' in body.keys():
            self.scope = body['scope']
        if 'created_at' in body.keys():
            self.created_at = body['created_at']
        if 'expires_in' in body.keys():
            self.expires_in = body['expires_in']
        return self

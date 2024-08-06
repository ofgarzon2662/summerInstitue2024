import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Administrador, Restaurante

from app import app

class TestRestaurante(TestCase):

    
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Administrador(usuario=nombre_usuario, contrasena=contrasena_encriptada)
        db.session.add(usuario_nuevo)
        db.session.commit()
        
        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        solicitud_login = self.client.post("/login",
                                                data=json.dumps(usuario_login),
                                                headers={'Content-Type': 'application/json'})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]
        
        self.restaurantes_creados = []
        
    def test_crear_restaurante_Un_Campo_Vacio(self):
        nombre = ""
        direccion = self.data_factory.sentence()
        telefono = self.data_factory.sentence()
        redes_sociales = self.data_factory.url()
        hora_apertura = self.data_factory.time()
        servicio_sitio = self.data_factory.boolean()
        servicio_domicilio = self.data_factory.boolean()
        tipo_comida = self.data_factory.sentence()
        plataformas = self.data_factory.sentence()

        # Se crea el restaurante
        restaurante = {
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono,
            "redes_sociales": redes_sociales,
            "hora_apertura": hora_apertura,
            "servicio_sitio": servicio_sitio,
            "servicio_domicilio": servicio_domicilio,
            "tipo_comida": tipo_comida,
            "plataformas": plataformas
        }
        # Se envía la solicitud de creación del restaurante
        endpoint = "/usuarios/{}/restaurantes".format(str(self.usuario_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        solicitud_restaurante = self.client.post(endpoint,
                                                 data=json.dumps(restaurante),
                                                 headers=headers)
        # Se verifica que la solicitud haya sido fallida
        self.assertEqual(solicitud_restaurante.status_code, 400)

    def test_crear_restaurante(self):
        # Se crean los datos del restaurante
        nombre = self.data_factory.name()
        direccion = self.data_factory.sentence()
        telefono = self.data_factory.sentence()
        redes_sociales = self.data_factory.url()
        hora_apertura = self.data_factory.time()
        servicio_sitio = self.data_factory.boolean()
        servicio_domicilio = self.data_factory.boolean()
        tipo_comida = self.data_factory.sentence()
        plataformas = self.data_factory.sentence()

        # Se crea el restaurante
        restaurante = {
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono,
            "redes_sociales": redes_sociales,
            "hora_apertura": hora_apertura,
            "servicio_sitio": servicio_sitio,
            "servicio_domicilio": servicio_domicilio,
            "tipo_comida": tipo_comida,
            "plataformas": plataformas
        }
        # Se envía la solicitud de creación del restaurante
        endpoint = "/usuarios/{}/restaurantes".format(str(self.usuario_id))

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        solicitud_restaurante = self.client.post(endpoint,
                                                 data=json.dumps(restaurante),
                                                 headers=headers)
        # Se verifica que la solicitud haya sido exitosa
        self.assertEqual(solicitud_restaurante.status_code, 200)

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar    
        respuesta_restaurante = json.loads(solicitud_restaurante.get_data())
        restaurante_creado = Restaurante.query.get(respuesta_restaurante["id"])
        self.restaurantes_creados.append(restaurante_creado)

        # Se verifica que los datos del restaurante creado sean los mismos que los enviados
        self.assertEqual(restaurante_creado.nombre, nombre)
        self.assertEqual(restaurante_creado.direccion, direccion)
        self.assertEqual(restaurante_creado.telefono, telefono)
        self.assertEqual(restaurante_creado.redes_sociales, redes_sociales)
        self.assertEqual(restaurante_creado.hora_apertura, hora_apertura)
        self.assertEqual(restaurante_creado.servicio_sitio, servicio_sitio)
        self.assertEqual(restaurante_creado.servicio_domicilio, servicio_domicilio)
        self.assertEqual(restaurante_creado.tipo_comida, tipo_comida)
        self.assertEqual(restaurante_creado.plataformas, plataformas)
            
    def test_crear_restaurante_ya_creado(self):
        # Se crea el restaurante
         # Se crean los datos del restaurante
        nombre = self.data_factory.name()
        direccion = self.data_factory.sentence()
        telefono = self.data_factory.sentence()
        redes_sociales = self.data_factory.url()
        hora_apertura = self.data_factory.time()
        servicio_sitio = self.data_factory.boolean()
        servicio_domicilio = self.data_factory.boolean()
        tipo_comida = self.data_factory.sentence()
        plataformas = self.data_factory.sentence()

        # Se crea el restaurante
        restaurante = {
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono,
            "redes_sociales": redes_sociales,
            "hora_apertura": hora_apertura,
            "servicio_sitio": servicio_sitio,
            "servicio_domicilio": servicio_domicilio,
            "tipo_comida": tipo_comida,
            "plataformas": plataformas
        }
        # Se envía la solicitud de creación del restaurante
        endpoint = "/usuarios/{}/restaurantes".format(str(self.usuario_id))

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        solicitud_restaurante = self.client.post(endpoint,
                                                 data=json.dumps(restaurante),
                                                 headers=headers)
        

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar    
        respuesta_restaurante = json.loads(solicitud_restaurante.get_data())
        restaurante_creado = Restaurante.query.get(respuesta_restaurante["id"])

        # Se crea un nuevo restaurante con el mismo nombre

        restaurante = {
            "nombre": restaurante_creado.nombre,
            "direccion": restaurante_creado.direccion,
            "telefono": restaurante_creado.telefono,
            "redes_sociales": restaurante_creado.redes_sociales,
            "hora_apertura": restaurante_creado.hora_apertura,
            "servicio_sitio": restaurante_creado.servicio_sitio,
            "servicio_domicilio": restaurante_creado.servicio_domicilio,
            "tipo_comida": restaurante_creado.tipo_comida,
            "plataformas": restaurante_creado.plataformas
        }

        # Se envía la solicitud de creación del restaurante
        endpoint = "/usuarios/{}/restaurantes".format(str(self.usuario_id))

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        solicitud_restaurante = self.client.post(endpoint,
                                                 data=json.dumps(restaurante),
                                                 headers=headers)
        # Se verifica que la solicitud haya sido exitosa
        self.assertEqual(solicitud_restaurante.status_code, 422)

        #Se verifica el mensaje de error
        json_data = json.loads(solicitud_restaurante.data)
        
        self.assertIn('El Restaurante con nombre {} ya existe dentro de la cadena'.format(restaurante_creado.nombre), json_data['mensaje'])
        


    def tearDown(self):
        for restaurante_creados in self.restaurantes_creados:
            restaurante = Restaurante.query.get(restaurante_creados.id)
            db.session.delete(restaurante)
            db.session.commit()
            
        usuario_login = Administrador.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_obtener_lista_vacia_restaurantes(self):
        #Definir endpoint, encabezados y hacer el llamado
        endpoint = "/usuarios/{}/restaurantes".format(str(self.usuario_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_restaurantes = self.client.get(endpoint, headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_restaurantes.get_data())   

        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_consulta_restaurantes.status_code, 200)

        #Verificar que la lista de restaurantes este vacia
        self.assertEquals(len(datos_respuesta),0)

    def test_obtener_lista_restaurantes(self):
         #Generar 10 restaurantes con datos aleatorios
        for i in range(0,10):
            #Crear los datos del restaurante
            nombre_nuevo_restaurante = self.data_factory.sentence()
            direccion_nuevo_ingrediente = self.data_factory.sentence()
            telefono_nuevo_ingrediente = self.data_factory.sentence()
            redes_sociales_nuevo_ingrediente = self.data_factory.sentence()
            hora_apertura_nuevo_ingrediente = self.data_factory.sentence()
            servicio_sitio_nuevo_ingrediente = bool(random.getrandbits(1))
            servicio_domicilio_nuevo_ingrediente = bool(random.getrandbits(1))
            tipo_comida_nuevo_ingrediente = self.data_factory.sentence()
            plataformas_nuevo_ingrediente = self.data_factory.sentence()
            
            #Crear el restaurante con los datos originales para obtener su id
            restaurante = Restaurante(
                nombre = nombre_nuevo_restaurante,
                direccion = direccion_nuevo_ingrediente,
                telefono = telefono_nuevo_ingrediente,
                redes_sociales = redes_sociales_nuevo_ingrediente,
                hora_apertura = hora_apertura_nuevo_ingrediente,               
                servicio_sitio = servicio_sitio_nuevo_ingrediente,
                servicio_domicilio = servicio_domicilio_nuevo_ingrediente,
                tipo_comida = tipo_comida_nuevo_ingrediente,
                plataformas = plataformas_nuevo_ingrediente,
                administrador = self.usuario_id
            )
            db.session.add(restaurante)
            db.session.commit()
            self.restaurantes_creados.append(restaurante)

        #Definir endpoint, encabezados y hacer el llamado
        endpoint = "/usuarios/{}/restaurantes".format(str(self.usuario_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_restaurantes = self.client.get(endpoint, headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_restaurantes.get_data())   

        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_consulta_restaurantes.status_code, 200)

        #Verificar los restaurantes creados con sus datos
        for restaurante in datos_respuesta:
            for restaurante_creado in self.restaurantes_creados:
                if restaurante['id'] == str(restaurante_creado.id):
                    self.assertEqual(restaurante['nombre'], restaurante_creado.nombre)
                    self.assertEqual(restaurante['direccion'], restaurante_creado.direccion)
                    self.assertEqual(restaurante['telefono'], restaurante_creado.telefono)
                    self.assertEqual(restaurante['redes_sociales'], restaurante_creado.redes_sociales)
                    self.assertEqual(restaurante['hora_apertura'], restaurante_creado.hora_apertura)
                    self.assertEqual(restaurante['servicio_sitio'], restaurante_creado.servicio_sitio)
                    self.assertEqual(restaurante['servicio_domicilio'], restaurante_creado.servicio_domicilio)
                    self.assertEqual(restaurante['plataformas'], restaurante_creado.plataformas)

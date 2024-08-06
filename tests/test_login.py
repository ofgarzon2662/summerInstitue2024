import json
import hashlib
from unittest import TestCase
from faker import Faker
from faker.generator import random
from modelos import db, Administrador, Chef
from app import app

class TestLogin(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        # Se crea el usuario para identificarse en la aplicación
        administrador = Administrador(usuario=nombre_usuario, contrasena=contrasena_encriptada)
        db.session.add(administrador)
        db.session.commit()
        self.usuario_login_admin = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }
        solicitud_login_admin = self.client.post("/login",
                                                data=json.dumps(self.usuario_login_admin),
                                                headers={'Content-Type': 'application/json'})
        respuesta_login_admin = json.loads(solicitud_login_admin.get_data())
        self.token = respuesta_login_admin["token"]
        self.usuario_id_admin = respuesta_login_admin["id"]

        nombre_usuario_chef = 'testC' + self.data_factory.name()
        contrasena_chef = 'T1$' + self.data_factory.word()
        contrasena_encriptada_chef = hashlib.md5(contrasena_chef.encode('utf-8')).hexdigest()
        # Se crea el usuario para identificarse en la aplicación
        chef = Chef(usuario=nombre_usuario_chef, contrasena=contrasena_encriptada_chef)
        db.session.add(chef)
        db.session.commit()
        self.usuario_login_chef = {
            "usuario": nombre_usuario_chef,
            "contrasena": contrasena_chef
        }
        solicitud_login_chef = self.client.post("/login",
                                                data=json.dumps(self.usuario_login_chef),
                                                headers={'Content-Type': 'application/json'})
        respuesta_login_chef = json.loads(solicitud_login_chef.get_data())
        self.token = respuesta_login_chef["token"]
        self.usuario_id_chef = respuesta_login_chef["id"]

    def tearDown(self):
        # Eliminar administrador creado para la prueba
        administrador = Administrador.query.get(self.usuario_id_admin)
        db.session.delete(administrador)
        db.session.commit()
        # Eliminar chef creado para la prueba
        chef = Chef.query.get(self.usuario_id_chef)
        db.session.delete(chef)
        db.session.commit()

    def test_obtener_tipo_login_admin(self):
         #Definir endpoint, encabezados y hacer el llamado
        endpoint_login = "/login"
        headers = {'Content-Type': 'application/json'}
        
        resultado_login_admin = self.client.post(endpoint_login, data=json.dumps(self.usuario_login_admin),
                                                   headers=headers)
        datos_respuesta = json.loads(resultado_login_admin.get_data())
        self.assertEqual(datos_respuesta["tipo"], "Administrador")
    
    def test_obtener_tipo_login_chef(self):
         #Definir endpoint, encabezados y hacer el llamado
        endpoint_login = "/login"
        headers = {'Content-Type': 'application/json'}
        
        resultado_login_chef = self.client.post(endpoint_login, data=json.dumps(self.usuario_login_chef),
                                                   headers=headers)
        datos_respuesta = json.loads(resultado_login_chef.get_data())
        self.assertEqual(datos_respuesta["tipo"], "Chef")
    
    def test_crear_admin_usuario_existe(self):
         #Definir endpoint, encabezados y hacer el llamado
        endpoint_login = "/signin"
        headers = {'Content-Type': 'application/json'}
        
        resultado_login_admin = self.client.post(endpoint_login, data=json.dumps(self.usuario_login_chef),
                                                   headers=headers)
        datos_respuesta = json.loads(resultado_login_admin.get_data())
        self.assertEqual(datos_respuesta['mensaje'], "El usuario ya existe")
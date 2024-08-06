import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Administrador, Restaurante, Chef

from app import app

class TestChef(TestCase):

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
        # Crear restaurante
        restaurante = Restaurante(administrador = self.usuario_id)
        db.session.add(restaurante)
        db.session.commit()
        self.restaurante_id = restaurante.id
        self.chef_creados = []

    def tearDown(self):
        # Eliminar chef creados en la prueba
        for chef_creado in self.chef_creados:
            chef = Chef.query.get(chef_creado.id)
            db.session.delete(chef)
            db.session.commit()
        # Eliminar restaurante creado para la prueba
        restaurante = Restaurante.query.get(self.restaurante_id)
        db.session.delete(restaurante)
        db.session.commit()
        # Eliminar administrador creado para la prueba
        administrador = Administrador.query.get(self.usuario_id)
        db.session.delete(administrador)
        db.session.commit()

    def test_obtener_chefs(self):
        for i in range(0, 10):
            nombre_nuevo_chef = self.data_factory.name()
            usuario_nuevo_chef = self.data_factory.name()
            contrasena_nuevo_chef = self.data_factory.password()
            administrador_nuevo_chef = self.usuario_id
            chef = Chef(nombre=nombre_nuevo_chef, usuario=usuario_nuevo_chef, contrasena=contrasena_nuevo_chef, restaurante=self.restaurante_id)
            db.session.add(chef)
            db.session.commit()
            self.chef_creados.append(chef)
        endpoint = "/restaurantes/{}/chefs".format(str(self.restaurante_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())
        self.assertEqual(resultado.status_code, 200)
        for chef in datos:
            for chef_creado in self.chef_creados:
                if chef['id'] == str(chef_creado.id):
                    self.assertEqual(chef['nombre'], chef_creado.nombre)
                    self.assertEqual(chef['usuario'], chef_creado.usuario)
                    self.assertEqual(chef['contrasena'], chef_creado.contrasena)
    
    def test_crear_chef(self):
        #Crear los datos del chef
        nombre_nuevo_chef = self.data_factory.name()
        usuario_nuevo_chef = self.data_factory.name()
        contrasena_nuevo_chef = self.data_factory.password()
        restaurante_nuevo_chef = self.restaurante_id
        
        #Crear el json con el chef a crear
        nuevo_chef = {
            "nombre": nombre_nuevo_chef,
            "usuario": usuario_nuevo_chef,
            "contrasena": contrasena_nuevo_chef,
            "restaurante": restaurante_nuevo_chef
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_chefs = "/restaurantes/{}/chefs".format(str(self.restaurante_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_nuevo_chef = self.client.post(endpoint_chefs,
                                                   data=json.dumps(nuevo_chef),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_chef.get_data())

        chef = Chef.query.get(datos_respuesta['id'])
        self.chef_creados.append(chef)        
                                                   
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nuevo_chef.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], chef.nombre)
        self.assertEqual(datos_respuesta['usuario'], chef.usuario)
        self.assertEqual(datos_respuesta['contrasena'], chef.contrasena)
        self.assertIsNotNone(datos_respuesta['id'])
        
import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Administrador, Restaurante, Receta, Menu

from app import app

class TestMenu(TestCase):
    
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        nombre_usuario = self.data_factory.name()
        contrasena = self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        # Crear administrador
        administrador = Administrador(usuario=nombre_usuario, contrasena=contrasena_encriptada)
        db.session.add(administrador)
        db.session.commit()
        # Obtener token administrador
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
        # Crear receta
        receta = Receta(usuario = self.usuario_id, administrador = self.usuario_id)
        db.session.add(receta)
        db.session.commit()
        self.receta_id = receta.id

        self.menus_creados = []

    def tearDown(self):
        # Eliminar menus creados
        for menu_creado in self.menus_creados:
            db.session.delete(menu_creado)
            db.session.commit()
        # Eliminar receta
        receta = Receta.query.get(self.receta_id)
        db.session.delete(receta)
        db.session.commit()
        # Eliminar restaurante
        restaurante = Restaurante.query.get(self.restaurante_id)
        db.session.delete(restaurante)
        db.session.commit()
        # Eliminar administrador
        administrador = Administrador.query.get(self.usuario_id)
        db.session.delete(administrador)
        db.session.commit()

    def test_crear_menu_como_administrador(self):
        # Crear cuerpo de la petición
        cuerpo_peticion = {
            'nombre': self.data_factory.name(),
            'fechaInicio': "2023-01-01",
            'fechaFin': '2023-01-02',
            'autor': self.receta_id,
            'descripcion':self.data_factory.sentence(),
            'foto': "https://picsum.photos/200/300",
            'restaurante':self.restaurante_id,
            'recetas': [{
                'personas': 10,
                'receta': self.receta_id 
            }]
        }
        # Crear URL
        url = "/usuarios/{}/menus".format(self.usuario_id)
        # Crear cabeceras
        cabeceras = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        # Enviar la petición
        respuesta = self.client.post(url, data = json.dumps(cuerpo_peticion), headers = cabeceras)
        datos = json.loads(respuesta.get_data())
        # Verificar respuesta
        self.assertEqual(respuesta.status_code, 200)
        self.assertIsNotNone(datos['id'])
        self.menus_creados.append(Menu.query.get(datos['id']))

    def test_editar_menu_usuario_incorrecto(self):
        cuerpo_peticion_editar = {}

         #URL para editar menu
        url = "/usuarios/{}/menu/{}".format(random.randint(1000, 2000), random.randint(1000, 2000))

        #Crear cabeceras
        cabeceras = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }

         # Enviar la petición de editar menu
        respuesta = self.client.put(url, data = json.dumps(cuerpo_peticion_editar), headers = cabeceras)
        datos = json.loads(respuesta.get_data())

        # Verificar respuesta de crear menu
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual("No existe un usuario con ese id", datos['mensaje'])

    def test_editar_menu_incorrecto(self):
        cuerpo_peticion_editar = {}

         #URL para editar menu
        url = "/usuarios/{}/menu/{}".format(self.usuario_id, random.randint(1000, 2000))

        #Crear cabeceras
        cabeceras = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }

         # Enviar la petición de editar menu
        respuesta = self.client.put(url, data = json.dumps(cuerpo_peticion_editar), headers = cabeceras)
        datos = json.loads(respuesta.get_data())

        # Verificar respuesta de crear menu
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual("No existe un menú con ese id", datos['mensaje'])    

    def test_editar_menu(self):
        # Crear cuerpo de la petición para crear el menu
        cuerpo_peticion_crear = {
            'nombre': self.data_factory.name(),
            'fechaInicio': "2023-01-01",
            'fechaFin': "2023-01-02",
            'autor': self.receta_id,
            'descripcion':self.data_factory.sentence(),
            'foto': "https://picsum.photos/200/300",
            'restaurante':self.restaurante_id,
            'recetas': [{
                'personas': random.randint(1, 100),
                'receta': self.receta_id 
            }]
        }

        #URL para crear menu
        url = "/usuarios/{}/menus".format(self.usuario_id)

        #Crear cabeceras
        cabeceras = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }

        # Enviar la petición de crear menu
        respuesta = self.client.post(url, data = json.dumps(cuerpo_peticion_crear), headers = cabeceras)
        datos = json.loads(respuesta.get_data())

        # Verificar respuesta de crear menu
        self.assertEqual(respuesta.status_code, 200)
        self.assertIsNotNone(datos['id'])
        self.menus_creados.append(Menu.query.get(datos['id']))

        #Crear cuerpo de la petición para editar el menu
        nombre = self.data_factory.name()
        fechaInicio = "2024-05-01"
        fechaFin = "2024-05-02"
        descripcion = self.data_factory.sentence()
        foto = "https://picsum.photos/200/300"
        personas = random.randint(100, 200)
        cuerpo_peticion_editar = {
            'nombre': nombre,
            'fechaInicio': fechaInicio,
            'fechaFin': fechaFin,
            'descripcion': descripcion,
            'foto': foto,
            'recetas': [{
                'personas': personas,
                'receta': self.receta_id 
            }]
        }

        #URL para editar menu
        url = "/usuarios/{}/menu/{}".format(self.usuario_id, self.menus_creados[0].id)

         # Enviar la petición de editar menu
        respuesta = self.client.put(url, data = json.dumps(cuerpo_peticion_editar), headers = cabeceras)
        datos = json.loads(respuesta.get_data())

        # Verificar respuesta de crear menu
        self.assertEqual(respuesta.status_code, 200)
        self.assertIsNotNone(datos['id'])
        self.assertEqual(nombre, datos['nombre'])
        self.assertEqual(fechaInicio, datos['fechaInicio'])
        self.assertEqual(fechaFin, datos['fechaFin'])
        self.assertEqual(descripcion, datos['descripcion'])
        self.assertEqual(foto, datos['foto'])
        self.assertEqual(personas, int(datos['recetas'][0]['personas']))
        self.assertEqual(self.receta_id, int(datos['recetas'][0]['receta']))

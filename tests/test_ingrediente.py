import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Administrador, Ingrediente

from app import app


class TestIngrediente(TestCase):

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
        
        self.ingredientes_creados = []
        
    
    def tearDown(self):
        for ingrediente_creado in self.ingredientes_creados:
            ingrediente = Ingrediente.query.get(ingrediente_creado.id)
            db.session.delete(ingrediente)
            db.session.commit()
            
        usuario_login = Administrador.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_crear_ingrediente(self):
        #Crear los datos del ingrediente
        nombre_nuevo_ingrediente = self.data_factory.sentence()
        unidad_nuevo_ingrediente = self.data_factory.sentence()
        costo_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        calorias_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        sitio_nuevo_ingrediente = self.data_factory.sentence()
        
        #Crear el json con el ingrediente a crear
        nuevo_ingrediente = {
            "nombre": nombre_nuevo_ingrediente,
            "unidad": unidad_nuevo_ingrediente,
            "costo": costo_nuevo_ingrediente,
            "calorias": calorias_nuevo_ingrediente,
            "sitio": sitio_nuevo_ingrediente
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_ingredientes = "/usuarios/{}/ingredientes".format(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_nuevo_ingrediente = self.client.post(endpoint_ingredientes,
                                                   data=json.dumps(nuevo_ingrediente),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_ingrediente.get_data())
        ingrediente = Ingrediente.query.get(datos_respuesta['id'])
        self.ingredientes_creados.append(ingrediente)

        
                                                   
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nuevo_ingrediente.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], ingrediente.nombre)
        self.assertEqual(datos_respuesta['unidad'], ingrediente.unidad)
        self.assertEqual(float(datos_respuesta['costo']), float(ingrediente.costo))
        self.assertEqual(float(datos_respuesta['calorias']), float(ingrediente.calorias))
        self.assertEqual(datos_respuesta['sitio'], ingrediente.sitio)
        self.assertIsNotNone(datos_respuesta['id'])

    def test_editar_ingrediente(self):
        #Crear los datos del ingrediente
        nombre_nuevo_ingrediente = self.data_factory.sentence()
        unidad_nuevo_ingrediente = self.data_factory.sentence()
        costo_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        calorias_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        sitio_nuevo_ingrediente = self.data_factory.sentence()
        
        #Crear los datos que quedarán luego de la edición
        nombre_ingrediente_editado = self.data_factory.sentence()
        unidad_ingrediente_editado = self.data_factory.sentence()
        costo_ingrediente_editado = round(random.uniform(0.1, 0.99), 2)
        calorias_ingrediente_editado = round(random.uniform(0.1, 0.99), 2)
        sitio_ingrediente_editado = self.data_factory.sentence()
        
        #Crear el ingrediente con los datos originales para obtener su id
        ingrediente = Ingrediente(nombre = nombre_nuevo_ingrediente,
                              unidad=unidad_nuevo_ingrediente,
                              costo=costo_nuevo_ingrediente,
                              calorias=calorias_nuevo_ingrediente,
                              sitio=sitio_nuevo_ingrediente)
        db.session.add(ingrediente)
        db.session.commit()
        self.ingredientes_creados.append(ingrediente)
        
        #Crear el json con el ingrediente a editar
        ingrediente_editado = {
            "nombre": nombre_ingrediente_editado,
            "unidad": unidad_ingrediente_editado,
            "costo": costo_ingrediente_editado,
            "calorias": calorias_ingrediente_editado,
            "sitio": sitio_ingrediente_editado
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_ingredientes = "/ingredientes/{}".format(str(ingrediente.id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_edicion_ingrediente = self.client.put(endpoint_ingredientes,
                                                   data=json.dumps(ingrediente_editado),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_edicion_ingrediente.get_data())
                                                   
        #Verificar que el llamado fue exitoso y que el objeto recibido no tiene los datos originales
        self.assertEqual(resultado_edicion_ingrediente.status_code, 200)
        self.assertNotEqual(datos_respuesta['nombre'], nombre_nuevo_ingrediente)
        self.assertNotEqual(datos_respuesta['unidad'], unidad_nuevo_ingrediente)
        self.assertNotEqual(float(datos_respuesta['costo']), costo_nuevo_ingrediente)
        self.assertNotEqual(float(datos_respuesta['calorias']), calorias_nuevo_ingrediente)
        self.assertNotEqual(datos_respuesta['sitio'], sitio_nuevo_ingrediente)
        
        #Verificar que el llamado retornó los datos cambiados según el id enviado
        self.assertEqual(datos_respuesta['id'],str(ingrediente.id))
        self.assertEqual(datos_respuesta['nombre'], nombre_ingrediente_editado)
        self.assertEqual(datos_respuesta['unidad'], unidad_ingrediente_editado)
        self.assertEqual(float(datos_respuesta['costo']), costo_ingrediente_editado)
        self.assertEqual(float(datos_respuesta['calorias']), calorias_ingrediente_editado)
        self.assertEqual(datos_respuesta['sitio'], sitio_ingrediente_editado)

    def test_borrar_ingrediente(self):
        nombre_nuevo_ingrediente = self.data_factory.sentence()
        unidad_nuevo_ingrediente = self.data_factory.sentence()
        costo_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        calorias_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        sitio_nuevo_ingrediente = self.data_factory.sentence()
        
        #Crear el ingrediente directamente con los datos originales para obtener su id
        ingrediente = Ingrediente(nombre = nombre_nuevo_ingrediente,
                              unidad=unidad_nuevo_ingrediente,
                              calorias=calorias_nuevo_ingrediente,
                              costo=costo_nuevo_ingrediente,
                              sitio=sitio_nuevo_ingrediente)
        db.session.add(ingrediente)
        db.session.commit()
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_ingredientes = "/ingredientes/{}".format(str(ingrediente.id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        resultado_borrado_ingrediente = self.client.delete(endpoint_ingredientes,
                                                   headers=headers)
                                                   
        #Verificar que el llamado retornó los datos cambiados según el id enviado
        self.assertEqual(resultado_borrado_ingrediente.status_code, 204)
        
        #Busco el ingrediente y verfico que ya no exista
        ingrediente_borrado = Ingrediente.query.get(ingrediente.id)
        self.assertIsNone(ingrediente_borrado)

    def test_dar_ingrediente(self):
        #Crear los datos del ingrediente
        nombre_nuevo_ingrediente = self.data_factory.sentence()
        unidad_nuevo_ingrediente = self.data_factory.sentence()
        costo_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        calorias_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        sitio_nuevo_ingrediente = self.data_factory.sentence()
        
        #Crear el ingrediente con los datos originales para obtener su id
        ingrediente = Ingrediente(nombre = nombre_nuevo_ingrediente,
                              unidad=unidad_nuevo_ingrediente,
                              calorias=calorias_nuevo_ingrediente,
                              costo=costo_nuevo_ingrediente,
                              sitio=sitio_nuevo_ingrediente)
        db.session.add(ingrediente)
        db.session.commit()
        self.ingredientes_creados.append(ingrediente)
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_ingredientes = "/ingredientes/{}".format(str(ingrediente.id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_ingrediente = self.client.get(endpoint_ingredientes,
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_ingrediente.get_data())
                                                   
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_consulta_ingrediente.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], nombre_nuevo_ingrediente)
        self.assertEqual(datos_respuesta['unidad'], unidad_nuevo_ingrediente)
        self.assertEqual(float(datos_respuesta['costo']), float(costo_nuevo_ingrediente))
        self.assertEqual(float(datos_respuesta['calorias']), float(calorias_nuevo_ingrediente))
        self.assertEqual(datos_respuesta['sitio'], sitio_nuevo_ingrediente)
        self.assertIsNotNone(datos_respuesta['id'])

    
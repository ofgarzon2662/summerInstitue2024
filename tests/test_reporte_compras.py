import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Administrador, Restaurante, RecetaIngrediente, Ingrediente, Receta

from app import app


class TestReporteCompras(TestCase):

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
        # Crear restaurante
        restaurante = Restaurante(administrador = self.usuario_id)
        db.session.add(restaurante)
        db.session.commit()
        self.restaurante_id = restaurante.id
        
        self.recetas_creadas = []
        self.recetas_ingrediente_creadas = []
        self.ingredientes_creados = []
        
    
    def tearDown(self):
        for receta_ingrediente_creado in self.recetas_ingrediente_creadas:
            receta_ingrediente = RecetaIngrediente.query.get(receta_ingrediente_creado.id)
            db.session.delete(receta_ingrediente)
            db.session.commit()
        
        for receta_creada in self.recetas_creadas:
            receta = Receta.query.get(receta_creada.id)
            db.session.delete(receta)
            db.session.commit()

        for ingrediente_creado in self.ingredientes_creados:
            ingrediente = Ingrediente.query.get(ingrediente_creado.id)
            db.session.delete(ingrediente)
            db.session.commit()
        
        restaurante = Restaurante.query.get(self.restaurante_id)
        db.session.delete(restaurante)
        db.session.commit()

        usuario_login = Administrador.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_una_receta_un_ingrediente_misma_porcion(self):
        #Crear ingrediente
        nombre_nuevo_ingrediente = self.data_factory.word()
        unidad_nuevo_ingrediente = self.data_factory.word()
        costo_nuevo_ingrediente = self.data_factory.random_number(digits=5)
        calorias_nuevo_ingrediente = self.data_factory.random_number(digits=3)
        sitio_nuevo_ingrediente = self.data_factory.word()
        administrador_nuevo_ingrediente = self.usuario_id
        ingrediente = Ingrediente(nombre = nombre_nuevo_ingrediente, unidad = unidad_nuevo_ingrediente, costo = costo_nuevo_ingrediente, calorias = calorias_nuevo_ingrediente, sitio = sitio_nuevo_ingrediente, administrador = administrador_nuevo_ingrediente)
        db.session.add(ingrediente)
        db.session.commit()
        self.ingredientes_creados.append(ingrediente)
        #Crear receta
        nombre_nueva_receta = self.data_factory.word()
        duracion_nueva_receta = self.data_factory.random_number(digits=3)
        porcion_random = self.data_factory.random_number(digits=2)
        porcion_nueva_receta = porcion_random
        preparacion_nueva_receta = self.data_factory.sentence()
        receta = Receta(nombre = nombre_nueva_receta, duracion = duracion_nueva_receta, porcion = porcion_nueva_receta, preparacion = preparacion_nueva_receta, usuario = self.usuario_id, administrador = self.usuario_id)
        db.session.add(receta)
        db.session.commit()
        self.recetas_creadas.append(receta)
        #Crear union ingrediente receta
        cantidad_random = self.data_factory.random_number(digits=1)
        receta_ingrediente = RecetaIngrediente(cantidad = cantidad_random, ingrediente = ingrediente.id, receta = receta.id)
        db.session.add(receta_ingrediente)
        db.session.commit()
        self.recetas_ingrediente_creadas.append(receta_ingrediente)

        endpoint_reporte = "/reporteMenu"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        cuerpo_peticion = {
            'recetas': [{
                'personas': porcion_random,
                'id': receta.id 
            }]
        }
        print(cuerpo_peticion)
        resultado_reporte = self.client.post(endpoint_reporte,
                                                   data=json.dumps(cuerpo_peticion),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_reporte.get_data())
        self.assertEqual(datos_respuesta[str(ingrediente.id)]['cantidad'], str(cantidad_random))
    
    def test_una_receta_un_ingrediente_diferente_porcion(self):
        #Crear ingrediente
        nombre_nuevo_ingrediente = self.data_factory.word()
        unidad_nuevo_ingrediente = self.data_factory.word()
        costo_nuevo_ingrediente = self.data_factory.random_number(digits=5)
        calorias_nuevo_ingrediente = self.data_factory.random_number(digits=3)
        sitio_nuevo_ingrediente = self.data_factory.word()
        administrador_nuevo_ingrediente = self.usuario_id
        ingrediente = Ingrediente(nombre = nombre_nuevo_ingrediente, unidad = unidad_nuevo_ingrediente, costo = costo_nuevo_ingrediente, calorias = calorias_nuevo_ingrediente, sitio = sitio_nuevo_ingrediente, administrador = administrador_nuevo_ingrediente)
        db.session.add(ingrediente)
        db.session.commit()
        self.ingredientes_creados.append(ingrediente)
        #Crear receta
        nombre_nueva_receta = self.data_factory.word()
        duracion_nueva_receta = self.data_factory.random_number(digits=3)
        porcion_random = self.data_factory.random_number(digits=2)
        porcion_nueva_receta = porcion_random
        preparacion_nueva_receta = self.data_factory.sentence()
        receta = Receta(nombre = nombre_nueva_receta, duracion = duracion_nueva_receta, porcion = porcion_nueva_receta, preparacion = preparacion_nueva_receta, usuario = self.usuario_id, administrador = self.usuario_id)
        db.session.add(receta)
        db.session.commit()
        self.recetas_creadas.append(receta)
        #Crear union ingrediente receta
        cantidad_random = self.data_factory.random_number(digits=1)
        receta_ingrediente = RecetaIngrediente(cantidad = cantidad_random, ingrediente = ingrediente.id, receta = receta.id)
        db.session.add(receta_ingrediente)
        db.session.commit()
        self.recetas_ingrediente_creadas.append(receta_ingrediente)

        endpoint_reporte = "/reporteMenu"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        personas_random = self.data_factory.random_number(digits=2)
        cuerpo_peticion = {
            'recetas': [{
                'personas': personas_random,
                'id': receta.id 
            }]
        }
        print(cuerpo_peticion)
        resultado_reporte = self.client.post(endpoint_reporte,
                                                   data=json.dumps(cuerpo_peticion),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_reporte.get_data())
        self.assertEqual(float(datos_respuesta[str(ingrediente.id)]['cantidad']), float((personas_random*cantidad_random)/porcion_random))
    
    def test_dos_receta_mismo_ingrediente_misma_porcion(self):
        #Crear ingrediente
        nombre_nuevo_ingrediente = self.data_factory.word()
        unidad_nuevo_ingrediente = self.data_factory.word()
        costo_nuevo_ingrediente = self.data_factory.random_number(digits=5)
        calorias_nuevo_ingrediente = self.data_factory.random_number(digits=3)
        sitio_nuevo_ingrediente = self.data_factory.word()
        administrador_nuevo_ingrediente = self.usuario_id
        ingrediente = Ingrediente(nombre = nombre_nuevo_ingrediente, unidad = unidad_nuevo_ingrediente, costo = costo_nuevo_ingrediente, calorias = calorias_nuevo_ingrediente, sitio = sitio_nuevo_ingrediente, administrador = administrador_nuevo_ingrediente)
        db.session.add(ingrediente)
        db.session.commit()
        self.ingredientes_creados.append(ingrediente)
        #Crear receta 1
        nombre_nueva_receta = self.data_factory.word()
        duracion_nueva_receta = self.data_factory.random_number(digits=3)
        porcion_random1 = self.data_factory.random_number(digits=2)
        porcion_nueva_receta = porcion_random1
        preparacion_nueva_receta = self.data_factory.sentence()
        receta1 = Receta(nombre = nombre_nueva_receta, duracion = duracion_nueva_receta, porcion = porcion_nueva_receta, preparacion = preparacion_nueva_receta, usuario = self.usuario_id, administrador = self.usuario_id)
        db.session.add(receta1)
        db.session.commit()
        self.recetas_creadas.append(receta1)
        #Crear receta 2
        nombre_nueva_receta = self.data_factory.word()
        duracion_nueva_receta = self.data_factory.random_number(digits=3)
        porcion_random2 = self.data_factory.random_number(digits=2)
        porcion_nueva_receta = porcion_random2
        preparacion_nueva_receta = self.data_factory.sentence()
        receta2 = Receta(nombre = nombre_nueva_receta, duracion = duracion_nueva_receta, porcion = porcion_nueva_receta, preparacion = preparacion_nueva_receta, usuario = self.usuario_id, administrador = self.usuario_id)
        db.session.add(receta2)
        db.session.commit()
        self.recetas_creadas.append(receta2)
        #Crear union ingrediente receta 1
        cantidad_random1 = self.data_factory.random_number(digits=1)
        receta_ingrediente1 = RecetaIngrediente(cantidad = cantidad_random1, ingrediente = ingrediente.id, receta = receta1.id)
        db.session.add(receta_ingrediente1)
        db.session.commit()
        self.recetas_ingrediente_creadas.append(receta_ingrediente1)
        #Crear union ingrediente receta 2
        cantidad_random2 = self.data_factory.random_number(digits=1)
        receta_ingrediente2 = RecetaIngrediente(cantidad = cantidad_random2, ingrediente = ingrediente.id, receta = receta2.id)
        db.session.add(receta_ingrediente2)
        db.session.commit()
        self.recetas_ingrediente_creadas.append(receta_ingrediente2)

        endpoint_reporte = "/reporteMenu"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        personas_random1 = self.data_factory.random_number(digits=2)
        personas_random2 = self.data_factory.random_number(digits=2)
        cuerpo_peticion = {
            'recetas': [{
                'personas': personas_random1,
                'receta': receta1.id 
            }, {'personas': personas_random2,
                'receta': receta2.id }]
        }
        print(cuerpo_peticion)
        resultado_reporte = self.client.post(endpoint_reporte,
                                                   data=json.dumps(cuerpo_peticion),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_reporte.get_data())
        self.assertEqual(str(datos_respuesta[str(ingrediente.id)]['cantidad']), str(((personas_random1*cantidad_random1)/porcion_random1) + ((personas_random2*cantidad_random2)/porcion_random2)))
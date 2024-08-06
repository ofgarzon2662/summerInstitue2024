import json
import hashlib
from unittest import TestCase
from faker import Faker
from modelos import db, Administrador, Restaurante, Receta, Menu, Chef, MenuReceta
from app import app
from datetime import date

class TestMenu(TestCase):
    
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        self.menus_creados = []
        self.chef_creados = []
        self.recetas_creadas = []
        self.admin_creados = []
        self.restaurante_creados = []
        
        #self.admin_token, self.admin_usuario_id = self.create_and_login_user(Administrador)
        #self.chef_token, self.chef_usuario_id = self.create_and_login_user(Chef)
        #self.restaurante_id = self.create_restaurante()
        #self.receta_id = self.create_receta()

        # Add chef to restaurant
        #chef = Chef.query.get(self.chef_usuario_id)
        #chef.restaurante = self.restaurante_id
        #db.session.commit()

        # Create a menu
    def create_menu(self, 
                    nombre=None, 
                    descripcion=None, 
                    fechaInicio=None, 
                    fechaFin=None,
                    foto=None, 
                    autor=None, 
                    restaurante=None,
                    recetas=None):  # Adicionamos un parametro para tener en cuenta recetas
        menu = Menu(
            nombre=nombre, 
            descripcion=descripcion, 
            fechaInicio=fechaInicio,
            fechaFin=fechaFin, 
            foto=foto, 
            autor=autor or self.chef_usuario_id, 
            restaurante=restaurante or self.restaurante.id
            )
        db.session.add(menu)
        db.session.commit()

        # Adicionamos instancias MenuReceta para asociar recetas con menu
        if recetas:
            for receta in recetas:
                menu_receta = MenuReceta(
                    personas=4, # Seteamos un valor por defecto
                    menu=menu.id,  
                    receta=receta.id,
                )
                db.session.add(menu_receta)

        db.session.commit()
        return menu


    def create_and_login_user(self, user_class):
        nombre_usuario, contrasena = self.generate_user_data()
        encrypted_password = self.encrypt_password(contrasena)
        self.create_user_in_db(user_class, nombre_usuario, encrypted_password)
        return self.login_and_get_token(nombre_usuario, contrasena)

    def generate_user_data(self):
        return self.data_factory.name(), self.data_factory.word()

    def encrypt_password(self, contrasena):
        return hashlib.md5(contrasena.encode('utf-8')).hexdigest()

    def create_user_in_db(self, user_class, nombre_usuario, encrypted_password):
        user = user_class(usuario=nombre_usuario, contrasena=encrypted_password)
        db.session.add(user)
        db.session.commit()

    def login_and_get_token(self, nombre_usuario, contrasena):
        login_payload = {"usuario": nombre_usuario, "contrasena": contrasena}
        login_request = self.client.post("/login",
                                         data=json.dumps(login_payload),
                                         headers={'Content-Type': 'application/json'})
        login_response = json.loads(login_request.get_data())
        return login_response["token"], login_response["id"]

    def create_restaurante(self, admin_usuario_id=None):
        restaurante = Restaurante(administrador = admin_usuario_id)
        db.session.add(restaurante)
        db.session.commit()
        return restaurante.id

    def create_receta(self, admin_usuario_id, nombre=None, duracion=None,         porcion=None, preparacion=None):
        receta = Receta(usuario = admin_usuario_id, administrador = admin_usuario_id, nombre=nombre, duracion=duracion, porcion=porcion, preparacion=preparacion)
        db.session.add(receta)
        db.session.commit()
        return receta

    def tearDown(self):
        try:
            for menu in self.menus_creados:
                self.delete_resources(Menu, menu.id)
            for receta in self.recetas_creadas:
                self.delete_resources(Receta, receta.id)
            for chef in self.chef_creados:
                self.delete_resources(Chef, chef.id)
            for admin in self.admin_creados:
                self.delete_resources(Administrador, admin.id)
            for restaurante in self.restaurante_creados:
                self.delete_resources(Restaurante, restaurante.id)
        except Exception as e:
            print("Exception during tearDown:", str(e))
            db.session.rollback()
        else:
            db.session.commit()

    def delete_resources(self, resource_class, resource_id):
        resource = resource_class.query.get(resource_id)
        if resource:
            db.session.delete(resource)
    
    def test_Admin_ve_2_Menus(self):
        # Creamos un Admin
        admin_token, admin_usuario_id = self.create_and_login_user(Administrador)
        admin = Administrador.query.get(admin_usuario_id)
        self.admin_creados.append(admin)
        # Creamos un Restaurante
        restaurante_id = self.create_restaurante()
        restaurante = Restaurante.query.get(restaurante_id)
        restaurante.administrador = admin_usuario_id
        self.restaurante_creados.append(restaurante)
        # Creamos dos Receta
        receta1 = self.create_receta(nombre='Bandeja Paisa', 
                                     duracion=3, 
                                     porcion=4, 
                                     preparacion='Preparar la bandeja paisa', admin_usuario_id=admin_usuario_id)
        
        receta2 = self.create_receta(nombre = 'Sancocho',
                                     duracion = 2, 
                                     porcion = 5, 
                                     preparacion = 'Preparar el sancocho', admin_usuario_id=admin_usuario_id) 
        
        receta3 = self.create_receta(nombre = 'Ajiaco', 
                                     duracion=2, 
                                     porcion=3, 
                                     preparacion='Preparar el ajiaco',
                                     admin_usuario_id=admin_usuario_id)
        
        self.recetas_creadas.append(receta1)
        self.recetas_creadas.append(receta2)
        self.recetas_creadas.append(receta3)

        # Creamos dos Menus
        menu1 = self.create_menu('Menu1', 'Menu1', date.today(), date.today(), 'Menu1', admin_usuario_id, restaurante_id, [receta1, receta2])

        menu2 = self.create_menu('Menu2', 'Menu2', date.today(), date.today(), 'Menu2', admin_usuario_id, restaurante_id, [receta2, receta3])

        self.menus_creados.append(menu1)
        self.menus_creados.append(menu2)

        # Hacemos un request al endpoint
        endpoint = f"/usuarios/{admin_usuario_id}/restaurantes/{restaurante_id}/menus"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {admin_token}"}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())

        # Verificamos que el request fue exitoso
        self.assertEqual(resultado.status_code, 200)
        # Verificamos que el request devolvio 2 menus
        self.assertEqual(len(datos), 2)
        # Verificamos que los menus devueltos son los correctos
        self.assertEqual(datos[0]['nombre'], 'Menu1')
        self.assertEqual(datos[1]['nombre'], 'Menu2')
        # Verificamos que los menus devueltos tienen las recetas correctas
        self.assertEqual(len(datos[0]['recetas']), 2)
        self.assertEqual(len(datos[1]['recetas']), 2)

        # Verificamos que las recetas devueltas son las correctas
        bandeja_paisa = Receta.query.get(datos[0]['recetas'][0]['receta']).nombre
        sanchoco = Receta.query.get(datos[0]['recetas'][1]['receta']).nombre
        sanchoco_2 = Receta.query.get(datos[1]['recetas'][0]['receta']).nombre
        ajiaco = Receta.query.get(datos[1]['recetas'][1]['receta']).nombre
        
        self.assertEqual(bandeja_paisa, 'Bandeja Paisa')
        self.assertEqual(sanchoco, 'Sancocho')
        self.assertEqual(sanchoco_2, 'Sancocho')
        self.assertEqual(ajiaco, 'Ajiaco')

        # Verificamos que usuario retornado corresponde con Admin Creado
        endpoint = f"/usuarios/{admin_usuario_id}"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {admin_token}"}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())
        self.assertEqual(datos['usuario'], admin.usuario)
        self.assertEqual(datos['nombre'], admin.nombre)
        self.assertEqual(datos['tipo'], admin.tipo)
        
    
    # Test para verificar que un Admin no puede ver los menus de un restaurante que no slecciona

    def test_admin_ve_menu_restaurante_seleccionado(self):
        # Creamos un Admin
        admin_token, admin_usuario_id = self.create_and_login_user(Administrador)
        admin = Administrador.query.get(admin_usuario_id)
        self.admin_creados.append(admin)

        # Creamos 2 Restaurantes asocuados al Admin
        restaurante1_id = self.create_restaurante(admin_usuario_id)
        restaurante2_id = self.create_restaurante(admin_usuario_id)
        restaurante1 = Restaurante.query.get(restaurante1_id)
        restaurante2 = Restaurante.query.get(restaurante2_id)
        self.restaurante_creados.append(restaurante1)
        self.restaurante_creados.append(restaurante2)

        # Creamos dos Receta
        receta1 = self.create_receta(nombre='Bandeja Paisa', 
                                     duracion=3, 
                                     porcion=4, 
                                     preparacion='Preparar la bandeja paisa', admin_usuario_id=admin_usuario_id)
        
        receta2 = self.create_receta(nombre = 'Sancocho',
                                     duracion = 2, 
                                     porcion = 5, 
                                     preparacion = 'Preparar el sancocho', admin_usuario_id=admin_usuario_id) 
        
        receta3 = self.create_receta(nombre = 'Ajiaco', 
                                     duracion=2, 
                                     porcion=3, 
                                     preparacion='Preparar el ajiaco',
                                     admin_usuario_id=admin_usuario_id)
        
        self.recetas_creadas.append(receta1)
        self.recetas_creadas.append(receta2)
        self.recetas_creadas.append(receta3)

        # Creamos dos Menus, cada uno asociado a cada uno de los restaurantes

        menu1 = self.create_menu('Menu1', 'Menu1', date.today(), date.today(), 'Menu1', admin_usuario_id, restaurante1_id, [receta1, receta2])
        menu2 = self.create_menu('Menu2', 'Menu2', date.today(), date.today(), 'Menu2', admin_usuario_id, restaurante2_id, [receta2, receta3])
        self.menus_creados.append(menu1)
        self.menus_creados.append(menu2)

        # Hacemos un request al endpoint

        endpoint = f"/usuarios/{admin_usuario_id}/restaurantes/{restaurante1_id}/menus"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {admin_token}"}
        resultado1 = self.client.get(endpoint, headers=headers)
        datos1 = json.loads(resultado1.get_data())

        endpoint = f"/usuarios/{admin_usuario_id}/restaurantes/{restaurante2_id}/menus"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {admin_token}"} 
        resultado2 = self.client.get(endpoint, headers=headers)
        datos2 = json.loads(resultado2.get_data())

        # Verificamos que el request fue exitoso
        self.assertEqual(resultado1.status_code, 200)
        self.assertEqual(resultado2.status_code, 200)

        # Verificamos que el request devolvio 1 menu
        self.assertEqual(len(datos1), 1)
        self.assertEqual(len(datos2), 1)

        # Verificamos que los menus devueltos son los correctos

        self.assertEqual(datos1[0]['nombre'], 'Menu1')
        self.assertEqual(datos2[0]['nombre'], 'Menu2')
        self.assertNotEqual(datos1[0]['nombre'], datos2[0]['nombre'])
        self.assertNotEqual(datos2[0]['nombre'], 'Menu1')
        self.assertNotEqual(datos1[0]['nombre'], 'Menu2')

        # Verificamos que los menus devueltos tienen las recetas correctas

        self.assertEqual(len(datos1[0]['recetas']), 2)
        self.assertEqual(len(datos2[0]['recetas']), 2)

        # Verificamos que las recetas devueltas son las correctas


        bandeja_paisa = Receta.query.get(datos1[0]['recetas'][0]['receta']).nombre
        sanchoco = Receta.query.get(datos1[0]['recetas'][1]['receta']).nombre
        sanchoco_2 = Receta.query.get(datos2[0]['recetas'][0]['receta']).nombre
        ajiaco = Receta.query.get(datos2[0]['recetas'][1]['receta']).nombre
        
        self.assertEqual(bandeja_paisa, 'Bandeja Paisa')
        self.assertEqual(sanchoco, 'Sancocho')
        self.assertEqual(sanchoco_2, 'Sancocho')
        self.assertEqual(ajiaco, 'Ajiaco')

        # Verificamos que usuario retornado corresponde con Admin Creado
        endpoint = f"/usuarios/{admin_usuario_id}"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {admin_token}"}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())
        self.assertEqual(datos['usuario'], admin.usuario)
        self.assertEqual(datos['nombre'], admin.nombre)
        self.assertEqual(datos['tipo'], admin.tipo)

        



        

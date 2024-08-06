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
        self.recetas_creadas = []
        
        self.admin_token, self.admin_usuario_id = self.create_and_login_user(Administrador)
        self.chef_token, self.chef_usuario_id = self.create_and_login_user(Chef)
        self.restaurante_id = self.create_restaurante()
        self.receta_id = self.create_receta()

        # Add chef to restaurant
        chef = Chef.query.get(self.chef_usuario_id)
        chef.restaurante = self.restaurante_id
        db.session.commit()

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

        # Adicionamos instancias MenuReceta para asociar associate recetas con menu
        if recetas:
            for receta in recetas:
                menu_receta = MenuReceta(
                    personas=4, # Seteamos un valor por defecto
                    menu=menu.id,  
                    receta=receta.id
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

    def create_restaurante(self):
        restaurante = Restaurante(administrador=self.admin_usuario_id)
        db.session.add(restaurante)
        db.session.commit()
        return restaurante.id

    def create_receta(self, 
                      nombre=None, 
                      duracion=None,         
                      porcion=None,       
                      preparacion=None):
        receta = Receta(usuario=self.admin_usuario_id, administrador=self.admin_usuario_id, nombre=nombre, duracion=duracion, porcion=porcion, preparacion=preparacion)
        db.session.add(receta)
        db.session.commit()
        return receta

    def tearDown(self):
        try:
            for menu in self.menus_creados:
                self.delete_resources(Menu, menu.id)
            for receta in self.recetas_creadas:
                self.delete_resources(Receta, receta.id)
            self.delete_resources(Restaurante, self.restaurante_id)
            self.delete_resources(Administrador, self.admin_usuario_id)
        except Exception as e:
            print("Exception during tearDown:", str(e))
            db.session.rollback()
        else:
            db.session.commit()

    def delete_resources(self, resource_class, resource_id):
        resource = resource_class.query.get(resource_id)
        if resource:
            db.session.delete(resource)
    
    def test_menu_existence(self):
        # Llamamos al Chef y a su restaurante
        chef = Chef.query.get(self.chef_usuario_id)
        restaurante = Restaurante.query.get(self.restaurante_id)

        # creamos recetas
        receta1 = self.create_receta(nombre="Receta1")
        receta2 = self.create_receta(nombre="Receta2")
        receta3 = self.create_receta(nombre="Receta3")

        self.recetas_creadas.append(receta1)
        self.recetas_creadas.append(receta2)
        self.recetas_creadas.append(receta3)


        # Creamos un menu con recetas
        menu = self.create_menu('Menu1', 'Menu1 Description',
                                date(2020, 1, 1), date(2020, 1, 2),
                                'Menu1 Photo', chef.id, restaurante.id,
                                self.recetas_creadas)
        self.menus_creados.append(menu)


        # Hacemos un GET request al endpoint del API
        endpoint = "/usuarios/{}/menus".format(str(self.chef_usuario_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.chef_token)}
        resultado = self.client.get(endpoint, headers=headers)
        
        # Parse the JSON data and perform assertions
        datos = json.loads(resultado.get_data())
        self.assertEqual(resultado.status_code, 200)

        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["nombre"], menu.nombre)
        self.assertEqual(datos[0]["descripcion"], menu.descripcion)
        self.assertEqual(datos[0]["fechaInicio"], str(menu.fechaInicio))
        self.assertEqual(datos[0]["fechaFin"], str(menu.fechaFin))
        self.assertEqual(datos[0]["foto"], menu.foto)
        self.assertEqual(int(datos[0]["autor"]), menu.autor)
        self.assertEqual(datos[0]["restaurante"], menu.restaurante)

        # Adicionamos aserciones para recetas

        returned_recetas = datos[0].get("recetas", [])
        self.assertEqual(len(returned_recetas), len(self.recetas_creadas))
        self.assertCountEqual([r["receta"] for r in returned_recetas], [r.id for r in self.recetas_creadas])

        # Verificamos que usuario retornado corresponde con Chef Creado
        endpoint = f"/usuarios/{chef.id}"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {self.chef_token}"}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())
        self.assertEqual(datos['usuario'], chef.usuario)
        self.assertEqual(datos['nombre'], chef.nombre)
        self.assertEqual(datos['tipo'], chef.tipo)

    def test_cero_Menus(self):

        # Hacemos un GET request al endpoint del API
        endpoint = "/usuarios/{}/menus".format(str(self.chef_usuario_id))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.chef_token)}
        resultado = self.client.get(endpoint, headers=headers)
        
        # Parse the JSON data and perform assertions
        datos = json.loads(resultado.get_data())
        self.assertEqual(resultado.status_code, 200)
        if datos is not None:
            self.assertEqual(len(datos), 0)  # Verificamos que no hayan menus
        else:
            self.assertIsNone(datos, "The API returned None.")
    
    def test_chefs_ven_menus_de_propio_restaurante(self):
        # Creamos 2 chefs y dos restaurantes bajo el mismo Administrador
        chef1_token, chef1_usuario_id = self.create_and_login_user(Chef)
        chef2_token, chef2_usuario_id = self.create_and_login_user(Chef)

        restaurante1_id = self.create_restaurante()
        restaurante2_id = self.create_restaurante()

        # Asociamos chef con su respectivo restaurante
        chef1 = Chef.query.get(chef1_usuario_id)
        chef1.restaurante = restaurante1_id
        chef2 = Chef.query.get(chef2_usuario_id)
        chef2.restaurante = restaurante2_id
        db.session.commit()

        # Creamos un menu para cada chef
        receta1 = self.create_receta(nombre="Receta1")
        receta2 = self.create_receta(nombre="Receta2")
        self.recetas_creadas.extend([receta1, receta2])

        menu1 = self.create_menu(nombre="Menu1", autor=chef1_usuario_id, restaurante=restaurante1_id, recetas=[receta1])
        menu2 = self.create_menu(nombre="Menu2", autor=chef2_usuario_id, restaurante=restaurante2_id, recetas=[receta2])
        self.menus_creados.extend([menu1, menu2])

        # Hacemos request para traer menus de cada chef
        def check_chef_menus(chef_token, chef_id, expected_menu_id, bad_menu_id=None):
            endpoint = f"/usuarios/{chef_id}/menus"
            headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {chef_token}"}
            resultado = self.client.get(endpoint, headers=headers)
            datos = json.loads(resultado.get_data())
            self.assertEqual(resultado.status_code, 200)
            self.assertEqual(len(datos), 1)
            self.assertEqual(int(datos[0]["id"]), expected_menu_id)
            # Verificamos que no se retorne el menu que no pertenece al chef
            if bad_menu_id:
                self.assertNotEqual(int(datos[0]["id"]), bad_menu_id)


        check_chef_menus(chef1_token, chef1_usuario_id, menu1.id, menu2.id)
        check_chef_menus(chef2_token, chef2_usuario_id, menu2.id, menu1.id)

        # Verificamos que usuario retornado corresponde con Chef1 Creado
        endpoint = f"/usuarios/{chef1_usuario_id}"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {chef1_token}"}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())
        chef1 = Chef.query.get(chef1_usuario_id)
        self.assertEqual(datos['usuario'], chef1.usuario)
        self.assertEqual(datos['nombre'], chef1.nombre)
        self.assertEqual(datos['tipo'], chef1.tipo)

        # Verificamos que usuario retornado corresponde con Chef2 Creado
        endpoint = f"/usuarios/{chef2_usuario_id}"
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {chef1_token}"}
        resultado = self.client.get(endpoint, headers=headers)
        datos = json.loads(resultado.get_data())
        chef2 = Chef.query.get(chef2_usuario_id)
        self.assertEqual(datos['usuario'], chef2.usuario)
        self.assertEqual(datos['nombre'], chef2.nombre)
        self.assertEqual(datos['tipo'], chef2.tipo)
        
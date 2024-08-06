from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from datetime import datetime
import hashlib
from marshmallow import Schema, fields


from modelos import \
    db, \
    Ingrediente, IngredienteSchema, \
    RecetaIngrediente, RecetaIngredienteSchema, \
    Receta, RecetaSchema, \
    Administrador, AdministradorSchema, \
    Restaurante, RestauranteSchema, \
    Chef, ChefSchema, Menu, MenuSchema, MenuReceta, MenuRecetaSchema, Usuario, UsuarioSchema


ingrediente_schema = IngredienteSchema()
receta_ingrediente_schema = RecetaIngredienteSchema()
receta_schema = RecetaSchema()
administrador_schema = AdministradorSchema()
restaurante_schema = RestauranteSchema()
chef_schema = ChefSchema()
menu_schema = MenuSchema()
usuario_schema = UsuarioSchema()

class UsuarioUtil():

    @staticmethod
    def obtenerIdAdministrador(id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if (usuario.tipo == 'Chef'):
            chef = Chef.query.filter(Chef.id == id_usuario).first()
            restaurante = Restaurante.query.filter(Restaurante.id == chef.restaurante).first()
            return restaurante.administrador
        return id_usuario

class ErrorSchema(Schema):
    message = fields.Str(required=True)
    
class VistaSignIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
            nuevo_usuario = Administrador(nombre="Administrador", usuario=request.json["usuario"], contrasena=contrasena_encriptada)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
        else:
            return {"mensaje": "El usuario ya existe"}, 422
        
    def put(self, id_usuario):
        usuario = Administrador.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return administrador_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Administrador.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204

class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"], Usuario.contrasena == contrasena_encriptada).first()
        db.session.commit()
        if usuario is None:
            return { "mensaje": "Usuario o contraseña incorrectos"} , 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id, "tipo": usuario.tipo, "nombre": usuario.nombre}


class VistaRestaurantes(Resource):

    @jwt_required()
    def get(self, id_usuario):
        id_administrador = UsuarioUtil.obtenerIdAdministrador(id_usuario)
        restaurantes = Restaurante.query.filter(Restaurante.administrador == id_administrador).all()
        return [restaurante_schema.dump(restaurante) for restaurante in restaurantes]
    
    @jwt_required()
    def post(self, id_usuario):
        error_schema = ErrorSchema()
        nombre = request.json.get("nombre")
        
        # Check if a restaurant with the same name already exists
        existing_restaurant = Restaurante.query.filter_by(nombre=nombre).first()

        if existing_restaurant:
            return {'mensaje': 'El Restaurante con nombre {} ya existe dentro de la cadena'.format(nombre)}, 422
        
        required_fields = ["nombre", "direccion", "telefono", "redes_sociales", "hora_apertura", "servicio_sitio", "servicio_domicilio", "tipo_comida", "plataformas"]
        
        missing_fields = []
        for field in required_fields:
            value = request.json.get(field)
            if field == "servicio_sitio" or field == "servicio_domicilio":
                if value is not None and isinstance(value, bool):
                    continue
                elif value is None or value == "":
                    missing_fields.append(field)
            elif value is None or value == "":
                missing_fields.append(field)

        if missing_fields:
            error_obj = { "mensaje": "Campos faltantes", "campos_faltantes": missing_fields}
            error_json = error_schema.dump(error_obj)
            return error_json, 400

        nuevo_restaurante = Restaurante( \
            nombre = request.json["nombre"], \
            direccion = request.json["direccion"], \
            telefono = request.json["telefono"], \
            redes_sociales = request.json["redes_sociales"], \
            hora_apertura = request.json["hora_apertura"], \
            servicio_sitio = bool(request.json["servicio_sitio"]), \
            servicio_domicilio = bool(request.json["servicio_domicilio"]), \
            tipo_comida = request.json["tipo_comida"], \
            plataformas = request.json["plataformas"], \
            administrador = id_usuario)
        db.session.add(nuevo_restaurante)
        db.session.commit()
        return restaurante_schema.dump(nuevo_restaurante)
    
class VistaRestaurante(Resource):    
    @jwt_required()
    def get(self, id_usuario, id_restaurante):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        buscado_restaurante = Restaurante.query.filter(Restaurante.id == id_restaurante).first()
        if(usuario == None):
            return {'mensaje': "No existe un usuario con ese id"}, 422
        if(buscado_restaurante == None):
            return {'mensaje': "No existe un restaurante con ese id"}, 422
        else:
            return restaurante_schema.dump(buscado_restaurante)
        

class VistaIngredientes(Resource):

    @jwt_required()
    def get(self, id_usuario):
        id_administrador = UsuarioUtil.obtenerIdAdministrador(id_usuario)
        ingredientes = Ingrediente.query.filter(Ingrediente.administrador == id_administrador).all()
        return [ingrediente_schema.dump(ingrediente) for ingrediente in ingredientes]

    @jwt_required()
    def post(self, id_usuario):
        id_administrador = UsuarioUtil.obtenerIdAdministrador(id_usuario)
        nuevo_ingrediente = Ingrediente( \
            nombre = request.json["nombre"], \
            unidad = request.json["unidad"], \
            costo = float(request.json["costo"]), \
            calorias = float(request.json["calorias"]), \
            sitio = request.json["sitio"], \
            administrador = id_administrador)
        db.session.add(nuevo_ingrediente)
        db.session.commit()
        return ingrediente_schema.dump(nuevo_ingrediente)
    
class VistaIngrediente(Resource):

    @jwt_required()
    def get(self, id_ingrediente):
        return ingrediente_schema.dump(Ingrediente.query.get_or_404(id_ingrediente))
        
    @jwt_required()
    def put(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        ingrediente.nombre = request.json["nombre"]
        ingrediente.unidad = request.json["unidad"]
        ingrediente.costo = float(request.json["costo"])
        ingrediente.calorias = float(request.json["calorias"])
        ingrediente.sitio = request.json["sitio"]
        db.session.commit()
        return ingrediente_schema.dump(ingrediente)

    @jwt_required()
    def delete(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        recetasIngrediente = RecetaIngrediente.query.filter_by(ingrediente=id_ingrediente).all()
        if not recetasIngrediente:
            db.session.delete(ingrediente)
            db.session.commit()
            return '', 204
        else:
            return {'mensaje': 'El ingrediente se está usando en diferentes recetas'}, 409

class VistaRecetas(Resource):

    @jwt_required()
    def get(self, id_usuario):
        id_administrador = UsuarioUtil.obtenerIdAdministrador(id_usuario)
        recetas = self.obtenerRecetas(id_administrador, id_usuario, request.args.get('todos'))
        resultados = [receta_schema.dump(receta) for receta in recetas]
        ingredientes = Ingrediente.query.all()
        for receta in resultados:
            for receta_ingrediente in receta['ingredientes']:
                self.actualizar_ingredientes_util(receta_ingrediente, ingredientes)
        return resultados

    @jwt_required()
    def post(self, id_usuario):
        id_administrador = UsuarioUtil.obtenerIdAdministrador(id_usuario)
        nueva_receta = Receta( \
            nombre = request.json["nombre"], \
            preparacion = request.json["preparacion"], \
            ingredientes = [], \
            administrador = id_administrador, \
            duracion = float(request.json["duracion"]), \
            porcion = float(request.json["porcion"]), \
            usuario = id_usuario)
        for receta_ingrediente in request.json["ingredientes"]:
            nueva_receta_ingrediente = RecetaIngrediente( \
                cantidad = receta_ingrediente["cantidad"], \
                ingrediente = int(receta_ingrediente["idIngrediente"])
            )
            nueva_receta.ingredientes.append(nueva_receta_ingrediente)
            
        db.session.add(nueva_receta)
        db.session.commit()
        return ingrediente_schema.dump(nueva_receta)
        
    def actualizar_ingredientes_util(self, receta_ingrediente, ingredientes):
        for ingrediente in ingredientes: 
            if str(ingrediente.id)==receta_ingrediente['ingrediente']:
                receta_ingrediente['ingrediente'] = ingrediente_schema.dump(ingrediente)
                receta_ingrediente['ingrediente']['costo'] = float(receta_ingrediente['ingrediente']['costo'])

    def obtenerRecetas(self, id_administrador, id_usuario, todos):
        if (id_administrador == id_usuario or todos == 'true'):
            return Receta.query.filter(Receta.administrador == id_administrador).all()
        else:
            return Receta.query.filter(Receta.usuario == id_usuario).all()

class VistaReceta(Resource):

    @jwt_required()
    def get(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        ingredientes = Ingrediente.query.all()
        resultados = receta_schema.dump(receta)
        recetaIngredientes = resultados['ingredientes']
        for recetaIngrediente in recetaIngredientes:
            for ingrediente in ingredientes: 
                if str(ingrediente.id)==recetaIngrediente['ingrediente']:
                    recetaIngrediente['ingrediente'] = ingrediente_schema.dump(ingrediente)
                    recetaIngrediente['ingrediente']['costo'] = float(recetaIngrediente['ingrediente']['costo'])
        return resultados

    @jwt_required()
    def put(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        receta.nombre = request.json["nombre"]
        receta.preparacion = request.json["preparacion"]
        receta.duracion = float(request.json["duracion"])
        receta.porcion = float(request.json["porcion"])
        #Verificar los ingredientes que se borraron
        for receta_ingrediente in receta.ingredientes:
            borrar = self.borrar_ingrediente_util(request.json["ingredientes"], receta_ingrediente)
            if borrar==True:
                db.session.delete(receta_ingrediente)
        db.session.commit()
        for receta_ingrediente_editar in request.json["ingredientes"]:
            if receta_ingrediente_editar['id']=='':
                #Es un nuevo ingrediente de la receta porque no tiene código
                nueva_receta_ingrediente = RecetaIngrediente( \
                    cantidad = receta_ingrediente_editar["cantidad"], \
                    ingrediente = int(receta_ingrediente_editar["idIngrediente"])
                )
                receta.ingredientes.append(nueva_receta_ingrediente)
            else:
                #Se actualiza el ingrediente de la receta
                receta_ingrediente = self.actualizar_ingrediente_util(receta.ingredientes, receta_ingrediente_editar)
                db.session.add(receta_ingrediente)
        db.session.add(receta)
        db.session.commit()
        return ingrediente_schema.dump(receta)

    @jwt_required()
    def delete(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        db.session.delete(receta)
        db.session.commit()
        return '', 204
        
    def borrar_ingrediente_util(self, receta_ingredientes, receta_ingrediente):
        borrar = True
        for receta_ingrediente_editar in receta_ingredientes:
            if receta_ingrediente_editar['id']!='':
                if int(receta_ingrediente_editar['id']) == receta_ingrediente.id:
                    borrar = False
        return(borrar)

    def actualizar_ingrediente_util(self, receta_ingredientes, receta_ingrediente_editar):
        receta_ingrediente_retornar = None
        for receta_ingrediente in receta_ingredientes:
            if int(receta_ingrediente_editar['id']) == receta_ingrediente.id:
                receta_ingrediente.cantidad = receta_ingrediente_editar['cantidad']
                receta_ingrediente.ingrediente = receta_ingrediente_editar['idIngrediente']
                receta_ingrediente_retornar = receta_ingrediente
        return receta_ingrediente_retornar

class VistaChefs(Resource):

    @jwt_required()
    def get(self, id_restaurante):
        chefs = Chef.query.filter(Chef.restaurante == id_restaurante).all()
        resultado = []
        for chef in chefs:        
            resultado.append(chef_schema.dump(chef))
        return resultado
    
    @jwt_required()
    def post(self, id_restaurante):
        nuevo_chef = Chef( \
            nombre = request.json["nombre"], \
            usuario = request.json["usuario"], \
            contrasena = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest(), \
            restaurante = id_restaurante \
        )
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()
        if usuario is None:
            db.session.add(nuevo_chef)
            db.session.commit()
            return chef_schema.dump(nuevo_chef)
        else:
            return {'mensaje': "Ya existe un chef con el mismo usuario"}, 422 

class VistaMenus(Resource):

    @jwt_required()
    def post(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        id_restaurante = request.json["restaurante"]
        if (usuario.tipo == 'Chef'):
            chef = Chef.query.filter(Chef.id == id_usuario).first()
            id_restaurante = chef.restaurante
        nuevo_menu = Menu(nombre=request.json["nombre"],
                          descripcion=request.json["descripcion"],
                          fechaInicio=datetime.strptime(request.json["fechaInicio"], '%Y-%m-%d').date(),
                          fechaFin=datetime.strptime(request.json["fechaFin"], '%Y-%m-%d').date(),
                          foto=request.json["foto"],
                          autor=id_usuario,
                          autor_name=usuario.usuario,
                          restaurante=id_restaurante)
        for receta in request.json["recetas"]:
            nuevo_menu_receta = MenuReceta(
                personas = receta["personas"], 
                receta = int(receta["receta"])
            )
            nuevo_menu.recetas.append(nuevo_menu_receta)
        db.session.add(nuevo_menu)
        db.session.commit()
        return menu_schema.dump(nuevo_menu) 
    
class VistaMenu(Resource):
    @jwt_required()
    def get(self, id_usuario, id_menu):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        buscado_menu = Menu.query.filter(Menu.id == id_menu).first()
        if(usuario == None):
            return {'mensaje': "No existe un usuario con ese id"}, 422
        elif(buscado_menu == None):
            return {'mensaje': "No existe un menú con ese id"}, 422 
        else:
            return menu_schema.dump(buscado_menu)


    @jwt_required()
    def put(self, id_usuario, id_menu):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        editar_menu = Menu.query.filter(Menu.id == id_menu).first()
        id_restaurante = request.json["restaurante"]['id']
        if(usuario == None):
            return {'mensaje': "No existe un usuario con ese id"}, 422
        elif(editar_menu == None):
            return {'mensaje': "No existe un menú con ese id"}, 422 
        else:
            if(editar_menu.autor != usuario.id):
               if(usuario.tipo == 'Chef'):
                chef = Chef.query.filter(Chef.id == id_usuario).first()
                id_restaurante = chef.restaurante
                if(chef.restaurante != editar_menu.restaurante):
                    return {'mensaje': "El usuario no tiene permisos para editar el menú"}, 422
       
            editar_menu.nombre = request.json["nombre"]
            editar_menu.descripcion = request.json["descripcion"]
            editar_menu.fechaInicio = datetime.strptime(request.json["fechaInicio"], '%Y-%m-%d').date()
            editar_menu.fechaFin = datetime.strptime(request.json["fechaFin"], '%Y-%m-%d').date()
            editar_menu.foto = request.json["foto"]
            editar_menu.autor = id_usuario
            editar_menu.restaurante = id_restaurante
            editar_menu.recetas = []

            for receta in request.json["recetas"]:
                nuevo_menu_receta = MenuReceta(
                    personas = receta["personas"], 
                    receta = int(receta["receta"])
                )
                editar_menu.recetas.append(nuevo_menu_receta)
            db.session.commit()
            return menu_schema.dump(editar_menu)     
            

class VistaMenusChef(Resource):
    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if (usuario.tipo == 'Chef'):
            chef = Chef.query.filter(Chef.id == id_usuario).first()
            id_restaurante = chef.restaurante
        # Obetener la lista de menus por restaurante
        menus = Menu.query.filter(Menu.restaurante == id_restaurante).all()
        resultado = []
        for menu in menus:
            resultado.append(menu_schema.dump(menu))        
        return resultado

class VistaMenusAdmin(Resource):
    @jwt_required()
    def get(self, id_usuario, id_restaurante):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if (usuario.tipo == 'Administrador'):
            admin = Administrador.query.filter(Administrador.id == id_usuario).first()
        # Obetener la lista de menus por restaurante
        restaurante = Restaurante.query.filter(Restaurante.administrador == admin.id).filter(Restaurante.id == id_restaurante).first()
        menus = Menu.query.filter(Menu.restaurante == restaurante.id).all()

        resultado = []
        for menu in menus:
            resultado.append(menu_schema.dump(menu))        
        return resultado
    
class VistaUsuarios(Resource):
    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        return usuario_schema.dump(usuario)



class VistaReporteMenus(Resource):
    
    @jwt_required()
    def post(self):  
        reporte = {}
        for receta in request.json['recetas']:
            rec = Receta.query.filter(Receta.id == receta['receta']).first()
            recetasIngredientes = RecetaIngrediente.query.filter(RecetaIngrediente.receta == rec.id).all()
            for recetaIngrediente in recetasIngredientes:
                ingrediente = Ingrediente.query.filter(Ingrediente.id == recetaIngrediente.ingrediente).first()
                if ingrediente.id in reporte:
                    reporte[ingrediente.id]['cantidad'] = str(round(float(reporte[ingrediente.id]['cantidad']) + float(((receta['personas'] * recetaIngrediente.cantidad)/rec.porcion))))
                else:
                    reporte[ingrediente.id] = {'nombre': ingrediente.nombre, 'cantidad': str(round((receta['personas'] * recetaIngrediente.cantidad)/rec.porcion)), 'unidad': ingrediente.unidad, 'sitio': ingrediente.sitio} 
        
        arrayReporte = []
        for elemento in reporte:
            arrayReporte.append(reporte[elemento])

        return arrayReporte
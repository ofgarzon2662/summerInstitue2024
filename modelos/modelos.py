from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Date

db = SQLAlchemy()

class Restaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    direccion = db.Column(db.String(128))
    telefono = db.Column(db.String(128))
    redes_sociales = db.Column(db.String(128))
    hora_apertura = db.Column(db.String(128))
    servicio_sitio = db.Column(db.Boolean)
    servicio_domicilio = db.Column(db.Boolean)
    tipo_comida = db.Column(db.String(128))
    plataformas = db.Column(db.String(128))
    administrador = db.Column(db.Integer, db.ForeignKey('administrador.id'))
    chefs = db.relationship('Chef', cascade='all, delete, delete-orphan')

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    unidad = db.Column(db.String(128))
    costo = db.Column(db.Numeric)
    calorias = db.Column(db.Numeric)
    sitio = db.Column(db.String(128))
    administrador = db.Column(db.Integer, db.ForeignKey('administrador.id'))

class RecetaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Numeric)
    ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'))
    receta = db.Column(db.Integer, db.ForeignKey('receta.id'))

class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    duracion = db.Column(db.Numeric)
    porcion = db.Column(db.Numeric)
    preparacion = db.Column(db.String)
    ingredientes = db.relationship('RecetaIngrediente', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    administrador = db.Column(db.Integer, db.ForeignKey('administrador.id'))

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(1000))
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String)
    __mapper_args__ = {
        'polymorphic_identity': 'Usuario',
        'polymorphic_on': tipo
    }

class Administrador(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    recetas = db.relationship('Receta', cascade='all, delete, delete-orphan')
    restaurantes = db.relationship('Restaurante', cascade='all, delete, delete-orphan')
    __mapper_args__ = {
        'polymorphic_identity': 'Administrador',
    }

class Chef(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))
    __mapper_args__ = {
        'polymorphic_identity': 'Chef',
    }

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(200))
    fechaInicio = db.Column(db.Date)
    fechaFin = db.Column(db.Date)
    foto = db.Column(db.String(1000))
    autor = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    autor_name = db.Column(db.String, db.ForeignKey('usuario.usuario'))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))
    recetas = db.relationship('MenuReceta', cascade='all, delete, delete-orphan')

class MenuReceta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personas = db.Column(db.Integer)
    menu = db.Column(db.Integer, db.ForeignKey('menu.id'))
    receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    
class MenuRecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MenuReceta
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()   
    personas = fields.String()

class MenuSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Menu
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()   
    autor = fields.String()
    recetas = fields.List(fields.Nested(MenuRecetaSchema()))

class RestauranteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurante
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()          

class IngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ingrediente
        load_instance = True
        
    id = fields.String()
    costo = fields.String()
    calorias = fields.String()
    administrador = fields.String()

class RecetaIngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RecetaIngrediente
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    cantidad = fields.String()
    ingrediente = fields.String()

class RecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Receta
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    duracion = fields.String()
    porcion = fields.String()
    ingredientes = fields.List(fields.Nested(RecetaIngredienteSchema()))

class AdministradorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Administrador
        include_relationships = True
        load_instance = True

    id = fields.String()

class ChefSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Chef
        include_relationships = True
        load_instance = True
        
    id = fields.String()

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    recetas = fields.List(fields.Nested(RecetaSchema()))
    restaurantes = fields.List(fields.Nested(RestauranteSchema()))
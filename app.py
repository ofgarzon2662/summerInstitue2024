from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from modelos import db
from vistas import \
    VistaIngrediente, VistaIngredientes, \
    VistaReceta, VistaRecetas, \
    VistaSignIn, VistaLogIn, \
    VistaRestaurantes, \
    VistaRestaurante, \
    VistaChefs, \
    VistaMenus, \
    VistaMenusChef, \
    VistaMenusAdmin, \
    VistaMenu, \
    VistaReporteMenus

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbapp.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaRestaurantes, '/usuarios/<int:id_usuario>/restaurantes')
api.add_resource(VistaRestaurante, '/usuarios/<int:id_usuario>/restaurante/<int:id_restaurante>')
api.add_resource(VistaIngredientes, '/usuarios/<int:id_usuario>/ingredientes')
api.add_resource(VistaIngrediente, '/ingredientes/<int:id_ingrediente>')
api.add_resource(VistaRecetas, '/usuarios/<int:id_usuario>/recetas')
api.add_resource(VistaReceta, '/recetas/<int:id_receta>')
api.add_resource(VistaChefs, '/restaurantes/<int:id_restaurante>/chefs')
api.add_resource(VistaMenus, '/usuarios/<int:id_usuario>/menus')
api.add_resource(VistaMenusChef, '/usuarios/<int:id_usuario>/menus')
api.add_resource(VistaMenusAdmin, '/usuarios/<int:id_usuario>/restaurantes/<int:id_restaurante>/menus')
api.add_resource(VistaMenu, '/usuarios/<int:id_usuario>/menu/<int:id_menu>')
api.add_resource(VistaReporteMenus, '/reporteMenu')

jwt = JWTManager(app)

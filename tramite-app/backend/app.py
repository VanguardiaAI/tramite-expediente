from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps
from werkzeug.utils import secure_filename
import uuid
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
# Configurar CORS para permitir peticiones desde el frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tramites.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_segura'

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf'}

db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    solicitudes = db.relationship('Solicitud', backref='user', lazy=True)
    tramites = db.relationship('Tramite', backref='user', lazy=True)

class Solicitud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipoTramite = db.Column(db.String(50), nullable=False)
    documentoAdjunto = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Tramite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # 'Modificación', 'Individual', 'Alta'
    nombreCliente = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefonoMovil = db.Column(db.String(20), nullable=False)
    cups = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    refCatastral = db.Column(db.String(100), nullable=False)
    potenciaNumerica = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    estado = db.Column(db.String(20), default='Pendiente')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Campos específicos para cada tipo de trámite
    aumentoPotencia = db.Column(db.Boolean, default=False)  # Para Modificación
    vivienda = db.Column(db.String(50))  # Para Individual
    variosSuministros = db.Column(db.Boolean, default=False)  # Para Alta
    acometidaCentralizada = db.Column(db.Boolean, default=False)  # Para Alta
    
    # Guarda las rutas a los archivos (en una implementación real se usaría un servicio de almacenamiento)
    dniPdf = db.Column(db.String(200))
    formatoAutorizacion = db.Column(db.String(200))
    plantillaRelacionPuntos = db.Column(db.String(200))

# Función auxiliar para verificar token desde parámetro de consulta o header
def get_token_from_request():
    # Primero intentar desde el header de Authorization
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Si no está en el header, intentar desde parámetros de consulta
    return request.args.get('token')

# Decorador para validar token (modificado para soportar query params)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                raise Exception('Usuario no encontrado')
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# Rutas de autenticación
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json

    # Validar que se proporcionen los datos necesarios
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Faltan datos requeridos'}), 400

    # Verificar si el correo ya está registrado
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Este correo ya está registrado'}), 400

    # Crear nuevo usuario
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Faltan datos requeridos'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Generar token JWT
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token}), 200

@app.route('/api/user', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email
    }), 200

# Rutas para solicitudes
@app.route('/api/solicitudes', methods=['POST'])
@token_required
def create_solicitud(current_user):
    data = request.json

    # Validar que se proporcionen los datos necesarios
    if not data or not data.get('titulo') or not data.get('descripcion') or not data.get('tipoTramite'):
        return jsonify({'message': 'Faltan datos requeridos'}), 400

    # Crear nueva solicitud
    new_solicitud = Solicitud(
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        tipoTramite=data['tipoTramite'],
        documentoAdjunto=data.get('documentoAdjunto', ''),
        user_id=current_user.id
    )
    db.session.add(new_solicitud)
    db.session.commit()

    return jsonify({'message': 'Solicitud creada exitosamente', 'id': new_solicitud.id}), 201

@app.route('/api/solicitudes', methods=['GET'])
@token_required
def get_solicitudes(current_user):
    solicitudes = Solicitud.query.filter_by(user_id=current_user.id).all()
    
    result = []
    for solicitud in solicitudes:
        result.append({
            'id': solicitud.id,
            'titulo': solicitud.titulo,
            'descripcion': solicitud.descripcion,
            'tipoTramite': solicitud.tipoTramite,
            'documentoAdjunto': solicitud.documentoAdjunto,
            'fecha_creacion': solicitud.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return jsonify(result), 200

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para guardar archivo y obtener ruta
def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Generar nombre único para evitar colisiones
        unique_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

# Rutas para tramites (formularios)
@app.route('/api/tramites', methods=['POST'])
@token_required
def create_tramite(current_user):
    try:
        # Comprobar si la solicitud tiene archivos adjuntos
        if request.files:
            print("DEBUG - Request tiene archivos")
            # Obtener datos del formulario
            data = {key: request.form.get(key) for key in request.form.keys()}
            
            # Mostrar los campos del formulario recibido
            print(f"DEBUG - Campos del formulario: {data.keys()}")
            
            # Procesar archivos
            files_data = {}
            
            # Procesar DNI PDF
            if 'dniPdf' in request.files:
                dniPdf = request.files['dniPdf']
                if dniPdf.filename != '':
                    print(f"DEBUG - Procesando DNI PDF: {dniPdf.filename}")
                    dniPdf_filename = save_file(dniPdf)
                    if dniPdf_filename:
                        files_data['dniPdf'] = dniPdf_filename
                        print(f"DEBUG - DNI PDF guardado como: {dniPdf_filename}")
                    else:
                        print("DEBUG - Error al guardar DNI PDF")
            
            # Procesar Formato de Autorización
            if 'formatoAutorizacion' in request.files:
                formatoAuth = request.files['formatoAutorizacion']
                if formatoAuth.filename != '':
                    print(f"DEBUG - Procesando Formato Autorización: {formatoAuth.filename}")
                    formatoAuth_filename = save_file(formatoAuth)
                    if formatoAuth_filename:
                        files_data['formatoAutorizacion'] = formatoAuth_filename
                        print(f"DEBUG - Formato Autorización guardado como: {formatoAuth_filename}")
                    else:
                        print("DEBUG - Error al guardar Formato Autorización")
            
            # Procesar Plantilla Relación Puntos (para Alta)
            if 'plantillaRelacionPuntos' in request.files:
                plantilla = request.files['plantillaRelacionPuntos']
                if plantilla.filename != '':
                    print(f"DEBUG - Procesando Plantilla Relación Puntos: {plantilla.filename}")
                    plantilla_filename = save_file(plantilla)
                    if plantilla_filename:
                        files_data['plantillaRelacionPuntos'] = plantilla_filename
                        print(f"DEBUG - Plantilla Relación Puntos guardada como: {plantilla_filename}")
                    else:
                        print("DEBUG - Error al guardar Plantilla Relación Puntos")
        else:
            # Si no hay archivos, usar el método anterior (solo para compatibilidad)
            print("DEBUG - Request sin archivos")
            data = request.json
            files_data = {}
        
        # Validar datos básicos
        required_fields = ['tipo', 'nombreCliente', 'email', 'telefonoMovil', 
                        'cups', 'direccion', 'refCatastral', 'potenciaNumerica']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Falta el campo requerido: {field}'}), 400
        
        # Crear nuevo trámite con campos comunes
        new_tramite = Tramite(
            tipo=data['tipo'],
            nombreCliente=data['nombreCliente'],
            email=data['email'],
            telefonoMovil=data['telefonoMovil'],
            cups=data['cups'],
            direccion=data['direccion'],
            refCatastral=data['refCatastral'],
            potenciaNumerica=data['potenciaNumerica'],
            user_id=current_user.id
        )
        
        # Añadir campos específicos según el tipo
        if data['tipo'] == 'Modificación':
            new_tramite.aumentoPotencia = data.get('aumentoPotencia') == 'true'
        elif data['tipo'] == 'Individual':
            new_tramite.vivienda = data.get('vivienda', '')
        elif data['tipo'] == 'Alta':
            new_tramite.variosSuministros = data.get('variosSuministros') == 'true'
            new_tramite.acometidaCentralizada = data.get('acometidaCentralizada') == 'true'
        
        # Añadir los archivos
        new_tramite.dniPdf = files_data.get('dniPdf', '')
        new_tramite.formatoAutorizacion = files_data.get('formatoAutorizacion', '')
        new_tramite.plantillaRelacionPuntos = files_data.get('plantillaRelacionPuntos', '')
        
        # Mostrar información de depuración
        print(f"DEBUG - Trámite a guardar: tipo={new_tramite.tipo}, dniPdf={new_tramite.dniPdf}, formatoAuth={new_tramite.formatoAutorizacion}")
        
        db.session.add(new_tramite)
        db.session.commit()
        
        return jsonify({
            'message': 'Trámite creado exitosamente',
            'id': new_tramite.id,
            'documentos': {
                'dniPdf': new_tramite.dniPdf,
                'formatoAutorizacion': new_tramite.formatoAutorizacion,
                'plantillaRelacionPuntos': new_tramite.plantillaRelacionPuntos
            }
        }), 201
    except Exception as e:
        print(f"ERROR - Excepción en create_tramite: {str(e)}")
        return jsonify({'message': f'Error al crear el trámite: {str(e)}'}), 500

@app.route('/api/tramites', methods=['GET'])
@token_required
def get_tramites(current_user):
    tramites = Tramite.query.filter_by(user_id=current_user.id).all()
    
    # Imprimir información de depuración de cada trámite
    for tramite in tramites:
        print(f"DEBUG - Tramite ID: {tramite.id}, DNI PDF: {tramite.dniPdf}, Formato Auth: {tramite.formatoAutorizacion}")
    
    result = []
    for tramite in tramites:
        tramite_data = {
            'id': tramite.id,
            'tipo': tramite.tipo,
            'nombreCliente': tramite.nombreCliente,
            'email': tramite.email,
            'telefonoMovil': tramite.telefonoMovil,
            'cups': tramite.cups,
            'direccion': tramite.direccion,
            'refCatastral': tramite.refCatastral,
            'potenciaNumerica': tramite.potenciaNumerica,
            'fecha': tramite.fecha.strftime('%d/%m/%Y'),
            'estado': tramite.estado,
            # Incluir información de documentos
            'dniPdf': tramite.dniPdf,
            'formatoAutorizacion': tramite.formatoAutorizacion,
            'plantillaRelacionPuntos': tramite.plantillaRelacionPuntos
        }
        
        # Añadir campos específicos según el tipo
        if tramite.tipo == 'Modificación':
            tramite_data['aumentoPotencia'] = tramite.aumentoPotencia
        elif tramite.tipo == 'Individual':
            tramite_data['vivienda'] = tramite.vivienda
        elif tramite.tipo == 'Alta':
            tramite_data['variosSuministros'] = tramite.variosSuministros
            tramite_data['acometidaCentralizada'] = tramite.acometidaCentralizada
        
        result.append(tramite_data)
    
    # Depurar el resultado JSON
    print(f"DEBUG - JSON Result: {result}")
    
    return jsonify(result), 200

@app.route('/api/tramites/<int:tramite_id>', methods=['PATCH'])
@token_required
def update_tramite_estado(current_user, tramite_id):
    data = request.json
    
    if not data or 'estado' not in data:
        return jsonify({'message': 'Falta el campo estado'}), 400
    
    tramite = Tramite.query.filter_by(id=tramite_id, user_id=current_user.id).first()
    
    if not tramite:
        return jsonify({'message': 'Trámite no encontrado o no autorizado'}), 404
    
    tramite.estado = data['estado']
    db.session.commit()
    
    return jsonify({'message': 'Estado actualizado correctamente'}), 200

# Rutas para obtener documentos
@app.route('/api/documents/<filename>', methods=['GET'])
def get_document(filename):
    try:
        token = get_token_from_request()
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                raise Exception('Usuario no encontrado')
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401
            
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'message': f'Error al obtener el documento: {str(e)}'}), 404

@app.route('/api/documents/download/<filename>', methods=['GET'])
def download_document(filename):
    try:
        token = get_token_from_request()
        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                raise Exception('Usuario no encontrado')
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401
            
        return send_from_directory(
            app.config['UPLOAD_FOLDER'], 
            filename, 
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'message': f'Error al descargar el documento: {str(e)}'}), 404

# Ruta para reiniciar la base de datos (solo para pruebas)
@app.route('/api/reset_db', methods=['GET'])
def reset_db():
    try:
        # Borrar todas las tablas
        db.drop_all()
        
        # Recrear todas las tablas
        db.create_all()
        
        # Crear un usuario de prueba
        hashed_password = generate_password_hash('password')
        test_user = User(
            name='Usuario de Prueba',
            email='test@example.com',
            password=hashed_password
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Generar un token para este usuario
        token = jwt.encode({
            'user_id': test_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Base de datos reiniciada correctamente',
            'test_user': {
                'email': 'test@example.com',
                'password': 'password',
                'token': token
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al reiniciar la base de datos: {str(e)}'}), 500

# Crear las tablas en el contexto de la aplicación
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 
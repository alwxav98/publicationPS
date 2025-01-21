from flask import Flask, render_template, request, redirect, url_for, session, make_response
import redis
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = 'claveSuperSecreta'

# Configuración de MySQL
MYSQL_CONFIG = {
    "host": "ec2-3-230-92-158.compute-1.amazonaws.com",
    "user": "root",
    "password": "claveSegura123@",
    "database": "postsDB",
}

# Configuración de Redis
REDIS_CONFIG = {
    "host": "ec2-34-201-173-204.compute-1.amazonaws.com",
    "port": 6379,
    "password": "claveSegura123@",
}

# Conectar a Redis
try:
    redis_client = redis.StrictRedis(
        host=REDIS_CONFIG["host"],
        port=REDIS_CONFIG["port"],
        password=REDIS_CONFIG["password"],
        decode_responses=True
    )
    print("Conexión exitosa a Redis")
except Exception as e:
    print(f"Error al conectar a Redis: {e}")
    redis_client = None


@app.route("/", methods=["GET"])
def index():
    """Página principal que muestra las publicaciones."""
    auth_token = request.cookies.get("auth_token")

    if not auth_token:
        return "Error: No estás autenticado. Token no encontrado.", 401

    # Recuperar el email del usuario desde Redis
    user_email = redis_client.get(auth_token) if redis_client else None

    if not user_email:
        return "Error: Sesión expirada o no válida.", 403

    # Conectar a MySQL para obtener publicaciones
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Posts ORDER BY CreatedAt DESC")
        posts = cursor.fetchall()
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return render_template("index.html", user_email=user_email, posts=posts)


@app.route("/upload", methods=["POST"])
def upload_post():
    """Subir una nueva publicación (implementación futura)."""
    return "Funcionalidad de subir publicaciones no implementada aún."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

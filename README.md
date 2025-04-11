# Aplicación de Gestión de Trámites

Una aplicación web para gestionar trámites y solicitudes relacionadas con instalaciones eléctricas.

## Requisitos

- Docker
- Docker Compose

## Configuración para desarrollo local

1. Clona el repositorio:
   ```
   git clone https://github.com/tu-usuario/tramite.git
   cd tramite
   ```

2. Construye e inicia los contenedores:
   ```
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. La aplicación estará disponible en:
   - Frontend: http://localhost (o http://localhost:80)
   - API Backend: http://localhost/api
   - API directamente: http://localhost:5075

## Despliegue en VPS

1. Clona el repositorio en tu VPS:
   ```
   git clone https://github.com/tu-usuario/tramite.git
   cd tramite
   ```

2. Si deseas cambiar el puerto (configurado al estándar 80 por defecto), edita el archivo `docker-compose.yml` para cambiar el puerto de exposición.

3. Inicia los contenedores:
   ```
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. Configura tu firewall para permitir el tráfico en los puertos elegidos:
   ```
   ufw allow 80/tcp
   ufw allow 5075/tcp
   ```

## Estructura del proyecto

```
tramite/
├── tramite-app/
│   ├── backend/        # API REST con Flask
│   ├── frontend/       # Aplicación React
│   └── nginx/          # Configuración de Nginx
└── docker-compose.yml  # Configuración de Docker
```

## Características

- Autenticación con JWT
- Gestión de solicitudes
- Gestión de trámites
- Subida y descarga de documentos
- Interfaz de usuario responsiva 
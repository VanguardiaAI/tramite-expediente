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
   docker-compose up -d --build
   ```

3. La aplicación estará disponible en:
   - Frontend: http://localhost:8090
   - API Backend: http://localhost:8090/api

## Despliegue en VPS

1. Clona el repositorio en tu VPS:
   ```
   git clone https://github.com/tu-usuario/tramite.git
   cd tramite
   ```

2. Opcionalmente, edita el archivo `docker-compose.yml` para cambiar el puerto de exposición (8090 por defecto).

3. Inicia los contenedores:
   ```
   docker-compose up -d --build
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
FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Contenedor final
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

# Solo para desarrollo/debug - para que el volumen funcione correctamente
WORKDIR /app
RUN mkdir -p /app/dist
VOLUME /app/dist
COPY --from=build /app/dist /app/dist/

CMD ["nginx", "-g", "daemon off;"] 
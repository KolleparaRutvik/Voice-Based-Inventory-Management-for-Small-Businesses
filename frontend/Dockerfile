# DukaanSetu Frontend — Multi-Stage Production Dockerfile

# Build Stage
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package descriptors
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build production bundle
RUN npm run build

# Serve Stage with Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

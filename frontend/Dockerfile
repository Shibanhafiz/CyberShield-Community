# CyberShield frontend — build with Node, serve statically with nginx.
# Build context is frontend/:
#   docker build -f frontend/Dockerfile -t cybershield-frontend ./frontend
# VITE_* values are PUBLIC (embedded in the browser bundle) — never secrets.

FROM node:20-alpine AS builder
WORKDIR /fe
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
ARG VITE_BACKEND_URL=http://localhost:8001
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /fe/dist /usr/share/nginx/html
EXPOSE 80

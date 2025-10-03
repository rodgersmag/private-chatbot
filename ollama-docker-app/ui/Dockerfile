# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Set build arguments
ARG VITE_OLLAMA_URL
ARG VITE_DEFAULT_MODEL
ARG VITE_API_URL
ARG VITE_ANON_KEY

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

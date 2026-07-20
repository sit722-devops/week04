# Build stage
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG VITE_STUDENT_SERVICE_URL
ARG VITE_COURSE_SERVICE_URL

ENV VITE_STUDENT_SERVICE_URL=$VITE_STUDENT_SERVICE_URL
ENV VITE_COURSE_SERVICE_URL=$VITE_COURSE_SERVICE_URL

RUN npm run build


# Runtime stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# FROM node:22-alpine

# WORKDIR /app

# COPY package.json .

# RUN npm install

# COPY . .

# EXPOSE 5173

# CMD ["npm", "run", "dev"]
FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# COPY /certs/cert.pem /etc/ssl/
# COPY /certs/key.pem /etc/ssl/
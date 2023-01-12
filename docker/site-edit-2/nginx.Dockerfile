FROM nginx:1.23
WORKDIR /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p /var/logs
COPY ./docker/site-edit-2/nginx-gun.conf /etc/nginx/conf.d/
EXPOSE 80

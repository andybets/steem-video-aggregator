FROM nginx:1.11.3

# todo - try installing certbot for auto renewable SSL certificates
# RUN apt-get update
# RUN apt-get install software-properties-common
# RUN add-apt-repository ppa:certbot/certbot
# RUN apt-get update
# RUN apt-get install python-certbot-nginx

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf

# for non-SSL server
COPY mysettings.conf /etc/nginx/conf.d/

# for SSL server
COPY mysettings-ssl.conf /etc/nginx/conf.d/

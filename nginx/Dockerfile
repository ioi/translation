FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY conf.d/ /etc/nginx/conf.d/
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
CMD ["nginx", "-g", "daemon off;"]
ENTRYPOINT ["/docker-entrypoint.sh"]

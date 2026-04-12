FROM postgres:15-alpine

RUN apk add --no-cache aws-cli curl

COPY backup.sh /backup.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /backup.sh /entrypoint.sh

VOLUME /backups

ENTRYPOINT ["/entrypoint.sh"]

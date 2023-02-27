FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.02.09

RUN mkdir -p /beacon/config
WORKDIR /beacon

# Copy whole project directory
COPY . .

RUN pip install -r requirements.txt

RUN chmod 775 ./entrypoint.sh
CMD [ "sh", "./entrypoint.sh" ]

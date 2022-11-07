FROM ghcr.io/bento-platform/bento_base_image:python-debian-latest

RUN mkdir /beacon
WORKDIR /beacon

# Copy whole project directory
COPY . .

RUN pip install -r requirements.txt

RUN chmod 775 ./entrypoint.sh
CMD [ "sh", "./entrypoint.sh" ]

FROM python:3.8.5
WORKDIR /code
COPY . .
ENV DB_HOST infra_db_1
RUN pip install pip --upgrade && pip install -r requirements.txt
ENTRYPOINT ["/code/entrypoint.sh"]
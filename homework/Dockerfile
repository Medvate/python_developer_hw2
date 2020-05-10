FROM python:3.8

RUN mkdir -p /usr/src/homework_3/
WORKDIR /usr/src/homework_3/

COPY . /usr/src/homework_3/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5433

CMD ["python", "cli.py", "create", "Илья", "Иванов", "--birth-date", "1990-01-01", "--phone", "+7(916)000-00-00", "--document-type", "Паспорт РФ", "--document-id", "0000 000000"]
FROM python:latest

WORKDIR /usr/app/src
COPY src ./
COPY requirements.txt ../
RUN mkdir -p ../data
RUN pip install -r ../requirements.txt

CMD ["python", "-u", "./crawl_controller.py", "--db_path", "../data/kl_cars.db"]
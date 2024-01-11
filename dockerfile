FROM python:latest

WORKDIR /usr/app/src
COPY src ./
COPY requirements.txt ../
RUN mkdir -p ../data
RUN pip install -r ../requirements.txt
ENV WD_URL=http://192.168.0.2:4444/wd/hub

CMD ["python", "-u", "./crawl_controller.py", "--db_path", "../data/kl_cars.db", "--wd_url", "$WD_URL"]
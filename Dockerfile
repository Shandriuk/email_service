FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV WEB=/email_service

RUN mkdir -p $WEB
RUN mkdir -p $WEB/static

WORKDIR $WEB/
COPY requirements.txt $WEB
RUN pip3 install --upgrade pip && pip install -r requirements.txt
ADD . $WEB

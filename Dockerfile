# nutrition-irrigation-model-1.2.0

FROM python:3.14-slim

RUN mkdir /src
# Copy REQUIREMENT_FILE in src folder
COPY ./requirements.txt  /src/

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get install git -y \
&& apt-get clean

RUN pip install --upgrade pip
RUN pip install -r /src/requirements.txt
RUN pip install flake8 black jupyter

# Set PYTHONPATH
ENV PYTHONPATH="/src/:$PATH"
ENV TZ="Europe/Rome"

EXPOSE 8888

COPY .  /src/
WORKDIR /src
RUN apt install pandoc texlive-latex-base -y
RUN apt install texlive-latex-recommended -y
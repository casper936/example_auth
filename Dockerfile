###########
# BUILDER #
###########

# Скачиваем официальный образ с Docker Hub
FROM python:3.12.2-slim-bullseye as builder

# устанавливаем рабочую директорию
WORKDIR /tmp

# устанавливаем psycopg2 зависимости
RUN apt-get update \
    && apt-get upgrade -y && apt-get install -qy --no-install-recommends build-essential

RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

# Generate the requirements.txt file.
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

#########
# FINAL #
#########

# Запускаем приложение от пользователя `app`,
# т.к. от пользователя `root` запускать приложение совершенно не секурно >.<

# Скачиваем официальный образ с Docker Hub
FROM python:3.12.2-slim-bullseye

# создатем соответствующие каталоги
ENV HOME=/home/app
ENV APP_HOME=/home/app/src

# устанавливаем пременные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $APP_HOME

# создаем директорию для пользователя `app`
RUN mkdir -p ${APP_HOME}

# создаем пользователя `app`
RUN groupadd -g 1234 -r app && \
    useradd -u 1234 -r -g app -d /home/app -s /sbin/nologin -c "Docker image user" app

WORKDIR ${HOME}

COPY --from=builder /tmp/requirements.txt ${HOME}/requirements.txt

RUN pip install --no-cache-dir --upgrade -r ${HOME}/requirements.txt
RUN rm -rf /root/.local/* /root/.cache/* /var/lib/apt/lists/* /var/cache/apt/*

COPY entrypoint.sh ${HOME}
COPY src/ ${APP_HOME}/

# даем права на все файлы приложения пользователю `app`
RUN chown -R app:app $HOME
RUN chmod +x $HOME/entrypoint.sh

# меняем на пользователя `app`
USER app

# запускаем entrypoint.sh
ENTRYPOINT ["bash","-c"]
CMD ["${HOME}/entrypoint.sh"]
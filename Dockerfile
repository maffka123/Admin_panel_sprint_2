FROM python:3.7
WORKDIR /home
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="config.settings.production"
EXPOSE 8000
COPY ./ /home/
RUN pip3 install -r movies_admin/requirements/production.txt
ENTRYPOINT ["src/entrypoint.sh"]
FROM python

WORKDIR /opt/app
COPY . /opt/app
RUN pip install -r requirement.txt
ENV PORT 8080
EXPOSE 8080

ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]w
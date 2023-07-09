FROM python:3-alpine AS builder

# upgrade pip
RUN pip install --upgrade pip

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /app/ && chown -R nonroot:nonroot /app
RUN mkdir -p /var/log/flask-app
RUN touch /var/log/flask-app/flask-app.err.log
RUN touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /app
USER nonroot

# venv
ENV VIRTUAL_ENV=/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --chown=nonroot:nonroot requirements.txt .
RUN pip install -r requirements.txt

FROM builder AS copy_code
# copy all the files to the container
COPY --chown=nonroot:nonroot . .

CMD ["python", "app.py"]

FROM python:3-alpine AS builder

# upgrade pip
RUN pip install --upgrade pip

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /appdir/ && chown -R nonroot:nonroot /appdir
RUN mkdir -p /var/log/flask-app
RUN touch /var/log/flask-app/flask-app.err.log
RUN touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /appdir
USER nonroot

# venv
ENV VIRTUAL_ENV=/appdir/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --chown=nonroot:nonroot requirements.txt .
RUN pip install -r requirements.txt

FROM builder AS copy_code
# copy all the files to the container
COPY --chown=nonroot:nonroot . .


WORKDIR /appdir
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# CMD ["python", "app.py"]
CMD ["gunicorn"]

FROM python
RUN pip install boto
RUN pip install Flask
RUN pip install flask-httpauth
RUN pip install gunicorn

# Debugging stuff below
#RUN pip install ipython
#RUN apt-get update && apt-get install vim -y

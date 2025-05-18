FROM python:3
#Creates a dir where things will be copy and also where commands will be run
WORKDIR /docker_back

COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
#Copy things in this dir into working dir 
COPY . .
#Have to set up the PYTHONPATH or my custom modules wont be find
ENV PYTHONPATH /docker_back/app

RUN chmod +x start.sh

CMD ["./start.sh"]

# specify our base image
FROM python:3.9.7

# setting the working directory
WORKDIR /home/mark/docker

# copy our requirements.txt file from our local machine onto our docker container
COPY requirements.txt ./

# responsible for installing all of our dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy everything in our current directory to the current directory in our container
COPY . .

# give the command that we wanna run when we start the container
CMD ["uvicorn", "ORM.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Docker file is complete and we can actually build our image
# docker build --help
# docker build -t fastapi .
# docker image ls (we got our fastapi right up there)
# Now we can go ahead and use the image for actually building out a container
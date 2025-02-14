#Take the node image
FROM node:20-alpine 

#Make this the dir where we work, same as mkdir app -> cd app
WORKDIR /app

ARG NEXT_PUBLIC_BACKEND_HOST
ARG NEXT_PUBLIC_BACKEND_PORT
ENV NEXT_PUBLIC_BACKEND_HOST=${NEXT_PUBLIC_BACKEND_HOST}
ENV NEXT_PUBLIC_BACKEND_PORT=${NEXT_PUBLIC_BACKEND_PORT}

#Copy dependecies specs files
COPY package*.json ./
#This is clean install
RUN npm ci

#Copy code
COPY . .

#show port 
EXPOSE 3000

#https://stackoverflow.com/questions/53192540/difference-between-npm-run-dev-and-npm-start
#Use this for now
CMD ["npm","run","dev"]

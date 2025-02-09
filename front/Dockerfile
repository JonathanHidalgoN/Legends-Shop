#Multi stage docker build, first install node and dependecies, create html files 
#Then install nginx, copy html into the server directly and run it
#https://blog.alexellis.io/mutli-stage-docker-builds/

#Take the node image
FROM node:20-alpine as builder 

#Make this the dir where we work, same as mkdir app -> cd app
WORKDIR /app

#Copy dependecies specs files
COPY package*.json ./
#This is clean install
RUN npm ci

#Copy code
COPY . .
#Generate the files that go into the server, this is store in /app/dist
RUN npm run build 

#Take nginx
FROM nginx:stable-alpine 

#Take the files and put in the server
COPY --from=builder /app/dist /usr/share/nginx/html
#Shows that we want to use this port 
EXPOSE 3000 
#Run nginx in teh foreground
CMD ["nginx", "-g", "daemon off;"]

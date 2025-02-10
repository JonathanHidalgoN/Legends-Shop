#Take the node image
FROM node:20-alpine 

#Make this the dir where we work, same as mkdir app -> cd app
WORKDIR /app

#Copy dependecies specs files
COPY package*.json ./
#This is clean install
RUN npm ci

#Copy code
COPY . .

#show port 
EXPOSE 3000

CMD ["npm","run","start"]

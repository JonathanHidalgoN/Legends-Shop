#Take the node image
FROM node:20-alpine 

#Make this the dir where we work, same as mkdir app -> cd app
WORKDIR /app

ARG NEXT_PUBLIC_SERVER_DOMAIN
ARG NEXT_PUBLIC_CLIENT_DOMAIN
ENV NEXT_PUBLIC_CLIENT_DOMAIN=${NEXT_PUBLIC_CLIENT_DOMAIN}
ENV NEXT_PUBLIC_SERVER_DOMAIN=${NEXT_PUBLIC_SERVER_DOMAIN}

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

# TODO: MAKE THIS WORK 
# FROM node:20-alpine AS base
#
# # Install dependencies only when needed
# FROM base AS deps
# # Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
# RUN apk add --no-cache libc6-compat
# WORKDIR /app
#
# ARG NEXT_PUBLIC_BACKEND_HOST
# ARG NEXT_PUBLIC_BACKEND_PORT
# ENV NEXT_PUBLIC_BACKEND_HOST=${NEXT_PUBLIC_BACKEND_HOST}
# ENV NEXT_PUBLIC_BACKEND_PORT=${NEXT_PUBLIC_BACKEND_PORT}
#
# # Install dependencies based on the preferred package manager
# COPY package*.json ./
# #This is clean install
# RUN npm ci
#
# # Rebuild the source code only when needed
# FROM base AS builder
# WORKDIR /app
# COPY --from=deps /app/node_modules ./node_modules
# COPY . .
#
# # Next.js collects completely anonymous telemetry data about general usage.
# # Learn more here: https://nextjs.org/telemetry
# # Uncomment the following line in case you want to disable telemetry during the build.
# ENV NEXT_TELEMETRY_DISABLED 1
#
# RUN npm run build
#
# # Production image, copy all the files and run next
# FROM base AS runner
# WORKDIR /app
#
# ENV NODE_ENV production
# # Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED 1
#
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs
#
# COPY --from=builder /app/public ./public
#
# # Set the correct permission for prerender cache
# RUN mkdir .next
# RUN chown nextjs:nodejs .next
#
# # Automatically leverage output traces to reduce image size
# # https://nextjs.org/docs/advanced-features/output-file-tracing
# COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
#
# USER nextjs
#
# EXPOSE 3000
#
# ENV PORT 3000
# # set hostname to localhost
# ENV HOSTNAME "0.0.0.0"
#
# # server.js is created by next build from the standalone output
# # https://nextjs.org/docs/pages/api-reference/next-config-js/output
# CMD ["node", "server.js"]

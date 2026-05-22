FROM node:22-alpine

WORKDIR /app

RUN npm install -g @quasar/cli

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 9000
CMD ["npx", "quasar", "dev", "--host", "0.0.0.0", "--port", "9000"]

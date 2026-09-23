FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

# --host exposes Vite's dev server outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

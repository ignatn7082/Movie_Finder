# Sử dụng Node.js 18
FROM node:18

WORKDIR /app

# Copy package.json và cài dependencies
COPY package*.json ./
RUN npm install

# Copy toàn bộ mã nguồn
COPY . .

# Expose cổng Vite dev server
EXPOSE 3000

# Chạy server Vite với --host 0.0.0.0
CMD ["npx", "vite", "--host", "0.0.0.0"]

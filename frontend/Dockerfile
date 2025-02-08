FROM node:18 as build
WORKDIR /app
# COPY package*.json ./
# RUN npm install -g pnpm
# RUN pnpm install --registry https://registry.npmmirror.com
# COPY . .
# RUN pnpm build

# 容器内 pnpm build 报错，暂时在本地编译
COPY ./dist ./dist

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

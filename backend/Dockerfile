FROM python:3.10-slim

# RUN apt-get update && apt-get install -y curl net-tools

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
EXPOSE 5000
ENTRYPOINT ["python", "specification.py"]
FROM docker.mexxxxai.win/library/python:3.10.9
# # 设定时区
ENV TZ=Asia/Shanghai

# 2. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Shanghai

# 3. 安装必要的系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. 设置工作目录
WORKDIR /app

# 5. 复制并安装Python依赖
COPY requirements.txt /app/
RUN pip install -r requirements.txt  

# 6. 复制项目代码
COPY . /app/

# # 7. 暴露端口
# EXPOSE 8000

# # 8. 设置默认启动命令
# CMD ["python", "start_api.py", "--host", "0.0.0.0"]

EXPOSE 8000

CMD ["gunicorn", "fastapi_mongodb:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "60"]
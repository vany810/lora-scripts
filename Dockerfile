FROM nvcr.io/nvidia/pytorch:23.07-py3

EXPOSE 28000
EXPOSE 6006

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && apt update && apt install python3-tk -y

RUN mkdir /app

WORKDIR /app
RUN git clone --recurse-submodules -b tyj --single-branch https://github.com/vany810/lora-scripts.git

WORKDIR /app/lora-scripts
RUN pip install xformers==0.0.21 --no-deps && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements_tyj.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app/lora-scripts/sd-scripts
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app/lora-scripts

CMD ["python", "gui.py", "--listen"]
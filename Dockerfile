FROM pytorch/pytorch:latest

WORKDIR /

ENV ENCODER encode/encode.yml
ENV TMP_WORKSPACE /workspace

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl libmagic-dev

RUN pip install -r requirements.txt

RUN python -c "import torchvision.models as models; models.mobilenet_v2(pretrained=True)"

COPY . /

RUN bash get_data.sh && \
    python app.py -t index -n 5 && \
    rm -rf /tmp/jina/ndvr

CMD ["python", "app.py","-t","query"]
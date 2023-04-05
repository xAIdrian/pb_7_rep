FROM python:3.8-slim-buster
ENV TZ=US/Eastern
# Install Git and other dependencies
RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY src/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

CMD [ "python", "src/content_creator.py"]
# Start cron service
# CMD ["cron", "-f"]
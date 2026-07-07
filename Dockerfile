FROM joyzoursky/python-chromedriver:3.9-selenium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# DrissionPage can use the pre-installed chromedriver/chrome in this image
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pas de port exposé, ce service n'écoute pas, il "poll" activement.
CMD ["python", "-u", "main.py"]
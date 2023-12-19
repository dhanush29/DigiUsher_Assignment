FROM python:3.11.2-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV ATLAS_URI mongodb+srv://dhanush:dhanush@cluster0.pelg3oa.mongodb.net/?retryWrites=true&w=majority

CMD ["uvicorn", "main:app"]
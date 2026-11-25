FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 lab && mkdir /app/data && chown lab:lab /app/data
USER lab
EXPOSE 8000
CMD ["uvicorn","redteam_lab.api:app","--host","0.0.0.0","--port","8000"]

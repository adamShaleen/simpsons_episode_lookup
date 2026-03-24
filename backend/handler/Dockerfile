FROM public.ecr.aws/lambda/python:3.12

COPY backend/handler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

CMD ["backend.handler.handler.lambda_handler"]

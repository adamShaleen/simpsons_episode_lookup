FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py search.py bedrock.py simpsons_api.py ./

CMD ["handler.lambda_handler"]

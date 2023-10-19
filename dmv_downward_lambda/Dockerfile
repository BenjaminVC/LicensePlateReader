FROM public.ecr.aws/lambda/python:3.8

# Copy the lambda functions and any other necessary files
COPY plate_reader_function.py ./

# install dependencies
RUN pip install boto3

# Set the CMD to the handler (this can be overwritten by providing a different command in the template directly)
CMD ["plate_reader_function.lambda_handler"]

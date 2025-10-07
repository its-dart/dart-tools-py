# Lambda functions

To use the `dart-tools` Python library in an AWS Lambda function, you need to package the library with your Lambda deployment package (see more details at [Working with .zip file archives for Python Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)). Follow these steps:

## Navigate to the directory containing your `lambda_function.py` source file. In this example, the directory is named `my_function`.

  ```sh
  cd my_function
  ```

## Create a Deployment Package

  Use Docker to create a deployment package that includes the `dart-tools` library. Run the following commands in your terminal, ensuring that the `RUNTIME_PYTHON_VERSION` and `RUNTIME_ARCHITECTURE` environment variables match the runtime settings of your Lambda function:

  ```sh
  export RUNTIME_PYTHON_VERSION=3.12
  export RUNTIME_ARCHITECTURE=x86_64
  docker run --rm --volume ${PWD}:/app --entrypoint /bin/bash public.ecr.aws/lambda/python:${RUNTIME_PYTHON_VERSION}-${RUNTIME_ARCHITECTURE} -c "pip install --target /app/package dart-tools"
  ```

  This command installs the `dart-tools` library into a directory named `package` in your current working directory.

## Zip the contents of the `package` directory along with your `lambda_function.py`

  ```sh
  cd package
  zip -r ../my_deployment_package.zip .
  cd ..
  zip -r my_deployment_package.zip lambda_function.py
  ```

## Deploy the Lambda function

  Upload the `my_deployment_package.zip` file to AWS Lambda using the AWS Management Console or the AWS CLI.

By following these steps, you can use the `dart-tools` Python library within your AWS Lambda functions.

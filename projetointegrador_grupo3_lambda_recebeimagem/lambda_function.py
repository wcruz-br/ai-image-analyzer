import base64
import json
import boto3
import time
import socket
import botocore.exceptions

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

def resposta(statusCode, body):
    return {
        'statusCode': statusCode,
        'body': body,
        "responseParameters": {
            "method.response.header.Access-Control-Allow-Origin": '*'  # Allow requests from any origin
        },
        'headers': {
            'Access-Control-Allow-Origin': '*'  # Allow requests from any origin
        },
        "Access-Control-Allow-Origin": '*',  # Allow requests from any origin
        "origin": "*"
}

def lambda_handler(event, context):
    """
    Lambda function to handle image upload from HTML form.

    Args:
        event (dict): API Gateway event containing form data.
        context (object): Lambda context object.

    Returns:
        dict: API Gateway response object.
    """

    # print(event)
    # print(context)

    try:
        # Extract image data from the JSON body
        try:
            image_data = event['body']
            content_type = event["headers"]["content-type"]
        except Exception as e:
            return resposta( 500, json.dumps({'error': str(e)}) )

        # Check if image data exists
        if not image_data:
            return resposta( 400, json.dumps({'error': 'No image data provided.'}) )

        # Convert image_data, que contém a imagem enviada pelo formulário html e codificada como "multipart/form-data", em dados binários
        image_binary = base64.b64decode(image_data)

        # Save the image to the S3 bucket
        timestamp = int(time.time())
        ip = socket.gethostbyname(socket.gethostname()).replace('.', '')
        filename = f"{timestamp}_{ip}.jpg"
        s3.put_object(Bucket='projetointegrador-grupo3-bucket', Key=filename, Body=image_binary)

        # chama o rekognition para analisar a imagem que foi colocada no bucket
        response = rekognition.detect_labels(Image={'Bytes': image_binary})
        print(response)

    except botocore.exceptions.ClientError as e:
        # Handle ClientError (e.g., invalid bucket names, permissions issues)
        return resposta(500, json.dumps({'ClientError': str(e)}))

    except botocore.exceptions.ParamValidationError as e:
        # Handle parameter validation errors
        return resposta(400, json.dumps({'ParamValidationError': str(e)}))

    except Exception as e:
        # Handle any other unexpected exceptions
        return resposta(500, json.dumps({'Exception': str(e)}))

    return resposta( 200, json.dumps({'message': 'Image received successfully.'}) )

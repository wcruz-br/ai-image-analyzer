import base64
import json
import boto3
import time
import socket
import botocore.exceptions

def lambda_handler(event, context):
    """
    Lambda function to handle image upload from HTML form.

    Args:
        event (dict): API Gateway event containing form data.
        context (object): Lambda context object.

    Returns:
        dict: API Gateway response object.
    """

    # text = ""
    # for s in event.keys():
    #     text += s + '\n'
    # return {
    #     'statusCode': 200,
    #     'body': event["body"]
    # }

    try:
        # encontra o 'body' no json contido em event e coloca em uma variável chamada image_data
        try:
            image_data = event['body']
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Acesso invalido - ' + str(e)})
            }            

        # Check if image data exists
        if not image_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data provided.'})
            }

        # Decode the base64 encoded image data
        image_binary = base64.b64decode(image_data)

        # Grava a imagem no bucket S3, usando como nome o timestampunix + o ip de origem sem os pontos
        # Exemplo: 1678801234_192168110
        s3 = boto3.client('s3')
        timestamp = int(time.time())
        ip = socket.gethostbyname(socket.gethostname()).replace('.', '')
        # filename = f"{timestamp}_{ip}.jpg"
        # s3.put_object(Bucket='projetointegrador-grupo3-bucket', Key=filename, Body=image_binary)
        filename_debug = f"{timestamp}_{ip}.txt"
        s3.put_object(Bucket='projetointegrador-grupo3-bucket', Key=filename_debug, Body="teste")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Imagem recebida com sucesso.'})
        }
    except botocore.exceptions as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'ClientError': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'Exception': str(e)})
        }

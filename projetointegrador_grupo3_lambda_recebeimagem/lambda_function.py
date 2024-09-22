import base64
import json
import boto3
import time
import socket
import botocore.exceptions
import cgi
from io import BytesIO 

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
# dynamodb = boto3.client('dynamodb')

def resposta(statusCode, body):
    return {
        'statusCode': statusCode,
        'body': body,
        "responseParameters": {
            "method.response.header.Access-Control-Allow-Origin": '*'  # Allow requests from any origin
        },
        'headers': {
            'Access-Control-Allow-Origin': '*',  # Allow requests from any origin
            'Content-Type': 'text/html'  # Allow requests from any origin
        },
        "Access-Control-Allow-Origin": '*',  # Allow requests from any origin
        "origin": "*"
    }

def grava_objeto_no_bucket_s3(image_binary):
    timestamp = int(time.time())
    ip = socket.gethostbyname(socket.gethostname()).replace('.', '')
    filename = f"{timestamp}_{ip}.jpg"
    s3.put_object(Bucket='projetointegrador-grupo3-bucket', Key=filename, Body=image_binary)

def pagina_de_resposta(labels, html_imagem_com_boxes):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>An&aacute;lise de imagem</title>
        <style>
            body {{
                font-family: sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                background-color: #f0f0f0;
            }}
            .container {{
                background-color: #fff;
                padding: 30px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            h1, h2 {{
                text-align: center;
                margin-bottom: 20px;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                margin-bottom: 10px;
            }}
            table {{
                border: 1px solid black; 
                margin: 0 auto; /* Centraliza a tabela horizontalmente */
            }}
            th {{ /* Estilos para a linha de título da tabela */
                background-color: blue; 
                color: white;
                padding: 5px 10px 5px 10px;
            }}
            tbody tr:nth-child(even) {{ /* Estilo para linhas pares */
                background-color: #e0f0f0;
            }}
            /* Centraliza o conteúdo da coluna Confiança */
            td:nth-child(2) {{ /* Seleciona a segunda coluna (Confiança) */
                text-align: center;
            }}
            td {{
                padding: 3px 10px 3px 10px;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h2>Resultados da an&aacute;lise da imagem</h2>

            <div style="display: flex; align-items: flex-start;"> 
                <div style="position: relative;">
                    {html_imagem_com_boxes}
                </div>
                <div style="width: 300;">
                    <table>
                        <thead>
                            <tr>
                                <th>R&oacute;tulo</th>
                                <th>Confian&ccedil;a</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f'<tr id="row-{label["Name"]}">'
                                    f'<td>{label["Name"]}</td><td>{label["Confidence"]:.2f}</td></tr>' 
                                    for label in labels])}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </body>

    </html>
    """
    
    return html

def gerar_html_imagem_com_boxes(imagem_base64, labels):
    """Gera o HTML da imagem com os bounding boxes dos labels.

    Args:
        imagem_base64: String base64 da imagem.
        labels: Lista de labels retornados pelo Rekognition.

    Returns:
        String: HTML da imagem com os bounding boxes.
    """

    html_boxes = ""
    for label in labels:
        if 'Instances' in label:
            for i, instance in enumerate(label['Instances']):
                box = instance['BoundingBox']
                top = box['Top'] * 100
                left = box['Left'] * 100
                width = box['Width'] * 100
                height = box['Height'] * 100

                # Adiciona um ID único para cada linha da tabela
                row_id = f"row-{label['Name']}"

                html_boxes += f"""
                    <div style="
                        position: absolute; 
                        top: {top}%; 
                        left: {left}%; 
                        width: {width}%; 
                        height: {height}%; 
                        border: 2px solid white;
                        background-color: rgba(255, 255, 255, 0.3); /* Translucent white */
                    " 
                        id="box-{label['Name']}-{i}"  # Keep the ID for the label
                        data-row-id="row-{label['Name']}"  # Add data-row-id attribute
                        onmouseover="showLabel(event); highlightRow(this.dataset.rowId)" 
                        onmouseout="hideLabel(event); unhighlightRow(this.dataset.rowId)"
                    >
                        <div id="label-{label['Name']}-{i}" class="label" style="
                            display: none;
                            position: absolute;
                            top: -20px; 
                            left: 50%;
                            transform: translateX(-50%);
                            background-color: black;
                            color: white;
                            padding: 3px 5px;
                            font-size: 12px;
                            border-radius: 3px;
                            white-space: nowrap;
                        ">
                            {label['Name']}
                        </div>
                    </div>
                """

    html_imagem = f"""
        <div style="position: relative;"> 
            <img src="data:image/jpeg;base64,{imagem_base64}" style="max-width: 100%; height: auto;">
            {html_boxes}
        </div>
        <script>
            let highlightedRowId = null; // Variable to store the highlighted row ID

            function showLabel(event) {{
                const labelDiv = event.target.querySelector('.label');
                if (labelDiv) {{
                    labelDiv.style.display = 'block';
                }}
            }}

            function hideLabel(event) {{
                const labelDiv = event.target.querySelector('.label'); 
                if (labelDiv) {{
                    labelDiv.style.display = 'none';
                }}
            }}

            // Attach event listeners after the DOM is loaded
            document.addEventListener('DOMContentLoaded', function() {{
                const boundingBoxes = document.querySelectorAll('div[id^="box-"]');
                boundingBoxes.forEach(box => {{
                    box.addEventListener('mouseover', function(event) {{
                        const rowId = this.dataset.rowId; // Get rowId from data attribute
                        showLabel(event);
                        highlightRow(rowId);
                    }});
                    box.addEventListener('mouseout', function(event) {{
                        const rowId = this.dataset.rowId; // Get rowId from data attribute
                        hideLabel(event);
                        unhighlightRow(rowId);
                    }});
                }});
            }});

            function highlightRow(rowId) {{
                document.getElementById(rowId).style.backgroundColor = 'rgba(255, 255, 0, 0.3)'; // Amarelo transparente
            }}

            function unhighlightRow(rowId) {{
                document.getElementById(rowId).style.backgroundColor = ''; // Remove o highlight
            }}
        </script>
    """
    return html_imagem

def lambda_handler(event, context):
    """
    Lambda function to handle image upload from HTML form.

    Args:
        event (dict): API Gateway event containing form data.
        context (object): Lambda context object.

    Returns:
        string: HTML de resposta
    """

    # print(event)
    # print(context)

#    try:

    # Decode the base64-encoded body
    body_decoded = base64.b64decode(event['body'])

    # Create a BytesIO object from the decoded body
    body_stream = BytesIO(body_decoded)

    # Parse multipart/form-data using the BytesIO object
    form = cgi.FieldStorage(
        fp=body_stream,
        headers=event['headers'],
        environ={'REQUEST_METHOD': 'POST'}
    )

    # Get the uploaded file
    image_file = form['image']
    image_binary = image_file.file.read()

    # Save the image to the S3 bucket
    grava_objeto_no_bucket_s3(image_binary)

    # chama o rekognition para analisar a imagem que foi colocada no bucket
    response = rekognition.detect_labels(Image={'Bytes': image_binary})
    labels = response['Labels']

    # Gera HTML com a imagem e os boxes
    imagem_base64 = base64.b64encode(image_binary).decode('utf-8')
    html_imagem_com_boxes = gerar_html_imagem_com_boxes(imagem_base64, labels)

    # Cria página de resposta
    html = pagina_de_resposta(labels, html_imagem_com_boxes)

    return resposta(200, html)

    # except botocore.exceptions.ClientError as e:
    #     # Handle ClientError (e.g., invalid bucket names, permissions issues)
    #     return resposta(500, json.dumps({'ClientError': str(e)}))

    # except botocore.exceptions.ParamValidationError as e:
    #     # Handle parameter validation errors
    #     return resposta(400, json.dumps({'ParamValidationError': str(e)}))

    # except Exception as e:
    #     # Handle any other unexpected exceptions
    #     return resposta(500, json.dumps({'Exception': str(e)}))


import unittest
import base64
import json
from unittest.mock import MagicMock, patch
from lambda_function import lambda_handler

class LambdaFunctionTest(unittest.TestCase):

    @patch('boto3.client')
    def test_lambda_handler_success(self, mock_boto3_client):
        # Mock the event and context objects
        event = {
            'body': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgYGBgYGBggGBgYGBggGBgYGBggGBggGBggGBggGBggGBggGBggDeqh/AMcHEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwTElQmJygpKissLS0dAntonio8C/8QAGwEBAAMBAQEBAAAAAAAAAAAAAAECAwQFBgf/xAA+EQACAQIDBAcGBQQDAQAAAAAAAQIDBBEhMRITFBEFRImFxMoGRoQcjQlKxwdEVIzNS8HL/2gAMAwEAAhEDEQA/APfNAAu2EUx222XbCigD/2Q=='
        }
        context = MagicMock()

        # Call the lambda_handler function
        response = lambda_handler(event, context)

        # Assertions
        with self.subTest(msg="Checking status code"):
            self.assertEqual(response['statusCode'], 200)
        with self.subTest(msg="Checking response message"):
            self.assertEqual(response['body'], json.dumps({'message': 'Imagem recebida com sucesso.'}))
        mock_boto3_client('s3').put_object.assert_called_once()

    @patch('boto3.client')
    def test_lambda_handler_no_image_data(self, mock_boto3_client):
        # Mock the event and context objects
        event = {}
        context = MagicMock()

        # Call the lambda_handler function
        response = lambda_handler(event, context)

        # Assertions
        with self.subTest(msg="Checking status code"):
            self.assertEqual(response['statusCode'], 400)
        with self.subTest(msg="Checking response message"):
            self.assertEqual(response['body'], json.dumps({'error': 'No image data provided.'}))
        mock_boto3_client('s3').put_object.assert_not_called()

    @patch('boto3.client')
    def test_lambda_handler_invalid_image_data(self, mock_boto3_client):
        # Mock the event and context objects
        event = {
            'body': ''
        }
        context = MagicMock()

        # Call the lambda_handler function
        response = lambda_handler(event, context)

        # Assertions
        with self.subTest(msg="Checking status code"):
            self.assertEqual(response['statusCode'], 500)
        with self.subTest(msg="Checking response message"):
            self.assertIn("error", response['body'])
        mock_boto3_client('s3').put_object.assert_not_called()

    @patch('boto3.client')
    def test_lambda_handler_missing_body(self, mock_boto3_client):
        # Mock the event and context objects
        event = {
        }
        context = MagicMock()

        # Call the lambda_handler function
        response = lambda_handler(event, context)

        # Assertions
        with self.subTest(msg="Checking status code"):
            self.assertEqual(response['statusCode'], 500)
        with self.subTest(msg="Checking response message"):
            self.assertIn("error", response['body'])
        mock_boto3_client('s3').put_object.assert_not_called()        

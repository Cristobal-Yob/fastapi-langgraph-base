import os
import unittest
from unittest.mock import AsyncMock, patch
import httpx
from cloud.api import create_app

TOKEN='offline_only_A9xB7yC5zD3wE1vF8uG6tH4sJ2rK0qM'


class SwaggerTests(unittest.IsolatedAsyncioTestCase):
    async def test_swagger_authorize_and_schema_do_not_unlock_operations(self):
        with patch.dict(os.environ,{'AGENT_API_TOKEN':TOKEN,'APP_VARIANT':'base','PUBLIC_ORIGIN':'http://localhost:8000'}):
            app=create_app(graph=AsyncMock())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost:8000') as http:
            page=await http.get('/docs')
            self.assertEqual(page.status_code,200)
            schema=await http.get('/openapi.json')
            self.assertEqual(schema.status_code,200)
            data=schema.json()
            scheme=data['components']['securitySchemes']['OperatorToken']
            self.assertEqual(scheme,{'type':'http','description':'Generated bearer secret for the single operator.','scheme':'bearer'})
            self.assertEqual(data['paths']['/chat']['post']['security'],[{'OperatorToken':[]}])
            self.assertNotIn(TOKEN,schema.text+page.text)
            self.assertEqual((await http.post('/chat',json={'message':'test','request_id':'synthetic'},
                headers={'Origin':'http://localhost:8000'})).status_code,401)

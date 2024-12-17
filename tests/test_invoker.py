import unittest
from unittest.mock import patch, Mock
from src.tools import Invoker


class TestInvoker(unittest.TestCase):
    def test_init(self):
        invoker = Invoker("./tests/samples/openapi.yaml")
        self.assertEqual(invoker.base_url, "https://api.petstore.example.com/v1")

    @patch("requests.request")
    def test_get(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "dog"}]
        mock_request.return_value = mock_response

        invoker = Invoker("./tests/samples/openapi.yaml")
        response = invoker.invoke("/pets", "get")

        mock_request.assert_called_once_with(
            method="get",
            url="https://api.petstore.example.com/v1/pets",
            params={},
            headers={},
            data=None,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": 1, "name": "dog"}])

    @patch("requests.request")
    def test_post_with_bearer_auth(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "name": "dog"}
        mock_request.return_value = mock_response

        invoker = Invoker("./tests/samples/openapi.yaml")
        response = invoker.invoke(
            path="/pets",
            method="post",
            parameters={"body": {"name": "dog", "type": "bulldog"}},
            headers={"Authorization": "Bearer test-token"},
        )

        mock_request.assert_called_once_with(
            method="post",
            url="https://api.petstore.example.com/v1/pets",
            params={},
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json",
            },
            data='{"name": "dog", "type": "bulldog"}',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": 1, "name": "dog"})

    @patch("requests.request")
    def test_post_with_basic_auth(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "name": "dog"}
        mock_request.return_value = mock_response

        invoker = Invoker("./tests/samples/openapi.yaml")
        response = invoker.invoke(
            path="/pets",
            method="post",
            parameters={"body": {"name": "dog", "type": "bulldog"}},
            headers={"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="},
        )

        mock_request.assert_called_once_with(
            method="post",
            url="https://api.petstore.example.com/v1/pets",
            params={},
            headers={
                "Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
                "Content-Type": "application/json",
            },
            data='{"name": "dog", "type": "bulldog"}',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": 1, "name": "dog"})

    @patch("requests.request")
    def test_get_pet_by_id(self, mock_request):
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "dog", "type": "bulldog"}
        mock_request.return_value = mock_response

        invoker = Invoker("./tests/samples/openapi.yaml")

        # Invoke the GET /pets/{petId} endpoint
        response = invoker.invoke(
            path="/pets/{petId}", method="get", parameters={"petId": 1}
        )

        # Assert the request was made correctly
        mock_request.assert_called_once_with(
            method="get",
            url="https://api.petstore.example.com/v1/pets/1",
            params={},
            headers={},
            files=None,
            data=None,
        )

        # Assert the response is as expected
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "name": "dog", "type": "bulldog"})


if __name__ == "__main__":
    unittest.main()

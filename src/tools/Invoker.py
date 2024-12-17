from typing import Dict, Any, Optional
import yaml
import json
import requests


class Invoker:
    def __init__(self, spec_path: str):
        """Initialize with OpenAPI spec file path"""
        with open(spec_path) as f:
            if spec_path.endswith(".yaml") or spec_path.endswith(".yml"):
                self.spec = yaml.safe_load(f)
            else:
                self.spec = json.load(f)

        self.base_url = self.spec.get("servers", [{"url": "/"}])[0]["url"]

    def invoke(
        self,
        path: str,
        method: str,
        parameters: Dict[str, Any] = {},
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Invoke API endpoint with parameters and security"""
        # Validate path exists
        if path not in self.spec["paths"]:
            raise ValueError(f"Path {path} not found in API spec")

        # Validate method exists for path
        path_spec = self.spec["paths"][path]
        method = method.lower()
        if method not in path_spec:
            raise ValueError(f"Method {method} not allowed for path {path}")

        operation = path_spec[method]

        # Prepare request parameters
        query_params = {}
        path_params = parameters.copy()
        request_headers = headers or {}
        body = None

        # Map parameters to correct location
        for param in operation.get("parameters", []):
            param_name = param["name"]
            if param_name in parameters:
                if param["in"] == "query":
                    query_params[param_name] = parameters[param_name]
                elif param["in"] == "path":
                    path_params[param_name] = parameters[param_name]
                elif param["in"] == "header":
                    request_headers[param_name] = parameters[param_name]

        # Handle request body if present
        if "requestBody" in operation:
            content_types = operation["requestBody"]["content"]
            if "application/json" in content_types:
                request_headers["Content-Type"] = "application/json"
                body = json.dumps(parameters.get("body", {}))
            elif "application/x-www-form-urlencoded" in content_types:
                request_headers["Content-Type"] = "application/x-www-form-urlencoded"
                body = parameters.get("body", {})
            elif "multipart/form-data" in content_types:
                request_headers["Content-Type"] = "multipart/form-data"
                body = parameters.get("body", {})

        # Format path with path parameters
        formatted_path = path.format(**path_params)
        url = self.base_url + formatted_path

        if not request_headers.get("Content-Type") == "multipart/form-data":
            body = None

        # Make request
        response = requests.request(
            method=method,
            url=url,
            params=query_params,
            headers=request_headers,
            files=body,
            data=body,
        )

        return response

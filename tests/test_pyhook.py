import json
import os
import tempfile

import pytest
from unittest.mock import Mock, patch

from app import app


@pytest.fixture
def client():
  app.app.config["TESTING"] = True

  # an example deployment config
  deployment = {
    "deploy": "service-deploy",
    "image": "mshade/pyhook",
    "key": "xxx",
    "ns": "service-test",
    "valid_tag": "^(v[0-9.]+|sha-[a-z0-9]+)",
  }

  app.app.config["deployments"] = {"deployment": deployment}

  with app.app.test_client() as client:
    yield client

# Import deploy object
with open('./tests/get_deploy.json', mode='r') as f:
  from types import SimpleNamespace as Namespace
  deploy_obj = json.load(f, object_hook=lambda d: Namespace(**d))
with open('./tests/get_deploy.json', mode='r') as f:
  deploy_json = json.load(f)

def test_index(client):
  resp = client.get('/')
  assert '403' in resp.status

def test_unconfigured_deployment(client):
  resp = client.get('/404me')
  assert '404' in resp.status

def test_deployment_get_without_key(client):
  resp = client.get('/deployment')
  assert '403' in resp.status

def test_deployment_get_with_key(client):
  with patch('kubernetes.client.AppsV1Api.read_namespaced_deployment') as mock_get:
    mock_get.return_value = deploy_json
    resp = client.get('/deployment?key=xxx')
  assert "200" in resp.status

def test_deployment_post_with_bad_key(client):
  post_data = {
    "push_data": {"tag": "v0.1.1"},
  }
  with patch('kubernetes.client.AppsV1Api.read_namespaced_deployment') as mock_get, \
      patch('kubernetes.client.AppsV1Api.patch_namespaced_deployment') as mock_update:
    mock_get.return_value = deploy_obj
    mock_update.return_value = "200 OK"
    resp = client.post('/deployment?key=aaa', json=post_data)
#    print(deploy_json["spec"])
  assert "403" in resp.status

def test_deployment_post_with_key(client):
  post_data = {
    "push_data": {"tag": "v0.1.1"},
  }
  with patch('kubernetes.client.AppsV1Api.read_namespaced_deployment') as mock_get, \
      patch('kubernetes.client.AppsV1Api.patch_namespaced_deployment') as mock_update:
    mock_get.return_value = deploy_obj
    mock_update.return_value = "200 OK"
    resp = client.post('/deployment?key=xxx', json=post_data)
#    print(deploy_json["spec"])
  assert "200" in resp.status

def test_deployment_post_with_key_bad_tag(client):
  post_data = {
    "push_data": {"tag": "latest"},
  }
  with patch('kubernetes.client.AppsV1Api.read_namespaced_deployment') as mock_get, \
      patch('kubernetes.client.AppsV1Api.patch_namespaced_deployment') as mock_update:
    mock_get.return_value = deploy_obj
    mock_update.return_value = "200 OK"
    resp = client.post('/deployment?key=xxx', json=post_data)
#    print(deploy_json["spec"])
  assert "400" in resp.status

def test_bad_path(client):
  resp = client.get('/bad/path')
  assert "40" in resp.status

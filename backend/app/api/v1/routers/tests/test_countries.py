# import random
#
# from starlette import status
#
# from app.api.routers.testing_utils.service import get_new_service
# from app.core import config
# from app.db import schemas
#
# SERVICE_URL_PREFIX = config.MAP_URL("countries")
#
#
# def test_get_service_list(client, test_service):
#     response = client.get(SERVICE_URL_PREFIX)
#     assert response.status_code == 200
#     assert response.json()['items'] == [
#         schemas.ServiceView(**test_service.__dict__).dict()
#     ]
#
#
# def test_create_service(client):
#     new_service = get_new_service()
#     response = client.post(SERVICE_URL_PREFIX, json=new_service)
#     assert response.status_code == status.HTTP_201_CREATED
#     response_data = response.json()['data']
#     assert response_data == schemas.ServiceView(id=response_data['id'], **new_service).dict()
#
#
# def test_get_service(client, test_service):
#     response = client.get(f"{SERVICE_URL_PREFIX}/{test_service.id}")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == schemas.ServiceView(**test_service.__dict__).dict()
#
#
# def test_get_service_not_found(client,):
#     response = client.get(f"{SERVICE_URL_PREFIX}/{random.randint(100,500)}")
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#
#
# def test_delete_service(client, test_service):
#     response = client.delete(
#         f"{SERVICE_URL_PREFIX}/{test_service.id}"
#     )
#     assert response.status_code == status.HTTP_200_OK
#
#
# def test_delete_service_not_found(client):
#     response = client.delete(
#         f"{SERVICE_URL_PREFIX}/{random.randint(100,500)}"
#     )
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#
#
# def test_edit_service(client, test_service):
#     new_service = get_new_service()
#     response = client.put(
#         f"{SERVICE_URL_PREFIX}/{test_service.id}",
#         json=new_service
#     )
#
#     assert response.status_code == status.HTTP_202_ACCEPTED
#     response_data = response.json()['data']
#     assert response_data == schemas.ServiceView(id=response_data['id'], **new_service).dict()
#
#
# def test_edit_service_not_found(client):
#     response = client.put(
#         f"{SERVICE_URL_PREFIX}/{random.randint(100,500)}",
#         json=get_new_service()
#     )
#     assert response.status_code == status.HTTP_404_NOT_FOUND

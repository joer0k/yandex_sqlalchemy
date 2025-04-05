import requests

print(requests.get('http://127.0.0.1:8080/api/v2/users').json())
# корректно
print(requests.get('http://127.0.0.1:8080/api/v2/users/2').json())
# неверный id
print(requests.get('http://127.0.0.1:8080/api/v2/users/2123').json())
# корректно
print(requests.post('http://127.0.0.1:8080/api/v2/users', json={'name': 'Sonya', 'position': 'junior programmer',
                                                                'surname': 'Wolf', 'age': '17', 'address': 'module_3',
                                                                'speciality': 'computer sciences',
                                                                'hashed_password': 'wolf',
                                                                'email': 'wolf10@mars.org'}).json())
# нет словаря
print(requests.post('http://127.0.0.1:8080/api/v2/users', json={}).json())

# возраст - строка
print(requests.post('http://127.0.0.1:8080/api/v2/users', json={'name': 'Sonya', 'position': 'junior programmer',
                                                                'surname': 'Wolf', 'age': 'фывфыв21фсчя17',
                                                                'address': 'module_3',
                                                                'speciality': 'computer sciences',
                                                                'hashed_password': 'wolf',
                                                                'email': 'wolf10@mars.org'}).json())

# корректно
print(requests.delete('http://127.0.0.1:8080/api/v2/users/8').json())
# неверный id
print(requests.delete('http://127.0.0.1:8080/api/v2/users/1238').json())

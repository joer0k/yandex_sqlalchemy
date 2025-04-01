import requests

print(requests.get('http://127.0.0.1:8080/api/jobs').json())
# корректный запрос
print(requests.put('http://127.0.0.1:8080/api/jobs/8', json={'job_title': 'пasdas работа',
                                                             'work_size': 15,
                                                             'collaborators': '1, 2',
                                                             'is_finished': False,
                                                             'team_leader_id': 1,
                                                             'hazard_category_id': 1,
                                                             }).json())
# некорректный запрос. работа с таким названием уже есть в списке
print(requests.put('http://127.0.0.1:8080/api/jobs/9', json={'job_title': 'первая работа',
                                                             'work_size': 15,
                                                             'collaborators': '1, 2',
                                                             'is_finished': False,
                                                             'team_leader_id': 1,
                                                             'hazard_category_id': 1,
                                                             }).json())
# некорректный запрос. объем работы меньше 0
print(requests.put('http://127.0.0.1:8080/api/jobs/10', json={'job_title': 'фыв работа',
                                                              'work_size': -1212,
                                                              'collaborators': '1, 2',
                                                              'is_finished': False,
                                                              'team_leader_id': 1,
                                                              'hazard_category_id': 1,
                                                              }).json())
print(requests.get('http://127.0.0.1:8080/api/jobs').json())

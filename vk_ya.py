import requests
import dload
from pprint import pprint
import os
import time
from tqdm import tqdm

vk_token = ''
ya_token = ''
user_id = input('Введите id пользователя: ')
count = input('Введите количество фото для загрузки: ')


def users_foto(id, token, count):
    url = 'https://api.vk.com/method/photos.getAll'
    params = {'owner_id': id,
              'extended': '1',
              'count': count,
              'no_service_albums': '0',
              'v': '5.131',
              'oauth': '1',
              'access_token': token}
    response = requests.get(url, params=params)
    for i in tqdm([i for i in range(int(count))]):
        time.sleep(0.5)
    return response.json()


class YaDisk:
    def __init__(self, token):
        self.token = token

    def get_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self.get_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(f'{user_id}/{filename}', 'rb'))
        response.raise_for_status()
        return response.status_code

    def new_folder_disk(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.put(upload_url, headers=headers, params=params)
        return response.json()

    def del_folder_disk(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        params = {"path": disk_file_path, "permanently": "true"}
        response = requests.delete(upload_url, headers=headers, params=params)
        if response.status_code == 204:
            print("Success")
        return response.status_code


id_shelfes = os.listdir(path=".")
if user_id in id_shelfes:
    print(f'Папка для пользователя id {user_id} уже есть. Обновим фотографии...')
else:
    os.mkdir(user_id)
    print(f'Создана папка для фотографий пользователя id {user_id}')

fotos = users_foto(user_id, vk_token, count)

foto_vk = {}
for news in fotos['response']['items']:
    if news['likes']['count'] not in foto_vk:
        foto_vk[news['likes']['count']] = [x['url'] for x in news['sizes'] if x['type'] == 'z']
    else:
        foto_vk[news['likes']['count'] + news['date']] = [x['url'] for x in news['sizes'] if x['type'] == 'z']

print(f'Получены ссылки для загрузки {len(foto_vk)} фотографий.')
dl = input(f'Для продолжения введите 1, для отмены 2: ')

if dl == '1':
    coun = 0
    for fotographies in foto_vk.items():
        url = ''.join(fotographies[1])
        filename = str(fotographies[0]) + '.jpg'
        dload.save(url, f'{user_id}/{filename}', overwrite=True)
        coun += 1
        for i in tqdm([i for i in range(1)]):
            time.sleep(0.5)
    new_list = [x for x in os.listdir(str(user_id)) if x[-4:] == '.jpg']
    print(f'Загружено {coun} фотографий в папку {user_id}. '
          f'Всего фотографий в папке {len(new_list)}. Грузим на яндекс-диск?')
    dy = input(f'Для продолжения введите 1, для отмены 2: ')
elif dl == '2':
    print('Ок, загрузим потом')
else:
    print('Что-то пошло не так')

new_list = [x for x in os.listdir(str(user_id)) if x[-4:] == '.jpg']
print(new_list)

if dy == '1':
    if __name__ == '__main__':
        disk = YaDisk(token=ya_token)
        disk.new_folder_disk(f'{user_id}')
        for files in new_list:
            disk.upload_file_to_disk(f'{user_id}/{files}', files)
        print("Фото загружены")

else:
    print('Ок, загрузим потом')

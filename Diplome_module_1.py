# -*- coding: utf-8 -*-

import os
import requests
from datetime import datetime
import tzlocal
import json


def upload_photos(ya_token, photos_likes, photos_url, photos_counter, sizes):
    folder_path = 'https://cloud-api.yandex.net/v1/disk/resources?path=%2Fvk_photos_test'
    headers_upload = {'Authorization': f'OAuth {ya_token}'}
    create_folder = requests.get(folder_path, headers=headers_upload)
    photos_dict = []
    if create_folder.status_code != 200:
        requests.put(folder_path, headers=headers_upload)
    for i in range(int(photos_counter)):
        file_name = photos_likes[i] + '.jpg'
        path = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path=%2Fvk_photos_test/{file_name}?&overwrite=true'
        upload_request = requests.get(path, headers=headers_upload)
        upload_url = upload_request.json()['href']
        upload_file = requests.put(upload_url, data=requests.get(photos_url[i]).content)
        if upload_file.status_code == 201:
            print(
                f'Файл {file_name} успешно записан на Яндекс Диск. Процент выполнения задачи: {round(100 / (int(photos_counter)) * (i + 1))}%', )
        else:
            print(f'Ошибка. Файл {file_name} не записан на Яндекс Диск. Код ошибки:', upload_file.status_code)
        size = str(sizes[i])
        photos_dict += [{'file_name': file_name, 'size': size}]
    file_path = os.path.join(os.getcwd(), 'json_file.json')
    with open(file_path, 'w') as file:
        json.dump(photos_dict, file)
    with open(file_path, 'rb') as file:
        path = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path=%2Fvk_photos_test/json_file.json?&overwrite=true'
        upload_request = requests.get(path, headers=headers_upload)
        upload_url = upload_request.json()['href']
        requests.put(upload_url, data=file)
    print('Выходной JSON-файл успешно записан на Яндекс Диск')
    return


class VkRequest:

    def __init__(self, access_token, owner_id):
        request_url = f'https://api.vk.com/method/photos.get?owner_id={owner_id}&album_id=profile&extended=1&rev=0&v=5.52&access_token={access_token}'
        self.request = requests.get(request_url).json()
        self.photo_url_list = []
        self.likes_list = []
        self.sizes = []
        return

    def photos_lists(self, photos_counter):
        for i in range(int(photos_counter)):
            if self.request['response']['items'][i].get('photo_2560') is not None:
                self.photo_url_list += [self.request['response']['items'][i].get('photo_2560')]
                self.sizes += ['2560']
            elif self.request['response']['items'][i].get('photo_1280') is not None:
                self.photo_url_list += [self.request['response']['items'][i].get('photo_1280')]
                self.sizes += ['1280']
            elif self.request['response']['items'][i].get('photo_807') is not None:
                self.photo_url_list += [self.request['response']['items'][i].get('photo_807')]
                self.sizes += ['807']
            elif self.request['response']['items'][i].get('photo_604') is not None:
                self.photo_url_list += [self.request['response']['items'][i].get('photo_604')]
                self.sizes += ['604']
            elif self.request['response']['items'][i].get('photo_130') is not None:
                self.photo_url_list += [self.request['response']['items'][i].get('photo_130')]
                self.sizes += ['130']
            else:
                self.photo_url_list += [self.request['response']['items'][i].get('photo_75')]
                self.sizes += ['75']
            like_count = str(self.request['response']['items'][i].get('likes').get('count'))
            if str(like_count) not in self.likes_list:
                self.likes_list += [like_count]
            else:
                date_timestamp = self.request['response']['items'][i].get('date')
                local_timezone = tzlocal.get_localzone()
                local_time = str(datetime.fromtimestamp(date_timestamp, local_timezone))
                local_time = local_time[0:10:1]
                self.likes_list += [str(like_count) + "_date_" + local_time]
        return self.likes_list, self.photo_url_list


def main_menu():
    vk_token = '14ecbd7414ecbd7414ecbd748d149baf43114ec14ecbd7474b10e46ed414ad017577f67'
    user_id = input('Введите id пользователя VK: ')
    yandex_token = input('Введите токен для доступа к Яндекс Диск: ')
    photos_counter_global = input('Введите количество фотографий для записи на Яндекс Диск: ')
    photos = VkRequest(vk_token, user_id)
    print()
    print('Ход выполнения программы:')
    print('Формирование списка фотографий для записи на Яндекс Диск')
    photos.photos_lists(photos_counter_global)
    photos_url = photos.photo_url_list
    photos_likes = photos.likes_list
    photos_sizes = photos.sizes
    print('Запись фотографий на Яндекс Диск: ')
    upload_photos(yandex_token, photos_likes, photos_url, photos_counter_global, photos_sizes)
    print()
    print('Все файлы успешно записаны на Яндекс Диск')
    return


if __name__ == "__main__":
    main_menu()

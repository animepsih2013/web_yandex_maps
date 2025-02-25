import os
import sys

import pygame
import requests
server_address = 'https://static-maps.yandex.ru/v1?'
api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

coor1 = 30.152669901990738
coor2 = 59.851508439897124
spn1 = 0.002
spn2 = 0.002

ll = f'{coor1},{coor2}&spn={spn1},{spn2}'
map_request = f"{server_address}ll={ll}&apikey={api_key}"
response = requests.get(map_request)

if not response:
    print("Ошибка выполнения запроса:")
    print(map_request)
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)

map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()
os.remove(map_file)
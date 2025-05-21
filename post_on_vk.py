import requests
from dotenv import load_dotenv


load_dotenv()
access_token = 'vk1.a.3xG_ivjvsmvw4_kilsOknSVaRKVSOjfUUMVSCC4mIKlHFbaPIp-FL0LO96KhaW6S3dRs3Gp7X9OdM411ZeeKNHBTwL4v19DSCw3IaeZ6CpZ1osFpRk7crVc4jPI4gaFL43EikbnOzORL7cCnDKX-cMtKQm1ZVHg2nDs23qG2n8Mlnbxmv7JwwFeyuFqrSF26cnzBx5idvBt6dsr4l24cRA'
group_id = '230572126'
message = 'Hello, VK!'

url = 'https://api.vk.com/method/wall.post'
params = {
    'owner_id': f'-{group_id}',  # Для группы используйте отрицательное значение
    'message': message,
    'access_token': access_token,
    'v': '5.199'  # Версия API
}

response = requests.post(url, params=params)
print(response.json())

from authx import AuthX, AuthXConfig
from fastapi import Response

config = AuthXConfig()
config.JWT_SECRET_KEY = "secret_key"
config.JWT_ACCESS_COOKIE_NAME = "token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)



def cookie(response: Response, user_id):

    token = security.create_access_token(uid=user_id)

    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)






   


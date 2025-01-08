from fastapi import HTTPException, Depends, security, status
from utils.scheme import SUser
from passlib.context import CryptContext
import logging
import colorlog
from core.config.config import auth_settings
from core.dependencies.dependencies import get_rmq_connection
from jose import jwt, JWTError
import aio_pika
import json
import httpx


SECRET_KEY = auth_settings.secret_key.get_secret_value()
ACCESS_TOKEN_EXPIRE_DAYS = 365
ALGORITHM = "HS256"


oauth2_scheme = security.OAuth2PasswordBearer(
    tokenUrl="http://localhost:8000/auth/service/api/v1/auth-login/",
)


pwd_password = CryptContext(schemes=["bcrypt"])




def get_logger() -> logging.Logger:
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    # Проверяем, есть ли уже обработчики, чтобы избежать дублирования
    if not log.handlers:
        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            datefmt=None,
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log




async def consume_data(queue_name: str, connection: aio_pika.RobustConnection):

    async with connection.channel() as channel:
        queue = await channel.declare_queue(queue_name, durable=True)

        async for message in queue.iterator():
            async with message.process():
                try:
                    body_str = message.body.decode("utf-8")
                    json_data = json.loads(body_str)
                    return json_data
                except json.JSONDecodeError as e:
                    get_logger.error("Error of decoding message %s:", e)
                    continue




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    connection: aio_pika.RobustConnection = Depends(get_rmq_connection),
) -> SUser:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8081/user/api/v1/get-user-by-username/{user_id}/"
            )
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ошибка взаимодействия с внешним сервисом: {e}",
        )

    queue_name = f"get-user-by-username-{user_id}"
    user_data = await consume_data(queue_name, connection)
    user_data["token"] = token
    user = SUser.parse_obj(user_data)
    return user




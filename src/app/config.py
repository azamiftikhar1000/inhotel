import os
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

class AbstractModel(BaseModel):
    """Schema Models

    Args:
        BaseModel (_type_): Inherits from Pydantic and specifies Config
    """

    class Config:
        orm_mode = True
        use_enum_values = True


class AbstractSettings(BaseSettings):
    """Settings Models

    Args:
        BaseModel (_type_): Inherits from Pydantic and specifies Config
    """

    class Config:
        env_file = ".env"



class DBSettings(AbstractSettings):
    """Database Settings

    Args:
        AbstractSettings (_type_): inherits Core settings.
    """

    name: str
    username: str
    password: str
    hostname: str
    port: int



class MilvusSettings(AbstractSettings):
    """Milvus Settings

    Args:
        AbstractSettings (_type_): inherits Core settings.
    """

    MILVUS_URI: str
    MILVUS_API_KEY: str
    MILVUS_ALIAS: str
    MILVUS_COLLECTION_NAME: str
    MILVUS_COLLECTION_DIMENSION: int


db_settings = DBSettings()
milvus_settings = MilvusSettings()


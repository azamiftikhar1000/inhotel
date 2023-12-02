from pymilvus import (
    FieldSchema,
    DataType,
    CollectionSchema,
    Collection,
    has_collection,
    connections,
)
from src.app.config import import settings

milvus_manager = None


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MilvusManager(metaclass=Singleton):
    def __init__(
        self, collection_name, dim, metric_type="IP", index_type="AUTOINDEX", top_k=3,
    ):
        self.collection_name = collection_name
        self.dim = dim
        self.metric_type = metric_type
        self.index_type = index_type
        self.top_k = top_k
        self.outputFields = [
            "id",
            "S3_URI",
            "meta_data",
            "filters",
        ]
        self.collection = Collection(self.collection_name)

    def drop_collection(self):
        self.collection.drop()
        print("\nDrop collection: {}".format(self.collection_name))

    def get_collection(self):
        self.load_collection()
        return self.collection

    def delete_entity(self, object_id):
        expr = f"id in {[object_id]}"
        response = self.collection.delete(expr)
        return response

    def query(self, id_list):
        res = self.collection.query(expr=f"id in {id_list}", output_fields=["id"],)
        return res

    def insert(
        self,
        id,
        embedding_vector,
        S3_URI,

    ):
        if grade_level is None:
            grade_level = []
        if len(embedding_vector) != self.dim:
            return False

        book = [
            {
                "id": id,
                "S3_URI": S3_URI,
        
            }
        ]
        result = self.collection.insert(book)
        self.collection.flush()
        return result

    def get_entity_count(self):
        print("\nThe number of entity:")
        print(self.collection.num_entities)

    def drop_index(self):
        self.collection.drop_index()
        print("\nDropped index successfully")

    def load_collection(self):
        self.collection.load()

    def release_collection(self):
        self.collection.release()

    def search(self, search_vectors, filters=None, top_k=None):
        """Search for similar vectors in the collection.
        Args:
            search_vectors (list): List of vectors to search for.
            filters (dict): Dict of filters to apply for a hybrid search.
            top_k (int): Number of vectors to return.
        """
        if not top_k:
            top_k = self.top_k

        if type(search_vectors) == str:
            search_vectors = [search_vectors]
        search_param = {
            "data": search_vectors,
            "anns_field": "embedding_vector",
            "param": {"metric_type": self.metric_type,},
            "limit": top_k,
            "consistency_level": "Strong",
        }

        # Hybrid search
        if filters:
            expr = []
            for key, value in filters.items():
                if value is not None:
                    if type(value) == str:
                        expr.append(f'filters["{key}"] == "{value}"')
                    if type(value) == int:
                        expr.append(f'filters["{key}"] == {value}')
                    elif type(value) == list:
                        # Future filters will use list of values (json_contains_any)
                        condition = " || ".join(
                            [f'json_contains(filters["{key}"], "{val}")' for val in value]
                        )
                        expr.append(f"({condition})")

            search_param["expr"] = " && ".join(expr)

        results = self.collection.search(
            **search_param, output_fields=self.outputFields
        )
        if len(results) > 0:
            return {"hits_data": results}
        else:
            return None


def create_collection(collection_name, dim):
    fields = [
        FieldSchema(
            name="id", dtype=DataType.INT64, description="int64", is_primary=True
        ),
        FieldSchema(
            name="S3_URI", dtype=DataType.VARCHAR, max_length=300, description="S3 URI"
        ),
        FieldSchema(
            name="meta_data",
            dtype=DataType.VARCHAR,
            max_length=10000,
            description="Meta Data",
        ),
        FieldSchema(
            name="embedding_vector",
            dtype=DataType.FLOAT_VECTOR,
            description="float embedding vector",
            dim=dim,
        ),
        FieldSchema(
            name="filters",
            dtype=DataType.JSON,
            description="Document fields for filtering",
        ),
    ]

    schema = CollectionSchema(fields=fields)

    collection = Collection(name=collection_name, schema=schema)
    print("\nCollection created:", collection_name)
    return collection


def create_index(collection, metric_type="IP", index_type="AUTOINDEX"):
    index_param = {"index_type": index_type, "metric_type": metric_type}
    collection.create_index(
        field_name="embedding_vector",
        index_params=index_param,
        index_name="embedding_vector_index",
    )
    print("\nCreated index:\n{}".format(collection.index().params))


def setup_milvus():
    global milvus_manager
    connections.connect(
        alias=settings.MILVUS_ALIAS,
        uri=settings.MILVUS_URI,
        token=settings.MILVUS_API_KEY,
    )

    if not has_collection(settings.MILVUS_COLLECTION_NAME):
        collection_object = create_collection(
            dim=settings.MILVUS_COLLECTION_DIMENSION,
            collection_name=settings.MILVUS_COLLECTION_NAME,
        )
        create_index(collection_object)

    if milvus_manager is None:
        milvus_manager = MilvusManager(
            settings.MILVUS_COLLECTION_NAME, settings.MILVUS_COLLECTION_DIMENSION
        )
    return milvus_manager

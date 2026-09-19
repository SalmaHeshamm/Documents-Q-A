from qdrant_client import QdrantClient, models
from stores.vectordb import VectorDBInterface, DistanceMetricEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_metric: str):

        self.client = None
        self.db_path = db_path
        self.distance_metric = None

        if distance_metric == DistanceMetricEnums.COSINE.value:
            self.distance_metric = models.Distance.COSINE

        elif distance_metric == DistanceMetricEnums.EUCLIDEAN.value:
            self.distance_metric = models.Distance.EUCLIDEAN

        elif distance_metric == DistanceMetricEnums.DOT.value:
            self.distance_metric = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info(f"Connected to QdrantDB at {self.db_path}")

    def disconnect(self):
        if self.client:
            self.client.close()
            self.logger.info("Disconnected from QdrantDB")

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str,
                                vector_size: int,
                                do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name)

        if not self.is_collection_exists(collection_name):
            _ = self.client.create_collection(
                                        collection_name=collection_name,
                                        vectors_config=models.VectorParams(size=vector_size, distance=self.distance_metric)
            )

            return True

        return False

    def insert_one(self, collection_name: str, text: list,
                         vector: list,
                         metadata: dict = None,
                         record_id: str = None):

        if not self.is_collection_exists(collection_name):
            logging.error(f"Collection {collection_name} does not exist.")
            return False

        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, "metadata": metadata}
                    )
                ]
            )
        except Exception as e:
            logging.error(f"Error inserting record: {e}")
            return False


        return True

    def insert_many(self, collection_name: str, texts: list,
                          vectors: list,
                          metadatas: list = None,
                          record_ids: list = None,
                          batch_size: int = 100):

        if metadatas is None:
            metadatas = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):

            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = [

                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadatas[x]
                    }
                ) 

                for x in range(len(batch_texts))
            ]


            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                logging.error(f"Error inserting batch: {e}")
                return False

        return True

    def query_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        results=  self.client.search(collection_name=collection_name,
                                    query_vector=vector,
                                    limit=limit)

        if not results or len(results) == 0:
            return None

        return [

            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload.get("text")
            })
            for result in results    
        ]
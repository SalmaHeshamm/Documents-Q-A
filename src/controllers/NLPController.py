from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from typing import List
from stores.llm import DocumentTypeEnum
import json

class NLPController(BaseController):

    def __init__(self, embedding_client, vectordb_client,
                 generation_client, template_parser):
        super().__init__()

        self.embedding_client = embedding_client
        self.vectordb_client = vectordb_client        
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str) -> str:
        return f"{project_id}_collection".strip().lower().replace(" ", "_")


    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)


    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info =  self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )


    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunk_ids: List[int], do_reset: bool = False):
        
        # get collection name
        collection_name = self.create_collection_name(project.project_id)

        # manage items
        texts = [ chunk.chunk_text for chunk in chunks]
        metadata = [ chunk.chunk_metadata for chunk in chunks]

        vectors = [
            self.embedding_client.embed_text(text=text, document_type= DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        # create collction if not exists
        _ = self.vectordb_client.create_collection(collection_name=collection_name,
                                                   do_reset=do_reset,
                                                   vector_size=self.embedding_client.embedding_size)

        # insert items into collection
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts= texts,
            vectors=vectors,
            metadatas=metadata,
            record_ids=chunk_ids
        )

        return True


    def query_vector_db_collection(self, project: Project, query_text: str, limit: int = 5):
        collection_name = self.create_collection_name(project.project_id)

        query_vector = self.embedding_client.embed_text(text=query_text, document_type= DocumentTypeEnum.QUERY.value)

        if not query_vector or len(query_vector) == 0:
            return False

        results = self.vectordb_client.query_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        if not results or len(results) == 0:
            return False
        
        return results


    def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = self.query_vector_db_collection(
            project=project,
            query_text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history


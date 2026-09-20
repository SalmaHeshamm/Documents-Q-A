from fastapi import FastAPI, APIRouter, Depends, UploadFile, logger, status, Request
from fastapi.responses import JSONResponse
from .schemes.nlp import PushRequest, QueryRequest
from models import ProjectModel, ChunkModel
from controllers import NLPController
from models import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["api_v1", "nlp"])

@nlp_router.post("/index/push/{project_name}")
async def index_project(request: Request, project_name: str, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_name=project_name)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value,
            }
        )

    nlp_controller = NLPController(
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vector_db(project=project, chunks=page_chunks,
                                                          chunk_ids=chunk_ids, do_reset=push_request.do_reset)

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content = {
                    "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_FAILED.value,
                }
            )

        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content = {
            "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

        
@nlp_router.get("/index/info/{project_name}")
async def get_project_index_info(request: Request, project_name: str):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_name=project_name)

    nlp_controller = NLPController(
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content = {
            "signal": ResponseSignal.VECTOR_DB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/query/{project_name}")
async def query_project_index(request: Request, project_name: str, query_request: QueryRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_name=project_name)

    nlp_controller = NLPController(
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        template_parser = request.app.template_parser
    )

    results = nlp_controller.query_vector_db_collection(project=project,
                                                        query_text=query_request.text,
                                                        limit=query_request.limit)

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                "signal": ResponseSignal.QUERY_VECTOR_DB_FAILED.value,
            }
        )

    return JSONResponse(
        content = {
            "signal": ResponseSignal.QUERY_VECTOR_DB_SUCCESS.value,
            "results": [result.dict() for result in results]
        }
    )


@nlp_router.post("/index/answer/{project_name}")
async def answer_Rag(request: Request, project_name: str, query_request: QueryRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_name=project_name)

    nlp_controller = NLPController(
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        template_parser = request.app.template_parser
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(project= project,
                                                                           query= query_request.text,
                                                                           limit= query_request.limit) 

    if not answer:
        return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content = {
                        "signal": ResponseSignal.RAG_ANSWER_ERROR.value,
                    }
        )

    return JSONResponse(
        content = {
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )
    

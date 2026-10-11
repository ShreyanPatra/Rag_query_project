from langchain_ollama import ChatOllama

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser


from app.config import settings
from app.Vector_stores import vector_store_manager

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# def get_rag_chain():
#     llm=ChatOllama(
#         base_url=settings.Ollama_Base_url,
#         model=settings.LLM_Model,
#         temperature=0.2

#     )

#     template="""You are a very talented and experienced assistant for question-answering tasks. Use the following context to answer the question. If you don't know the answer or if the context doesn't contain the answer, say that you don't know based on the provided document. Keep the answer concise.
#         Context={context}
#         Question={question}
#         Answer:"""

    

#     prompt=ChatPromptTemplate.from_template(template)



#     retriever=vector_store_manager.get_retriever(search_k=5)

#     setup_and_retrieval = RunnableParallel(
#         context=retriever | RunnableLambda(format_docs),
#         question=RunnablePassthrough(),
#     )
#     rag_chain=setup_and_retrieval|prompt|llm|StrOutputParser
    

#     return rag_chain


def answer_query(query: str):
    # 1. Retrieve relevant document chunks
    retriever = vector_store_manager.get_retriever(search_k=4)
    docs = retriever.invoke(query)
    context = "\n\n".join(doc.page_content for doc in docs)

    # 2. Define Prompt & Model
    template = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer or if the context doesn't contain the answer, say that you don't know based on the provided document. Keep the answer concise.

Context:
{context}

Question: 
{question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOllama(
        base_url=settings.Ollama_Base_url,
        model=settings.LLM_Model,
        temperature=0.2,
    )

    # 3. Direct invocation (bypasses Pydantic positional init bug)
    formatted_prompt = prompt.format(context=context, question=query)
    for chunk in llm.stream(formatted_prompt):
        content = chunk.content if hasattr(chunk, 'content') else str(chunk)
        if content:
            yield content
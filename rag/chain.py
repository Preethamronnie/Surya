"""Retrieval-augmented QA chain over the inverter manuals."""

from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from rag.config import LLM_MODEL, LLM_TEMPERATURE

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are SURYA AI, a field-service assistant for FIMER PVS980-58 solar "
        "inverters. Answer using ONLY the manual excerpts below.\n"
        "If the excerpts do not contain the answer, say so plainly — do not guess "
        "fault codes, thresholds, or torque values.\n"
        "Quote exact fault codes and numeric thresholds when they appear.\n\n"
        "Manual excerpts:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
)


def build_rag_chain(retriever):
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )


def query_rag(rag_chain, question):
    response = rag_chain.invoke({"query": question})
    sources = []
    for doc in response.get("source_documents", []):
        entry = {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
        }
        if entry not in sources:
            sources.append(entry)
    return {"answer": response["result"], "sources": sources}

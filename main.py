import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

# Fetch API keys from environment variables
gemini_api = os.getenv("GEMINI_API_KEY")
inference_api_key = os.getenv("HF_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat history and retrieval chain initialization
chat_history = []

def create_db():
    embedding = HuggingFaceInferenceAPIEmbeddings(
        api_key=inference_api_key, model_name="sentence-transformers/all-MiniLM-l6-v2"
    )
    vectorStore = FAISS.load_local("faiss_index_law", embedding, allow_dangerous_deserialization=True)
    return vectorStore

def create_chain(vectorStore):
    model = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly Law AI Bot. You always greet the user well and treat respectfully. You have knowledge related to Indian Constitution. You have to give detailed answer on any law for atleast 500 words. \n Note: Only respond as Law AI, no other character. ALWAYS START Your Answer Directly, without mentioning your name. Do Not add extra Spaces. Always write in third person. Always make your answer clear and complete. Answer only if a relevant question is asked, and Answer only if you know the answer, otherwise don't answer with unknown or vague information. Take care of the ethics. Answer the user's questions based on the relevant sentences: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )

    retriever = vectorStore.as_retriever(search_kwargs={"k": 10})

    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above chat history, generate a search query to look up in order to get information relevant to the conversation")
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        chain
    )

    return retrieval_chain

def process_chat(chain, question, chat_history):
    response = chain.invoke({
        "chat_history": chat_history,
        "input": question,
    })
    return response.get("answer")

vectorStore = create_db()
chain = create_chain(vectorStore)

# Pydantic model for API request/response
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    global chat_history
    user_input = request.question

    try:
        response = process_chat(chain, user_input, chat_history)
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Run the application (optional for Jupyter Notebook environments)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
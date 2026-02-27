import os
import sys
import logging
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from llama_cpp import Llama

# Local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from emotional_state import EmotionalAnalyzer, EmotionalState
from rag_engine import RAGEngine
from context_manager import ContextManager
from post_processor import PostProcessor

# Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "/opt/neuro-lite/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf")
DB_PATH = os.getenv("DB_PATH", "/opt/neuro-lite/data/knowledge.db")
N_CTX = 2048 # Limit context for RAM
N_THREADS = 3 # Optimal for i3 (Dual Core with HT)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("NeuroLite")

# Global State
llm: Optional[Llama] = None
rag_engine: Optional[RAGEngine] = None
emotional_analyzer: Optional[EmotionalAnalyzer] = None
context_manager: Optional[ContextManager] = None

# Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm, rag_engine, emotional_analyzer, context_manager
    
    logger.info("Initializing Neuro-Lite Server...")
    
    # 1. Init LLM
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model not found at {MODEL_PATH}")
        raise RuntimeError("Model file missing.")
    
    logger.info("Loading LLM into memory (CPU Only)...")
    try:
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            n_batch=512,
            verbose=False,
            use_mlock=True # Prevent swapping if possible
        )
        logger.info("LLM Loaded.")
    except Exception as e:
        logger.critical(f"Failed to load LLM: {e}")
        raise

    # 2. Init Components
    rag_engine = RAGEngine(DB_PATH)
    emotional_analyzer = EmotionalAnalyzer()
    
    # System Prompt
    sys_prompt = (
        "You are Neuro-Lite, a professional technical support assistant. "
        "You are efficient, polite, and factual. "
        "Do not hallucinate. If you do not know the answer, admit it professionally."
    )
    context_manager = ContextManager(system_prompt=sys_prompt)

    yield

    # Cleanup
    logger.info("Shutting down Neuro-Lite Server...")

app = FastAPI(title="Neuro-Lite", lifespan=lifespan)

# Request Schema
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

# API Endpoints
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not llm:
        raise HTTPException(status_code=503, detail="Model not loaded")

    user_msg = request.message
    
    # 1. Emotional Analysis (Sync, fast)
    emotion, persona_modifier = emotional_analyzer.analyze(user_msg)
    
    # 2. RAG Retrieval (Sync, fast)
    context_docs = rag_engine.search(user_msg)
    
    # 3. Construct Prompt
    # Inject RAG context
    rag_context = ""
    if context_docs:
        rag_context = "Relevant Knowledge Base Entries:\n"
        for doc in context_docs:
            rag_context += f"- Q: {doc['question']} A: {doc['answer']}\n"
        rag_context += "\n"
    else:
        rag_context = "No direct knowledge base entry found. Rely on general knowledge.\n"

    # Inject Persona Modifier
    current_sys_prompt = f"{context_manager.system_prompt}\n{persona_modifier}\n{rag_context}"
    
    # Update Context Manager (Memory)
    context_manager.add_message("user", user_msg)
    
    # Prepare messages for LLM
    messages = context_manager.get_full_context()
    # Override the system prompt in the list with the augmented one
    for m in messages:
        if m['role'] == 'system':
            m['content'] = current_sys_prompt
            break

    # 4. Inference (Async Stream)
    async def generate_stream():
        full_response = ""
        try:
            # llama-cpp-python creates a generator
            # We run the blocking call in an executor to not block event loop
            loop = asyncio.get_event_loop()
            
            # Function to call
            def infer():
                return llm.create_chat_completion(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=256, # Keep low for speed
                    stream=True
                )

            stream = await loop.run_in_executor(None, infer)
            
            for chunk in stream:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    token = delta['content']
                    full_response += token
                    yield f"data: {token}\n\n"
            
            # 5. Post Processing (After stream completes)
            # We apply this to the final text in the context manager, 
            # but for SSE we can't modify already sent text.
            # To strictly follow post-processing rules, we should ideally buffer, 
            # but for "Fast" perception we stream raw tokens, 
            # then we apply logic to the stored history.
            
            # Apply Post Processing for history storage
            processed_response = PostProcessor.process(full_response, persona_modifier)
            
            # If post processor added empathy prefix, we can't send it to client now (already streamed).
            # COMPROMISE: Post processor logic is applied to context history for future turns.
            # We log the diff for debugging.
            if processed_response != full_response:
                logger.info(f"Post-processed history: Added empathy/formatting.")
            
            context_manager.add_message("assistant", processed_response)
            
            # Send End signal
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield "data: [ERROR]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'webui', 'index.html')
    if not os.path.exists(index_path):
        return "<html><body><h1>WebUI not found.</h1></body></html>"
    with open(index_path, 'r') as f:
        return f.read()

# Run with: uvicorn main_server:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

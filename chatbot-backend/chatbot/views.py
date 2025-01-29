import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM
model = ChatOpenAI(
    model="gpt-4o-mini",  
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Load JSON Data
with open("chatbot/scraped_data/event_cards_with_text.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract relevant text and URLs
documents = []
for entry in data:
    content = f"Title: {entry['title']}\nDate: {entry['date']}\nLocation: {entry['location']}\nURL: {entry['url']}\nInfo: {entry['page_text'][:500]}"  # Limit text size
    documents.append(content)

# Split text for better vector search
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_text("\n".join(documents))

# Convert documents to vectors for retrieval
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = FAISS.from_texts(texts, embeddings)

# Load retriever
retriever = vectorstore.as_retriever()

# Set up search functionalities for the model
search = DuckDuckGoSearchResults()

def fetch_latest_information(query):
    search_query = f"{query} Tomorrowland 2025"
    results = search.run(search_query)
    return results

# Prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
     You are a helpful professional in the music entertainment industry. 
     You will help answer all the questions about the music event Tomorrowland with the most up-to-date information available.
     Use retrieved data and live search results to answer accurately.
    """),
    ("human", "User question: {question}\n\nRetrieved Knowledge Base Info: {retrieved_data}\n\nLatest Search Results: {search_results}")
])

# Set up chatbot with memory
memory = MemorySaver()
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    response = model.invoke(state['messages'])
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}} # Thread configuration

@csrf_exempt # Exempt view from CSRF for dev/test as it is safely hosted locally
def chat(request):
    if request.method == 'POST':
        try:
            user_input = request.POST.get('query', '')

            if not user_input:
                return JsonResponse({'error': 'No query provided'}, status=400)
            
            # Retrieve data from the knowledge base
            retrieved_data = retriever.invoke(user_input)

            # Get search results
            search_results = fetch_latest_information(user_input)

            # Format the prompt with updated context
            messages = prompt_template.format_messages(
                question=user_input, 
                retrieved_data="\n".join([doc.page_content for doc in retrieved_data[:]]),  # Limit to 4 most relevant results
                search_results=search_results
            )

            # Generate response
            response = app.invoke({"messages": messages}, config)

            # Extract the AIMessage object
            ai_message = response["messages"][-1]
            ai_message_dict = ai_message.dict()

            return JsonResponse({'response': ai_message_dict['content']})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
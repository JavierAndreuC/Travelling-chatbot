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

# Set up search functionalities for the model
search = DuckDuckGoSearchResults()

def fetch_latest_information(query):
    search_query = f"{query} Tomorrowland 2025"
    results = search.run(search_query)
    return results

# Prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
    You are a smart and helpful Flight and Travel Assistant chatbot. Your primary role is to help users with their travel-related needs, including finding flights, tracking delays, checking visa and entry requirements, and recommending hotels and car rentals.

    You provide real-time and accurate responses by fetching data from reliable APIs such as Skyscanner, FlightAware, and Amadeus. If a user asks for flight prices, you check Skyscanner for the best deals. If they need live flight tracking, you use FlightAware. For visa and travel restrictions, you fetch the latest updates from Amadeus.

    Your responses should be concise, clear, and traveler-friendly. You can also provide additional tips on airport navigation, baggage policies, and travel hacks when relevant.

    When a user provides a location, always confirm if they need information for departures, arrivals, or general airport guidance. If flight details are missing, politely ask for the date, airline, and route to provide better assistance.
     """),
    ("human", "User question: {question}")
])

############ Set up chatbot with memory ############
memory = MemorySaver()
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    response = model.invoke(state['messages'])
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}} # Thread configuration

################################################

@csrf_exempt # Exempt view from CSRF for dev/test as it is safely hosted locally
def chat(request):
    if request.method == 'POST':
        try:
            user_input = request.POST.get('query', '')

            if not user_input:
                return JsonResponse({'error': 'No query provided'}, status=400)
            
            # Get search results
            search_results = fetch_latest_information(user_input)

            # Format the prompt with updated context
            messages = prompt_template.format_messages(
                question=user_input, 
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
Here is my Tomorrowland chatbot that you asked for. It should all work well locally.

The backend is in Django as you asked and it has a "env" folder in it which is the virtual environment I made to handle all the dependencies so as long as you make that the working environment for the backend it shoudl run well. It also has e .env file within the "chatbot" directory that contains the value for the "OPENAI_API_KEY", which is currently a placeholder, so relpace with your own API key to be able to use it.
The frontend I made using React, it has the package files so as long as you are in that directory and run "npm install" it shoudlw work fine.
Finally the web scraper. I used them to retreive online data and use it for a RAG implementation. It also has a "env" folder in it, like the backend folder, so you can make that the working environment for the directory and it should work fine if you want to see how the web scrapers work.

The main work with the LLM chatbot is done in the 'views.py' file in 'chatbot-backend/chatbot' directory.
All the frontend is a single component in the 'chatbot-frontend/src/components/' directory.

I hope you like what I did in this project!

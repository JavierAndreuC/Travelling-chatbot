✈️ Flight and Travel Assistant Chatbot

This is a Flight and Travel Assistant Chatbot that helps users find flights, track delays, check visa and entry requirements, and recommend hotels and car rentals. The chatbot integrates with real-time APIs like Amadeus, FlightAware, and Skyscanner to provide accurate travel information.

🚀 Features
	•	🛫 Flight Search & Booking – Find flights using the Amadeus API.
	•	⏳ Real-time Flight Tracking – Track flights in real-time using FlightAware.
	•	🌍 Visa & Travel Restrictions – Get entry requirements for destinations.
	•	🏨 Hotel & Car Rental Recommendations – Discover accommodations and transport options.
	•	🛄 Airport & Baggage Information – Get guidance on airport navigation and policies.

🛠️ Installation

1️⃣ Clone the Repository

```
git clone https://github.com/JavierAndreuC/Travelling-chatbot.git
cd flight-travel-chatbot
```
2️⃣ Create a Virtual Environment (Python Backend)
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3️⃣ Install Dependencies
```
pip install -r requirements.txt
```
4️⃣ Set Up Environment Variables

Create a .env file in the root directory and add your API credentials:
```
OPENAI_API_KEY=your_openai_api_key
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
```

Ensure your .env file is ignored in .gitignore to prevent exposing credentials.

🔥 Running the Chatbot
```
python main.py
```
To run the frontend navigate to the frontend directory and start the app:
```
cd chatbot-frontend
npm install
npm run dev  # If using Vite
```
🛜 API Integration

Amadeus API
	•	Endpoint: https://test.api.amadeus.com
	•	Used for:
	•	Flight Offers
	•	Visa & Entry Requirements
	•	Hotel & Car Rentals

FlightAware API
	•	Used for live flight tracking.

Skyscanner API
	•	Used for flight pricing and booking.

📂 Project Structure
```
/flight-travel-chatbot
│── chatbot-backend/
│   ├── main.py  # Backend logic
│   ├── views.py  # API requests
│   ├── config.py  # Configuration settings
│── chatbot-frontend/
│   ├── src/
│   ├── App.tsx  # React Frontend
│── .env  # API credentials (ignored by Git)
│── .gitignore
│── README.md  # Project documentation
│── requirements.txt # Project dependencies
```
🛠️ Future Enhancements
	•	📡 Add support for additional APIs (Google Maps, Uber, etc.)
	•	📱 Create a mobile-friendly UI for better user experience.
	•	🧠 Enhance AI responses using GPT-based contextual understanding.

👨‍💻 Contributing
	1.	Fork the repo
	2.	Create a new branch
	3.	Make your changes
	4.	Submit a pull request

📜 License

This project is licensed under the MIT License.

Let me know if you’d like any modifications to better fit your project! 🚀

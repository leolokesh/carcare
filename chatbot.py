import streamlit as st
import requests
from dotenv import load_dotenv
import os
import io
import base64
from PIL import Image
import logging
import PIL
import time
 
# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="5K Car Care Assistant",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="auto",
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# Google Generative AI API key from .env
#api_key = os.getenv("GOOGLE_API_KEY")
 
# Check if API key exists
#if not api_key:
#    st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")
#    st.stop()

def get_zai_fi_response(question, max_retries=3, retry_delay=2):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 250,
    }

    system_instruction = """You are an AI assistant for 5K Car Care. Provide concise, accurate information about our services and products. Be polite, friendly, and professional. Focus only on 5K Car Care offerings.

Key Information:

1. Services:
   a) Car Wash: RO Water Wash, Exterior Car Spa, Sanitizer Foam Car Spa
   b) Anti-Bacteria Treatment: Interior cleaning, Odor removal, AC disinfection
   c) Teflon Coating: Protects paint, prevents rust
   d) Ceramic Coating: Long-lasting paint protection
   e) Interior Enrichment: Seat cover customization, dashboard cleaning
   f) Car AC Services: Gas refilling, cooling restoration
   g) Car Detailing: Exterior/interior services, underbody coating
   h) Special Treatments: Engine room cleaning, rat repellent, wiper smoother

2. Booking:
   - Ask for preferred date, time, location, service type, and vehicle details
   - Electronic City branch available

3. Franchise Information:
   - Explain franchise-based business model
   - Highlight benefits of choosing 5K Car Care
   - Provide steps to apply for a franchise

4. Contact:
   - Phone: +91 91500 78405 (Electronic City branch)
   - Email: 5kcc.bangaloreec@gmail.com
   - Address: 15th Cross, Behind Village Hyper Market, Neeladri Road, Electronic City

5. About Us:
   - Founded in 2012 in Coimbatore
   - 150+ branches, 30 million+ customers
   - Awards: "IKON of Bangalore City 2019", "ISO 9001:2015 Certification"
   - Open 365 days, 10 AM to 7 PM

6. Locations:
   - Multiple branches in Tamil Nadu, Karnataka, Kerala
   - Provide nearest branch based on user's location

Additional Features:
- Offer to share customer reviews/testimonials
- Mention any ongoing promotions or offers
- Provide emergency assistance information if asked
- Offer to connect with a live agent for complex queries

Respond to queries concisely and accurately. If information is not available, politely state so. Always focus on 5K Car Care's services and avoid mentioning competitors."""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": system_instruction}]
            },
            {
                "role": "model",
                "parts": [{"text": "Understood. I'm ready to assist with 5K Car Care information."}]
            },
            {
                "role": "user",
                "parts": [{"text": question}]
            }
        ],
        "generationConfig": generation_config
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=AIzaSyBhYT2O9QyISU7_9319oJWLIgIihf3sLX4"
    headers = {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"API Response Status Code: {response.status_code}")
            logger.info(f"API Response Content: {response.text[:500]}...")  # Log first 500 characters of response
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data and "candidates" in response_data and len(response_data["candidates"]) > 0:
                    return response_data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.warning("No valid response in API result")
                    return get_fallback_response(question)
            else:
                logger.error(f"API Error: Status Code {response.status_code}, Response: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return get_fallback_response(question)

        except requests.RequestException as e:
            logger.error(f"Request Exception: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                return get_fallback_response(question)

    return get_fallback_response(question)

def get_fallback_response(question):
    fallback_info = {
        "car_wash": ["RO Water Wash", "Exterior Car Spa", "Sanitizer Foam Car Spa"],
        "services": ["Car Wash", "Anti-Bacteria Treatment", "Teflon Coating", "Ceramic Coating", "Interior Enrichment", "Car AC Services", "Car Detailing", "Special Treatments"],
        "contact": {
            "phone": "+91 91500 78405",
            "email": "5kcc.bangaloreec@gmail.com",
            "address": "15th Cross, Behind Village Hyper Market, Neeladri Road, Electronic City"
        },
        "hours": "Open 365 days, 10 AM to 7 PM"
    }

    question_lower = question.lower()
    if "car wash" in question_lower or "wash service" in question_lower:
        services = ", ".join(fallback_info["car_wash"])
        return f"5K Car Care offers the following car wash services: {services}. For more details or to book a service, please contact us."
    elif "service" in question_lower:
        services = ", ".join(fallback_info["services"])
        return f"5K Car Care offers a range of services including: {services}. For specific information on any service, please ask or contact us directly."
    elif "contact" in question_lower or "phone" in question_lower or "email" in question_lower:
        contact = fallback_info["contact"]
        return f"You can contact 5K Car Care at:\nPhone: {contact['phone']}\nEmail: {contact['email']}\nAddress: {contact['address']}"
    elif "hour" in question_lower or "time" in question_lower:
        return f"5K Car Care is {fallback_info['hours']}."
    else:
        return "I apologize, but I'm having trouble providing specific information at the moment. 5K Car Care offers various services including car wash, detailing, and coating. For the most up-to-date information, please contact us directly at +91 91500 78405 or visit our website."
 
def resize_image(image_path, max_size=(1000, 1000)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
 
def hide_streamlit_menu():
    st.markdown(
        """
<style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
</style>
        """,
        unsafe_allow_html=True
    )

def add_custom_css():
    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            height: 100%;
            width: 100%;
            background: linear-gradient(135deg, #0B204C, #FFFFFF);
        }
        .stApp {
            margin: 0;
            padding: 0;
            height: 100vh;
        }
        .logo-container {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            position: absolute;
            top: -50px;
            left: -370px;
        }
        .logo-container img {
            margin-bottom: 8px;
            height:30px;
            width: 40px;
        }
        .logo-container .tagline {
            color: #3498db;
            font-style: italic;
        }
        .center-logo {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        ::-webkit-scrollbar {
            width: 12px;
        }
        ::-webkit-scrollbar-track {
            background: #f0f0f0;
        }
        ::-webkit-scrollbar-thumb {
            background-color: red;
            border-radius: 10px;
            border: 3px solid #f0f0f0;
        }
       .chat-container {
            display: flex;
            flex-direction: column;
            gap: 20px;  /* Increased gap between messages */
            margin-bottom: 20px;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 20px;
            display: inline-block;
            max-width: 70%;
            color: #000000;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #e6f3ff;
            align-self: flex-end;
            margin-left: 70%;
            margin-bottom: 20px;  /* Add space below user messages */
        }
        .assistant-bubble {
            background-color: #f0f0f0;
            align-self: flex-start;
            margin-right: 30%;
            margin-top: 10px; 
            margin-bottom: 20px /* Add space above assistant messages */
        }
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 50px;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    add_custom_css()
    hide_streamlit_menu()

    # Load and display the ZAi-Fi logo
    zai_fi_logo_path = "zaifilogo.png"
    try:
        logo = Image.open(zai_fi_logo_path)
        max_width = 100
        if logo.width > max_width:
            ratio = max_width / logo.width
            new_size = (max_width, int(logo.height * ratio))
            logo = logo.resize(new_size, Image.LANCZOS)
        logo = logo.convert('RGB')
        buf = io.BytesIO()
        logo.save(buf, format="JPEG")
        st.markdown(
            f"""
            <div class="logo-container">
                <img src="data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"
                     alt="ZAi-Fi Logo"
                     style="width: 100px; height: auto;">
                <span class="tagline">Empowering Intelligence, everywhere</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"An error occurred while loading the ZAi-Fi logo: {str(e)}")

    # Display the 5K Car Care logo
    car_care_logo_path = "5kCarCare.png"
    try:
        car_care_logo = Image.open(car_care_logo_path)
        max_width = 200
        if car_care_logo.width > max_width:
            ratio = max_width / car_care_logo.width
            new_size = (max_width, int(car_care_logo.height * ratio))
            car_care_logo = car_care_logo.resize(new_size, Image.LANCZOS)
        car_care_logo = car_care_logo.convert('RGB')
        buf = io.BytesIO()
        car_care_logo.save(buf, format="PNG")
        st.markdown(
            f"""
            <div class="center-logo">
                <img src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
                     alt="5K Car Care Logo"
                     style="width: 200px; height: auto;">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"An error occurred while loading the 5K Car Care logo: {str(e)}")

    st.title("5K Car Care Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a placeholder for the chat container
    chat_container = st.empty()

    # Function to display all messages
    def display_messages():
        with chat_container.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
                st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Display initial messages
    display_messages()

    if prompt := st.chat_input("What is your question?"):
        # Add the user message to the session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Update the display with the new user message
        display_messages()
        
        loading_placeholder = st.empty()
        with loading_placeholder:
            st.markdown('<div class="loading"><div class="loading-spinner"></div></div>', unsafe_allow_html=True)
            response = get_zai_fi_response(prompt)
        
        # Remove the loading spinner
        loading_placeholder.empty()

        # Add the assistant's response to the session state
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Update the display with the new assistant message
        display_messages()

if __name__ == "__main__":
    main()
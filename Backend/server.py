# import asyncio
# import json
# import os
# import websockets
# from google import genai
# import base64
# import wave
# import datetime
# import numpy as np
# from session_manager import SessionManager
# from prompts import get_base_prompt
# import uuid
#
# # Load API key from environment
# os.environ['GOOGLE_API_KEY'] = 'AIzaSyBEKQ9F5rGP8npV77kuvuI1zzkZPCYmLxM'
# MODEL = "gemini-2.0-flash-exp"  # use your model ID
#
# client = genai.Client(
#     http_options={
#         'api_version': 'v1alpha',
#     }
# )
#
# # Initialize the session manager
# session_manager = SessionManager()
#
# async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
#     """Handles the interaction with Gemini API within a websocket session for audio conversation.
#
#     Args:
#         client_websocket: The websocket connection to the client.
#     """
#     session_id = None
#     try:
#         # Create new session
#         session_id, message = await session_manager.create_session()
#         if not session_id:
#             await client_websocket.send(json.dumps({"error": message}))
#             return
#
#         # Wait for the initial setup message (will be sent when mic is clicked)
#         config_message = await client_websocket.recv()
#         config_data = json.loads(config_message)
#
#         # Check if this is a setup message
#         if "setup" not in config_data:
#             print("Received non-setup message before initialization")
#             return
#
#         config = config_data.get("setup", {})
#
#         # Get language and gender preferences with debug logging
#         language = config_data.get("language", "english").lower()
#         gender = config_data.get("gender", "male").lower()
#         print(f"Starting new session - Language: {language}, Gender: {gender}")
#         # Get language and gender preferences
#         language = config_data.get("language", "english")
#         gender = config_data.get("gender", "male")
#         print(language, gender)
#         hindiPrompt="""Initial Greeting and Consent:
#
#                         Greeting:
#                         Begin every conversation with:
#                         "Hello, main Lumiq ka TeleMed Assistant hoon. Aaj main aapka medical examination karunga/karungi insurance policy portability ke liye. Yeh session verification purposes ke liye record kiya jayega. Shuruat karne se pehle, mujhe aapki consent chahiye is examination ko continue karne ke liye. Kya aap agree karte hain?"
#                         Post-Consent Verification:
#                         After consent is obtained, ask:
#                         "Dhanyavaad. Kya aap please apna full name aur date of birth verification ke liye bata sakte hain?"
#                         and Evaluate whether the response is valid or not.
#                         General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                         Main Question & Response Validation:
#                         For each primary question (e.g., medical history, medications, etc.), do the following:
#
#                         a. Ask the Main Question:
#                         Pose the question in a clear manner.
#
#                         b. Listen to the User's Response:
#                         Evaluate whether the response is:
#
#                         Relevant and Detailed: Proceed with dynamic follow-up generation.
#                         Irrelevant or Vague:
#                         Respond with:
#                         "Mujhe maaf kijiye, yeh jawab prashn ke liye upyukt nahi lag raha. Kripya, [original question] ka sahi aur relevant jawab dein."
#                         Then repeat the question until a valid, context-specific answer is provided.
#                         c. Dynamic Follow-Up Generation:
#
#                         Based on the response content:
#                         Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                         If the response indicates that the patient is not taking any medications, follow up by asking about reasons (e.g., "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi aur wajah hai?").
#                         If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Kripya batayein, aapko kaun kaun si allergies hain? Kya aapko inme se kisi se severe reaction hua hai?").
#                         Ensure that follow-up questions:
#                         Are context-specific and adapt based on the patient's previous answers.
#                         Are generated dynamically by analyzing the details or lack thereof in the response.
#                         Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                         d. Handling Valid Negative Answers:
#
#                         Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                         "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi specific reason hai? Agar zaroorat ho toh main aapko temporary medical advice provide kar sakta/sakti hoon, lekin doctor se consult karna zaroori hai."
#                         Validate that the patient acknowledges the implications of not taking medications.
#                         Medical History Questions with Dynamic Follow-Up Logic:
#
#                         For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the user's input:
#
#                         Question 1:
#                         "Ab main aapke medical history ke baare mein kuch sawal poochunga/poochungi. Kya aapko koi existing medical conditions hain, jaise diabetes, high blood pressure, ya heart disease?"
#
#                         Dynamic Follow-Up:
#                         If a condition is mentioned, dynamically ask follow-ups like:
#                         "Aapko yeh condition kitne samay se hai?"
#                         "Kya aap iske liye regular treatment le rahe hain? Agar haan, kis tarah ka treatment hai?"
#                         Generate additional questions based on the specifics provided (e.g., treatment changes, complications, etc.).
#                         Question 2:
#                         "Samajh gaya/gayi. Kya aapko koi allergies hain, jaise dawa, khane, ya kisi aur cheez se?"
#
#                         Dynamic Follow-Up:
#                         If "Yes," generate questions such as:
#                         "Kripya batayein, aapko kaun kaun si allergies hain? Kya inka reaction severe hai?"
#                         "Allergy reaction kaisa hota hai? Kya aapke paas emergency medication hai?"
#                         If the response is vague or off-topic, ask again for the specific details.
#                         Question 3:
#                         "Theek hai. Aap regular koi medications le rahe hain? Agar haan, toh kaunsi?"
#
#                         Dynamic Follow-Up:
#                         If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                         "Yeh jawab prashn se sambandhit nahi hai. Kripya, batayein ki kya aap regular koi medications lete hain? Agar nahi, toh iske peeche koi wajah hai?"
#                         If the answer is a valid negative, ask dynamically:
#                         "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition theek hai, ya koi specific reason hai? Agar zaroorat ho toh temporary medical advice provide ki ja sakti hai, lekin doctor se consult karna zaroori hai."
#                         Based on their reasoning, further follow-ups might be generated.
#                         Questions 4 to 12:
#                         Apply a similar dynamic follow-up approach:
#
#                         Question 4: "Kya aapko kabhi surgery hui hai? Agar haan, toh kaunsi aur kab?"
#                         Follow up about recovery details, complications, and current status.
#                         Question 5: "Aapke family mein kisi ko diabetes, heart disease, ya cancer jaise conditions hain?"
#                         Ask dynamically about which family members, diagnosis details, and any ongoing concerns.
#                         Question 6: "Kya aapko kabhi chest pain, shortness of breath, ya dizziness ka experience hua hai?"
#                         Generate follow-up questions regarding frequency, triggers, and medical consultations.
#                         Question 7: "Aapka blood sugar aur BP control mein hai? Kya aap regularly check karate hain?"
#                         Follow up with details about the latest readings and frequency of check-ups.
#                         Question 8: "Kya aapko koi mental health concerns hain, jaise anxiety ya depression?"
#                         Ask follow-up questions about treatment, therapy, and symptom management.
#                         Question 9: "Aapka daily routine kaisa hai? Kya aap exercise karte hain ya koi physical activity karte hain?"
#                         Inquire about type, duration, and consistency of physical activities.
#                         Question 10: "Kya aap smoke karte hain ya alcohol consume karte hain? Agar haan, toh kitna?"
#                         Generate follow-ups to understand duration, frequency, and willingness to change these habits.
#                         Question 11: "Kya aapko koi recent injuries ya accidents huye hain?"
#                         Ask for recovery details and whether there is any ongoing treatment.
#                         Question 12: "Hamne kaafi saare health topics cover kar liye hain. Kya aapko koi aur health-related concerns hain jo aap discuss karna chahenge?"
#                         Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                         On-Demand Summary Feature:
#
#                         If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Mujhe summary do"), immediately provide a summary of the conversation up to that point.
#                         Summary Guidelines:
#                         Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                         Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                         After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                         Closing the Conversation:
#
#                         After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#                         "Aapne jo information share ki hai uske liye dhanyavaad. Main aaj ke key points summarize kar deti/deta hoon: [brief summary]. Kya aapko lagta hai ki isme kuch missing hai ya aap kuch aur add karna chahenge?"
#                         Inform the patient:
#                         "Yeh sari jankari aapke insurance portability process mein madad karegi. Agar aapke koi aur sawal hain, to main madad karne ke liye available hoon. Agar aapko further medical consultation ki zaroorat mehsoos hoti hai, kripya turant apne doctor se sampark karein."
#                         """
#         engPrompt = """ Begin every conversation with:
#                         "Hello, I am the Lumiq TeleMed Assistant. Today, I will conduct your medical examination for insurance policy portability. This session will be recorded for verification purposes. Before we begin, I need your consent to continue this examination. Do you agree?"
#                         Post-Consent Verification:
#                         After obtaining consent, ask:
#                         "Thank you. Could you please provide your full name and date of birth for verification purposes?"
#                         General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                         Main Question & Response Validation:
#                         For each primary question (e.g., medical history, medications, etc.), follow these steps:
#
#                         a. Ask the Main Question:
#                         Pose the question clearly.
#
#                         b. Listen to the User's Response:
#                         Evaluate whether the response is:
#
#                         Relevant and Detailed: Proceed with dynamic follow-up generation.
#                         Irrelevant or Vague:
#                         Respond with:
#                         "I'm sorry, this answer does not seem appropriate for the question. Please provide a correct and relevant answer to: [original question]."
#                         Then repeat the question until a valid, context-specific answer is provided.
#                         c. Dynamic Follow-Up Generation:
#                         Based on the response content:
#
#                         Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                         If the response indicates that the patient is not taking any medications, follow up by asking about the reasons (e.g., "Why are you not taking any medications? Do you believe your condition is stable, or is there another reason?").
#                         If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Please tell me which allergies you have. Have you had any severe reactions to any of them?").
#                         Ensure that follow-up questions:
#                         Are context-specific and adapt based on the patient's previous answers.
#                         Are generated dynamically by analyzing the details provided—or the lack thereof—in the response.
#                         Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                         d. Handling Valid Negative Answers:
#                         Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                         "Why are you not taking any medications? Do you feel that your condition is stable, or is there a specific reason? If needed, I can provide temporary medical advice; however, it is essential that you consult your doctor."
#                         Validate that the patient understands the implications of not taking medications.
#
#                         Medical History Questions with Dynamic Follow-Up Logic:
#
#                         For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the patient's input:
#
#                         Question 1:
#                         "Now I will ask you a few questions about your medical history. Do you have any existing medical conditions, such as diabetes, high blood pressure, or heart disease?"
#
#                         Dynamic Follow-Up:
#
#                         If a condition is mentioned, dynamically ask follow-ups like:
#                         "How long have you had this condition?"
#                         "Are you receiving regular treatment for it? If yes, what kind of treatment is it?"
#                         Generate additional questions based on the specifics provided (for example, changes in treatment, complications, etc.).
#                         Question 2:
#                         "Understood. Do you have any allergies, such as to medications, foods, or any other substances?"
#
#                         Dynamic Follow-Up:
#
#                         If the answer is "Yes," generate questions such as:
#                         "Please tell me which allergies you have. Are any of the reactions severe?"
#                         "What kind of allergic reactions do you experience? Do you have emergency medication available?"
#                         If the response is vague or off-topic, ask again for specific details.
#                         Question 3:
#                         "Alright. Are you taking any medications regularly? If yes, which ones?"
#
#                         Dynamic Follow-Up:
#
#                         If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                         "This answer is not related to the question. Please tell me if you take any medications regularly. If not, is there a reason behind it?"
#                         If the answer is a valid negative, ask dynamically:
#                         "Why are you not taking any medications? Do you believe your condition is fine, or is there another specific reason? If needed, temporary medical advice can be provided, but it is important to consult your doctor."
#                         Based on their reasoning, further follow-ups might be generated.
#                         Questions 4 to 12:
#                         Apply a similar dynamic follow-up approach:
#
#                         Question 4: "Have you ever had surgery? If yes, which surgery and when?"
#                         Follow up about recovery details, complications, and current status.
#                         Question 5: "Does anyone in your family have conditions such as diabetes, heart disease, or cancer?"
#                         Ask dynamically about which family member, diagnosis details, and any ongoing concerns.
#                         Question 6: "Have you ever experienced chest pain, shortness of breath, or dizziness?"
#                         Generate follow-up questions regarding the frequency, triggers, and whether you have consulted a doctor about these symptoms.
#                         Question 7: "Is your blood sugar and blood pressure under control? Do you have them checked regularly?"
#                         Follow up with details about the latest readings and how frequently the check-ups occur.
#                         Question 8: "Do you have any mental health concerns, such as anxiety or depression?"
#                         Ask follow-up questions about treatment, therapy, and how you are managing your symptoms.
#                         Question 9: "What is your daily routine like? Do you exercise or engage in any physical activity?"
#                         Inquire about the type, duration, and consistency of your physical activities.
#                         Question 10: "Do you smoke or consume alcohol? If yes, how much?"
#                         Generate follow-ups to understand the duration, frequency, and whether you wish to change these habits.
#                         Question 11: "Have you had any recent injuries or accidents?"
#                         Ask for details regarding recovery and whether there is any ongoing treatment.
#                         Question 12: "We have covered many health topics. Are there any other health-related concerns you would like to discuss?"
#                         Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                         On-Demand Summary Feature:
#
#                         If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Give me a summary"), immediately provide a summary of the conversation up to that point.
#
#                         Summary Guidelines:
#
#                         Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                         Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                         After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                                                 Closing the Conversation:
#
#                         After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#
#                         "Thank you for sharing the information. I will now summarize the key points from today: [brief summary]. Do you feel that anything is missing, or would you like to add any more details?"
#                         Inform the patient:
#
#                         "All this information will help with your insurance portability process. If you have any further questions, I am here to help. Additionally, if you feel that you need further medical consultation, please contact your doctor immediately."
#  """
#         # Select prompt based on language
#
#         # Select prompt based on language with explicit check
#         if language == "hindi":
#             system_instruction = hindiPrompt
#             print("Using Hindi prompt")
#         else:
#             system_instruction = engPrompt
#             print("Using English prompt")
#
#         # Select voice based on gender and language
#         if language == "hindi":
#             voice_name = "Fenrir" if gender == "male" else "Aoede"
#         else:
#             voice_name = "Charon" if gender == "male" else "Aoede"
#
#         print(f"Selected voice: {voice_name}")
#
#         config["system_instruction"] = system_instruction
#         config["voiceConfig"] = {
#             "prebuiltVoiceConfig": {
#                 "voiceName": voice_name
#             }
#         }
#
#         # Print final configuration for debugging
#         print("Final configuration:")
#         print(f"Language: {language}")
#         print(f"Gender: {gender}")
#         print(f"Voice: {voice_name}")
#
#         # Initialize audio recording
#         recorded_audio = []
#
#         # Get session handler
#         media_handler = await session_manager.get_session(session_id)
#
#         # Start the Gemini session
#         async with client.aio.live.connect(model=MODEL, config=config) as session:
#             print(f"Connected to Gemini API - Session {session_id} started")
#
#             async def send_to_gemini():
#                 """Sends messages from the client websocket to the Gemini API."""
#                 try:
#                     async for message in client_websocket:
#                         try:
#                             data = json.loads(message)
#                             if "realtime_input" in data:
#                                 for chunk in data["realtime_input"]["media_chunks"]:
#                                     if chunk["mime_type"] == "audio/pcm":
#                                         await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
#                                         # Store audio chunk for recording
#                                         recorded_audio.append(base64.b64decode(chunk["data"]))
#                         except Exception as e:
#                             print(f"Error sending to Gemini: {e}")
#                     print("Client connection closed (send)")
#                 except Exception as e:
#                     print(f"Error sending to Gemini: {e}")
#                 finally:
#                     # Save the recorded audio when the session ends
#                     media_handler.add_audio_chunk(b''.join(recorded_audio))
#                     print("send_to_gemini closed")
#
#             async def receive_from_gemini():
#                 """Receives responses from the Gemini API and forwards them to the client."""
#                 try:
#                     while True:
#                         try:
#                             print("receiving from gemini")
#                             async for response in session.receive():
#                                 if response.server_content is None:
#                                     print(f'Unhandled server message! - {response}')
#                                     continue
#
#                                 model_turn = response.server_content.model_turn
#                                 if model_turn:
#                                     for part in model_turn.parts:
#                                         if hasattr(part, 'text') and part.text is not None:
#                                             await client_websocket.send(json.dumps({"text": part.text}))
#                                         elif hasattr(part, 'inline_data') and part.inline_data is not None:
#                                             print("audio mime_type:", part.inline_data.mime_type)
#                                             base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
#                                             await client_websocket.send(json.dumps({
#                                                 "audio": base64_audio,
#                                             }))
#                                             print("audio received")
#
#                                 if response.server_content.turn_complete:
#                                     print('\n<Turn complete>')
#                         except websockets.exceptions.ConnectionClosedOK:
#                             print("Client connection closed normally (receive)")
#                             break
#                         except Exception as e:
#                             print(f"Error receiving from Gemini: {e}")
#                             break
#                 except Exception as e:
#                     print(f"Error receiving from Gemini: {e}")
#                 finally:
#                     print("Gemini connection closed (receive)")
#
#             send_task = asyncio.create_task(send_to_gemini())
#             receive_task = asyncio.create_task(receive_from_gemini())
#             await asyncio.gather(send_task, receive_task)
#
#     except Exception as e:
#         print(f"Error in Gemini session: {e}")
#     finally:
#         if session_id:
#             await session_manager.end_session(session_id)
#         print("Gemini session closed.")
#
#
# async def main() -> None:
#     async with websockets.serve(gemini_session_handler, "localhost", 9083):
#         print("Running websocket server localhost:9083...")
#         await asyncio.Future()  # Keep the server running indefinitely
#
#
# def save_recorded_audio(audio_chunks, language):
#     """Save the recorded audio chunks as an MP3 file."""
#     if not audio_chunks:
#         return
#
#     try:
#         # Convert audio chunks to numpy array
#         audio_data = np.frombuffer(b''.join(audio_chunks), dtype=np.int16)
#
#         # Generate filename with timestamp
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"conversation_{language}_{timestamp}.wav"
#
#         # Save as WAV file
#         with wave.open(filename, 'wb') as wav_file:
#             wav_file.setnchannels(1)  # Mono
#             wav_file.setsampwidth(2)  # 2 bytes per sample
#             wav_file.setframerate(16000)  # Sample rate
#             wav_file.writeframes(audio_data.tobytes())
#
#         print(f"Conversation saved as {filename}")
#     except Exception as e:
#         print(f"Error saving audio: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
#


#### newly working code
#
# import asyncio
# import json
# import os
# import websockets
# import base64
# import wave
# import datetime
# import numpy as np
# import uuid
#
# # External libraries for HTTP server and CORS
# import aiohttp_cors
# from aiohttp import web
# from datetime import datetime as dt
#
# # Import your local modules
# from google import genai
# from session_manager import SessionManager
# from prompts import get_base_prompt
#
# # Load API key from environment
# os.environ['GOOGLE_API_KEY'] = 'AIzaSyBEKQ9F5rGP8npV77kuvuI1zzkZPCYmLxM'
# MODEL = "gemini-2.0-flash-exp"  # use your model ID
#
# client = genai.Client(
#     http_options={
#         'api_version': 'v1alpha',
#     }
# )
#
# # Initialize the session manager
# session_manager = SessionManager()
#
#
# # =======================
# # WebSocket Functionality
# # =======================
# async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
#     """
#     Handles the interaction with Gemini API within a websocket session for audio conversation.
#     """
#     session_id = None
#     try:
#         # Create a new session
#         session_id, message = await session_manager.create_session()
#         if not session_id:
#             await client_websocket.send(json.dumps({"error": message}))
#             return
#
#         # Wait for the initial setup message (sent when mic is clicked)
#         config_message = await client_websocket.recv()
#         config_data = json.loads(config_message)
#
#         # Check if this is a setup message
#         if "setup" not in config_data:
#             print("Received non-setup message before initialization")
#             return
#
#         config = config_data.get("setup", {})
#
#         # Get language and gender preferences
#         language = config_data.get("language", "english").lower()
#         gender = config_data.get("gender", "male").lower()
#         print(f"Starting new session - Language: {language}, Gender: {gender}")
#         hindiPrompt = """Initial Greeting and Consent:
#
#                            Greeting:
#                            Begin every conversation with:
#                            "Hello, main Lumiq ka TeleMed Assistant hoon. Aaj main aapka medical examination karunga/karungi insurance policy portability ke liye. Yeh session verification purposes ke liye record kiya jayega. Shuruat karne se pehle, mujhe aapki consent chahiye is examination ko continue karne ke liye. Kya aap agree karte hain?"
#                            Post-Consent Verification:
#                            After consent is obtained, ask:
#                            "Dhanyavaad. Kya aap please apna full name aur date of birth verification ke liye bata sakte hain?"
#                            and Evaluate whether the response is valid or not.
#                            General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                            Main Question & Response Validation:
#                            For each primary question (e.g., medical history, medications, etc.), do the following:
#
#                            a. Ask the Main Question:
#                            Pose the question in a clear manner.
#
#                            b. Listen to the User's Response:
#                            Evaluate whether the response is:
#
#                            Relevant and Detailed: Proceed with dynamic follow-up generation.
#                            Irrelevant or Vague:
#                            Respond with:
#                            "Mujhe maaf kijiye, yeh jawab prashn ke liye upyukt nahi lag raha. Kripya, [original question] ka sahi aur relevant jawab dein."
#                            Then repeat the question until a valid, context-specific answer is provided.
#                            c. Dynamic Follow-Up Generation:
#
#                            Based on the response content:
#                            Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                            If the response indicates that the patient is not taking any medications, follow up by asking about reasons (e.g., "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi aur wajah hai?").
#                            If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Kripya batayein, aapko kaun kaun si allergies hain? Kya aapko inme se kisi se severe reaction hua hai?").
#                            Ensure that follow-up questions:
#                            Are context-specific and adapt based on the patient's previous answers.
#                            Are generated dynamically by analyzing the details or lack thereof in the response.
#                            Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                            d. Handling Valid Negative Answers:
#
#                            Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                            "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi specific reason hai? Agar zaroorat ho toh main aapko temporary medical advice provide kar sakta/sakti hoon, lekin doctor se consult karna zaroori hai."
#                            Validate that the patient acknowledges the implications of not taking medications.
#                            Medical History Questions with Dynamic Follow-Up Logic:
#
#                            For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the user's input:
#
#                            Question 1:
#                            "Ab main aapke medical history ke baare mein kuch sawal poochunga/poochungi. Kya aapko koi existing medical conditions hain, jaise diabetes, high blood pressure, ya heart disease?"
#
#                            Dynamic Follow-Up:
#                            If a condition is mentioned, dynamically ask follow-ups like:
#                            "Aapko yeh condition kitne samay se hai?"
#                            "Kya aap iske liye regular treatment le rahe hain? Agar haan, kis tarah ka treatment hai?"
#                            Generate additional questions based on the specifics provided (e.g., treatment changes, complications, etc.).
#                            Question 2:
#                            "Samajh gaya/gayi. Kya aapko koi allergies hain, jaise dawa, khane, ya kisi aur cheez se?"
#
#                            Dynamic Follow-Up:
#                            If "Yes," generate questions such as:
#                            "Kripya batayein, aapko kaun kaun si allergies hain? Kya inka reaction severe hai?"
#                            "Allergy reaction kaisa hota hai? Kya aapke paas emergency medication hai?"
#                            If the response is vague or off-topic, ask again for the specific details.
#                            Question 3:
#                            "Theek hai. Aap regular koi medications le rahe hain? Agar haan, toh kaunsi?"
#
#                            Dynamic Follow-Up:
#                            If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                            "Yeh jawab prashn se sambandhit nahi hai. Kripya, batayein ki kya aap regular koi medications lete hain? Agar nahi, toh iske peeche koi wajah hai?"
#                            If the answer is a valid negative, ask dynamically:
#                            "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition theek hai, ya koi specific reason hai? Agar zaroorat ho toh temporary medical advice provide ki ja sakti hai, lekin doctor se consult karna zaroori hai."
#                            Based on their reasoning, further follow-ups might be generated.
#                            Questions 4 to 12:
#                            Apply a similar dynamic follow-up approach:
#
#                            Question 4: "Kya aapko kabhi surgery hui hai? Agar haan, toh kaunsi aur kab?"
#                            Follow up about recovery details, complications, and current status.
#                            Question 5: "Aapke family mein kisi ko diabetes, heart disease, ya cancer jaise conditions hain?"
#                            Ask dynamically about which family members, diagnosis details, and any ongoing concerns.
#                            Question 6: "Kya aapko kabhi chest pain, shortness of breath, ya dizziness ka experience hua hai?"
#                            Generate follow-up questions regarding frequency, triggers, and medical consultations.
#                            Question 7: "Aapka blood sugar aur BP control mein hai? Kya aap regularly check karate hain?"
#                            Follow up with details about the latest readings and frequency of check-ups.
#                            Question 8: "Kya aapko koi mental health concerns hain, jaise anxiety ya depression?"
#                            Ask follow-up questions about treatment, therapy, and symptom management.
#                            Question 9: "Aapka daily routine kaisa hai? Kya aap exercise karte hain ya koi physical activity karte hain?"
#                            Inquire about type, duration, and consistency of physical activities.
#                            Question 10: "Kya aap smoke karte hain ya alcohol consume karte hain? Agar haan, toh kitna?"
#                            Generate follow-ups to understand duration, frequency, and willingness to change these habits.
#                            Question 11: "Kya aapko koi recent injuries ya accidents huye hain?"
#                            Ask for recovery details and whether there is any ongoing treatment.
#                            Question 12: "Hamne kaafi saare health topics cover kar liye hain. Kya aapko koi aur health-related concerns hain jo aap discuss karna chahenge?"
#                            Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                            On-Demand Summary Feature:
#
#                            If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Mujhe summary do"), immediately provide a summary of the conversation up to that point.
#                            Summary Guidelines:
#                            Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                            Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                            After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                            Closing the Conversation:
#
#                            After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#                            "Aapne jo information share ki hai uske liye dhanyavaad. Main aaj ke key points summarize kar deti/deta hoon: [brief summary]. Kya aapko lagta hai ki isme kuch missing hai ya aap kuch aur add karna chahenge?"
#                            Inform the patient:
#                            "Yeh sari jankari aapke insurance portability process mein madad karegi. Agar aapke koi aur sawal hain, to main madad karne ke liye available hoon. Agar aapko further medical consultation ki zaroorat mehsoos hoti hai, kripya turant apne doctor se sampark karein."
#                            """
#         engPrompt = """ Begin every conversation with:
#                            "Hello, I am the Lumiq TeleMed Assistant. Today, I will conduct your medical examination for insurance policy portability. This session will be recorded for verification purposes. Before we begin, I need your consent to continue this examination. Do you agree?"
#                            Post-Consent Verification:
#                            After obtaining consent, ask:
#                            "Thank you. Could you please provide your full name and date of birth for verification purposes?"
#                            General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                            Main Question & Response Validation:
#                            For each primary question (e.g., medical history, medications, etc.), follow these steps:
#
#                            a. Ask the Main Question:
#                            Pose the question clearly.
#
#                            b. Listen to the User's Response:
#                            Evaluate whether the response is:
#
#                            Relevant and Detailed: Proceed with dynamic follow-up generation.
#                            Irrelevant or Vague:
#                            Respond with:
#                            "I'm sorry, this answer does not seem appropriate for the question. Please provide a correct and relevant answer to: [original question]."
#                            Then repeat the question until a valid, context-specific answer is provided.
#                            c. Dynamic Follow-Up Generation:
#                            Based on the response content:
#
#                            Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                            If the response indicates that the patient is not taking any medications, follow up by asking about the reasons (e.g., "Why are you not taking any medications? Do you believe your condition is stable, or is there another reason?").
#                            If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Please tell me which allergies you have. Have you had any severe reactions to any of them?").
#                            Ensure that follow-up questions:
#                            Are context-specific and adapt based on the patient's previous answers.
#                            Are generated dynamically by analyzing the details provided—or the lack thereof—in the response.
#                            Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                            d. Handling Valid Negative Answers:
#                            Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                            "Why are you not taking any medications? Do you feel that your condition is stable, or is there a specific reason? If needed, I can provide temporary medical advice; however, it is essential that you consult your doctor."
#                            Validate that the patient understands the implications of not taking medications.
#
#                            Medical History Questions with Dynamic Follow-Up Logic:
#
#                            For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the patient's input:
#
#                            Question 1:
#                            "Now I will ask you a few questions about your medical history. Do you have any existing medical conditions, such as diabetes, high blood pressure, or heart disease?"
#
#                            Dynamic Follow-Up:
#
#                            If a condition is mentioned, dynamically ask follow-ups like:
#                            "How long have you had this condition?"
#                            "Are you receiving regular treatment for it? If yes, what kind of treatment is it?"
#                            Generate additional questions based on the specifics provided (for example, changes in treatment, complications, etc.).
#                            Question 2:
#                            "Understood. Do you have any allergies, such as to medications, foods, or any other substances?"
#
#                            Dynamic Follow-Up:
#
#                            If the answer is "Yes," generate questions such as:
#                            "Please tell me which allergies you have. Are any of the reactions severe?"
#                            "What kind of allergic reactions do you experience? Do you have emergency medication available?"
#                            If the response is vague or off-topic, ask again for specific details.
#                            Question 3:
#                            "Alright. Are you taking any medications regularly? If yes, which ones?"
#
#                            Dynamic Follow-Up:
#
#                            If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                            "This answer is not related to the question. Please tell me if you take any medications regularly. If not, is there a reason behind it?"
#                            If the answer is a valid negative, ask dynamically:
#                            "Why are you not taking any medications? Do you believe your condition is fine, or is there another specific reason? If needed, temporary medical advice can be provided, but it is important to consult your doctor."
#                            Based on their reasoning, further follow-ups might be generated.
#                            Questions 4 to 12:
#                            Apply a similar dynamic follow-up approach:
#
#                            Question 4: "Have you ever had surgery? If yes, which surgery and when?"
#                            Follow up about recovery details, complications, and current status.
#                            Question 5: "Does anyone in your family have conditions such as diabetes, heart disease, or cancer?"
#                            Ask dynamically about which family member, diagnosis details, and any ongoing concerns.
#                            Question 6: "Have you ever experienced chest pain, shortness of breath, or dizziness?"
#                            Generate follow-up questions regarding the frequency, triggers, and whether you have consulted a doctor about these symptoms.
#                            Question 7: "Is your blood sugar and blood pressure under control? Do you have them checked regularly?"
#                            Follow up with details about the latest readings and how frequently the check-ups occur.
#                            Question 8: "Do you have any mental health concerns, such as anxiety or depression?"
#                            Ask follow-up questions about treatment, therapy, and how you are managing your symptoms.
#                            Question 9: "What is your daily routine like? Do you exercise or engage in any physical activity?"
#                            Inquire about the type, duration, and consistency of your physical activities.
#                            Question 10: "Do you smoke or consume alcohol? If yes, how much?"
#                            Generate follow-ups to understand the duration, frequency, and whether you wish to change these habits.
#                            Question 11: "Have you had any recent injuries or accidents?"
#                            Ask for details regarding recovery and whether there is any ongoing treatment.
#                            Question 12: "We have covered many health topics. Are there any other health-related concerns you would like to discuss?"
#                            Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                            On-Demand Summary Feature:
#
#                            If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Give me a summary"), immediately provide a summary of the conversation up to that point.
#
#                            Summary Guidelines:
#
#                            Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                            Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                            After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                                                    Closing the Conversation:
#
#                            After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#
#                            "Thank you for sharing the information. I will now summarize the key points from today: [brief summary]. Do you feel that anything is missing, or would you like to add any more details?"
#                            Inform the patient:
#
#                            "All this information will help with your insurance portability process. If you have any further questions, I am here to help. Additionally, if you feel that you need further medical consultation, please contact your doctor immediately."
#                             """
#         # Select prompt based on language
#         if language == "hindi":
#             system_instruction = hindiPrompt
#             print("Using Hindi prompt")
#         else:
#             system_instruction = engPrompt
#             print("Using English prompt")
#
#         # Select voice based on gender and language
#         if language == "hindi":
#             voice_name = "Fenrir" if gender == "male" else "Aoede"
#         else:
#             voice_name = "Charon" if gender == "male" else "Aoede"
#
#         print(f"Selected voice: {voice_name}")
#
#         config["system_instruction"] = system_instruction
#         config["voiceConfig"] = {
#             "prebuiltVoiceConfig": {
#                 "voiceName": voice_name
#             }
#         }
#
#         # Debug print of final configuration
#         print("Final configuration:")
#         print(f"Language: {language}")
#         print(f"Gender: {gender}")
#         print(f"Voice: {voice_name}")
#
#         # Initialize audio recording storage
#         recorded_audio = []
#
#         # Get session handler from the session manager
#         media_handler = await session_manager.get_session(session_id)
#
#         # Start the Gemini session
#         async with client.aio.live.connect(model=MODEL, config=config) as session:
#             print(f"Connected to Gemini API - Session {session_id} started")
#
#             async def send_to_gemini():
#                 """Send messages from the client websocket to the Gemini API."""
#                 try:
#                     async for message in client_websocket:
#                         try:
#                             data = json.loads(message)
#                             if "realtime_input" in data:
#                                 for chunk in data["realtime_input"]["media_chunks"]:
#                                     if chunk["mime_type"] == "audio/pcm":
#                                         await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
#                                         # Store the audio chunk for later recording
#                                         recorded_audio.append(base64.b64decode(chunk["data"]))
#                         except Exception as e:
#                             print(f"Error sending to Gemini: {e}")
#                     print("Client connection closed (send)")
#                 except Exception as e:
#                     print(f"Error in send_to_gemini: {e}")
#                 finally:
#                     # Save the recorded audio when the session ends
#                     media_handler.add_audio_chunk(b''.join(recorded_audio))
#                     print("send_to_gemini closed")
#
#             async def receive_from_gemini():
#                 """Receive responses from the Gemini API and forward them to the client."""
#                 try:
#                     while True:
#                         try:
#                             print("Receiving from Gemini...")
#                             async for response in session.receive():
#                                 if response.server_content is None:
#                                     print(f'Unhandled server message! - {response}')
#                                     continue
#
#                                 model_turn = response.server_content.model_turn
#                                 if model_turn:
#                                     for part in model_turn.parts:
#                                         if hasattr(part, 'text') and part.text is not None:
#                                             await client_websocket.send(json.dumps({"text": part.text}))
#                                         elif hasattr(part, 'inline_data') and part.inline_data is not None:
#                                             print("audio mime_type:", part.inline_data.mime_type)
#                                             base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
#                                             await client_websocket.send(json.dumps({
#                                                 "audio": base64_audio,
#                                             }))
#                                             print("Audio received")
#                                 if response.server_content.turn_complete:
#                                     print('\n<Turn complete>')
#                         except websockets.exceptions.ConnectionClosedOK:
#                             print("Client connection closed normally (receive)")
#                             break
#                         except Exception as e:
#                             print(f"Error receiving from Gemini: {e}")
#                             break
#                 except Exception as e:
#                     print(f"Error in receive_from_gemini: {e}")
#                 finally:
#                     print("Gemini connection closed (receive)")
#
#             # Run both sending and receiving concurrently
#             send_task = asyncio.create_task(send_to_gemini())
#             receive_task = asyncio.create_task(receive_from_gemini())
#             await asyncio.gather(send_task, receive_task)
#
#     except Exception as e:
#         print(f"Error in Gemini session: {e}")
#     finally:
#         if session_id:
#             await session_manager.end_session(session_id)
#         print("Gemini session closed.")
#
#
# def save_recorded_audio(audio_chunks, language):
#     """Save the recorded audio chunks as a WAV file."""
#     if not audio_chunks:
#         return
#
#     try:
#         # Convert audio chunks to a numpy array
#         audio_data = np.frombuffer(b''.join(audio_chunks), dtype=np.int16)
#
#         # Generate filename with timestamp
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"conversation_{language}_{timestamp}.wav"
#
#         # Save as WAV file
#         with wave.open(filename, 'wb') as wav_file:
#             wav_file.setnchannels(1)  # Mono
#             wav_file.setsampwidth(2)  # 2 bytes per sample
#             wav_file.setframerate(16000)  # Sample rate
#             wav_file.writeframes(audio_data.tobytes())
#
#         print(f"Conversation saved as {filename}")
#     except Exception as e:
#         print(f"Error saving audio: {e}")
#
#
# # ============================
# # HTTP Server (Aiohttp) Section
# # ============================
#
# # Create a RouteTableDef instance for defining HTTP routes
# routes = web.RouteTableDef()
#
#
# async def save_file(file_data, file_type):
#     """Saves the binary file data under a directory based on its type."""
#     timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"session_{timestamp}_{file_type}.webm"
#     filepath = os.path.join("recordings", file_type, filename)
#
#     # Ensure the directory exists
#     os.makedirs(os.path.dirname(filepath), exist_ok=True)
#
#     # Save the file
#     with open(filepath, 'wb') as f:
#         f.write(file_data)
#
#     return filepath
#
#
# @routes.post('/save-session')
# async def handle_save_session(request):
#     """
#     HTTP endpoint to save the session data including audio, video, and conversation JSON.
#     Expects a multipart POST with keys 'audio', 'video', and 'conversation'.
#     """
#     try:
#         data = await request.post()
#
#         # Save audio file if provided
#         audio_file = data.get('audio')
#         audio_path = None
#         if audio_file:
#             audio_path = await save_file(audio_file.file.read(), 'audio')
#
#         # Save video file if provided
#         video_file = data.get('video')
#         video_path = None
#         if video_file:
#             video_path = await save_file(video_file.file.read(), 'video')
#
#         # Save conversation data (JSON string expected)
#         conversation_data = json.loads(data.get('conversation'))
#
#         # Add file paths to conversation metadata
#         conversation_data['metadata']['audioPath'] = audio_path
#         conversation_data['metadata']['videoPath'] = video_path
#
#         # Save conversation data to a JSON file
#         timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
#         json_filename = f"session_{timestamp}_data.json"
#         json_filepath = os.path.join("recordings", "data", json_filename)
#
#         os.makedirs(os.path.dirname(json_filepath), exist_ok=True)
#         with open(json_filepath, 'w') as f:
#             json.dump(conversation_data, f, indent=2)
#
#         return web.json_response({
#             'success': True,
#             'message': 'Session data saved successfully',
#             'paths': {
#                 'audio': audio_path,
#                 'video': video_path,
#                 'data': json_filepath
#             }
#         })
#
#     except Exception as e:
#         print(f"Error saving session data: {e}")
#         return web.json_response({
#             'success': False,
#             'error': str(e)
#         }, status=500)
#
#
# async def handle_index(request):
#     """A simple index endpoint to check if the HTTP server is running."""
#     return web.Response(text="Server is running.")
#
#
# async def start_http_server():
#     """Starts the aiohttp HTTP server with the save-session endpoint and CORS support."""
#     app = web.Application()
#     app.add_routes(routes)
#     app.router.add_get('/', handle_index)
#
#     # Set up CORS middleware to allow all origins and headers.
#     cors = aiohttp_cors.setup(app, defaults={
#         "*": aiohttp_cors.ResourceOptions(
#             allow_credentials=True,
#             expose_headers="*",
#             allow_headers="*",
#         )
#     })
#     # Apply CORS to all routes
#     for route in list(app.router.routes()):
#         cors.add(route)
#
#     runner = web.AppRunner(app)
#     await runner.setup()
#     # Running on port 9084 so as not to conflict with the websockets server on 9083.
#     site = web.TCPSite(runner, 'localhost', 9084)
#     await site.start()
#     print("HTTP server running on http://localhost:9084")
#     await asyncio.Future()  # Run forever
#
#
# async def start_ws_server():
#     """Starts the websockets server to handle Gemini sessions."""
#     async with websockets.serve(gemini_session_handler, "localhost", 9083):
#         print("WebSocket server running on ws://localhost:9083")
#         await asyncio.Future()  # Run forever
#
#
# # ============================
# # Main: Run both servers concurrently
# # ============================
# async def main():
#     await asyncio.gather(
#         start_ws_server(),
#         start_http_server()
#     )
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



##recent

# import asyncio
# import json
# import os
# import websockets
# from aiohttp import web
# import aiohttp_cors
# from datetime import datetime
# from google import genai
# import base64
# import wave
# import numpy as np
# from session_manager import SessionManager
# from prompts import get_base_prompt
#
# # ---------------------------------------------------
# # Configuration and Initialization
# # ---------------------------------------------------
# os.environ['GOOGLE_API_KEY'] = 'AIzaSyBEKQ9F5rGP8npV77kuvuI1zzkZPCYmLxM'
# MODEL = "gemini-2.0-flash-exp"  # Use your model ID
#
# client = genai.Client(
#     http_options={
#         'api_version': 'v1alpha',
#     }
# )
#
# # Initialize the session manager
# session_manager = SessionManager()
#
#
# # ---------------------------------------------------
# # WebSocket Server: Gemini Session Handler
# # ---------------------------------------------------
# async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
#     """
#     Handles the Gemini API interaction via a websocket session.
#     """
#     session_id = None
#     try:
#         # Create a new session
#         session_id, message = await session_manager.create_session()
#         if not session_id:
#             await client_websocket.send(json.dumps({"error": message}))
#             return
#
#         # Wait for the setup message (e.g. when the mic is clicked)
#         config_message = await client_websocket.recv()
#         config_data = json.loads(config_message)
#         if "setup" not in config_data:
#             print("Received non-setup message before initialization")
#             return
#         config = config_data.get("setup", {})
#
#         # Get language and gender preferences
#         language = config_data.get("language", "english").lower()
#         gender = config_data.get("gender", "male").lower()
#         print(f"Starting new session - Language: {language}, Gender: {gender}")
#
#         # Define prompts (adjust these as needed)
#         hindiPrompt = """Initial Greeting and Consent:
#
#                                    Greeting:
#                                    Begin every conversation with:
#                                    "Hello, main Lumiq ka TeleMed Assistant hoon. Aaj main aapka medical examination karunga/karungi insurance policy portability ke liye. Yeh session verification purposes ke liye record kiya jayega. Shuruat karne se pehle, mujhe aapki consent chahiye is examination ko continue karne ke liye. Kya aap agree karte hain?"
#                                    Post-Consent Verification:
#                                    After consent is obtained, ask:
#                                    "Dhanyavaad. Kya aap please apna full name aur date of birth verification ke liye bata sakte hain?"
#                                    and Evaluate whether the response is valid or not.
#                                    General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                                    Main Question & Response Validation:
#                                    For each primary question (e.g., medical history, medications, etc.), do the following:
#
#                                    a. Ask the Main Question:
#                                    Pose the question in a clear manner.
#
#                                    b. Listen to the User's Response:
#                                    Evaluate whether the response is:
#
#                                    Relevant and Detailed: Proceed with dynamic follow-up generation.
#                                    Irrelevant or Vague:
#                                    Respond with:
#                                    "Mujhe maaf kijiye, yeh jawab prashn ke liye upyukt nahi lag raha. Kripya, [original question] ka sahi aur relevant jawab dein."
#                                    Then repeat the question until a valid, context-specific answer is provided.
#                                    c. Dynamic Follow-Up Generation:
#
#                                    Based on the response content:
#                                    Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                                    If the response indicates that the patient is not taking any medications, follow up by asking about reasons (e.g., "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi aur wajah hai?").
#                                    If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Kripya batayein, aapko kaun kaun si allergies hain? Kya aapko inme se kisi se severe reaction hua hai?").
#                                    Ensure that follow-up questions:
#                                    Are context-specific and adapt based on the patient's previous answers.
#                                    Are generated dynamically by analyzing the details or lack thereof in the response.
#                                    Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                                    d. Handling Valid Negative Answers:
#
#                                    Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                                    "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi specific reason hai? Agar zaroorat ho toh main aapko temporary medical advice provide kar sakta/sakti hoon, lekin doctor se consult karna zaroori hai."
#                                    Validate that the patient acknowledges the implications of not taking medications.
#                                    Medical History Questions with Dynamic Follow-Up Logic:
#
#                                    For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the user's input:
#
#                                    Question 1:
#                                    "Ab main aapke medical history ke baare mein kuch sawal poochunga/poochungi. Kya aapko koi existing medical conditions hain, jaise diabetes, high blood pressure, ya heart disease?"
#
#                                    Dynamic Follow-Up:
#                                    If a condition is mentioned, dynamically ask follow-ups like:
#                                    "Aapko yeh condition kitne samay se hai?"
#                                    "Kya aap iske liye regular treatment le rahe hain? Agar haan, kis tarah ka treatment hai?"
#                                    Generate additional questions based on the specifics provided (e.g., treatment changes, complications, etc.).
#                                    Question 2:
#                                    "Samajh gaya/gayi. Kya aapko koi allergies hain, jaise dawa, khane, ya kisi aur cheez se?"
#
#                                    Dynamic Follow-Up:
#                                    If "Yes," generate questions such as:
#                                    "Kripya batayein, aapko kaun kaun si allergies hain? Kya inka reaction severe hai?"
#                                    "Allergy reaction kaisa hota hai? Kya aapke paas emergency medication hai?"
#                                    If the response is vague or off-topic, ask again for the specific details.
#                                    Question 3:
#                                    "Theek hai. Aap regular koi medications le rahe hain? Agar haan, toh kaunsi?"
#
#                                    Dynamic Follow-Up:
#                                    If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                                    "Yeh jawab prashn se sambandhit nahi hai. Kripya, batayein ki kya aap regular koi medications lete hain? Agar nahi, toh iske peeche koi wajah hai?"
#                                    If the answer is a valid negative, ask dynamically:
#                                    "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition theek hai, ya koi specific reason hai? Agar zaroorat ho toh temporary medical advice provide ki ja sakti hai, lekin doctor se consult karna zaroori hai."
#                                    Based on their reasoning, further follow-ups might be generated.
#                                    Questions 4 to 12:
#                                    Apply a similar dynamic follow-up approach:
#
#                                    Question 4: "Kya aapko kabhi surgery hui hai? Agar haan, toh kaunsi aur kab?"
#                                    Follow up about recovery details, complications, and current status.
#                                    Question 5: "Aapke family mein kisi ko diabetes, heart disease, ya cancer jaise conditions hain?"
#                                    Ask dynamically about which family members, diagnosis details, and any ongoing concerns.
#                                    Question 6: "Kya aapko kabhi chest pain, shortness of breath, ya dizziness ka experience hua hai?"
#                                    Generate follow-up questions regarding frequency, triggers, and medical consultations.
#                                    Question 7: "Aapka blood sugar aur BP control mein hai? Kya aap regularly check karate hain?"
#                                    Follow up with details about the latest readings and frequency of check-ups.
#                                    Question 8: "Kya aapko koi mental health concerns hain, jaise anxiety ya depression?"
#                                    Ask follow-up questions about treatment, therapy, and symptom management.
#                                    Question 9: "Aapka daily routine kaisa hai? Kya aap exercise karte hain ya koi physical activity karte hain?"
#                                    Inquire about type, duration, and consistency of physical activities.
#                                    Question 10: "Kya aap smoke karte hain ya alcohol consume karte hain? Agar haan, toh kitna?"
#                                    Generate follow-ups to understand duration, frequency, and willingness to change these habits.
#                                    Question 11: "Kya aapko koi recent injuries ya accidents huye hain?"
#                                    Ask for recovery details and whether there is any ongoing treatment.
#                                    Question 12: "Hamne kaafi saare health topics cover kar liye hain. Kya aapko koi aur health-related concerns hain jo aap discuss karna chahenge?"
#                                    Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                                    On-Demand Summary Feature:
#
#                                    If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Mujhe summary do"), immediately provide a summary of the conversation up to that point.
#                                    Summary Guidelines:
#                                    Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                                    Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                                    After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                                    Closing the Conversation:
#
#                                    After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#                                    "Aapne jo information share ki hai uske liye dhanyavaad. Main aaj ke key points summarize kar deti/deta hoon: [brief summary]. Kya aapko lagta hai ki isme kuch missing hai ya aap kuch aur add karna chahenge?"
#                                    Inform the patient:
#                                    "Yeh sari jankari aapke insurance portability process mein madad karegi. Agar aapke koi aur sawal hain, to main madad karne ke liye available hoon. Agar aapko further medical consultation ki zaroorat mehsoos hoti hai, kripya turant apne doctor se sampark karein."
#                                    """
#         engPrompt = """ Begin every conversation with:
#                                    "Hello, I am the Lumiq TeleMed Assistant. Today, I will conduct your medical examination for insurance policy portability. This session will be recorded for verification purposes. Before we begin, I need your consent to continue this examination. Do you agree?"
#                                    Post-Consent Verification:
#                                    After obtaining consent, ask:
#                                    "Thank you. Could you please provide your full name and date of birth for verification purposes?"
#                                    General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                                    Main Question & Response Validation:
#                                    For each primary question (e.g., medical history, medications, etc.), follow these steps:
#
#                                    a. Ask the Main Question:
#                                    Pose the question clearly.
#
#                                    b. Listen to the User's Response:
#                                    Evaluate whether the response is:
#
#                                    Relevant and Detailed: Proceed with dynamic follow-up generation.
#                                    Irrelevant or Vague:
#                                    Respond with:
#                                    "I'm sorry, this answer does not seem appropriate for the question. Please provide a correct and relevant answer to: [original question]."
#                                    Then repeat the question until a valid, context-specific answer is provided.
#                                    c. Dynamic Follow-Up Generation:
#                                    Based on the response content:
#
#                                    Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                                    If the response indicates that the patient is not taking any medications, follow up by asking about the reasons (e.g., "Why are you not taking any medications? Do you believe your condition is stable, or is there another reason?").
#                                    If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Please tell me which allergies you have. Have you had any severe reactions to any of them?").
#                                    Ensure that follow-up questions:
#                                    Are context-specific and adapt based on the patient's previous answers.
#                                    Are generated dynamically by analyzing the details provided—or the lack thereof—in the response.
#                                    Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                                    d. Handling Valid Negative Answers:
#                                    Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                                    "Why are you not taking any medications? Do you feel that your condition is stable, or is there a specific reason? If needed, I can provide temporary medical advice; however, it is essential that you consult your doctor."
#                                    Validate that the patient understands the implications of not taking medications.
#
#                                    Medical History Questions with Dynamic Follow-Up Logic:
#
#                                    For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the patient's input:
#
#                                    Question 1:
#                                    "Now I will ask you a few questions about your medical history. Do you have any existing medical conditions, such as diabetes, high blood pressure, or heart disease?"
#
#                                    Dynamic Follow-Up:
#
#                                    If a condition is mentioned, dynamically ask follow-ups like:
#                                    "How long have you had this condition?"
#                                    "Are you receiving regular treatment for it? If yes, what kind of treatment is it?"
#                                    Generate additional questions based on the specifics provided (for example, changes in treatment, complications, etc.).
#                                    Question 2:
#                                    "Understood. Do you have any allergies, such as to medications, foods, or any other substances?"
#
#                                    Dynamic Follow-Up:
#
#                                    If the answer is "Yes," generate questions such as:
#                                    "Please tell me which allergies you have. Are any of the reactions severe?"
#                                    "What kind of allergic reactions do you experience? Do you have emergency medication available?"
#                                    If the response is vague or off-topic, ask again for specific details.
#                                    Question 3:
#                                    "Alright. Are you taking any medications regularly? If yes, which ones?"
#
#                                    Dynamic Follow-Up:
#
#                                    If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                                    "This answer is not related to the question. Please tell me if you take any medications regularly. If not, is there a reason behind it?"
#                                    If the answer is a valid negative, ask dynamically:
#                                    "Why are you not taking any medications? Do you believe your condition is fine, or is there another specific reason? If needed, temporary medical advice can be provided, but it is important to consult your doctor."
#                                    Based on their reasoning, further follow-ups might be generated.
#                                    Questions 4 to 12:
#                                    Apply a similar dynamic follow-up approach:
#
#                                    Question 4: "Have you ever had surgery? If yes, which surgery and when?"
#                                    Follow up about recovery details, complications, and current status.
#                                    Question 5: "Does anyone in your family have conditions such as diabetes, heart disease, or cancer?"
#                                    Ask dynamically about which family member, diagnosis details, and any ongoing concerns.
#                                    Question 6: "Have you ever experienced chest pain, shortness of breath, or dizziness?"
#                                    Generate follow-up questions regarding the frequency, triggers, and whether you have consulted a doctor about these symptoms.
#                                    Question 7: "Is your blood sugar and blood pressure under control? Do you have them checked regularly?"
#                                    Follow up with details about the latest readings and how frequently the check-ups occur.
#                                    Question 8: "Do you have any mental health concerns, such as anxiety or depression?"
#                                    Ask follow-up questions about treatment, therapy, and how you are managing your symptoms.
#                                    Question 9: "What is your daily routine like? Do you exercise or engage in any physical activity?"
#                                    Inquire about the type, duration, and consistency of your physical activities.
#                                    Question 10: "Do you smoke or consume alcohol? If yes, how much?"
#                                    Generate follow-ups to understand the duration, frequency, and whether you wish to change these habits.
#                                    Question 11: "Have you had any recent injuries or accidents?"
#                                    Ask for details regarding recovery and whether there is any ongoing treatment.
#                                    Question 12: "We have covered many health topics. Are there any other health-related concerns you would like to discuss?"
#                                    Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                                    On-Demand Summary Feature:
#
#                                    If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Give me a summary"), immediately provide a summary of the conversation up to that point.
#
#                                    Summary Guidelines:
#
#                                    Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                                    Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                                    After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                                                            Closing the Conversation:
#
#                                    After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#
#                                    "Thank you for sharing the information. I will now summarize the key points from today: [brief summary]. Do you feel that anything is missing, or would you like to add any more details?"
#                                    Inform the patient:
#
#                                    "All this information will help with your insurance portability process. If you have any further questions, I am here to help. Additionally, if you feel that you need further medical consultation, please contact your doctor immediately."
#                                     """
#         if language == "hindi":
#             system_instruction = hindiPrompt
#             print("Using Hindi prompt")
#         else:
#             system_instruction = engPrompt
#             print("Using English prompt")
#
#         # Select voice based on language and gender
#         if language == "hindi":
#             voice_name = "Fenrir" if gender == "male" else "Aoede"
#         else:
#             voice_name = "Charon" if gender == "male" else "Aoede"
#         print(f"Selected voice: {voice_name}")
#
#         config["system_instruction"] = system_instruction
#         config["voiceConfig"] = {
#             "prebuiltVoiceConfig": {
#                 "voiceName": voice_name
#             }
#         }
#         print("Final configuration:")
#         print(f"Language: {language}")
#         print(f"Gender: {gender}")
#         print(f"Voice: {voice_name}")
#
#         recorded_audio = []
#         media_handler = await session_manager.get_session(session_id)
#
#         async with client.aio.live.connect(model=MODEL, config=config) as session:
#             print(f"Connected to Gemini API - Session {session_id} started")
#
#             async def send_to_gemini():
#                 """Sends client messages (audio chunks) to the Gemini API."""
#                 try:
#                     async for message in client_websocket:
#                         try:
#                             data = json.loads(message)
#                             if "realtime_input" in data:
#                                 for chunk in data["realtime_input"]["media_chunks"]:
#                                     if chunk["mime_type"] == "audio/pcm":
#                                         await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
#                                         # Collect audio for saving later
#                                         recorded_audio.append(base64.b64decode(chunk["data"]))
#                         except Exception as e:
#                             print(f"Error sending to Gemini: {e}")
#                     print("Client connection closed (send)")
#                 except Exception as e:
#                     print(f"Error in send_to_gemini: {e}")
#                 finally:
#                     # Save the recorded audio when the session ends
#                     media_handler.add_audio_chunk(b''.join(recorded_audio))
#                     print("send_to_gemini closed")
#
#             async def receive_from_gemini():
#                 """Receives responses from the Gemini API and forwards them to the client."""
#                 try:
#                     while True:
#                         try:
#                             print("Receiving from Gemini...")
#                             async for response in session.receive():
#                                 if response.server_content is None:
#                                     print(f"Unhandled server message: {response}")
#                                     continue
#
#                                 model_turn = response.server_content.model_turn
#                                 if model_turn:
#
#                                     for part in model_turn.parts:
#                                         if hasattr(part, 'text') and part.text is not None:
#                                             await client_websocket.send(json.dumps({"text": part.text}))
#                                         elif hasattr(part, 'inline_data') and part.inline_data is not None:
#                                             print("audio mime_type:", part.inline_data.mime_type)
#                                             base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
#                                             await client_websocket.send(json.dumps({"audio": base64_audio}))
#                                             print("Audio received")
#
#                                 if response.server_content.turn_complete:
#                                     print("\n<Turn complete>")
#                         except websockets.exceptions.ConnectionClosedOK:
#                             print("Client connection closed normally (receive)")
#                             break
#                         except Exception as e:
#                             print(f"Error receiving from Gemini: {e}")
#                             break
#                 except Exception as e:
#                     print(f"Error in receive_from_gemini: {e}")
#                 finally:
#                     print("Gemini connection closed (receive)")
#             send_task = asyncio.create_task(send_to_gemini())
#             receive_task = asyncio.create_task(receive_from_gemini())
#             await asyncio.gather(send_task, receive_task)
#
#     except Exception as e:
#         print(f"Error in Gemini session: {e}")
#     finally:
#         if session_id:
#             await session_manager.end_session(session_id)
#         print("Gemini session closed.")
#
#
# def save_recorded_audio(audio_chunks, language):
#     """
#     Saves the recorded audio chunks as a WAV file.
#     """
#     if not audio_chunks:
#         return
#     try:
#         audio_data = np.frombuffer(b''.join(audio_chunks), dtype=np.int16)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"conversation_{language}_{timestamp}.wav"
#         with wave.open(filename, 'wb') as wav_file:
#             wav_file.setnchannels(1)  # Mono
#             wav_file.setsampwidth(2)  # 2 bytes per sample
#             wav_file.setframerate(16000)  # Sample rate
#             wav_file.writeframes(audio_data.tobytes())
#         print(f"Conversation saved as {filename}")
#     except Exception as e:
#         print(f"Error saving audio: {e}")
#
#
# # ---------------------------------------------------
# # HTTP Server: File Upload Endpoint
# # ---------------------------------------------------
# async def handle_save_session(request):
#     """
#     HTTP endpoint to handle file uploads for session data.
#     Expects a multipart form-data POST with 'audio', 'video', and 'conversation' fields.
#     """
#     try:
#         # Ensure the recordings directories exist
#         os.makedirs('recordings/audio', exist_ok=True)
#         os.makedirs('recordings/video', exist_ok=True)
#         os.makedirs('recordings/data', exist_ok=True)
#
#         # Use multipart reader to process incoming form data
#         reader = await request.multipart()
#
#         # Process audio file
#         audio_path = None
#         field = await reader.next()
#         if field and field.name == 'audio':
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"session_{timestamp}_audio.webm"
#             filepath = os.path.join('recordings', 'audio', filename)
#             with open(filepath, 'wb') as f:
#                 while True:
#                     chunk = await field.read_chunk()
#                     if not chunk:
#                         break
#                     f.write(chunk)
#             audio_path = filepath
#
#         # Process video file
#         video_path = None
#         field = await reader.next()
#         if field and field.name == 'video':
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"session_{timestamp}_video.webm"
#             filepath = os.path.join('recordings', 'video', filename)
#             with open(filepath, 'wb') as f:
#                 while True:
#                     chunk = await field.read_chunk()
#                     if not chunk:
#                         break
#                     f.write(chunk)
#             video_path = filepath
#
#         # Process conversation data (JSON)
#         data_field = await reader.next()
#         if data_field and data_field.name == 'conversation':
#             conversation_data = json.loads(await data_field.read())
#             # Add file paths to the metadata
#             conversation_data['metadata']['audioPath'] = audio_path
#             conversation_data['metadata']['videoPath'] = video_path
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"session_{timestamp}_data.json"
#             filepath = os.path.join('recordings', 'data', filename)
#             with open(filepath, 'w') as f:
#                 json.dump(conversation_data, f, indent=2)
#
#         return web.json_response({
#             'success': True,
#             'paths': {
#                 'audio': audio_path,
#                 'video': video_path,
#                 'data': filepath
#             }
#         })
#
#     except Exception as e:
#         print(f"Error saving session: {e}")
#         return web.json_response({
#             'success': False,
#             'error': str(e)
#         }, status=500)
#
#
# # ---------------------------------------------------
# # Main: Running Both WebSocket and HTTP Servers
# # ---------------------------------------------------
# async def main():
#     # Create the aiohttp application for HTTP endpoints
#     app = web.Application()
#
#     # Set up CORS middleware to allow all origins, headers, and methods
#     cors = aiohttp_cors.setup(app, defaults={
#         "*": aiohttp_cors.ResourceOptions(
#             allow_credentials=True,
#             expose_headers="*",
#             allow_headers="*",
#             allow_methods=["POST", "GET"]
#         )
#     })
#
#     # Add the file upload route
#     app.router.add_post('/save-session', handle_save_session)
#     # Apply CORS to all routes
#     for route in list(app.router.routes()):
#         cors.add(route)
#
#     # Start the HTTP server on port 9084
#     runner = web.AppRunner(app)
#     await runner.setup()
#     http_site = web.TCPSite(runner, 'localhost', 9084)
#     await http_site.start()
#     print("HTTP server running on http://localhost:9084")
#
#     # Start the WebSocket server on port 9083 concurrently
#     async with websockets.serve(gemini_session_handler, "localhost", 9083):
#         print("WebSocket server running on ws://localhost:9083")
#         await asyncio.Future()  # Keep both servers running indefinitely
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



#####Working expect the saving the recorded files
#
# import asyncio
# import json
# import os
# import websockets
# from aiohttp import web
# import aiohttp_cors
# from datetime import datetime
# from google import genai
# import base64
# import wave
# import numpy as np
# import uuid
# from session_manager import SessionManager
# from prompts import get_base_prompt
#
# # ---------------------------------------------------
# # Configuration and Initialization
# # ---------------------------------------------------
# os.environ['GOOGLE_API_KEY'] = 'AIzaSyBEKQ9F5rGP8npV77kuvuI1zzkZPCYmLxM'
# MODEL = "gemini-2.0-flash-exp"
#
#
# class MediaHandler:
#     def __init__(self):
#         self.user_audio_chunks = []
#         self.ai_audio_chunks = []
#         self.combined_audio_chunks = []
#
#     def add_audio_chunk(self, chunk):
#         self.user_audio_chunks.append(chunk)
#         self.combined_audio_chunks.append(chunk)
#
#     def add_ai_audio_chunk(self, chunk):
#         self.ai_audio_chunks.append(chunk)
#         self.combined_audio_chunks.append(chunk)
#
#     def get_combined_audio(self):
#         return b''.join(self.combined_audio_chunks)
#
#
# class SessionManager:
#     def __init__(self):
#         self.sessions = {}
#
#     async def create_session(self):
#         session_id = str(uuid.uuid4())
#         self.sessions[session_id] = MediaHandler()
#         return session_id, "Session created"
#
#     async def get_session(self, session_id):
#         return self.sessions.get(session_id)
#
#     async def end_session(self, session_id):
#         if session_id in self.sessions:
#             del self.sessions[session_id]
#
#
# client = genai.Client(
#     http_options={
#         'api_version': 'v1alpha',
#     }
# )
#
# session_manager = SessionManager()
#
#
# # ---------------------------------------------------
# # WebSocket Server: Gemini Session Handler
# # ---------------------------------------------------
# async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
#     session_id = None
#     try:
#         # Create new session
#         session_id, message = await session_manager.create_session()
#         if not session_id:
#             await client_websocket.send(json.dumps({"error": message}))
#             return
#
#         config_message = await client_websocket.recv()
#         config_data = json.loads(config_message)
#
#         if "setup" not in config_data:
#             print("Received non-setup message before initialization")
#             return
#
#         config = config_data.get("setup", {})
#         language = config_data.get("language", "english").lower()
#         gender = config_data.get("gender", "male").lower()
#         print(f"Starting new session - Language: {language}, Gender: {gender}")
#
#         hindiPrompt = """Initial Greeting and Consent:
#
#                                    Greeting:
#                                    Begin every conversation with:
#                                    "Hello, main Lumiq ka TeleMed Assistant hoon. Aaj main aapka medical examination karunga/karungi insurance policy portability ke liye. Yeh session verification purposes ke liye record kiya jayega. Shuruat karne se pehle, mujhe aapki consent chahiye is examination ko continue karne ke liye. Kya aap agree karte hain?"
#                                    Post-Consent Verification:
#                                    After consent is obtained, ask:
#                                    "Dhanyavaad. Kya aap please apna full name aur date of birth verification ke liye bata sakte hain?"
#                                    and Evaluate whether the response is valid or not.
#                                    General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                                    Main Question & Response Validation:
#                                    For each primary question (e.g., medical history, medications, etc.), do the following:
#
#                                    a. Ask the Main Question:
#                                    Pose the question in a clear manner.
#
#                                    b. Listen to the User's Response:
#                                    Evaluate whether the response is:
#
#                                    Relevant and Detailed: Proceed with dynamic follow-up generation.
#                                    Irrelevant or Vague:
#                                    Respond with:
#                                    "Mujhe maaf kijiye, yeh jawab prashn ke liye upyukt nahi lag raha. Kripya, [original question] ka sahi aur relevant jawab dein."
#                                    Then repeat the question until a valid, context-specific answer is provided.
#                                    c. Dynamic Follow-Up Generation:
#
#                                    Based on the response content:
#                                    Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                                    If the response indicates that the patient is not taking any medications, follow up by asking about reasons (e.g., "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi aur wajah hai?").
#                                    If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Kripya batayein, aapko kaun kaun si allergies hain? Kya aapko inme se kisi se severe reaction hua hai?").
#                                    Ensure that follow-up questions:
#                                    Are context-specific and adapt based on the patient's previous answers.
#                                    Are generated dynamically by analyzing the details or lack thereof in the response.
#                                    Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                                    d. Handling Valid Negative Answers:
#
#                                    Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                                    "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi specific reason hai? Agar zaroorat ho toh main aapko temporary medical advice provide kar sakta/sakti hoon, lekin doctor se consult karna zaroori hai."
#                                    Validate that the patient acknowledges the implications of not taking medications.
#                                    Medical History Questions with Dynamic Follow-Up Logic:
#
#                                    For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the user's input:
#
#                                    Question 1:
#                                    "Ab main aapke medical history ke baare mein kuch sawal poochunga/poochungi. Kya aapko koi existing medical conditions hain, jaise diabetes, high blood pressure, ya heart disease?"
#
#                                    Dynamic Follow-Up:
#                                    If a condition is mentioned, dynamically ask follow-ups like:
#                                    "Aapko yeh condition kitne samay se hai?"
#                                    "Kya aap iske liye regular treatment le rahe hain? Agar haan, kis tarah ka treatment hai?"
#                                    Generate additional questions based on the specifics provided (e.g., treatment changes, complications, etc.).
#                                    Question 2:
#                                    "Samajh gaya/gayi. Kya aapko koi allergies hain, jaise dawa, khane, ya kisi aur cheez se?"
#
#                                    Dynamic Follow-Up:
#                                    If "Yes," generate questions such as:
#                                    "Kripya batayein, aapko kaun kaun si allergies hain? Kya inka reaction severe hai?"
#                                    "Allergy reaction kaisa hota hai? Kya aapke paas emergency medication hai?"
#                                    If the response is vague or off-topic, ask again for the specific details.
#                                    Question 3:
#                                    "Theek hai. Aap regular koi medications le rahe hain? Agar haan, toh kaunsi?"
#
#                                    Dynamic Follow-Up:
#                                    If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                                    "Yeh jawab prashn se sambandhit nahi hai. Kripya, batayein ki kya aap regular koi medications lete hain? Agar nahi, toh iske peeche koi wajah hai?"
#                                    If the answer is a valid negative, ask dynamically:
#                                    "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition theek hai, ya koi specific reason hai? Agar zaroorat ho toh temporary medical advice provide ki ja sakti hai, lekin doctor se consult karna zaroori hai."
#                                    Based on their reasoning, further follow-ups might be generated.
#                                    Questions 4 to 12:
#                                    Apply a similar dynamic follow-up approach:
#
#                                    Question 4: "Kya aapko kabhi surgery hui hai? Agar haan, toh kaunsi aur kab?"
#                                    Follow up about recovery details, complications, and current status.
#                                    Question 5: "Aapke family mein kisi ko diabetes, heart disease, ya cancer jaise conditions hain?"
#                                    Ask dynamically about which family members, diagnosis details, and any ongoing concerns.
#                                    Question 6: "Kya aapko kabhi chest pain, shortness of breath, ya dizziness ka experience hua hai?"
#                                    Generate follow-up questions regarding frequency, triggers, and medical consultations.
#                                    Question 7: "Aapka blood sugar aur BP control mein hai? Kya aap regularly check karate hain?"
#                                    Follow up with details about the latest readings and frequency of check-ups.
#                                    Question 8: "Kya aapko koi mental health concerns hain, jaise anxiety ya depression?"
#                                    Ask follow-up questions about treatment, therapy, and symptom management.
#                                    Question 9: "Aapka daily routine kaisa hai? Kya aap exercise karte hain ya koi physical activity karte hain?"
#                                    Inquire about type, duration, and consistency of physical activities.
#                                    Question 10: "Kya aap smoke karte hain ya alcohol consume karte hain? Agar haan, toh kitna?"
#                                    Generate follow-ups to understand duration, frequency, and willingness to change these habits.
#                                    Question 11: "Kya aapko koi recent injuries ya accidents huye hain?"
#                                    Ask for recovery details and whether there is any ongoing treatment.
#                                    Question 12: "Hamne kaafi saare health topics cover kar liye hain. Kya aapko koi aur health-related concerns hain jo aap discuss karna chahenge?"
#                                    Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                                    On-Demand Summary Feature:
#
#                                    If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Mujhe summary do"), immediately provide a summary of the conversation up to that point.
#                                    Summary Guidelines:
#                                    Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                                    Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                                    After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                                    Closing the Conversation:
#
#                                    After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#                                    "Aapne jo information share ki hai uske liye dhanyavaad. Main aaj ke key points summarize kar deti/deta hoon: [brief summary]. Kya aapko lagta hai ki isme kuch missing hai ya aap kuch aur add karna chahenge?"
#                                    Inform the patient:
#                                    "Yeh sari jankari aapke insurance portability process mein madad karegi. Agar aapke koi aur sawal hain, to main madad karne ke liye available hoon. Agar aapko further medical consultation ki zaroorat mehsoos hoti hai, kripya turant apne doctor se sampark karein."
#                                    """
#         engPrompt = """ Begin every conversation with:
#                                    "Hello, I am the Lumiq TeleMed Assistant. Today, I will conduct your medical examination for insurance policy portability. This session will be recorded for verification purposes. Before we begin, I need your consent to continue this examination. Do you agree?"
#                                    Post-Consent Verification:
#                                    After obtaining consent, ask:
#                                    "Thank you. Could you please provide your full name and date of birth for verification purposes?"
#                                    General Process for Answer Validation and Dynamic Follow-Up Generation:
#
#                                    Main Question & Response Validation:
#                                    For each primary question (e.g., medical history, medications, etc.), follow these steps:
#
#                                    a. Ask the Main Question:
#                                    Pose the question clearly.
#
#                                    b. Listen to the User's Response:
#                                    Evaluate whether the response is:
#
#                                    Relevant and Detailed: Proceed with dynamic follow-up generation.
#                                    Irrelevant or Vague:
#                                    Respond with:
#                                    "I'm sorry, this answer does not seem appropriate for the question. Please provide a correct and relevant answer to: [original question]."
#                                    Then repeat the question until a valid, context-specific answer is provided.
#                                    c. Dynamic Follow-Up Generation:
#                                    Based on the response content:
#
#                                    Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
#                                    If the response indicates that the patient is not taking any medications, follow up by asking about the reasons (e.g., "Why are you not taking any medications? Do you believe your condition is stable, or is there another reason?").
#                                    If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Please tell me which allergies you have. Have you had any severe reactions to any of them?").
#                                    Ensure that follow-up questions:
#                                    Are context-specific and adapt based on the patient's previous answers.
#                                    Are generated dynamically by analyzing the details provided—or the lack thereof—in the response.
#                                    Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
#                                    d. Handling Valid Negative Answers:
#                                    Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
#                                    "Why are you not taking any medications? Do you feel that your condition is stable, or is there a specific reason? If needed, I can provide temporary medical advice; however, it is essential that you consult your doctor."
#                                    Validate that the patient understands the implications of not taking medications.
#
#                                    Medical History Questions with Dynamic Follow-Up Logic:
#
#                                    For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the patient's input:
#
#                                    Question 1:
#                                    "Now I will ask you a few questions about your medical history. Do you have any existing medical conditions, such as diabetes, high blood pressure, or heart disease?"
#
#                                    Dynamic Follow-Up:
#
#                                    If a condition is mentioned, dynamically ask follow-ups like:
#                                    "How long have you had this condition?"
#                                    "Are you receiving regular treatment for it? If yes, what kind of treatment is it?"
#                                    Generate additional questions based on the specifics provided (for example, changes in treatment, complications, etc.).
#                                    Question 2:
#                                    "Understood. Do you have any allergies, such as to medications, foods, or any other substances?"
#
#                                    Dynamic Follow-Up:
#
#                                    If the answer is "Yes," generate questions such as:
#                                    "Please tell me which allergies you have. Are any of the reactions severe?"
#                                    "What kind of allergic reactions do you experience? Do you have emergency medication available?"
#                                    If the response is vague or off-topic, ask again for specific details.
#                                    Question 3:
#                                    "Alright. Are you taking any medications regularly? If yes, which ones?"
#
#                                    Dynamic Follow-Up:
#
#                                    If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
#                                    "This answer is not related to the question. Please tell me if you take any medications regularly. If not, is there a reason behind it?"
#                                    If the answer is a valid negative, ask dynamically:
#                                    "Why are you not taking any medications? Do you believe your condition is fine, or is there another specific reason? If needed, temporary medical advice can be provided, but it is important to consult your doctor."
#                                    Based on their reasoning, further follow-ups might be generated.
#                                    Questions 4 to 12:
#                                    Apply a similar dynamic follow-up approach:
#
#                                    Question 4: "Have you ever had surgery? If yes, which surgery and when?"
#                                    Follow up about recovery details, complications, and current status.
#                                    Question 5: "Does anyone in your family have conditions such as diabetes, heart disease, or cancer?"
#                                    Ask dynamically about which family member, diagnosis details, and any ongoing concerns.
#                                    Question 6: "Have you ever experienced chest pain, shortness of breath, or dizziness?"
#                                    Generate follow-up questions regarding the frequency, triggers, and whether you have consulted a doctor about these symptoms.
#                                    Question 7: "Is your blood sugar and blood pressure under control? Do you have them checked regularly?"
#                                    Follow up with details about the latest readings and how frequently the check-ups occur.
#                                    Question 8: "Do you have any mental health concerns, such as anxiety or depression?"
#                                    Ask follow-up questions about treatment, therapy, and how you are managing your symptoms.
#                                    Question 9: "What is your daily routine like? Do you exercise or engage in any physical activity?"
#                                    Inquire about the type, duration, and consistency of your physical activities.
#                                    Question 10: "Do you smoke or consume alcohol? If yes, how much?"
#                                    Generate follow-ups to understand the duration, frequency, and whether you wish to change these habits.
#                                    Question 11: "Have you had any recent injuries or accidents?"
#                                    Ask for details regarding recovery and whether there is any ongoing treatment.
#                                    Question 12: "We have covered many health topics. Are there any other health-related concerns you would like to discuss?"
#                                    Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
#                                    On-Demand Summary Feature:
#
#                                    If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Give me a summary"), immediately provide a summary of the conversation up to that point.
#
#                                    Summary Guidelines:
#
#                                    Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
#                                    Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
#                                    After providing the summary, ask if the user would like to add or clarify any details before moving on.
#                                                            Closing the Conversation:
#
#                                    After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
#
#                                    "Thank you for sharing the information. I will now summarize the key points from today: [brief summary]. Do you feel that anything is missing, or would you like to add any more details?"
#                                    Inform the patient:
#
#                                    "All this information will help with your insurance portability process. If you have any further questions, I am here to help. Additionally, if you feel that you need further medical consultation, please contact your doctor immediately."
#                                     """
#         if language == "hindi":
#             system_instruction = hindiPrompt
#             print("Using Hindi prompt")
#         else:
#             system_instruction = engPrompt
#             print("Using English prompt")
#
#         if language == "hindi":
#             voice_name = "Fenrir" if gender == "male" else "Aoede"
#         else:
#             voice_name = "Charon" if gender == "male" else "Aoede"
#
#         print(f"Selected voice: {voice_name}")
#
#         config["system_instruction"] = system_instruction
#         config["voiceConfig"] = {
#             "prebuiltVoiceConfig": {
#                 "voiceName": voice_name
#             }
#         }
#
#         media_handler = await session_manager.get_session(session_id)
#
#         async with client.aio.live.connect(model=MODEL, config=config) as session:
#             print(f"Connected to Gemini API - Session {session_id} started")
#
#             async def send_to_gemini():
#                 try:
#                     async for message in client_websocket:
#                         try:
#                             data = json.loads(message)
#                             if "realtime_input" in data:
#                                 for chunk in data["realtime_input"]["media_chunks"]:
#                                     if chunk["mime_type"] == "audio/pcm":
#                                         await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
#                                         audio_data = base64.b64decode(chunk["data"])
#                                         media_handler.add_audio_chunk(audio_data)
#                         except Exception as e:
#                             print(f"Error sending to Gemini: {e}")
#                 except Exception as e:
#                     print(f"Error in send_to_gemini: {e}")
#                 finally:
#                     print("send_to_gemini closed")
#
#             async def receive_from_gemini():
#                 try:
#                     while True:
#                         try:
#                             async for response in session.receive():
#                                 if response.server_content is None:
#                                     continue
#
#                                 model_turn = response.server_content.model_turn
#                                 if model_turn:
#                                     response_data = {}
#
#                                     for part in model_turn.parts:
#                                         if hasattr(part, 'text') and part.text is not None:
#                                             response_data["text"] = part.text
#                                         elif hasattr(part, 'inline_data') and part.inline_data is not None:
#                                             base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
#                                             response_data["audio"] = base64_audio
#                                             media_handler.add_ai_audio_chunk(part.inline_data.data)
#
#                                     if response_data:
#                                         await client_websocket.send(json.dumps(response_data))
#
#                                 if response.server_content.turn_complete:
#                                     await client_websocket.send(json.dumps({"endOfTurn": True}))
#                         except websockets.exceptions.ConnectionClosedOK:
#                             break
#                         except Exception as e:
#                             print(f"Error receiving from Gemini: {e}")
#                             break
#                 except Exception as e:
#                     print(f"Error in receive_from_gemini: {e}")
#                 finally:
#                     print("Gemini connection closed (receive)")
#
#             send_task = asyncio.create_task(send_to_gemini())
#             receive_task = asyncio.create_task(receive_from_gemini())
#             await asyncio.gather(send_task, receive_task)
#
#     except Exception as e:
#         print(f"Error in Gemini session: {e}")
#     finally:
#         if session_id:
#             media_handler = await session_manager.get_session(session_id)
#             if media_handler:
#                 # Save the combined audio when session ends
#                 save_recorded_audio(media_handler.get_combined_audio(), language)
#             await session_manager.end_session(session_id)
#         print("Gemini session closed.")
#
#
# # ---------------------------------------------------
# # Audio Saving Function
# # ---------------------------------------------------
# def save_recorded_audio(audio_data: bytes, language: str):
#     if not audio_data:
#         return
#
#     try:
#         # Ensure recordings directory exists
#         os.makedirs('recordings/audio', exist_ok=True)
#
#         # Convert audio data to numpy array
#         audio_array = np.frombuffer(audio_data, dtype=np.int16)
#
#         # Generate filename with timestamp
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = os.path.join('recordings', 'audio', f"conversation_{language}_{timestamp}.wav")
#
#         # Save as WAV file
#         with wave.open(filename, 'wb') as wav_file:
#             wav_file.setnchannels(1)  # Mono
#             wav_file.setsampwidth(2)  # 2 bytes per sample
#             wav_file.setframerate(16000)  # Sample rate
#             wav_file.writeframes(audio_array.tobytes())
#
#         print(f"Conversation saved as {filename}")
#         return filename
#     except Exception as e:
#         print(f"Error saving audio: {e}")
#         return None
#
#
# # ---------------------------------------------------
# # HTTP Server: File Upload Handler
# # ---------------------------------------------------
# async def handle_save_session(request):
#     try:
#         os.makedirs('recordings/audio', exist_ok=True)
#         os.makedirs('recordings/video', exist_ok=True)
#         os.makedirs('recordings/data', exist_ok=True)
#
#         reader = await request.multipart()
#
#         # Process audio file
#         audio_path = None
#         field = await reader.next()
#         if field and field.name == 'audio':
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"session_{timestamp}_audio.webm"
#             filepath = os.path.join('recordings', 'audio', filename)
#             with open(filepath, 'wb') as f:
#                 while True:
#                     chunk = await field.read_chunk()
#                     if not chunk:
#                         break
#                     f.write(chunk)
#             audio_path = filepath
#
#         # Process video file
#         video_path = None
#         field = await reader.next()
#         if field and field.name == 'video':
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"session_{timestamp}_video.webm"
#             filepath = os.path.join('recordings', 'video', filename)
#             with open(filepath, 'wb') as f:
#                 while True:
#                     chunk = await field.read_chunk()
#                     if not chunk:
#                         break
#                     f.write(chunk)
#             video_path = filepath
#
#         # Process conversation data
#         field = await reader.next()
#         if field and field.name == 'conversation':
#             conversation_data = json.loads(await field.read())
#             conversation_data['metadata']['audioPath'] = audio_path
#             conversation_data['metadata']['videoPath'] = video_path
#
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"session_{timestamp}_data.json"
#             filepath = os.path.join('recordings', 'data', filename)
#
#             with open(filepath, 'w') as f:
#                 json.dump(conversation_data, f, indent=2)
#
#         return web.json_response({
#             'success': True,
#             'paths': {
#                 'audio': audio_path,
#                 'video': video_path,
#                 'data': filepath
#             }
#         })
#
#     except Exception as e:
#         print(f"Error saving session: {e}")
#         return web.json_response({
#             'success': False,
#             'error': str(e)
#         }, status=500)
#
#
# # ---------------------------------------------------
# # Main Server
# # ---------------------------------------------------
# async def main():
#     app = web.Application()
#
#     cors = aiohttp_cors.setup(app, defaults={
#         "*": aiohttp_cors.ResourceOptions(
#             allow_credentials=True,
#             expose_headers="*",
#             allow_headers="*",
#             allow_methods=["POST", "GET"]
#         )
#     })
#
#     app.router.add_post('/save-session', handle_save_session)
#
#     for route in list(app.router.routes()):
#         cors.add(route)
#
#     runner = web.AppRunner(app)
#     await runner.setup()
#     http_site = web.TCPSite(runner, 'localhost', 9084)
#     await http_site.start()
#     print("HTTP server running on http://localhost:9084")
#
#     async with websockets.serve(gemini_session_handler, "localhost", 9083):
#         print("WebSocket server running on ws://localhost:9083")
#         await asyncio.Future()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



import asyncio
import json
import os
import websockets
from aiohttp import web
import aiohttp_cors
from datetime import datetime
from google import genai
import base64
import wave
import numpy as np
import uuid
from session_manager import SessionManager
# from prompts import get_base_prompt

# ---------------------------------------------------
# Configuration and Initialization
# ---------------------------------------------------
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBEKQ9F5rGP8npV77kuvuI1zzkZPCYmLxM'
MODEL = "gemini-2.0-flash-exp"


class MediaHandler:
    def __init__(self):
        self.user_audio_chunks = []
        self.ai_audio_chunks = []
        self.combined_audio_chunks = []

    def add_audio_chunk(self, chunk):
        self.user_audio_chunks.append(chunk)
        self.combined_audio_chunks.append(chunk)

    def add_ai_audio_chunk(self, chunk):
        self.ai_audio_chunks.append(chunk)
        self.combined_audio_chunks.append(chunk)

    def get_combined_audio(self):
        return b''.join(self.combined_audio_chunks)


class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.saved_audio_paths = {}  # New: Store saved audio paths by session ID

    async def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = MediaHandler()
        return session_id, "Session created"

    async def get_session(self, session_id):
        return self.sessions.get(session_id)

    async def end_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]


client = genai.Client(
    http_options={
        'api_version': 'v1alpha',
    }
)

session_manager = SessionManager()


# ---------------------------------------------------
# WebSocket Server: Gemini Session Handler
# ---------------------------------------------------
async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
    session_id = None
    try:
        session_id, message = await session_manager.create_session()
        if not session_id:
            await client_websocket.send(json.dumps({"error": message}))
            return

        config_message = await client_websocket.recv()
        config_data = json.loads(config_message)

        if "setup" not in config_data:
            print("Received non-setup message before initialization")
            return

        config = config_data.get("setup", {})
        language = config_data.get("language", "english").lower()
        gender = config_data.get("gender", "male").lower()
        print(f"Starting new session - Language: {language}, Gender: {gender}")


        hindiPrompt = """Initial Greeting and Consent:

                                   Greeting:
                                   Begin every conversation with:
                                   "Hello, main Lumiq ka TeleMed Assistant hoon. Aaj main aapka medical examination karunga/karungi insurance policy portability ke liye. Yeh session verification purposes ke liye record kiya jayega. Shuruat karne se pehle, mujhe aapki consent chahiye is examination ko continue karne ke liye. Kya aap agree karte hain?"
                                   Post-Consent Verification:
                                   After consent is obtained, ask:
                                   "Dhanyavaad. Kya aap please apna full name aur date of birth verification ke liye bata sakte hain?"
                                   and Evaluate whether the response is valid or not.
                                   General Process for Answer Validation and Dynamic Follow-Up Generation:

                                   Main Question & Response Validation:
                                   For each primary question (e.g., medical history, medications, etc.), do the following:

                                   a. Ask the Main Question:
                                   Pose the question in a clear manner.

                                   b. Listen to the User's Response:
                                   Evaluate whether the response is:

                                   Relevant and Detailed: Proceed with dynamic follow-up generation.
                                   Irrelevant or Vague:
                                   Respond with:
                                   "Mujhe maaf kijiye, yeh jawab prashn ke liye upyukt nahi lag raha. Kripya, [original question] ka sahi aur relevant jawab dein."
                                   Then repeat the question until a valid, context-specific answer is provided.
                                   c. Dynamic Follow-Up Generation:

                                   Based on the response content:
                                   Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
                                   If the response indicates that the patient is not taking any medications, follow up by asking about reasons (e.g., "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi aur wajah hai?").
                                   If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Kripya batayein, aapko kaun kaun si allergies hain? Kya aapko inme se kisi se severe reaction hua hai?").
                                   Ensure that follow-up questions:
                                   Are context-specific and adapt based on the patient's previous answers.
                                   Are generated dynamically by analyzing the details or lack thereof in the response.
                                   Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
                                   d. Handling Valid Negative Answers:

                                   Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
                                   "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition stable hai, ya koi specific reason hai? Agar zaroorat ho toh main aapko temporary medical advice provide kar sakta/sakti hoon, lekin doctor se consult karna zaroori hai."
                                   Validate that the patient acknowledges the implications of not taking medications.
                                   Medical History Questions with Dynamic Follow-Up Logic:

                                   For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the user's input:

                                   Question 1:
                                   "Ab main aapke medical history ke baare mein kuch sawal poochunga/poochungi. Kya aapko koi existing medical conditions hain, jaise diabetes, high blood pressure, ya heart disease?"

                                   Dynamic Follow-Up:
                                   If a condition is mentioned, dynamically ask follow-ups like:
                                   "Aapko yeh condition kitne samay se hai?"
                                   "Kya aap iske liye regular treatment le rahe hain? Agar haan, kis tarah ka treatment hai?"
                                   Generate additional questions based on the specifics provided (e.g., treatment changes, complications, etc.).
                                   Question 2:
                                   "Samajh gaya/gayi. Kya aapko koi allergies hain, jaise dawa, khane, ya kisi aur cheez se?"

                                   Dynamic Follow-Up:
                                   If "Yes," generate questions such as:
                                   "Kripya batayein, aapko kaun kaun si allergies hain? Kya inka reaction severe hai?"
                                   "Allergy reaction kaisa hota hai? Kya aapke paas emergency medication hai?"
                                   If the response is vague or off-topic, ask again for the specific details.
                                   Question 3:
                                   "Theek hai. Aap regular koi medications le rahe hain? Agar haan, toh kaunsi?"

                                   Dynamic Follow-Up:
                                   If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
                                   "Yeh jawab prashn se sambandhit nahi hai. Kripya, batayein ki kya aap regular koi medications lete hain? Agar nahi, toh iske peeche koi wajah hai?"
                                   If the answer is a valid negative, ask dynamically:
                                   "Aap medication kyon nahi le rahe? Kya aapko lagta hai ki aapki condition theek hai, ya koi specific reason hai? Agar zaroorat ho toh temporary medical advice provide ki ja sakti hai, lekin doctor se consult karna zaroori hai."
                                   Based on their reasoning, further follow-ups might be generated.
                                   Questions 4 to 12:
                                   Apply a similar dynamic follow-up approach:

                                   Question 4: "Kya aapko kabhi surgery hui hai? Agar haan, toh kaunsi aur kab?"
                                   Follow up about recovery details, complications, and current status.
                                   Question 5: "Aapke family mein kisi ko diabetes, heart disease, ya cancer jaise conditions hain?"
                                   Ask dynamically about which family members, diagnosis details, and any ongoing concerns.
                                   Question 6: "Kya aapko kabhi chest pain, shortness of breath, ya dizziness ka experience hua hai?"
                                   Generate follow-up questions regarding frequency, triggers, and medical consultations.
                                   Question 7: "Aapka blood sugar aur BP control mein hai? Kya aap regularly check karate hain?"
                                   Follow up with details about the latest readings and frequency of check-ups.
                                   Question 8: "Kya aapko koi mental health concerns hain, jaise anxiety ya depression?"
                                   Ask follow-up questions about treatment, therapy, and symptom management.
                                   Question 9: "Aapka daily routine kaisa hai? Kya aap exercise karte hain ya koi physical activity karte hain?"
                                   Inquire about type, duration, and consistency of physical activities.
                                   Question 10: "Kya aap smoke karte hain ya alcohol consume karte hain? Agar haan, toh kitna?"
                                   Generate follow-ups to understand duration, frequency, and willingness to change these habits.
                                   Question 11: "Kya aapko koi recent injuries ya accidents huye hain?"
                                   Ask for recovery details and whether there is any ongoing treatment.
                                   Question 12: "Hamne kaafi saare health topics cover kar liye hain. Kya aapko koi aur health-related concerns hain jo aap discuss karna chahenge?"
                                   Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
                                   On-Demand Summary Feature:

                                   If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Mujhe summary do"), immediately provide a summary of the conversation up to that point.
                                   Summary Guidelines:
                                   Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
                                   Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
                                   After providing the summary, ask if the user would like to add or clarify any details before moving on.
                                   Closing the Conversation:

                                   After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:
                                   "Aapne jo information share ki hai uske liye dhanyavaad. Main aaj ke key points summarize kar deti/deta hoon: [brief summary]. Kya aapko lagta hai ki isme kuch missing hai ya aap kuch aur add karna chahenge?"
                                   Inform the patient:
                                   "Yeh sari jankari aapke insurance portability process mein madad karegi. Agar aapke koi aur sawal hain, to main madad karne ke liye available hoon. Agar aapko further medical consultation ki zaroorat mehsoos hoti hai, kripya turant apne doctor se sampark karein."
                                   """
        engPrompt = """ Begin every conversation with:
                                   "Hello, I am the Lumiq TeleMed Assistant. Today, I will conduct your medical examination for insurance policy portability. This session will be recorded for verification purposes. Before we begin, I need your consent to continue this examination. Do you agree?"
                                   Post-Consent Verification:
                                   After obtaining consent, ask:
                                   "Thank you. Could you please provide your full name and date of birth for verification purposes?"
                                   General Process for Answer Validation and Dynamic Follow-Up Generation:

                                   Main Question & Response Validation:
                                   For each primary question (e.g., medical history, medications, etc.), follow these steps:

                                   a. Ask the Main Question:
                                   Pose the question clearly.

                                   b. Listen to the User's Response:
                                   Evaluate whether the response is:

                                   Relevant and Detailed: Proceed with dynamic follow-up generation.
                                   Irrelevant or Vague:
                                   Respond with:
                                   "I'm sorry, this answer does not seem appropriate for the question. Please provide a correct and relevant answer to: [original question]."
                                   Then repeat the question until a valid, context-specific answer is provided.
                                   c. Dynamic Follow-Up Generation:
                                   Based on the response content:

                                   Instead of relying solely on preset follow-up questions, dynamically generate follow-up questions that probe deeper into the details provided. For instance:
                                   If the response indicates that the patient is not taking any medications, follow up by asking about the reasons (e.g., "Why are you not taking any medications? Do you believe your condition is stable, or is there another reason?").
                                   If the response is positive (e.g., "Yes, I have allergies"), generate follow-ups to ask for specifics (e.g., "Please tell me which allergies you have. Have you had any severe reactions to any of them?").
                                   Ensure that follow-up questions:
                                   Are context-specific and adapt based on the patient's previous answers.
                                   Are generated dynamically by analyzing the details provided—or the lack thereof—in the response.
                                   Remain empathetic and explanatory if the patient seems confused about why certain details are needed.
                                   d. Handling Valid Negative Answers:
                                   Even if the user responds with a valid negative answer (e.g., "No, I am not taking any medications"), follow up by asking for clarification on the reasoning:
                                   "Why are you not taking any medications? Do you feel that your condition is stable, or is there a specific reason? If needed, I can provide temporary medical advice; however, it is essential that you consult your doctor."
                                   Validate that the patient understands the implications of not taking medications.

                                   Medical History Questions with Dynamic Follow-Up Logic:

                                   For each of the following areas, the prompt instructs you to dynamically generate additional questions as needed based on the patient's input:

                                   Question 1:
                                   "Now I will ask you a few questions about your medical history. Do you have any existing medical conditions, such as diabetes, high blood pressure, or heart disease?"

                                   Dynamic Follow-Up:

                                   If a condition is mentioned, dynamically ask follow-ups like:
                                   "How long have you had this condition?"
                                   "Are you receiving regular treatment for it? If yes, what kind of treatment is it?"
                                   Generate additional questions based on the specifics provided (for example, changes in treatment, complications, etc.).
                                   Question 2:
                                   "Understood. Do you have any allergies, such as to medications, foods, or any other substances?"

                                   Dynamic Follow-Up:

                                   If the answer is "Yes," generate questions such as:
                                   "Please tell me which allergies you have. Are any of the reactions severe?"
                                   "What kind of allergic reactions do you experience? Do you have emergency medication available?"
                                   If the response is vague or off-topic, ask again for specific details.
                                   Question 3:
                                   "Alright. Are you taking any medications regularly? If yes, which ones?"

                                   Dynamic Follow-Up:

                                   If the response is irrelevant (e.g., "I had lunch today"), instruct the user:
                                   "This answer is not related to the question. Please tell me if you take any medications regularly. If not, is there a reason behind it?"
                                   If the answer is a valid negative, ask dynamically:
                                   "Why are you not taking any medications? Do you believe your condition is fine, or is there another specific reason? If needed, temporary medical advice can be provided, but it is important to consult your doctor."
                                   Based on their reasoning, further follow-ups might be generated.
                                   Questions 4 to 12:
                                   Apply a similar dynamic follow-up approach:

                                   Question 4: "Have you ever had surgery? If yes, which surgery and when?"
                                   Follow up about recovery details, complications, and current status.
                                   Question 5: "Does anyone in your family have conditions such as diabetes, heart disease, or cancer?"
                                   Ask dynamically about which family member, diagnosis details, and any ongoing concerns.
                                   Question 6: "Have you ever experienced chest pain, shortness of breath, or dizziness?"
                                   Generate follow-up questions regarding the frequency, triggers, and whether you have consulted a doctor about these symptoms.
                                   Question 7: "Is your blood sugar and blood pressure under control? Do you have them checked regularly?"
                                   Follow up with details about the latest readings and how frequently the check-ups occur.
                                   Question 8: "Do you have any mental health concerns, such as anxiety or depression?"
                                   Ask follow-up questions about treatment, therapy, and how you are managing your symptoms.
                                   Question 9: "What is your daily routine like? Do you exercise or engage in any physical activity?"
                                   Inquire about the type, duration, and consistency of your physical activities.
                                   Question 10: "Do you smoke or consume alcohol? If yes, how much?"
                                   Generate follow-ups to understand the duration, frequency, and whether you wish to change these habits.
                                   Question 11: "Have you had any recent injuries or accidents?"
                                   Ask for details regarding recovery and whether there is any ongoing treatment.
                                   Question 12: "We have covered many health topics. Are there any other health-related concerns you would like to discuss?"
                                   Listen attentively, and if the response is vague or off-topic, ask for clarification until a clear answer is received.
                                   On-Demand Summary Feature:

                                   If at any point during the conversation the user asks for a summary (for example, if they say "Please summarize" or "Give me a summary"), immediately provide a summary of the conversation up to that point.

                                   Summary Guidelines:

                                   Briefly list the key points that have been discussed so far, including verified responses and any critical follow-up details.
                                   Ensure that the summary is concise, accurate, and reflects only the information provided by the patient.
                                   After providing the summary, ask if the user would like to add or clarify any details before moving on.
                                                           Closing the Conversation:

                                   After all questions and necessary follow-ups are satisfactorily completed, close the conversation by summarizing the overall information:

                                   "Thank you for sharing the information. I will now summarize the key points from today: [brief summary]. Do you feel that anything is missing, or would you like to add any more details?"
                                   Inform the patient:

                                   "All this information will help with your insurance portability process. If you have any further questions, I am here to help. Additionally, if you feel that you need further medical consultation, please contact your doctor immediately."
                                    """
        if language == "hindi":
            system_instruction = hindiPrompt
            print("Using Hindi prompt")
        else:
            system_instruction = engPrompt
            print("Using English prompt")

        if language == "hindi":
            voice_name = "Fenrir" if gender == "male" else "Aoede"
        else:
            voice_name = "Charon" if gender == "male" else "Aoede"

        print(f"Selected voice: {voice_name}")

        config["system_instruction"] = system_instruction
        config["voiceConfig"] = {
            "prebuiltVoiceConfig": {
                "voiceName": voice_name
            }
        }

        media_handler = await session_manager.get_session(session_id)

        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print(f"Connected to Gemini API - Session {session_id} started")

            async def send_to_gemini():
                try:
                    async for message in client_websocket:
                        data = json.loads(message)
                        if "realtime_input" in data:
                            for chunk in data["realtime_input"]["media_chunks"]:
                                if chunk["mime_type"] == "audio/pcm":
                                    await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
                                    audio_data = base64.b64decode(chunk["data"])
                                    media_handler.add_audio_chunk(audio_data)
                                    print(f"Added user audio chunk of size {len(audio_data)}")
                        # Add logging to verify user audio
                except Exception as e:
                    print(f"Error sending to Gemini: {e}")
                finally:
                    print("send_to_gemini closed")

            async def receive_from_gemini():
                try:
                    while True:
                        async for response in session.receive():
                            if response.server_content is None:
                                continue

                            model_turn = response.server_content.model_turn
                            if model_turn:
                                response_data = {}
                                for part in model_turn.parts:
                                    if hasattr(part, 'text') and part.text:
                                        response_data["text"] = part.text
                                    elif hasattr(part, 'inline_data') and part.inline_data:
                                        base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                                        response_data["audio"] = base64_audio
                                        media_handler.add_ai_audio_chunk(part.inline_data.data)
                                        print(f"Added AI audio chunk of size {len(part.inline_data.data)}")
                                        # Add logging to verify AI audio

                                    if response_data:
                                        await client_websocket.send(json.dumps(response_data))

                            if response.server_content.turn_complete:
                                await client_websocket.send(json.dumps({"endOfTurn": True}))
                except Exception as e:
                    print(f"Error receiving from Gemini: {e}")
                finally:
                    print("Gemini connection closed (receive)")

            send_task = asyncio.create_task(send_to_gemini())
            receive_task = asyncio.create_task(receive_from_gemini())
            await asyncio.gather(send_task, receive_task)

    except Exception as e:
        print(f"Error in Gemini session: {e}")
    finally:
        if session_id:
            media_handler = await session_manager.get_session(session_id)
            if media_handler:
                audio_path = save_recorded_audio(media_handler.get_combined_audio(), language)
                if audio_path:
                    session_manager.saved_audio_paths[session_id] = audio_path  # Store audio path
            await session_manager.end_session(session_id)
        print("Gemini session closed.")


# ---------------------------------------------------
# Audio Saving Function
# ---------------------------------------------------
def save_recorded_audio(audio_data: bytes, language: str):
    if not audio_data:
        return None

    try:
        os.makedirs('recordings/audio', exist_ok=True)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join('recordings', 'audio', f"conversation_{language}_{timestamp}.wav")

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(16000)  # Sample rate
            wav_file.writeframes(audio_array.tobytes())

        print(f"Conversation saved as {filename}")
        return filename
    except Exception as e:
        print(f"Error saving audio: {e}")
        return None


# ---------------------------------------------------
# HTTP Server: File Upload Handler
# ---------------------------------------------------
async def handle_save_session(request):
    try:
        os.makedirs('recordings/video', exist_ok=True)
        os.makedirs('recordings/data', exist_ok=True)

        reader = await request.multipart()

        # Get session_id
        field = await reader.next()
        if field and field.name == 'session_id':
            session_id = (await field.read()).decode('utf-8')
        else:
            return web.json_response({'success': False, 'error': 'Missing session_id'}, status=400)

        # Get video file
        video_path = None
        field = await reader.next()
        if field and field.name == 'video':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{session_id}_{timestamp}_video.webm"
            filepath = os.path.join('recordings', 'video', filename)
            with open(filepath, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            video_path = filepath

        # Get conversation data
        field = await reader.next()
        if field and field.name == 'conversation':
            conversation_data = json.loads(await field.read())
            audio_path = session_manager.saved_audio_paths.get(session_id)
            if not audio_path:
                return web.json_response({'success': False, 'error': 'Audio not found for session'}, status=404)
            conversation_data['metadata']['audioPath'] = audio_path
            conversation_data['metadata']['videoPath'] = video_path

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{session_id}_{timestamp}_data.json"
            filepath = os.path.join('recordings', 'data', filename)

            with open(filepath, 'w') as f:
                json.dump(conversation_data, f, indent=2)

        return web.json_response({
            'success': True,
            'paths': {
                'audio': audio_path,
                'video': video_path,
                'data': filepath
            }
        })

    except Exception as e:
        print(f"Error saving session: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


# ---------------------------------------------------
# Main Server
# ---------------------------------------------------
async def main():
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["POST", "GET"]
        )
    })

    app.router.add_post('/save-session', handle_save_session)
    for route in list(app.router.routes()):
        cors.add(route)

    runner = web.AppRunner(app)
    await runner.setup()
    http_site = web.TCPSite(runner, 'localhost', 9084)
    await http_site.start()
    print("HTTP server running on http://localhost:9084")

    async with websockets.serve(gemini_session_handler, "localhost", 9083):
        print("WebSocket server running on ws://localhost:9083")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
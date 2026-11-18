from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Changed this
    google_api_key="AIzaSyAtg-gOdmv-0rLan-TYwN2N-J2hph4lQJg"
)

# response = llm.invoke("If you become hospital management ai agent then what things can you do? Can do tool calling like sending emails, sending messages,saving data into drive if I use langchain tools concept?")
# print(response.content)







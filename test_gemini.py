import google.genai as genai

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyCsEcoy9hSXj0qzoaY8tXgpb_2-PCjhB98")

# Simple test
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Hello Gemini! Summarize why pandas is used in Python."
)

print(response.text)

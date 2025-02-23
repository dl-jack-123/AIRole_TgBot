from google import genai
import asyncio

from airole_tgbot.tgbot import main

# API_KEY = 'AIzaSyAKQPxDUCXAnOXqNIJv9_pgh6OaA7ak8mM'
# client = genai.Client(api_key=API_KEY)
#
# response = client.models.generate_content(
#     model='gemini-2.0-flash',
#     contents='關於角色對話的一些範例及功能，用 Telegram BOT 來實現的功能'
# )
# print(response.text)

if __name__ == '__main__':
    asyncio.run(main())

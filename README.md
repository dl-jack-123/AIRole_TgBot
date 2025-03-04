# AIRole_TgBot


好的，這裡提供一些利用 Telegram Bot 實現角色對話功能的範例和說明，以及相關功能：
**核心概念：**
*   **角色資料庫：** Bot 需要儲存不同角色的資訊，例如：名稱、個性、口頭禪、背景故事、對話風格等。可以使用 JSON 檔案、資料庫（如 SQLite、MongoDB）來儲存這些資料。
*   **對話狀態管理：** Bot 需要追蹤目前的對話狀態，例如：目前與哪個角色互動、對話的階段、使用者提供的資訊等。可以使用 Session 或簡單的變數來管理。
*   **自然語言處理 (NLP)：** 選擇性功能。如果想讓 Bot 更自然地理解使用者意圖，可以使用 NLP 技術來分析使用者的訊息。
*   **狀態機 (State Machine)：** 用於管理複雜的對話流程，例如詢問一系列問題來創建角色。
**範例 1：簡單的角色扮演**
*   **功能：** 選擇一個預設角色，Bot 會以該角色的身份回覆訊息。
*   **實作：**
    1.  **角色資料：**
        ```json
        {
            "characters": [
                {
                    "name": "SarcasticBot",
                    "description": "A bot with a sarcastic and cynical attitude.",
                    "greeting": "Oh great, another human. What do you want?",
                    "response_patterns": [
                        {"pattern": "hello", "response": "Well, hello to you too. I'm just thrilled to be talking to you."},
                        {"pattern": "how are you", "response": "Living the dream, one pointless conversation at a time."},
                        {"pattern": "*", "response": "That's...interesting. Tell me more, I guess."}
                    ]
                },
                {
                    "name": "EnthusiasticBot",
                    "description": "A bot that's overly excited about everything!",
                    "greeting": "Hiya! I'm so excited to talk to you!",
                    "response_patterns": [
                        {"pattern": "hello", "response": "HELLO! It's so great to hear from you!"},
                        {"pattern": "how are you", "response": "I'm doing FANTASTIC! How about you?"},
                        {"pattern": "*", "response": "WOW! That's amazing!"}
                    ]
                }
            ]
        }
        ```
    2.  **Telegram Bot 程式碼 (範例，Python + `python-telegram-bot`):**
        ```python
        import telegram
        from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
        import json
        import random
        # Load character data from JSON
        with open("characters.json", "r") as f:
            characters_data = json.load(f)
            characters = characters_data["characters"]
        # Global variable to store the selected character
        selected_character = None
        def start(update, context):
            """Sends a welcome message and lists available characters."""
            character_list = "\n".join([f"- {c['name']}: {c['description']}" for c in characters])
            update.message.reply_text(f"Welcome! Choose a character to talk to:\n{character_list}\n\nUse /choose <character_name> to select a character.")
        def choose(update, context):
            """Selects a character based on user input."""
            global selected_character
            character_name = " ".join(context.args).strip()
            for character in characters:
                if character["name"].lower() == character_name.lower():
                    selected_character = character
                    update.message.reply_text(f"You have chosen to talk to {character['name']}! {character['greeting']}")
                    return
            update.message.reply_text(f"Character '{character_name}' not found.  Use /start to see the list of available characters.")
        def echo(update, context):
            """Echoes the user message as the selected character."""
            global selected_character
            if selected_character:
                user_message = update.message.text.lower()
                response = None
                # Find a matching response pattern
                for pattern in selected_character["response_patterns"]:
                    if pattern["pattern"] == "*" or pattern["pattern"] in user_message:  # Simple pattern matching
                        response = pattern["response"]
                        break
                if response:
                    update.message.reply_text(response)
                else:
                    update.message.reply_text("I don't know how to respond to that...")
            else:
                update.message.reply_text("Please choose a character first using /choose <character_name>.")
        def main():
            """Start the bot."""
            # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
            updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
            # Get the dispatcher to register handlers
            dp = updater.dispatcher
            # Add command handlers
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("choose", choose))
            # Add message handler (for echoing messages)
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
            # Start the Bot
            updater.start_polling()
            # Run the bot until you press Ctrl-C or the process receives SIGINT,
            # SIGTERM or SIGABRT. This should be used most of the time, since
            # start_polling() is non-blocking and will stop the bot gracefully.
            updater.idle()
        if __name__ == '__main__':
            main()
        ```
*   **使用方式：**
    1.  `/start`: 顯示歡迎訊息和角色列表。
    2.  `/choose <角色名稱>`: 選擇要扮演的角色 (例如 `/choose SarcasticBot`)
    3.  之後發送的訊息，Bot 都會以該角色的身份回覆。
**範例 2：角色創建與互動**
*   **功能：** 使用者可以創建自己的角色，並與其互動。
*   **實作：**
    1.  **角色創建：**
        *   使用狀態機來引導使用者提供角色資訊 (名稱、個性、背景等)。
        *   提供指令 (例如 `/create`) 觸發角色創建流程。
        *   Bot 詢問一系列問題，使用者依序回答。
        *   將創建的角色儲存到資料庫。
    2.  **角色互動：**
        *   使用者可以選擇與哪個角色互動。
        *   Bot 根據角色的資訊，產生回覆。
        *   可以使用規則或簡單的 AI 模型 (例如 GPT-2) 來生成更多樣化的回覆。
*   **程式碼片段 (Python + `python-telegram-bot`，簡化):**
    ```python
    from telegram import ReplyKeyboardMarkup
    from telegram.ext import (
        Updater,
        CommandHandler,
        MessageHandler,
        Filters,
        ConversationHandler,
    )
    # Define states for the conversation
    NAME, PERSONALITY, BACKGROUND = range(3)
    def create_character(update, context):
        update.message.reply_text("Let's create a character! What's their name?")
        return NAME
    def name(update, context):
        context.user_data['name'] = update.message.text
        update.message.reply_text("Okay, what's their personality like? (e.g., kind, sarcastic, etc.)")
        return PERSONALITY
    def personality(update, context):
        context.user_data['personality'] = update.message.text
        update.message.reply_text("Great! Now, what's a brief background story for your character?")
        return BACKGROUND
    def background(update, context):
        context.user_data['background'] = update.message.text
        # Save the character to a database or file
        # (Implementation omitted for brevity)
        update.message.reply_text(f"Character created! Name: {context.user_data['name']}, Personality: {context.user_data['personality']}, Background: {context.user_data['background']}")
        return ConversationHandler.END
    def cancel(update, context):
        update.message.reply_text("Character creation cancelled.")
        return ConversationHandler.END
    def main():
        # ... (Bot initialization) ...
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('create', create_character)],
            states={
                NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
                PERSONALITY: [MessageHandler(Filters.text & ~Filters.command, personality)],
                BACKGROUND: [MessageHandler(Filters.text & ~Filters.command, background)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        dp.add_handler(conv_handler)
        # ... (Start the bot) ...
    if __name__ == '__main__':
        main()
    ```
*   **使用方式：**
    1.  `/create`: 啟動角色創建流程。
    2.  Bot 會依序詢問角色名稱、個性、背景故事。
    3.  使用者依序回答。
    4.  Bot 儲存角色資訊，並顯示創建完成的訊息。
    5.  後續可以加入選擇與角色互動的指令。
**範例 3：進階角色互動 (NLP + AI)**
*   **功能：** 利用 NLP 和 AI 模型，讓 Bot 更智能地理解使用者的訊息，並產生更自然的回覆。
*   **實作：**
    1.  **NLP (例如 Rasa, spaCy):**
        *   訓練 NLP 模型，識別使用者的意圖 (例如問候、詢問、命令等)。
        *   提取使用者訊息中的實體 (例如角色名稱、地點、時間等)。
    2.  **AI 模型 (例如 GPT-2, GPT-3):**
        *   使用角色的資訊 (名稱、個性、背景故事) 來微調 AI 模型。
        *   根據使用者意圖和實體，生成更符合角色個性的回覆。
*   **技術挑戰：**
    *   需要較高的技術門檻。
    *   需要大量的訓練資料。
    *   需要較高的運算資源。
**其他功能：**
*   **角色列表：** 顯示已創建的角色列表。
*   **角色編輯：** 允許使用者編輯已創建的角色資訊。
*   **角色刪除：** 允許使用者刪除已創建的角色。
*   **角色共享：** 允許使用者將自己創建的角色分享給其他使用者。
*   **情境模擬：** 提供不同的情境，讓使用者與角色進行互動。
*   **多人對話：** 允許多個使用者同時與一個或多個角色互動。
*   **語音互動：** 支援語音輸入和輸出。
*   **圖像互動：** 支援圖像生成和識別。
**選擇適合的功能：**
選擇哪些功能取決於你的目標和技術能力。 從簡單的範例開始，逐步增加功能。 重要的是要考慮使用者體驗，並確保 Bot 的互動方式自然且有趣。
希望這些範例和說明對你有所幫助！ 記得根據你的具體需求調整程式碼和功能。

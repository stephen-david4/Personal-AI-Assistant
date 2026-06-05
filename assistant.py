import ollama

def chat_with_ai(user_message,conversation_his=[]):

    conversation_his.append({
        'role':'user',
        'content':user_message
    })
    
    response = ollama.chat(
        model='llama3.2:1b',
        messages=conversation_his
    )

    ai_response = response['message']['content']

    conversation_his.append({
        'role':'assistant',
        'content':ai_response
    })

    return ai_response,conversation_his

history=[]
print(" Hi Dude, I am here for you,shall we start?")
while True:
    user_input=input("You : ").strip()

    if user_input.lower() in ['exit','quit', 'bye']:
                              print("Good bye")
                              break
    
    if not user_input:
            continue
    response,history = chat_with_ai(user_input,history)
    print(f"Assistant : {response}\n")

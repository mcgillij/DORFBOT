import logging
import socketio
import discord
import os
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)

default_prompt = 'The expected response for a wise Dwarf that lives under a mountain in Dungeons & Dragons to >'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
# Create a Socket.IO client
sio = socketio.Client()
# Connect to the server and register the callback function
sio.connect('ws://localhost:3000')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    results = []
    def on_result(data, message, query):
        # Log the response data
        logging.info(f'Response data: {data["response"]}')
        if data['response'] == '\n\n<end>':
            result_string = ''.join(results).replace(default_prompt, '').replace(query, '')
            print(result_string)
            results.clear()
            asyncio.run_coroutine_threadsafe(message.channel.send(result_string), client.loop)
        else:
            logging.info(f'{data}')
            results.append(data['response'])
    # ignore self messages
    print(message.content)
    if message.author == client.user:
        return

    if ('!Dorf') in message.content:
        print('Dorfdd')
        query = message.content.replace('!Dorf', '')
        prompt = f"{default_prompt}{query} is"

        # Send a request to the server
        req = {
            'model': 'alpaca.30B',
            'prompt': prompt,
            'top_k': 40,
            'top_p': 0.9,
            'temp': 0.8,
            'repeat_last_n': 64,
            'repeat_penalty': 1.3
        }
        sio.emit('request', req, callback=lambda data: on_result(data, message, query))
        sio.on('result', lambda data: on_result(data, message, query))

    # Define a callback function to handle the 'result' event


# Wait for responses from the server
sio.start_background_task(sio.wait)

# Run the Discord bot
client.run(os.getenv('DISCORD_TOKEN'))

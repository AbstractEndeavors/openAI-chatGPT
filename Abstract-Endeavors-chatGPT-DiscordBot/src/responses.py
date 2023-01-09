import openai
import json
from asgiref.sync import sync_to_async
def get_config() -> dict:
    import os
    # get config.json path
    config_dir = os.path.abspath(__file__ + "/../../")
    config_name = 'config.json'
    config_path = os.path.join(config_dir, config_name)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config
config = get_config()
openai.api_key = config['openAI_key']
async def handle_response(message,defs) -> str:
    if defs['type'] == 'image':        
        response = await sync_to_async(openai.Image.create)(prompt=message,n=1,size="1024x1024")
        return response['data'][0]['url']
    
    response = await sync_to_async(openai.Completion.create)(
        model=defs['model'],
        prompt=message,
        temperature=defs['temperature'],
        max_tokens=defs['max_tokens'],
        top_p=defs['top_p'],
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    print(len(response),response)
    print(len(response.choices[0].text),response.choices[0].text)
    return response.choices[0].text

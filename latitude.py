import asyncio
from latitude_sdk import Latitude, LatitudeOptions, RunPromptOptions, StreamEvent, StreamEvents, ChainEvents
from typing import Any, Union

last_message_count = 0

# Do not expose the API key in client-side code
sdk = Latitude('bb53b630-9f3a-4070-8534-2194ca79080d', LatitudeOptions(project_id=16054))

def on_event(event: StreamEvent):
    global last_message_count

    if event.event == StreamEvents.Latitude and hasattr(event, 'messages'):
        new_messages = event.messages[last_message_count:]
        last_message_count = len(event.messages)  # Actualizar el contador

        for message in new_messages:
            role = message.role.value.upper()
            text_list = [c.text for c in message.content if c.type == 'text']
            text = text_list[0] if text_list else "(Sin texto)"
            if message.role.value == 'assistant' or message.role.value == 'user':
                print(f"[{role}] ➜ {text}")

def on_error(event: StreamEvent):
    global last_message_count
    last_message_count = 0  # Reiniciar el contador de mensajes en caso de error
    if event.event == StreamEvents.Error:
        print(f"[ERROR] {event.error.message}")

def on_finished(event: StreamEvent):
    global last_message_count
    last_message_count = 0  # Reiniciar el contador de mensajes en caso de error
    if event.event == StreamEvents.Finished:
        print(f"[FINISHED] {event.result.uuid}")

# Función principal asíncrona
async def main(): 
    result = await sdk.prompts.run('LoginAgent', RunPromptOptions(
        version_uuid='b02c79f6-502a-4297-8318-3105c8757793',
        parameters={
            'url': 'https://www.hackthissite.org/',
            'username': 'davidborregolatitude',
            'password': 'LatitudeHack2025'
        },
        # Enable streaming
        stream=True,
        # Provide callbacks for events
        on_finished=lambda result: print('\nRUN COMPLETED:', result.uuid),
        on_error=lambda error: print('\nERROR:', error.message),
        on_event=on_event
    ))
    return result

# Llamar a main() usando asyncio.run()
if __name__ == "__main__":
    result = asyncio.run(main())
    print('\nFINAL RESULT:', result)

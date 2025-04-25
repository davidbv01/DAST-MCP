import asyncio
from latitude_sdk import Latitude, LatitudeOptions, RunPromptOptions, StreamEvent, StreamEvents, ChainEvents
from typing import Any, Union

# Do not expose the API key in client-side code
sdk = Latitude('bb53b630-9f3a-4070-8534-2194ca79080d', LatitudeOptions(project_id=16054))

# Definir la función on_step antes de usarla en main()
"""async def on_step(messages: list[dict[str, Any]], config: dict[str, Any]) -> Union[str, dict[str, Any]]:
    # Procesar cada paso de la cadena
    print('\nSTEP:', messages)
    # Devuelve la respuesta del paso
    return 'Step response'"""

async def on_event(event: StreamEvent):
    print('\nEVENTO:', event)
    if event.event == StreamEvents.Provider and event.type == 'text-delta':
        print(event.text_delta)
    elif event.event == StreamEvents.Latitude and event.type == ChainEvents.ChainCompleted:
        print('Conversation UUID:', event.uuid)
        print('Conversation messages:', event.messages)

# Función principal asíncrona
async def main():
    result = await sdk.prompts.run('Test', RunPromptOptions(
        version_uuid='c3c0fda0-b89e-4ddb-b603-7d3669af8520',
        parameters={
            'message':'Which is the coldest place on Earth?'
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

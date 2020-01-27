from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel
import yaml
import sys
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    client = TelegramClient(config["session_name"],
                            config["api_id"],
                            config["api_hash"])
    client.start()

    input_channels_entities = []
    output_channel_entity = None
    for d in client.iter_dialogs():
        if config['input_is_id']:
            if (d.entity.id in config['input_channel']):
                print("from -> ",d.name)
                if hasattr (d.entity, 'access_hash'):
                    input_channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
                else:
                    input_channels_entities.append(d.entity.id)
        if not config['input_is_id']:
            if (d.name in config['input_channel']):
                print("from -> ", d.name)
                if hasattr(d.entity, 'access_hash'):
                    input_channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
                else:
                    input_channels_entities.append(d.entity.id)

        if config['output_is_id']:
            if (d.entity.id == config['output_channel']):
                print("to -> ", d.name)
                if hasattr(d.entity, 'access_hash'):
                    output_channel_entity = InputChannel(d.entity.id, d.entity.access_hash)
                else:
                    output_channel_entity = (d.entity.id)

        if not config['output_is_id']:
            if (d.name == config['output_channel']):
                print("from -> ", d.name)
                if hasattr(d.entity, 'access_hash'):
                    output_channel_entity = InputChannel(d.entity.id, d.entity.access_hash)
                else:
                    output_channel_entity = d.entity.id


    if output_channel_entity is None:
        logger.error(f"Could not find the channel \"{config['output_channel']}\" in the user's dialogs")
        sys.exit(1)
    logging.info(f"Listening on {len(input_channels_entities)} channels. Forwarding messages to {config['output_channel']}.")

    @client.on(events.NewMessage(chats=input_channels_entities))
    async def handler(event):
        if config['forward_message']:
            await client.forward_messages(output_channel_entity, event.message)
        else:
            await client.send_message(output_channel_entity, event.message)
            print(event.message)


    client.run_until_disconnected()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} CONFIG_PATH")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        config = yaml.safe_load(f)
    start(config)


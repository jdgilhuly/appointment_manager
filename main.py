import logging
import os
from fastapi import FastAPI
from vocode.streaming.models.telephony import TwilioConfig
from pyngrok import ngrok
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.server.base import (
    TwilioInboundCallConfig,
    TelephonyServer,
)
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, PunctuationEndpointingConfig

from speller_agent import SpellerAgentFactory
import sys
from event_manager import CustomEventsManager



# if running from python, this will load the local .env
# docker-compose will load the .env file by itself
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(docs_url=None)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_manager = RedisConfigManager()

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth is not None:
        ngrok.set_auth_token(ngrok_auth)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000

    # Open a ngrok tunnel to the dev server
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info('ngrok tunnel "{}" -> "http://127.0.0.1:{}"'.format(BASE_URL, port))

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

def read_prompt_from_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

prompts_file_path = os.path.join(os.path.dirname(__file__), 'prompts', 'prompt.txt')
prompt = read_prompt_from_file(prompts_file_path)

logger.info('TFFF')
logger.info(os.environ["TWILIO_ACCOUNT_SID"])
logger.info(os.environ["TWILIO_AUTH_TOKEN"])

#EndpointingConfig.time_cutoff_seconds = 10
telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    event_manager=CustomEventsManager(),
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello, you've reached Health HQ. How can I help you today?"),
                prompt_preamble=prompt,
                generate_responses=True,
                temperature=0.1,
                end_conversation_on_goodbye=True,
                allowed_idle_time_seconds=15,
                allow_agent_to_be_cut_off=False,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
                record=True
            ),
            transcriber_config=DeepgramTranscriberConfig.from_telephone_input_device(
                endpointing_config=PunctuationEndpointingConfig()
            ),
        )
    ],
    agent_factory=SpellerAgentFactory(),
    logger=logger,
)

app.include_router(telephony_server.get_router())

# Waxal: Realtime Assistant

## Description
Waxal is a real-time assistant that helps you manage your time and tasks. It is based on gpt-3.5-turbo and utilizes the [OpenAI API](https://beta.openai.com/).

**Note**: Before getting started, make sure to create a `.env` file and add your API key to it, as follows:
```bash
FRAMES_PER_BUFFER = 16000
CHANNELS = 1
RATE = 16000
PING_INTERVAL = 5
PING_TIMEOUT = 20
OPENAI_API_KEY = YOUR_API_KEY
```

## Installation and Usage
```bash
git clone https://github.com/abdouaziz/rltime.git
cd rltime
pip install -r requirements.txt

# Run Waxal
python waxal/server.py # for the server
python waxal/client.py # for the client
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Feel free to contribute and enhance the functionality of Waxal.
# Timewall Auto Clicker Bot

A Python bot that automatically clicks through Timewall website to generate traffic.

## Features

- Automated clicking through Timewall pages
- Configurable delays between clicks
- Simulates real user behavior
- Supports multiple browser sessions

## Requirements

- Python 3.7+
- Selenium WebDriver
- Chrome/Firefox browser
- ChromeDriver/GeckoDriver

## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/Pasonnn/timewall-auto-bot.git
   cd timewall-auto-bot
   ```

2. Create and activate a virtual environment (recommended)
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages
   ```bash
   pip install -r requirements.txt
   ```

4. Download the appropriate WebDriver for your browser:
   - [ChromeDriver](https://sites.google.com/chromium.org/driver/) for Chrome
   - [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for Firefox

   Make sure to add the WebDriver to your system PATH or place it in the project directory.

## Configuration

Edit the `config.py` file to customize the bot's behavior:

```.env
# Example .env configuration
FREECASH_URL = "https://freecash.com/"
TIMEWALL_URL = "https://timewall.io/clicks"
```

## Usage

Run the bot with:

```bash
python main.py
```

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with the terms of service of any websites you interact with.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or feedback, please contact [pason.dev](mailto:pason.dev@gmail.com).


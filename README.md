### how to dependencies 

```bash
pip install --upgrade pip
pip install ffmpeg-python
```

install the dev version of `discord.py`:
```bash
git clone https://github.com/Rapptz/discord.py
cd discord.py
python3 -m pip install -U .[voice]
```
install discord ext with voice receiver by [imayhaveborkedit](https://github.com/i)
```bash
python -m pip install discord-ext-voice-recv
```

### fyi

place your token in a file named `secret.py` with the following content:
```python
token = 'YOUR_DISCORD_BOT_TOKEN'
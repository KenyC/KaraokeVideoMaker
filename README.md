Karaoke Video Maker
==========================

I couldn't find free tools to create videos with scrolling lyrics and this is how this tool came into existence. This is a command line tool to do so. Provide a subtitle file (.srt) which contain text aligned to audio and the software will output something like this:

![Demo image](https://github.com/KenyC/KaraokeVideoMaker/blob/main/demo.gif?raw=true)

```bash
python main.py lyrics.srt --audio audio.mp3 -o video.mp4
```

**Features:**
	
  - Timebar indicating time to next verse
  - Preview of next verse

**What this tool cannot do:** 

  - align lyrics of a song to the music 
  - remove singers' voice from the audio 
  - highlight each word as they're sung  

Unfortunately, you'll need other tools to perform these tasks. 


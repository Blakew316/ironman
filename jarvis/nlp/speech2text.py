"""Speech-to-text using the SpeechRecognition library and Google's recogniser.

``speech_recognition`` (and the microphone backend it depends on) is imported
lazily so importing this module does not require a working audio stack.
"""

from jarvis.nlp.playsounds import startPlayAudio


def startStt(lang="en-in"):
    """Listen on the default microphone and return recognised text (lowercased)."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("[speech2text] SpeechRecognition not installed")
        return ""

    r = sr.Recognizer()
    print("Listening")
    startPlayAudio("jarvislistening.wav")

    try:
        with sr.Microphone() as source:
            print("Say something")
            audio = r.listen(source)
    except (OSError, AttributeError) as exc:
        # No microphone available (common in headless environments).
        print(f"[speech2text] microphone unavailable: {exc}")
        return ""

    speech = ""
    try:
        speech = r.recognize_google(audio, language=lang)
        print("Speech:", speech)
    except sr.UnknownValueError:
        speech = "Sorry! Couldn't understand"
        print("Sorry! Couldn't understand")
    except sr.RequestError:
        print("Could not process request")
        speech = "Could not process request"
    return speech.lower()


if __name__ == "__main__":
    startStt()

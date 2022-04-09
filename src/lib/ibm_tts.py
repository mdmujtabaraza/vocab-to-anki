from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pprint import pprint


def ibm_tts_authenticate(api_id, endpoint_url):
    authenticator = IAMAuthenticator(api_id)
    text_to_speech = TextToSpeechV1(
        authenticator=authenticator
    )
    text_to_speech.set_service_url(endpoint_url)
    return text_to_speech


def get_voice(tts, gender, lang):
    voices = tts.list_voices().get_result()
    app_voices = []
    for voice in voices['voices']:
        if voice['gender'] == gender and voice['language'] == lang:
            app_voices.append(voice)
    return app_voices[0]

# gender = 'male'
# language = 'en-GB'
# app_voices = []
# for voice in voices['voices']:
#     if voice['gender'] == gender and voice['language'] == language:
#         app_voices.append(voice)
# pprint.pprint(app_voices)


# with open('somefilename.txt', 'r') as f:
#     text = f.readlines()
# text = [line.replace('\n', '') for line in text]
# text = ''.join(str(line) for line in text)


# with open('files/speech.mp3', 'wb') as audio_file:
#     res = text_to_speech.synthesize('Hello World!', accept='audio/mp3', voice=app_voices[0]['name']).get_result()
#     audio_file.write(res.content)

import json
import requests


class FailedToFetch(Exception):
    pass

class ResponseNotProperFormat(Exception):
    pass


def load_api_key():
    with open('config.json', 'r') as f:
        return json.load(f)


def get_word_from_oxford(word, api_keys):
    url = 'https://od-api.oxforddictionaries.com/api/v2/entries/en-gb/'
    url += f'{word.lower()}'
    api_keys = {key: value for key, value in api_keys.items()
                if key in ["app_id", "app_key"]}
    response = requests.get(url, headers=api_keys)
    try:
        return response.json()
    except json.JSONDecodeError:
        raise FailedToFetch('Response is not valid JSON.')
    except ValueError:
        raise FailedToFetch('Response is not valid JSON.')


def extract_audio_and_ipa(response_json):
    results = response_json.get('results', [None])[0]
    if not results:
        msg = 'Response contains no results.'
        ResponseNotProperFormat(msg)
    lexicalEntry = results.get('lexicalEntries', [None])[0]
    if not lexicalEntry:
        msg = 'Results contain no Lexical Entry'
        ResponseNotProperFormat(msg)
    pronunciation = lexicalEntry.get('pronunciations', [None])[0]
    if not pronunciation:
        msg = 'Lexical Entry contain no pronunciation.'
        ResponseNotProperFormat(msg)
    audio = pronunciation.get('audioFile', None)
    ipa = pronunciation.get('phoneticSpelling', None)
    if not audio:
        msg = 'Response contains no reference to audio file.'
        raise ResponseNotProperFormat(msg)
    if not ipa:
        ipa = ''
    return audio, ipa


def get_audio_and_ipa(word, api_keys):
    result = get_word_from_oxford(word, api_keys)
    try:
        return extract_audio_and_ipa(result)
    except IndexError:
        msg = 'Response JSON was not in the proper format.'
        ResponseNotProperFormat(msg)


if __name__ == '__main__':
    api_keys = load_api_key()
    result = get_word_from_oxford('house', api_keys)
    audio, ipa = extract_audio_and_ipa(result)

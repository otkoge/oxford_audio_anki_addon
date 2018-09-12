from aqt import mw
from aqt.qt import QUrl, QDesktopServices
from aqt.utils import tooltip, showInfo, showWarning
from anki.hooks import addHook
from aqt.editor import Editor
from .oxford_api import get_audio_and_ipa
from .oxford_api import FailedToFetch
from .oxford_api import ResponseNotProperFormat


def load_config():
    return mw.addonManager.getConfig(__name__)


def get_word(editor, config):
    field_number_of_word = config.get('field_number_of_word', 0)
    allFields = editor.note.fields
    word = allFields[field_number_of_word]
    return word


def set_values_on_editor(audio, ipa, editor, config):
    audio = editor.urlToFile(audio)
    field_number_of_audio = config.get('field_number_of_audio', 1)
    field_number_of_ipa = config.get('field_number_of_ipa', 2)
    allFields = editor.note.fields
    allFields[field_number_of_audio] = f'[sound:{audio}]'
    allFields[field_number_of_ipa] = f'/{ipa}/'
    editor.loadNote()
    editor.web.setFocus()
    editor.web.eval(f'focusField({field_number_of_audio});')
    editor.web.eval(f'focusField({field_number_of_ipa});')
    editor.web.eval('caretToEnd();')


def open_browser(word, config):
    if(not config.get('open_in_browser', True)):
        return None
    url = 'https://en.oxforddictionaries.com/definition/' + str(word)
    tooltip(("Loading..."), period=1000)
    url = QUrl(url)
    QDesktopServices.openUrl(url)


def get_audio(editor):
    config = load_config()
    word = get_word(editor, config)
    headers = {}
    headers['app_id'] = config.get('app_id', None)
    headers['app_key'] = config.get('app_key', None)
    try:
        audio, ipa = get_audio_and_ipa(word, headers)
    except FailedToFetch:
        msg = 'Failed to get proper response from Oxford. Please try again.'
        showWarning(msg)
        open_browser(word, config)
        return None
    except ResponseNotProperFormat as exp:
        msg = f'Response from the API doesn seem to be correct: {str(exp)}'
        showWarning(msg)
        open_browser(word, config)
        return None
    set_values_on_editor(audio, ipa, editor, config)
    open_browser(word, config)


def mySetupButtons(buttons, editor):
    new_btn = editor.addButton("OxfordAudio", get_audio, get_audio,
                               label="OX",
                               tip="Get Audio and IPA for Word (Ctrl+O)",
                               keys="Ctrl+o")
    return buttons + [new_btn]


Editor.get_audio = get_audio
addHook("setupEditorButtons", mySetupButtons)

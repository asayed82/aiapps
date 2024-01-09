from vertexai.preview.generative_models import GenerativeModel
from vertexai.language_models import TextGenerationModel

from utils import consts

multimodal_model = GenerativeModel(consts.VAIModelName.MULTIMODAL.value)
text_gemini_model = GenerativeModel(consts.VAIModelName.TEXT_GEMINI.value)
text_palm_model = TextGenerationModel(consts.VAIModelName.TEXT_PALM.value)
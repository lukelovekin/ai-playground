from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

credentials = Credentials(
    url = "https://us-south.ml.cloud.ibm.com",
    # api_key = "<API_KEY>"
)

params = {
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
	GenTextParamsMetaNames.MAX_NEW_TOKENS: 100
}

model = ModelInference(
    model_id='ibm/granite-3-3-8b-instruct',
    params=params,
    credentials=credentials,
    project_id="skills-network"
)

text = """
Only reply with the answer. What is the capital of Australia?
"""

print(model.generate(text)['results'][0]['generated_text'])


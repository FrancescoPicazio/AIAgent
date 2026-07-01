import platform

import torch
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from transformers import pipeline


class LLM:

    def __init__(self, llm_name: str):

        self._tokenizer = AutoTokenizer.from_pretrained(llm_name)
        attn_implementation = "eager"
        if platform.system() == "Linux":
            attn_implementation = "sdpa"

        self._model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            attn_implementation= attn_implementation,
            dtype=torch.float16,
            device_map={"": 0}
        )

        # FIX: set generation config direttamente nel modello
        self._model.generation_config.max_new_tokens = 512

        self.pipe = pipeline(
            task="text-generation",
            model=self._model,
            tokenizer=self._tokenizer,
            return_full_text=False
        )

    def get_pipeline(self):
        return self.pipe

    def generate(self, prompt: str) -> str:
        result = self.pipe(prompt)
        return result[0]["generated_text"]
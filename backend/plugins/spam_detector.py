from __future__ import annotations

from typing import Any, Dict

from .base import PluginBase


class SpamDetector(PluginBase):
    plugin_name = "spam_detector"
    model_id = "bert-base-uncased"

    def load_model(self) -> None:
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig, pipeline

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
            )
            tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.model_id,
                quantization_config=quantization_config,
                device_map="auto",
            )
            self.model = pipeline("text-classification", model=model, tokenizer=tokenizer)
        except Exception:
            from transformers import pipeline

            self.model = pipeline("text-classification", model=self.model_id, device=-1)

    def run(self, text: str) -> Dict[str, Any]:
        if self.model is None:
            self.load_model()

        with self.isolated_cuda():
            result = self.model(text)

        return {
            "plugin": self.plugin_name,
            "result": result,
        }

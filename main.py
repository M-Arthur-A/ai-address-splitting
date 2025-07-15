from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import torch
from loguru import logger
import time

from config import Config
from csv_connector import Csv_processing



class Ai_agent:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logger.debug(f"using device: {self.device}")

        self.model = AutoModelForTokenClassification.from_pretrained(
            config.MODEL_PATH,
            local_files_only=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.MODEL_PATH,
            local_files_only=True
        )
        logger.debug("| AI | model and tokenizer loaded")


    @classmethod
    def model_download(cls, local_model_path):
        model = AutoModelForTokenClassification.from_pretrained("aidarmusin/address-ner-ru")
        tokenizer = AutoTokenizer.from_pretrained("aidarmusin/address-ner-ru")
        model.save_pretrained(local_model_path)
        tokenizer.save_pretrained(local_model_path)
        logger.info(f"Model has been dowloaded here: {local_model_path}")


    def run(self, address):
        start = time.perf_counter()
        address_ner_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
            aggregation_strategy='simple'
        )
        entities = address_ner_pipeline(address)
        elapsed = time.perf_counter() - start
        logger.info(f"| AI | Parsing <{address}> is DONE in {elapsed:.6f} sec.")
        return self.__beautify(entities)


    def __beautify(self, entities: list) -> dict:
        res = {}
        for item in entities:
            key = item['entity_group']
            if key in res.keys():
                key += '+'
            res[key] = item['word']
        return res


def main(address: str | None,
         config: Config
    ):
    ai = Ai_agent()
    if address:
        logger.info(ai.run(address))
    elif config.DB_PATH == 'sql':
        logger.error('SQL connector WIP')
    elif config.DB_PATH:
        Csv_processing(config, logger).process(ai)
    else:
        logger.error('no address / filename / SQLconnection provided')



if __name__ == "__main__":
    config = Config(logger)

    if config.APP_ARGS.init:
        Ai_agent.model_download(config.MODEL_PATH)

    if config.APP_ARGS.address:
        # main("628672,,,, Автономный Округ Ханты-Мансийский Автономный Округ - Югра,, Г. Лангепас, Ул. Солнечная, Д.21")
        main(address=config.APP_ARGS.address,
             config=config)
    elif config.DB_PATH:
        main(address=None, config=config)

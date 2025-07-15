from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import torch
from loguru import logger

from config import Config
from csv_connector import Csv_processing



def init(local_model_path):
    model = AutoModelForTokenClassification.from_pretrained("aidarmusin/address-ner-ru")
    tokenizer = AutoTokenizer.from_pretrained("aidarmusin/address-ner-ru")
    model.save_pretrained(local_model_path)
    tokenizer.save_pretrained(local_model_path)
    logger.info(f"Model has been dowloaded here: {local_model_path}")


def ai_run(address):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.debug(f"using device: {device}")

    model = AutoModelForTokenClassification.from_pretrained(
        config.MODEL_PATH,
        local_files_only=True
    )
    tokenizer = AutoTokenizer.from_pretrained(
        config.MODEL_PATH,
        local_files_only=True
    )
    logger.debug("model and tokenizer loaded")

    # address_ner_pipeline = pipeline("ner", model="aidarmusin/address-ner-ru", device=device)
    address_ner_pipeline = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        device=device,
        aggregation_strategy='simple'
    )
    entities = address_ner_pipeline(address)
    return beautify(entities)


def beautify(entities: list) -> dict:
    res = {}
    for item in entities:
        key = item['entity_group']
        if key in res.keys():
            key += '+'
        res[key] = item['word']
    return res


def main(address: str | None = None,
         config: Config = Config(logger)
    ):
    if address:
        logger.info(ai_run(address))
    elif config.DB_PATH == 'sql':
        logger.error('SQL connector WIP')
    elif config.DB_PATH:
        Csv_processing(config, logger).process(ai_run)
    else:
        logger.error('no address / filename / SQLconnection provided')



if __name__ == "__main__":
    config = Config(logger)

    if config.APP_ARGS.init:
        init(config.MODEL_PATH)

    if config.APP_ARGS.address:
        # main("628672,,,, Автономный Округ Ханты-Мансийский Автономный Округ - Югра,, Г. Лангепас, Ул. Солнечная, Д.21")
        main(address=config.APP_ARGS.address,
             config=config)
    elif config.DB_PATH:
        main(config=config)

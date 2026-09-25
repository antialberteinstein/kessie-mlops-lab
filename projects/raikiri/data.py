"""Dataset and tokenizer preparation built on Hugging Face Datasets."""

from itertools import chain
from pathlib import Path

from config import DataConfig


SPECIAL_TOKENS = {
    "unk_token": "<unk>",
    "pad_token": "<pad>",
    "bos_token": "<s>",
    "eos_token": "</s>",
}


def load_corpus(config: DataConfig):
    from datasets import DatasetDict, load_dataset

    corpus = load_dataset(config.dataset_name, split=config.dataset_split)
    if config.max_samples is not None:
        corpus = corpus.select(range(min(config.max_samples, len(corpus))))
    splits = corpus.train_test_split(test_size=config.validation_fraction, seed=config.seed)
    return DatasetDict(train=splits["train"], validation=splits["test"])


def load_or_train_tokenizer(train_dataset, config: DataConfig):
    from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers
    from transformers import AutoTokenizer, PreTrainedTokenizerFast

    tokenizer_dir = Path(config.tokenizer_dir)
    if (tokenizer_dir / "tokenizer.json").exists():
        return AutoTokenizer.from_pretrained(tokenizer_dir)

    tokenizer = Tokenizer(models.BPE(unk_token=SPECIAL_TOKENS["unk_token"]))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=config.tokenizer_vocab_size,
        min_frequency=2,
        special_tokens=list(SPECIAL_TOKENS.values()),
    )

    def text_batches(batch_size=1_000):
        for start in range(0, len(train_dataset), batch_size):
            yield train_dataset[start : start + batch_size][config.text_column]

    tokenizer.train_from_iterator(text_batches(), trainer=trainer, length=len(train_dataset))
    fast_tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer, **SPECIAL_TOKENS)
    fast_tokenizer.model_max_length = config.sequence_length
    fast_tokenizer.save_pretrained(tokenizer_dir)
    return fast_tokenizer


def group_token_batches(examples, sequence_length):
    """Concatenate tokenized rows and split them into fixed-size LM examples."""
    concatenated = {name: list(chain.from_iterable(values)) for name, values in examples.items()}
    usable_length = (len(concatenated["input_ids"]) // sequence_length) * sequence_length
    chunks = {
        name: [values[index : index + sequence_length] for index in range(0, usable_length, sequence_length)]
        for name, values in concatenated.items()
    }
    chunks["labels"] = [input_ids.copy() for input_ids in chunks["input_ids"]]
    return chunks


def prepare_dataset(corpus, tokenizer, config: DataConfig):
    def tokenize_rows(rows):
        encoded = tokenizer(
            rows[config.text_column],
            add_special_tokens=False,
            return_token_type_ids=False,
        )
        for input_ids, attention_mask in zip(encoded["input_ids"], encoded["attention_mask"]):
            input_ids.append(tokenizer.eos_token_id)
            attention_mask.append(1)
        return encoded

    tokenized = corpus.map(
        tokenize_rows,
        batched=True,
        remove_columns=corpus["train"].column_names,
        desc="Tokenizing",
    )
    return tokenized.map(
        lambda rows: group_token_batches(rows, config.sequence_length),
        batched=True,
        desc="Packing {}-token examples".format(config.sequence_length),
    )

import json
from pathlib import Path
from typing import Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from wordcloud import WordCloud

from src.data import DATA_DIR


class ChatStatistics:
    """Generate chat statistics from a telegram chat json file
    """
    def __init__(self, chat_json_file: Union[str, Path]):
        """
        :param chat_json-file: path to telegram exported json file
        """
        # load chat data
        logger.info(f'Loading chat data from {chat_json_file}')
        with open(Path(chat_json_file)) as f:
            self.chat_data = json.load(f)

        self.normalizer = Normalizer()

        # load stop words
        logger.info(f'Loading stop words from {DATA_DIR / "stop_words.txt"}')
        stop_words = open(DATA_DIR / 'stop_words.txt').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))

    def generate_wordcloud(
        self,
        output_dir: Union[str, Path],
        height: int = 200,
        width: int = 400,
        background_color: str = 'white',
        max_font_size: int = 200
    ):
        """Generate a word cloud from the chat data

        :param output_dir: path to output directory for wordcloud image
        :param height: height of wordcloud image
        :param width: width of wordcloud image
        :param background_color: background color of wordcloud image
        :param max_font_size: maximum font size of words in wordcloud image
        """
        logger.info('Loading text content')
        text_contents = ''

        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda item: item not in self.stop_words, tokens))
                text_contents += f" {' '.join(tokens)}"

        # normalize, reshape for final wordcloud
        text_contents = self.normalizer.normalize(text_contents)
        text_contents = arabic_reshaper.reshape(text_contents)
        text_contents = get_display(text_contents)

        # generate word cloud
        logger.info('Generating wordcloud')
        wordcloud = WordCloud(
            font_path=str(DATA_DIR / 'NotoNaskhArabic-Regular.ttf'),
            height=height,
            width=width,
            background_color=background_color,
            max_font_size=max_font_size
        ).generate(text_contents)

        logger.info(f'Saving wordcloud to {output_dir}')
        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png'))


if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json_file=DATA_DIR / 'result.json')
    chat_stats.generate_wordcloud(
        output_dir=DATA_DIR,
        height=600,
        width=800,
        max_font_size=250
    )
    print('Done')

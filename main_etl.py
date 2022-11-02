import argparse
import os

import yaml

# load config variables to environment variables
with open('global_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    for key in config:
        os.environ[key] = str(config[key])

from anime_recommender.etl import APIExtractor, APIProcessor, APITransformer


def get_args():
    parser = argparse.ArgumentParser(description='ETL Arguments', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-e',
        '--extract',
        required=False,
        action='store_true',
        default=False,
        help='''Optional. Extract data from API.''',
    )

    parser.add_argument(
        '-p',
        '--process',
        required=False,
        action='store_true',
        default=False,
        help='''Optional. Process data.''',
    )

    parser.add_argument(
        '-t',
        '--transform',
        required=False,
        action='store_true',
        default=False,
        help='''Optional. Transform data.''',
    )

    return parser.parse_args()


def main():
    args = get_args()

    if not any(vars(args).values()):
        extractor = APIExtractor()
        extractor.extract_pipe()
        processor = APIProcessor()
        processor.process_pipe()
        transformer = APITransformer()
        transformer.transform_pipe()

    else:
        if args.extract:
            extractor = APIExtractor()
            extractor.extract_pipe()
        if args.process:
            processor = APIProcessor()
            processor.process_pipe()
        if args.transform:
            transformer = APITransformer()
            transformer.transform_pipe()


if __name__ == '__main__':
    main()

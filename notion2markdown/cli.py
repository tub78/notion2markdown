
from notion2markdown import NotionExporter
from argparse import ArgumentParser
from notion2markdown.utils import logger
import json
import os


#  DEFAULT_FILTER = None
#  DEFAULT_FILTER = {
#          "property": "Status",
#          "status": {
#              "equals": "Done",
#          },
#      }

def main():
    parser = ArgumentParser('notion2markdown', description='Export Notion pages and databases to markdown.')
    parser.add_argument('url', type=str, help='URL of the Notion page or database to export. Must be public or explicitly shared with the token.')
    parser.add_argument('--token', type=str, help='Must be set here or in environment variable NOTION_TOKEN')
    parser.add_argument('--extension', type=str, help='The file extension to output', default="md")
    parser.add_argument('--strip-meta-chars', type=str, help='Strip characters from frontmatter')
    #  parser.add_argument('--no-filter', help='Filter for notion export', action="store_true")
    parser.add_argument('--filter', type=str, help='Filter for notion export, either as json string or as a json file path.  Must contain a valid JSON object.', default=None)
    parser.add_argument('--only-download', help='Stop after downloading json', action="store_true")
    parser.add_argument('--only-convert', help='Skip downloading json', action="store_true")
    args = parser.parse_args()

    token = args.token or os.environ.get("NOTION_TOKEN")
    assert token is not None, "Must set token using --token flag or in environment variable NOTION_TOKEN"

    strip_meta_chars = args.strip_meta_chars
    extension = args.extension
    #  no_filter = args.no_filter
    cli_filter = args.filter
    only_download = args.only_download
    only_convert = args.only_convert

    # prevent usage of --only-download and --only-convert at the same time
    if only_download and only_convert:
        raise ValueError("Cannot set both --only-download and --only-convert flags")

    # initialize filter
    if not cli_filter:
        filter = None
    else:
        # check if cli_filter is a file path and valid json file
        if os.path.isfile(cli_filter):
            with open(cli_filter, 'r') as f:
                try:
                    filter = json.load(f)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON file provided for --filter")
        else:
            try:
                filter = json.loads(cli_filter)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string provided for --filter")

    exporter = NotionExporter(token=token, strip_meta_chars=strip_meta_chars, extension=extension, filter=filter)

    if only_download:
        path = exporter.download_json(url=args.url)
        logger.info(f"Downloaded to {path} directory")
    elif only_convert:
        path = exporter.convert_json(url=args.url)
        logger.info(f"Converted to {path} directory")
    else:
        path = exporter.export_url(url=args.url)
        logger.info(f"Exported to {path} directory")

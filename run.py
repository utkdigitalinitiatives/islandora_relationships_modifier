from relationships.modify import FedoraObject
import argparse
import yaml


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Switch pages to large images or books to compound objects')
    pid = parser.add_argument("-p", "--pid", dest="pid", help="The PID you want to modify", required=True)
    model = parser.add_argument("-m", "--model", dest="model", help="The destination model: compound, large_image", required=True)
    args = parser.parse_args()
    settings = yaml.safe_load(open("config.yml", "r"))
    if args.model == 'compound':
        FedoraObject(
            settings['fedora_url'],
            auth=(
                settings['username'], settings['password']
            )
        ).convert_book_to_compound_object(args.pid)
    elif args.model == 'large_image':
        FedoraObject(
            settings['fedora_url'],
            auth=(
                settings['username'], settings['password']
            )
        ).convert_page_to_part_of_compound_object(args.pid)
    elif args.model == 'clean':
        FedoraObject(
            settings['fedora_url'],
            auth=(
                settings['username'], settings['password']
            )
        ).clean_up(args.pid)
    else:
        print(f'Operation not valid. Unknown model: {args.model}')

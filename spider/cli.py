import click
import anyconfig

from storage import Storage

config = anyconfig.load('spider.yaml')


@click.group()
def cli():
    pass


@cli.command()
@click.option('--test-upload', is_flag=True)
def run(test_upload):
    s = Storage(bucket=config['storage_bucket'])

    metadata = s.get_bucket_metadata()
    print(metadata)

    if test_upload:
        s.upload_object('__init__.py')
        s.delete_object('__init__.py')


if __name__ == '__main__':
    cli()

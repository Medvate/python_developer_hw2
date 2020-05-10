import click

from patient import Patient, PatientCollection


@click.group()
def cli():
    pass


@click.command()
@click.argument('first_name')
@click.argument('last_name')
@click.option('--birth-date')
@click.option('--phone')
@click.option('--document-type')
@click.option('--document-id', type=(str, str))
def create(first_name, last_name, birth_date,
           phone, document_type, document_id):
    document_id = ''.join(document_id)

    new_patient = Patient(first_name, last_name, birth_date,
                          phone, document_type, document_id, _with_check=False)

    new_patient.save()


@click.command()
@click.argument('last', default=10)
def show(last):
    collection = PatientCollection(create_from_db=True)

    for patient in collection.limit(last):
        print(patient)


@click.command()
def count():
    collection = PatientCollection(create_from_db=True)

    print(f"In the database: {len(collection)} patients.")


cli.add_command(create)
cli.add_command(show)
cli.add_command(count)


if __name__ == '__main__':
    cli()

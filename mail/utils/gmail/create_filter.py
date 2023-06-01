from googleapiclient.errors import HttpError


def create_filter(service):
    """Create a filter.
    Returns: Draft object, including filter id.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        label_name = 'IMPORTANT'
        filter_content = {
            'criteria': {
                'query': 'nec.edu.np'
            },
            'action': {
                'removeLabelIds': ['INBOX'],
                'hasAttachment': True,
                'newer_than': '1d'
            }
        }

        result = service.users().settings().filters().create(
            userId='me', body=filter_content).execute()

        print(F'Created filter with id: {result.get("id")}')
        return result.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

"""https://cloud.google.com/storage/docs/json_api/v1/json-api-python-samples"""

import sys

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery, http


class Storage:
    """Class for interacting with Google Cloud Storage."""

    def __init__(self, bucket):
        try:
            credentials = GoogleCredentials.get_application_default()
            self.service = discovery.build('storage', 'v1', credentials=credentials)
        except:    #pylint: disable=bare-except
            sys.exit(0)

        self.bucket = bucket

    def upload_object(self, filename, readers=None, owners=None):
        # This is the request body as specified:
        # http://g.co/cloud/storage/docs/json_api/v1/objects/insert#request
        body = {'name': filename,}

        # If specified, create the access control objects and add them to the
        # request body
        if readers or owners:
            body['acl'] = []

            for r in readers:
                body['acl'].append({
                    'entity': 'user-%s' % r,
                    'role': 'READER',
                    'email': r
                })
            for o in owners:
                body['acl'].append({'entity': 'user-%s' % o, 'role': 'OWNER', 'email': o})
        """
        Now insert them into the specified bucket as a media insertion.
        http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#insert

        You can also just set media_body=filename, but for the sake of
        demonstration, pass in the more generic file handle, which could
        very well be a StringIO or similar.
        """
        with open(filename, 'rb') as f:
            req = self.service.objects().insert(
                bucket=self.bucket,
                body=body,
                media_body=http.MediaIoBaseUpload(f, 'application/octet-stream'))
            resp = req.execute()

        return resp

    def get_object(self, filename, out_file):
        # Use get_media instead of get to get the actual contents of the object.
        # http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#get_media
        req = self.service.objects().get_media(bucket=self.bucket, object=filename)

        downloader = http.MediaIoBaseDownload(out_file, req)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download {}%.".format(int(status.progress() * 100)))

        return out_file

    def delete_object(self, filename):
        req = self.service.objects().delete(bucket=self.bucket, object=filename)
        resp = req.execute()

        return resp

    def get_bucket_metadata(self):
        """Retrieves metadata about the given bucket."""
        # Make a request to buckets.get to retrieve a list of objects in the
        # specified bucket.
        req = self.service.buckets().get(bucket=self.bucket)
        return req.execute()

    def list_bucket(self):
        """Returns a list of metadata of the objects within the given bucket."""
        # Create a request to objects.list to retrieve a list of objects.
        fields_to_return = \
            'nextPageToken,items(name,size,contentType,metadata(my-key))'
        req = self.service.objects().list(bucket=self.bucket, fields=fields_to_return)

        all_objects = []
        # If you have too many items to list in one request, list_next() will
        # automatically handle paging with the pageToken.
        while req:
            resp = req.execute()
            all_objects.extend(resp.get('items', []))
            req = self.service.objects().list_next(req, resp)
        return all_objects

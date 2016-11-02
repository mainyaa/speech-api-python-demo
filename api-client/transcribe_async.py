#!/usr/bin/env python
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Google Cloud Speech API sample application using the REST API for async
batch processing."""

# [START import_libraries]
import argparse
import base64
import json
import time

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
# [END import_libraries]


# [START authenticating]


# Application default credentials provided by env variable
# GOOGLE_APPLICATION_CREDENTIALS
def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('speech', 'v1beta1', http=http)
# [END authenticating]


def main(input_uri, encoding, sample_rate, languageCode):

    """Transcribe the given audio file asynchronously.

    Args:
        speech_file: the name of the audio file.
    """
    # [START construct_request]

    service = get_speech_service()
    service_request = service.speech().asyncrecognize(
        body={
            'config': {
                # There are a bunch of config options you can specify. See
                # https://goo.gl/KPZn97 for the full list.
                'encoding': encoding,  # raw 16-bit signed LE samples
                'sampleRate': sample_rate,  # 16 khz
                # See https://goo.gl/A9KJ1A for a list of supported languages.
                'languageCode': languageCode,  # a BCP-47 language tag
            },
            'audio': {
                'uri': input_uri
                }
            })
    # [END construct_request]
    # [START send_request]
    response = service_request.execute()
    print(json.dumps(response))
    # [END send_request]

    name = response['name']
    # Construct a GetOperation request.
    service_request = service.operations().get(name=name)

    while True:
        # Give the server a few seconds to process.
        print('Waiting for server processing...')
        time.sleep(1)
        # Get the long running operation with response.
        response = service_request.execute()

        if 'done' in response and response['done']:
            break

    print(json.dumps(response).decode('unicode-escape'))

def _gcs_uri(text):
    if not text.startswith('gs://'):
        raise argparse.ArgumentTypeError(
            'Cloud Storage uri must be of the form gs://bucket/path/')
    return text

# [START run_application]
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_uri', type=_gcs_uri)
    parser.add_argument(
        '--encoding', default='LINEAR16', choices=[
            'LINEAR16', 'FLAC', 'MULAW', 'AMR', 'AMR_WB'],
        help='How the audio file is encoded. See {}#L67'.format(
            'https://github.com/googleapis/googleapis/blob/master/'
            'google/cloud/speech/v1beta1/cloud_speech.proto'))
    parser.add_argument('--sample_rate', type=int, default=44100)
    parser.add_argument('--languageCode', default="ja_JP")
    
    args = parser.parse_args()
    main(args.input_uri, args.encoding, args.sample_rate, args.languageCode)

    # [END run_application]

# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
#
# ABOUT THIS PYTHON SAMPLE: This sample is part of the AWS General Reference
# Signing AWS API Requests top available at
# https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
#
#Changes made to original code:
#Changed EC2 statments to S3 statements, removed tutorial comments, and made function names conform to snake case

#original code can be found at:
#https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html#sig-v4-examples-get-auth-header

import sys, os, base64, datetime, hashlib, hmac

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

#creates header for s3 request, including signatures. needed in every request
#against a private s3 bucket
def create_s3_header(s3_params, file_name):

    method = 'GET'
    service = 's3'
    host = s3_params.get("host") #hostname must be declared expliclitly as it is different for europe
    region = s3_params.get("region")
    endpoint = s3_params.get("endpoint")
    request_parameters = s3_params.get("request_parameters", '')

    access_key = s3_params.get("access_key", None)
    secret_key = s3_params.get("secret_key", None)
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    bucket_name = s3_params.get("bucket_name")
    canonical_uri = '/' + bucket_name + '/' + file_name
    canonical_querystring = request_parameters
    canonical_headers = 'host:' + host + '\n' + 'x-amz-content-sha256:UNSIGNED-PAYLOAD' + '\n' + 'x-amz-date:' + amzdate + '\n'
    signed_headers = 'host;x-amz-content-sha256;x-amz-date'
    payload_hash = 'UNSIGNED-PAYLOAD'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    signing_key = get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    headers = {'x-amz-date':amzdate, 'x-amz-content-sha256': 'UNSIGNED-PAYLOAD', 'Authorization':authorization_header}

    return headers

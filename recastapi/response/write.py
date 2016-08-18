import recastapi
import recastapi.response.read
from termcolor import colored
import uuid
import yaml
import os

def scan_response(scan_request_id):
    """Adds scan request
    :param scan_response_id: ID of the scan response
    :param point_request_id: ID of the scan request
    :param result_data: result data (CLs, logL, etc.)
    :return: JSON object
    """
    payload = {
        'model_id': None,
        'scan_request_id': scan_request_id,
    }

    existing = recastapi.response.read.scan_response(scan_request_id = scan_request_id)
    if existing:
        url = '{}/{}'.format(recastapi.ENDPOINTS['SCAN_RESPONSES'],existing['id'])
        existing.update(**payload)
        existing = {k:v for k,v in existing.iteritems() if not (k.startswith('_') or k=='id')}
        recastapi.patch(url,existing)
        scan_response =  recastapi.response.read.scan_response(scan_request_id = scan_request_id)
        print 's EXISTS, return',scan_response
        return scan_response

    url = '{}/'.format(recastapi.ENDPOINTS['SCAN_RESPONSES'])
    return recastapi.post(url, data=payload)


def point_response(scan_response_id,point_request_id,result_data):
    """Adds point request
    :param scan_response_id: ID of the point response
    :param point_request_id: ID of the point request
    :param result_data: result data (CLs, logL, etc.)
    :return: JSON object
    """
    payload = {
        'model_id': None,
        'scan_response_id': scan_response_id,
        'point_request_id': point_request_id
    }
    payload.update(**result_data)


    print 'PAYLOAD',payload

    existing = recastapi.response.read.point_response(point_request_id = point_request_id)
    if existing:
        url = '{}/{}'.format(recastapi.ENDPOINTS['POINT_RESPONSES'],existing['id'])
        existing.update(**payload)
        existing = {k:v for k,v in existing.iteritems() if not (k.startswith('_') or k=='id')}
        recastapi.patch(url,existing)
        return recastapi.response.read.point_response(point_request_id = point_request_id)

    url = '{}/'.format(recastapi.ENDPOINTS['POINT_RESPONSES'])
    return recastapi.post(url, json=payload)

def basic_response(point_response_id,basic_request_id,result_data):
    """Adds basic request
    :param point_response_id: ID of the point response
    :param basic_request_id: ID of the basic request
    :param result_data: result data (CLs, logL, etc.)
    :return: JSON object
    """
    payload = {
        'model_id': None,
        'basic_request_id': basic_request_id,
        'point_response_id': point_response_id,
    }
    payload.update(**result_data)

    existing = recastapi.response.read.basic_response(basic_request_id = basic_request_id)
    if existing:
        url = '{}/{}'.format(recastapi.ENDPOINTS['BASIC_RESPONSES'],existing['id'])
        existing.update(**payload)
        existing = {k:v for k,v in existing.iteritems() if not (k.startswith('_') or k=='id')}
        recastapi.patch(url,existing)
        return recastapi.response.read.basic_response(basic_request_id = basic_request_id)
    url = '{}/'.format(recastapi.ENDPOINTS['BASIC_RESPONSES'])
    return recastapi.post(url, json=payload)


def basic_response_with_archive(point_response_id,basic_request_id,filename, result_data):
    br = basic_response(point_response_id,basic_request_id,result_data)
    request_archive(br['id'],filename)
    return br

def request_archive(basic_request_id, filename = None):
    payload = {
        'basic_response_id': basic_request_id,
        'original_file_name': os.path.basename(filename),
    }

    files = {'file': open(filename, 'rb')} if filename else {}
    url = '{}/'.format(recastapi.ENDPOINTS['RESPONSE_ARCHIVES'])
    basic_request_response = recastapi.post(
        url,
        data=payload,
        files=files,
    )
    return basic_request_response
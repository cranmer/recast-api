import json
import logging
import os
import recastapi.request.get
import recastapi.request.post
import recastapi.response.post
import recastapi.response.get
import yaml


class RecastApi(object):
    """ Helper class to POST requests and responses. """
    def __init__(self, request_id=None, json_file=None):
        self.all_responses = []
        self.request_id = request_id
        self.staged_point_request = {}
        self.staged_basic_request = {}
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(levelname)s] %(message)s')
        logging.info('Initialization')
        if json_file:
            self.read_file(json_file)

    def printout(self):
        """ Printout the staged parameters. """
        logging.info('point request: {}'.format(self.staged_point_request))
        logging.info('basic request: {}'.format(self.staged_basic_request))
        
    def current_responses(self):
        """ Prints latest response from API. """
        if self.all_responses:
            return self.all_responses[-1]
        logging.warning('Responses empty!')

    def read_file(self, filename):
        """ Reads file and populates objects. """
        if not os.path.isfile(filename):
            raise Exception('Filename does not exist!')

        with open(filename) as json_file:
            data = json.load(json_file)
        try:
            self.request_id = data['request_id']
            self.staged_point_request = data['point_request']
            logging.info('Read data: {}'.format(data))
        except Exception, e:
            print e
            raise Exception('File not correctly formatted!')
            
    def dump(self, filename=None):
        """ Dumps objects into files. """
        if not filename:
            filename = 'request_file_{}.json'.format(self.request_id)
        logging.info('filename: {}'.format(filename))
        data = {}
        data['request_id'] = self.request_id
        data['point_request'] = self.staged_point_request
        logging.info('Dumping to file: {}'.format(json.dumps(data)))
        # data dict to file
        with open(filename, 'w') as f:
            json.dump(data, f)

    def add_point(self, data, param_key=None):
        """ adds point request and archive data from a JSON datastructure.
        
        :param param_key: parameter key in the staged_point_request data structure
        :param data: data to be added
        e.g. input data structure
        {
            'coordinates': [
                             {'name': 'a', 'value': 1},
                             {'name': 'b', 'value': 2}
                           ],
            'basic': [
                       {'filename': 'samples/file11.zip'},
                       {'filename': 'samples/file12.zip'}
                     ]
        }
        :return param_key
        """

        if data is None:
            # for testing purpose
            data = {'coordinates': [{'name': 'a', 'value': 1},
                                    {'name': 'b', 'value': 2}
                                ],
                    'basic': [{'filename': 'samples/file11.zip'},
                              {'filename': 'samples/file12.zip'}]
                }            
        try: 
            coordinates = data['coordinates']
            basic_requests = data['basic']
        except Exception, e:
            print e
            raise Exception('Error retrieving "coordinates" or "basic" keys')

        if param_key is None:
            n_keys = len(self.staged_point_request.keys())
            param_key = self.make_parameter_key('param_{}'.format(n_keys))
        elif self.staged_point_request.has_key(param_key):
            raise Exception('Parameter key {} already exists!'.format(param_key))
        
        logging.info('Adding parameter for: {}'.format(coordinates))
        point_response = recastapi.request.post.parameter(request_id=self.request_id)
        parameter_id = point_response['id']
        logging.debug('Added point request with ID: {}'.format(parameter_id))
        staged_param = {}
        staged_param[param_key] = {}
        staged_param[param_key]['point_id'] = parameter_id
        staged_param[param_key]['data'] = coordinates
        point_response['coordinates'] = []
        
        for coordinate in coordinates:
            logging.info('\t Adding coordinates: {}'.format(coordinate))
            coordinate_response = recastapi.request.post.coordinate(
                parameter_id=parameter_id,
                coordinate_name=coordinate['name'],
                coordinate_value=float(coordinate['value'])
                )                    
            logging.debug('Added coordinate with ID: {}'.format(coordinate_response['id']))
            point_response['coordinates'].append(coordinate_response)
            
        point_response['files'] = []
        staged_param[param_key]['basic'] = {}
        for i, basic in enumerate(basic_requests):
            logging.info('\t Uploading file: {}'.format(basic['filename']))
            file_response = recastapi.request.post.upload_file(parameter_id=parameter_id,
                                                               filename=basic['filename'])
            logging.info('\t Successfully uploaded file: {}'.format(basic['filename']))
            point_response['files'].append(file_response)
            logging.debug('BASIC REQUEST: j = {}'.format(i))
            basic_key = 'basic_{}'.format(i)
            staged_param[param_key]['basic'][basic_key] = {}
            staged_param[param_key]['basic'][basic_key] = {
                'basic_id': file_response['id'],
                'data': basic['filename']
            }

        self.staged_point_request[param_key] = {}
        self.staged_point_request[param_key] = staged_param[param_key]
        self.all_responses.append(point_response)
        logging.debug('Added all files')
        return param_key
        

    def make_parameter_key(self, tentative_key):
        """ makes sure there are no duplicate keys.
        
        :param tentative_key: initial key.
        """
        if self.staged_point_request.has_key(tentative_key):            
            return self.make_parameter_key('{}_{}'.format(tentative_key, 1))
        return tentative_key

    def add_point_from_file(self, param_file='samples/param_data.yaml'):
        """ Function to add point requests.
        
        added and saved into dict that can later be retrieved to use
        for adding.
        :returns a list of parameter keys to refer to data added
        """
        f = open(param_file)
        param_data = yaml.load(f)
        f.close()

        # loop through file and fill
        keys = []
        response = []
        staged_param = {}
        for i, parameter in enumerate(param_data):
            logging.info('Adding parameter for: {}'.format(parameter['coordinates']))
            point_response = recastapi.request.post.parameter(request_id=self.request_id)
            parameter_id = point_response['id']
            logging.debug('Added point request with ID: {}'.format(parameter_id))
            n_keys = len(self.staged_point_request.keys())
            param_key = 'param_{}'.format(n_keys+i)
            keys.append(param_key)
            staged_param[param_key] = {}
            staged_param[param_key]['point_id'] = parameter_id
            staged_param[param_key]['data'] = parameter['coordinates']
            
            response.append(point_response)
            response[-1]['coordinate'] = []
            
            for coordinate in parameter['coordinates']:                
                # add coordinates one by one
                logging.info('\t Adding coordinates: {}'.format(coordinate))
                coordinate_response = recastapi.request.post.coordinate(
                    parameter_id=parameter_id,
                    coordinate_name=coordinate['name'],
                    coordinate_value=float(coordinate['value'])
                    )
                logging.debug('Added coordinate with ID: {}'.format(coordinate_response['id']))
                response[-1]['coordinate'].append(coordinate_response)                
                
            response[-1]['files'] = []
            staged_basic = {}
            staged_param[param_key]['basic'] = {}
            for j, basic in enumerate(parameter['basicrequests']):                
                # add basic requests one by one
                logging.info('\t Uploading file: {}'.format(basic))
                file_response = recastapi.request.post.upload_file(parameter_id=parameter_id,
                                                                   filename=basic)
                response[-1]['files'].append(file_response)
                logging.debug('BASIC  REQUEST: j = {}'.format(j))
                basic_key = 'basic_{}'.format(j)
                staged_param[param_key]['basic'][basic_key] = {}
                staged_param[param_key]['basic'][basic_key] = {
                    'basic_id': file_response['id'],
                    'data': basic}
                    
                logging.debug('basic key: {}'.format(basic_key))

        for k in staged_param.keys():
            self.staged_point_request[k] = staged_param[k]
        logging.debug('Added all files')
        self.all_responses.append(response)
        return keys

    def add_point_response(self, key_name, response_file, archive):
        """ Adds point response to staged point_request.
        
        :param key_name: point request key name in the directory
        :param response_file: Point response file, see pointresponse.json for format
        :param archive: file to upload
        """
        
        # find point_request_id given key name
        point_request_id = 0
        if self.staged_point_request.has_key(key_name):
            point_request_id = self.staged_point_request[key_name]['point_id']
        else:            
            logging.error('Key not found!')
            raise Exception('Key name not found!')        
        response = {}
        logging.info('Creating a scan response')
        scan_response = recastapi.response.post.response(request_id=self.request_id)
        logging.info('Adding a point response to point id: {}'.format(point_request_id))
        
        response = recastapi.response.post.parameter_response(
            yaml_file=response_file,
            point_request_id=point_request_id,
            scan_response_id=scan_response['id'],
            filename=archive
            )
        logging.debug('Added point response with ID: {}'.format(response['id']))
        response['scan_response'] = scan_response
        self.all_responses.append(response)
        return True

    def add_basic_response(self, point_key_name, key_name, basic_response_data, archive):
        """Adds basic response to staged basic_request.
        
        
        
        """

        point_request_id = 0
        if self.staged_point_request.has_key(point_key_name):
            point_request_id = self.staged_point_request[point_key_name]['point_id']
        else:
            logging.error('Point request key name not found!')
            raise Exception('Point key name not found!')
        basic_request_id = 0
        if self.staged_point_request.has_key(point_key_name):
            basic_request_id = self.staged_point_request[point_key_name]\
                               ['basic'][key_name]['basic_id']
        else:
            logging.error('Basic request key name not found!')
            raise Exception('Basic key name not found!')

        # get point response id given the point request id
        try:
            point_response = recastapi.response.get.point_response_by_id(point_request_id)
            print point_response
            point_response_id = point_response['id']
        except Exception, e:
            print e
            raise Exception('No point response available for this basic request!')

        logging.info('Adding basic request!')
        responses = recastapi.response.post.basic_response(
            yaml_file=basic_response_data,
            point_response_id=point_response_id,
            basic_request_id=basic_request_id,
            filename=archive)
        self.all_responses.append(responses)
        logging.info('Added basic request')

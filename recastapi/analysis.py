import os
import requests as httprequest
import json
import recastapi

def analysis(uuid = None):
  """List analysis given uuid or all analyses
  Usage::
       >>> analysis()
       
       >>> returns json object
  """
  single_analysis = '/{}'.format(uuid) if uuid else ''
  url = '{}{}'.format(recastapi.ENDPOINTS['ANALYSIS'], single_analysis)
  r = httprequest.get(url)
  analyses = json.loads(r.content)
  return analyses
  
def create(owner_id, title, collaboration, 
                   e_print, journal, doi, inspire_url, 
                   description, run_condition_id):
  """Create a new analysis given the run_condition id
      owner_id
      collaboration: ALICE, ATLAS,CMS...
      .
      .
      .
  """
  collaboration.toUpperCase()
  payload = {
    'owner_id':owner_id,
    'title':title,
    'collaboration':collaboration,
    'e_print':e_print,
    'journal':journal,
    'doi':doi,
    'inspire_URL':inspire_url,
    'description':description,
    'run_condition_id':run_condition_id,
  }
  url = '{}/'.format(recastapi.ENDPOINTS['ANALYSIS'])
  postbody = '&'.join(['='.join(x) for x in payload.iteritems()])
  r = httprequest.post(url, data = payload)
  if not r.ok:
    print "http request failed for payload: ()".format(postbody)
    print r.reason
    print r.content
    raise RuntimeError
  return json.loads(r.content)
  
def create(owner_id, title, collaboration,
                   e_print, journal, doi, inspire_url, 
                   description, run_condition_name, run_condition_description):
  """Create a new analysis and Run Condition
     see createAnalysis(...)
     .
     .
     .
  """
  
  r_condition_payload = {
    'name': run_condition_name,
    'description': run_condition_description,
    }
  r_condition_url = '{}/'.format(recastapi.ENDPOINTS['RUN_CONDITIONS'])
  r_condition_response = httprequest.post(url, data=r_condition_payload)
  if not r_condition_response.ok:
    print "http request failed for payload: ()".format(r_condition_payload)
    print r.reason
    print r.content
    raise RuntimeError
    return
  
  run_condition_id = r_condition_response['id']

  return create(owner_id, title, collaboration,
                 e_print, journal, doi, inspire_url,
                 description, run_condition_id)
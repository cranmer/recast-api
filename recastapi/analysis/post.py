import recastapi

def analysis(title, 
             collaboration,
             e_print, 
             journal,
             doi, 
             inspire_url, 
             description, 
             run_condition_name,
             run_condition_description):
    """Create a new analysis and Run Condition.
  
    :param title: Title of the analysis.
    :param collaboration: Choice among: ALICE, ATLAS, CMS, .
    :param e_print: link.
    :param journal: Name of journal.
    :param doi: Arxiv doi?
    :param inspire_url: URL on inspire website.
    :param description: A detailed description of the analysis.
    :param run_condition_name: Name of the run condition.
    :param run_condition_descprition: Detailed description of the run condition.

    :return: JSON object containing data that has been added into DB.
    """
    r_condition_payload = {
        'name': run_condition_name,
        'description': run_condition_description,
        }
    r_condition_url = '{}/'.format(recastapi.ENDPOINTS['RUN_CONDITIONS'])
  
    r_condition_response =  recastapi.post(r_condition_url, r_condition_payload)
    run_condition_id = r_condition_response['id']
    
    owner = recastapi.user.userData()
    owner_id = owner['_items'][0]['id']
    collaboration.upper()

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
    return recastapi.post(url, payload)


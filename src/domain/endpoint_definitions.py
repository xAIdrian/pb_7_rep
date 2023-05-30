import sys
import json
import os
import sys
import requests

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

#Reuse this facebook and instagram
def make_api_call( url, headers = '', req_params = '', req_json = '', req_auth = '', type = '' ):
	""" Request data from endpoint with params
	
	Args:
		url: string of the url endpoint to make request from
		endpointParams: dictionary keyed by the names of the url parameters
	Returns:
		object: data from the endpoint
	"""

	if type == 'POST' : # post request
		data = requests.post( 
			url = url, 
			headers=headers,
			data = req_params,
			json = req_json,
			auth=req_auth
		)
	else : # get request
		data = requests.get( 
			url = url, 
			params = req_params
		)

	response = dict() # hold response info
	response['url'] = url # url we are hitting
	
	response['endpoint_params'] = req_params #parameters for the endpoint
	response['json_data'] = json.loads( data.content ) # response data from the api
	response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

	return response # get and return content

def display_api_call_data( response ) :
	""" Print out to cli response from api call """

	print ("\nURL: ") # title
	print (response['url']) # display url hit
	print ("\nEndpoint Params: ") # title
	print (response['endpoint_params_pretty']) # display params passed to the endpoint
	print ("\nResponse: ") # title
	print (response['json_data_pretty']) # make look pretty for cli	

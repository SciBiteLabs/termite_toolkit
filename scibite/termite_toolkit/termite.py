"""

  ____       _ ____  _ _         _____ _____ ____  __  __ _ _         _____           _ _    _ _
 / ___|  ___(_) __ )(_) |_ ___  |_   _| ____|  _ \|  \/  (_) |_ ___  |_   _|__   ___ | | | _(_) |_
 \___ \ / __| |  _ \| | __/ _ \   | | |  _| | |_) | |\/| | | __/ _ \   | |/ _ \ / _ \| | |/ / | __|
  ___) | (__| | |_) | | ||  __/   | | | |___|  _ <| |  | | | ||  __/   | | (_) | (_) | |   <| | |_
 |____/ \___|_|____/|_|\__\___|   |_| |_____|_| \_\_|  |_|_|\__\___|   |_|\___/ \___/|_|_|\_\_|\__|


TERMiteRequestBuilder- make requests to the TERMite API and process results.

"""

__author__ = 'Joe Mullen & Michael Hughes'
__version__ = '1.0'
__copyright__ = '(c) 2018, SciBite Ltd'
__license__ = 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License'

import requests
import os
import pandas as pd


class TermiteRequestBuilder():
    """
    Class for creating TERMite requests.
    """

    def __init__(self):
        self.url = ''
        self.input_file_path = ''
        self.payload = {"output": "json"}
        self.options = {}
        self.binary_content = None
        self.basic_auth = ()
        self.verify_request = True

    def set_basic_auth(self, username, password, verification=True):
        """
        Pass basic authentication credentials.
        ** ONLY change verification if you are calling a known source **

        :param username: username to be used for basic authentication
        :param password: password to be used for basic authentication
        :return:
        """
        self.basic_auth = (username, password)
        self.verify_request = verification

    def set_url(self, url):
        """
        Set the URL of the TERMite instance e.g. for local instance http://localhost:9090/termite

        :param url: the URL of the TERMite instance to be hit
        :return:
        """
        self.url = url

    def set_binary_content(self, input_file_path):
        """
        For annotating file content, send file path string and process file as a binary
        multiple files of the same type can be scanned at once if placed in a zip archive.

        :param input_file_path: file path to the file to be sent to TERMite
        :return:
        """
        file_obj = open(input_file_path, 'rb')
        file_name = os.path.basename(input_file_path)
        self.binary_content = {"binary": (file_name, file_obj)}

    def set_text(self, string):
        """
        Use this for tagging raw text e.g. if looping through some file content

        :param string: text to be sent to TERMite
        :return:
        """
        self.payload["text"] = string

    def set_options(self, options_dict):
        """
        For bulk setting multiple TERMite API options in a single call, send a dictionary object here

        :param options_dict: a dictionary of options to be passed to TERMite
        :return:
        """

        if 'output' in options_dict:
            self.payload['output'] = options_dict['output']

        options = []
        for k, v in options_dict.items():
            options.append(k + "=" + str(v))
        option_string = '&'.join(options)
        if "opts" in self.payload:
            self.payload["opts"] = option_string + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = option_string

    #######
    # individual options for applying the major TERMite settings
    #######

    def set_fuzzy(self, bool):
        """
        Use fuzzy matching?

        :param bool: set to True if fuzzy matching is to be enabled
        :return:
        """
        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = "fzy.promote=" + input + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = "fzy.promote=" + input
        self.payload["fuzzy"] = input

    def set_subsume(self, bool):
        """
        Take longest hit where an entity is a hit against more than one dictionary
        :param bool: set subsume if True
        :return:
        """
        input = bool_to_string(bool)
        self.payload["subsume"] = input

    def set_entities(self, string):
        """
        Limit the entities to be annotated

        :param string: a comma separated string of entity types, e.g. 'DRUG,GENE'
        :return:
        """
        self.payload["entities"] = string

    def set_input_format(self, string):
        """
        Set input format e.g. txt, medline.xml, node.xml, pdf, xlsx

        :param string: string input format
        :return:
        """
        self.payload["format"] = string

    def set_output_format(self, string):
        """
        Set output format e.g. tsv, json, doc.json

        :param string: provide the output format to be used
        :return:
        """
        self.payload["output"] = string

    def set_reject_ambiguous(self, bool):
        """
        Automatically reject any hits flagged as ambiguous.

        :param bool: set True to reject any ambiguous hits
        :return:
        """
        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = self.payload["opts"] + "&rejectAmbig=" + input
        else:
            self.payload["opts"] = "rejectAmbig=" + input

    def set_max_docs(self, integer):
        """
        When tagging a zip file of multiple documents, limit how many to scan
        also applies where there are multiple document records in a single xml e.g. from a medline XML export

        :param integer: number of documents to limit annotation too
        :return:
        """
        self.payload["maxDocs"] = integer

    def set_no_empty(self, bool):
        """
        Reject all documents where there were no hits

        :param bool: if True do not return any docs with no hits
        :return:
        """
        input = bool_to_string(bool)
        self.payload["noEmpty"] = input

    def execute(self, display_request=False):
        """
        Once all settings are done, POST the parameters to the TERMite RESTful API

        :param display_request: if True request will be printed out before being submitted
        :return:
        """
        if display_request:
            print("REQUEST: ", self.url, self.payload)
        try:
            if self.binary_content and bool(self.basic_auth):
                response = requests.post(self.url, data=self.payload, files=self.binary_content, auth=self.basic_auth,
                                         verify=self.verify_request)
            elif self.binary_content and bool(self.basic_auth) == False:
                response = requests.post(self.url, data=self.payload, files=self.binary_content)
            elif not self.binary_content and bool(self.basic_auth):
                response = requests.post(self.url, data=self.payload, verify=self.verify_request, auth=self.basic_auth)
            else:
                response = requests.post(self.url, data=self.payload)
        except Exception as e:
            print(response.status_code, e)

        if self.payload["output"] in ["json", "doc.json", "doc.jsonx"]:
            return response.json()
        else:
            return response.text


def bool_to_string(bool):
    """
    Convert a boolean to a string

    :param bool: provide boolean to be converted
    :return:
    """
    string = str(bool)
    string = string.lower()

    return string


def annotate_files(url, input_file_path, options_dict):
    """
    Wrapper function to execute a TExpress request for annotating individual files or a zip archive

    :param url: url of TERMite instance
    :param input_file_path: path to file to be annotated
    :param options_dict: dictionary of options to be used during annotation
    :return:
    """
    t = TermiteRequestBuilder()
    t.set_url(url)
    t.set_binary_content(input_file_path)
    t.set_options(options_dict)
    result = t.execute()

    return result


def annotate_text(url, text, options_dict):
    """
    Wrapper function to execute a TExpress request for annotating strings of text

    :param url: url of TERMite instance
    :param input_file_path: path to file to be annotated
    :param options_dict: dictionary of options to be used during annotation
    :return:
    """
    t = TermiteRequestBuilder()
    t.set_url(url)
    t.set_text(text)
    t.set_options(options_dict)
    result = t.execute()

    return result


def get_entity(termite_home, entity_id, entity_type):
    """
    Entity lookup function, given and entity type (e.g. GENE, INDICATION) and entity ID (e.g. CSF1, D010024)
    creates and runs GET call of the format: http://localhost:9090/termite/toolkit/tool.api?t=describe&id=INDICATION:D001249
    returns TERMite json

    :param termite_home: url to TERMite instance
    :param entity_id: id of entity of interest
    :param entity_type: type of entity of interest
    :return:
    """
    url = ("%s/toolkit/tool.api?t=describe&id=%s:%s" % (termite_home, entity_type, entity_id))
    response = requests.get(url)

    if response.ok:
        entity_json = response.json()
        return entity_json

    else:
        return response.status_code


def get_entity_details(termite_home, entity_id, entity_type):
    """
    Returns a subset of metadata from the get_entity result: ID, name, mappings to external IDs

    :param termite_home: url to TERMite instance
    :param entity_id: id of entity of interest
    :param entity_type: type of entity of interest
    :return:
    """
    details = {"id": entity_id, "type": entity_type, "name": "", "mappings": []}
    entity_meta = get_entity(termite_home, entity_id, entity_type)
    if len(entity_meta["TOOL_RESULT"]) > 0:
        e = entity_meta["TOOL_RESULT"][0]
        details["name"] = e["name"]
        if "mappings" in e:
            mappings = e["mappings"]
            for m in mappings:
                items = m.split('|')
                details["mappings"].append(items)

    return details


def process_payload(filtered_hits, response_payload, filter_entity_types, doc_id='', reject_ambig=True, score_cutoff=0,
                    remove_subsumed=True):
    """
    Parses the termite json output to filter out only entity types of interest and their major metadata
    includes rules for rejecting ambiguous or low-relevance hits.

    :param filtered_hits:
    :param response_payload:
    :param filter_entity_types:
    :param doc_id:
    :param reject_ambig:
    :param score_cutoff:
    :param remove_subsumed:
    :return:
    """
    for entity_type, entity_hits in response_payload.items():
        if entity_type in filter_entity_types:
            for entity_hit in entity_hits:
                nonambigsyns = entity_hit["nonambigsyns"]
                entity_score = entity_hit["score"]
                if reject_ambig == True:
                    if nonambigsyns == 0:
                        continue
                if "subsume" in entity_hit and remove_subsumed == True:
                    if True in entity_hit["subsume"]:
                        continue
                if entity_hit["score"] >= score_cutoff:
                    hit_id = entity_hit["hitID"]
                    entity_id = entity_type + '$' + hit_id
                    entity_name = entity_hit["name"]
                    hit_count = entity_hit["hitCount"]
                    if entity_id in filtered_hits:
                        filtered_hits[entity_id]["hit_count"] += hit_count
                        filtered_hits[entity_id]["doc_count"] += 1
                        filtered_hits[entity_id]["doc_id"].append(doc_id)
                        if entity_score > filtered_hits[entity_id]["max_relevance_score"]:
                            filtered_hits[entity_id]["max_relevance_score"] = entity_score
                    else:
                        filtered_hits[entity_id] = {"id": hit_id, "type": entity_type, "name": entity_name,
                                                    "hit_count": hit_count, "max_relevance_score": entity_score,
                                                    "doc_id": [doc_id], "doc_count": 1}

    return filtered_hits


def get_entity_hits_from_json(termite_json_response, filter_entity_types, reject_ambig=True, score_cutoff=0,
                              asDataFrame=False):
    """


    :param termite_json_response: JSON returned from TERMite
    :param filter_entity_types: string of entity types separated by commas
    :param reject_ambig: boolean
    :param score_cutoff: a numeric value between 1-5
    :param asDataFrame: boolean
    :return:
    """
    filtered_hits = {}
    filter_entity_types = filter_entity_types.replace(' ', '').split(',')
    if "RESP_MULTIDOC_PAYLOAD" in termite_json_response:
        doc_results = termite_json_response["RESP_MULTIDOC_PAYLOAD"]
        for doc_id, response_payload in doc_results.items():
            filtered_hits = process_payload(filtered_hits, response_payload, filter_entity_types,
                                            reject_ambig=reject_ambig, score_cutoff=score_cutoff, doc_id=doc_id)

    elif "RESP_PAYLOAD" in termite_json_response:
        response_payload = termite_json_response["RESP_PAYLOAD"]
        filtered_hits = process_payload(filtered_hits, response_payload, filter_entity_types, reject_ambig=reject_ambig,
                                        score_cutoff=score_cutoff)

    if asDataFrame == True:
        filtered_hits_df = pd.DataFrame(filtered_hits).T
        return filtered_hits_df
    else:
        return filtered_hits

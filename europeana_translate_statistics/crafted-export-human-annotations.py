import requests
import json

def create_json_context(json):

    context = {}
    context['as'] = 'https://www.w3.org/ns/activitystreams#'
    context['dc'] = 'http://purl.org/dc/terms/'
    context['dce'] = 'http://purl.org/dc/elements/1.1/'
    context['foaf'] = 'http://xmlns.com/foaf/0.1/'
    context['oa'] = 'http://www.w3.org/ns/oa#'
    context['rdf'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    context['xsd'] = 'http://www.w3.org/2001/XMLSchema#'
    context['soa'] = 'http://sw.islab.ntua.gr/annotation/'
    context['id'] = {'@id': '@id', '@type': '@id'}
    context['type'] = {'@id': '@type', '@type': '@id'}
    context['value'] = 'rdf:value'
    context['created'] = {'@id': 'dc:created', '@type': 'xsd:dateTime'}
    context['creator'] = {'@id': 'dc:creator', '@type': '@id'}
    context['language'] = 'dc:language'
    context['Software'] = 'as:Application'
    context['name'] = 'foaf:name'
    context['Annotation'] = 'oa:Annotation'
    context['TextPositionSelector'] = 'oa:TextPositionSelector'
    context['TextualBody'] = 'oa:TextualBody'
    context['body'] = {'@id': 'oa:hasBody', '@type': '@id'}
    context['scope'] = {'@id': 'oa:hasScope', '@type': '@id'}
    context['selector'] = {'@id': 'oa:hasSelector', '@type': '@id'}
    context['source'] = {'@id': 'oa:hasSource', '@type': '@id'}
    context['target'] = {'@id': 'oa:hasTarget', '@type': '@id'}
    context['Literal'] = 'soa:Literal'
    json['@context'] = context
    return json
    # "@context": {
    # "as": "https://www.w3.org/ns/activitystreams#",
    # "dc": "http://purl.org/dc/terms/",
    # "dce": "http://purl.org/dc/elements/1.1/",
    # "foaf": "http://xmlns.com/foaf/0.1/",
    # "oa": "http://www.w3.org/ns/oa#",
    # "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    # "xsd": "http://www.w3.org/2001/XMLSchema#",
    # "soa": "http://sw.islab.ntua.gr/annotation/",
    # "id": {
    #   "@id": "@id",
    #   "@type": "@id"
    # },
    # "type": {
    #   "@id": "@type",
    #   "@type": "@id"
    # },
    # "value": "rdf:value",
    # "created": {
    #   "@id": "dc:created",
    #   "@type": "xsd:dateTime"
    # },
    # "creator": {
    #   "@id": "dc:creator",
    #   "@type": "@id"
    # },
    # "language": "dc:language",
    # "Software": "as:Application",
    # "name": "foaf:name",
    # "Annotation": "oa:Annotation",
    # "TextPositionSelector": "oa:TextPositionSelector",
    # "TextualBody": "oa:TextualBody",
    # "body": {
    #   "@id": "oa:hasBody",
    #   "@type": "@id"
    # },
    # "scope": {
    #   "@id": "oa:hasScope",
    #   "@type": "@id"
    # },
    # "selector": {
    #   "@id": "oa:hasSelector",
    #   "@type": "@id"
    # },
    # "source": {
    #   "@id": "oa:hasSource",
    #   "@type": "@id"
    # },
    # "target": {
    #   "@id": "oa:hasTarget",
    #   "@type": "@id"
    # },
    # "Literal": "soa: Literal "

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def key_exists_in_dict(dic, key):
    if key in dic.keys():
        return True
    else:
        return False
    
CAMPAIGN_NAME = 'crafted-prato'
# CAMPAIGN_NAME = 'crafted-momu'
# CAMPAIGN_NAME = 'crafted-ekt'

print(f'Campaign name: {CAMPAIGN_NAME}')

CROWDHERITAGE_API_BASE_URL = 'api.crowdheritage.eu'
CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL = "https://{}/annotation/exportCampaignAnnotations?filterForPublish=false&europeanaModelExport=false&campaignName={}".format(CROWDHERITAGE_API_BASE_URL, CAMPAIGN_NAME)
CROWDHERITAGE_GET_CAMPAGIN = f'https://{CROWDHERITAGE_API_BASE_URL}/campaign/getCampaignByName?cname={CAMPAIGN_NAME}'


CROWDHERITAGE_LIST_RECORD_IDS_OF_COLLECTION_URL = f'https://{CROWDHERITAGE_API_BASE_URL}/collection/:id/listRecordIds'
campaign = requests.get(CROWDHERITAGE_GET_CAMPAGIN).json()
campaign_collections = campaign['targetCollections']


record_ids = []
for collection_id in campaign_collections:
    rec_ids = requests.get(CROWDHERITAGE_LIST_RECORD_IDS_OF_COLLECTION_URL.replace(':id', collection_id)).json()['recordIds']
    record_ids.extend(rec_ids)

print(f'Total records in campaign: {len(record_ids)}')

export_annotations_crowdheritage_response = requests.get(CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL)
annotations_json = export_annotations_crowdheritage_response.json()

print(f'Total annotations: {len(annotations_json)}')

annotations_on_records = {}

correct_campaign_annotations = []
for annotation in annotations_json:
    rec_id = annotation['target']['recordId']
    if rec_id in record_ids:
        correct_campaign_annotations.append(annotation)
        if rec_id not in annotations_on_records.keys():
            annotations_on_records[rec_id] = []
        annotations_on_records[rec_id].append(annotation)

print(f'Correct annotations: {len(correct_campaign_annotations)}')

software_annotations = []
human_annotations = []


for annotation in correct_campaign_annotations:
    annotator = annotation['annotators'][0]
    if key_exists_in_dict(annotator, 'externalCreatorType'):
        software_annotations.append(annotation)
    else:
        human_annotations.append(annotation)

print(f'Software annotations: {len(software_annotations)}')
print(f'Human annotations: {len(human_annotations)}')

human_annotations_for_export = []

for annotation in human_annotations:

    if not key_exists_in_dict(annotation, 'score'):
            continue
    # calculate approvals, rejections
    approvals = 0
    if key_exists_in_dict(annotation['score'], 'approvedBy'):
        approvals = len([x for x in annotation['score']['approvedBy'] if x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
    
    rejections = 0
    if key_exists_in_dict(annotation['score'], 'rejectedBy'):
        rejections = len([x for x in annotation['score']['rejectedBy'] if  x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
    
    # if the annotation is not scored, we skip it
    if approvals == 0 and rejections == 0:
        continue

    if approvals > rejections and approvals > 1:
        human_annotations_for_export.append(annotation)

CROWDHERITAGE_GET_RECORD_IDS_CALL = f'https://{CROWDHERITAGE_API_BASE_URL}/record/getRecordsByIds?'
record_id_to_external_id = {}
for id_chunk in chunker(record_ids, 20):
    url = CROWDHERITAGE_GET_RECORD_IDS_CALL
    for id in id_chunk:
        url += f'id={id}&'

    response = requests.get(url)
    response_records = response.json()['records']
    for record in response_records:
        record_id_to_external_id[record['dbId']] = record['administrative']['externalId']

response_json_dict = {}
response_json_dict = create_json_context(response_json_dict)

graph_json_element = []

for annotation in human_annotations_for_export:
    ann = {}
    ann['type'] = 'Annotation'
    created = annotation['annotators'][0]['created']
    ann['created'] = created
    ann['creator'] = { 'type': 'Person' }
    ann['body'] = annotation['body']['uri']
    ann['target'] = { 'source': record_id_to_external_id[annotation['target']['recordId']] }

    graph_json_element.append(ann)

software_annotations_without_score = []
approved_software_annotations = []

for annotation in software_annotations:
    if not key_exists_in_dict(annotation, 'score'):
        software_annotations_without_score.append(annotation)
        continue
    # calculate approvals, rejections
    approvals = 0
    if key_exists_in_dict(annotation['score'], 'approvedBy'):
        approvals = len([x for x in annotation['score']['approvedBy'] if x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
    
    rejections = 0
    if key_exists_in_dict(annotation['score'], 'rejectedBy'):
        rejections = len([x for x in annotation['score']['rejectedBy'] if  x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
    
    if approvals == 0 and rejections == 0:
        software_annotations_without_score.append(annotation)
        continue
    
    if approvals >= rejections:
        approved_software_annotations.append(annotation)

for annotation in software_annotations_without_score:
    ann = {}
    ann['type'] = 'Annotation'
    created = annotation['annotators'][0]['created']
    ann['created'] = created
    ann['creator'] = { 'id': annotation['annotators'][0]['externalCreatorId'], 'type': 'Software', 'name': annotation['annotators'][0]['externalCreatorName'] }
    ann['body'] = annotation['body']['uri']
    ann['target'] = { 'source': record_id_to_external_id[annotation['target']['recordId']] }
    ann['scope'] = annotation['scope']
    graph_json_element.append(ann)

for annotation in approved_software_annotations:
    ann = {}
    ann['type'] = 'Annotation'
    created = annotation['annotators'][0]['created']
    ann['created'] = created
    ann['creator'] = { 'id': annotation['annotators'][0]['externalCreatorId'], 'type': 'Software', 'name': annotation['annotators'][0]['externalCreatorName'] }
    ann['body'] = annotation['body']['uri']
    ann['target'] = { 'source': record_id_to_external_id[annotation['target']['recordId']] }
    ann['review'] = { 'type': 'Validation', 'recommendation': 'accept' }
    ann['scope'] = annotation['scope']
    graph_json_element.append(ann)

# response_json_dict['@graph'] = graph_json_element

annotations_to_exclude = []
for annotation in graph_json_element:
    if key_exists_in_dict(annotation['creator'], 'name') and annotation['creator']['name'] != 'CRAFTED color recognizer with object detection':
        annotations_to_exclude.append(annotation)

response_json_dict['@graph'] = [i for i in graph_json_element if i not in annotations_to_exclude]

with open(f'{CAMPAIGN_NAME}-annotations.json', 'w') as outfile:
    json.dump(response_json_dict, outfile)
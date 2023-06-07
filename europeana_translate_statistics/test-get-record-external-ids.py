import requests

def key_exists_in_dict(dic, key):
    if key in dic.keys():
        return True
    else:
        return False
    
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


# CAMPAIGN_NAME = 'crafted-prato'
# CAMPAIGN_NAME = 'crafted-momu'
CAMPAIGN_NAME = 'crafted-ekt'

print(f'Campaign name: {CAMPAIGN_NAME}')

CROWDHERITAGE_API_BASE_URL = 'api.crowdheritage.eu'
CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL = "https://{}/annotation/exportCampaignAnnotations?filterForPublish=false&europeanaModelExport=false&campaignName={}".format(CROWDHERITAGE_API_BASE_URL, CAMPAIGN_NAME)
CROWDHERITAGE_GET_CAMPAGIN = f'https://{CROWDHERITAGE_API_BASE_URL}/campaign/getCampaignByName?cname={CAMPAIGN_NAME}'


CROWDHERITAGE_LIST_RECORD_IDS_OF_COLLECTION_URL = f'https://{CROWDHERITAGE_API_BASE_URL}/collection/:id/listRecordIds'
campaign = requests.get(CROWDHERITAGE_GET_CAMPAGIN).json()
campaign_collections = campaign['targetCollections']

CROWDHERITAGE_GET_RECORD_IDS_CALL = f'https://{CROWDHERITAGE_API_BASE_URL}/record/getRecordsByIds?'
record_ids = []
for collection_id in campaign_collections:
    rec_ids = requests.get(CROWDHERITAGE_LIST_RECORD_IDS_OF_COLLECTION_URL.replace(':id', collection_id)).json()['recordIds']
    record_ids.extend(rec_ids)

print(f'Total records in campaign: {len(record_ids)}')

record_id_to_external_id = {}
for id_chunk in chunker(record_ids, 20):
    url = CROWDHERITAGE_GET_RECORD_IDS_CALL
    for id in id_chunk:
        url += f'id={id}&'

    response = requests.get(url)
    response_records = response.json()['records']
    for record in response_records:
        record_id_to_external_id[record['dbId']] = record['administrative']['externalId']

print(len(record_id_to_external_id))
print(record_id_to_external_id)
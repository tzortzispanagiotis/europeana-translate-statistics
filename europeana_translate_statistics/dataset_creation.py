import requests
from datetime import date
import csv

def key_exists_in_dict(dic, key):
    if key in dic.keys():
        return True
    else:
        return False

def calculate_average_rating(ratings):  
    scores = 0
    for rating in ratings:
        scores += rating['confidence']
    return scores / len(ratings)

# CAMPAIGN_NAME = 'translate-dutch'
# CAMPAIGN_NAME = 'translate-italian'
CAMPAIGN_NAME = 'translate-french'

CROWDHERITAGE_API_BASE_URL = 'api.crowdheritage.eu'
CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL = "https://{}/annotation/exportCampaignAnnotations?filterForPublish=false&europeanaModelExport=false&campaignName={}".format(CROWDHERITAGE_API_BASE_URL, CAMPAIGN_NAME)

export_annotations_crowdheritage_response = requests.get(CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL)
annotations_json = export_annotations_crowdheritage_response.json()

OUTPUT_FILE_NAME = f'{CAMPAIGN_NAME}-translations-dataset-{date.today().strftime("%d-%m-%Y")}.tsv'
print(len(annotations_json))
with open(OUTPUT_FILE_NAME, 'w') as output_file:
    tsv_writer = csv.writer(output_file, delimiter='\t')
    tsv_writer.writerow(['ORIGINAL TEXT', 'TRANSLATION'])
    for annotation in annotations_json:
        if not (key_exists_in_dict(annotation, 'score') and key_exists_in_dict(annotation['score'], 'ratedBy')):
            continue
        translation = ''
        avg_rating = calculate_average_rating(annotation['score']['ratedBy'])
        if avg_rating >= 89:
            translation = annotation['body']['label']['default'][0]
        for rating in annotation['score']['ratedBy']:
            if key_exists_in_dict(rating, 'validationCorrection'): 
                translation = rating['validationCorrection']
                break
        if translation != '':
            tsv_writer.writerow([annotation['target']['selector']['origValue'], translation])
        else:
            print(annotation['score']['ratedBy'])

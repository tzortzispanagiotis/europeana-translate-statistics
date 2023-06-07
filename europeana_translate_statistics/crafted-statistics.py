import requests
import pprint
from datetime import date

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

# now correct_campaign_annotations holds all the annotations that target a record that participates in the campaign
# and also have the appropriate generator (e.g. CrowdHeritage crafted-prato)
colors = {'beige': 'http://thesaurus.europeanafashion.eu/thesaurus/10778', 
          'black': 'http://thesaurus.europeanafashion.eu/thesaurus/10401', 
          'blue': 'http://thesaurus.europeanafashion.eu/thesaurus/10402', 
          'brown': 'http://thesaurus.europeanafashion.eu/thesaurus/10403', 
          'cyan': 'http://thesaurus.europeanafashion.eu/thesaurus/11097', 
          'green': 'http://thesaurus.europeanafashion.eu/thesaurus/10404', 
          'grey': 'http://thesaurus.europeanafashion.eu/thesaurus/10405', 
          'olive': 'http://thesaurus.europeanafashion.eu/thesaurus/11098', 
          'orange': 'http://thesaurus.europeanafashion.eu/thesaurus/10411', 
          'pink': 'http://thesaurus.europeanafashion.eu/thesaurus/10412', 
          'purple': 'http://thesaurus.europeanafashion.eu/thesaurus/10413', 
          'red': 'http://thesaurus.europeanafashion.eu/thesaurus/10414', 
          'white': 'http://thesaurus.europeanafashion.eu/thesaurus/10416', 
          'yellow': 'http://thesaurus.europeanafashion.eu/thesaurus/10417'
}
colors_list = ['beige', 'black', 'blue', 'brown', 'cyan', 'green', 'grey', 'olive', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
software_annotations = []
human_annotations = []


for annotation in correct_campaign_annotations:
    annotator = annotation['annotators'][0]
    if key_exists_in_dict(annotator, 'externalCreatorType'):
        software_annotations.append(annotation)
    else:
        human_annotations.append(annotation)

print(f'Software annotations: {len(software_annotations)}')

simple_algorithm_color_statistics = {}
object_detection_algorithm_color_statistics = {}
human_annotation_statistics = {}
software_annotations_with_feedback = 0
total_upvotes = 0
total_downvotes = 0

total_annotations_object_algorithm = 0
total_approved_annotations_object_algorithm = 0
total_annotations_simple_algorithm = 0
total_approved_annotations_simple_algorithm = 0

for color in colors.keys():
    object_detection_algorithm_color_statistics[color] = {}
    # object_detection_algorithm_color_statistics[color]['url'] = colors[color]['url']
    object_detection_algorithm_color_statistics[color]['total'] = 0
    object_detection_algorithm_color_statistics[color]['upvotes'] = 0
    object_detection_algorithm_color_statistics[color]['downvotes'] = 0
    object_detection_algorithm_color_statistics[color]['true_positives'] = 0
    object_detection_algorithm_color_statistics[color]['true_negatives'] = 0
    object_detection_algorithm_color_statistics[color]['false_positives'] = 0
    object_detection_algorithm_color_statistics[color]['false_negatives'] = 0

    simple_algorithm_color_statistics[color] = {}
    # simple_algorithm_color_statistics[color]['url'] = colors[color]['url']
    simple_algorithm_color_statistics[color]['total'] = 0
    simple_algorithm_color_statistics[color]['upvotes'] = 0
    simple_algorithm_color_statistics[color]['downvotes'] = 0
    simple_algorithm_color_statistics[color]['true_positives'] = 0
    simple_algorithm_color_statistics[color]['true_negatives'] = 0
    simple_algorithm_color_statistics[color]['false_positives'] = 0
    simple_algorithm_color_statistics[color]['false_negatives'] = 0

    human_annotation_statistics[color] = {}
    human_annotation_statistics[color]['total'] = 0
    human_annotation_statistics[color]['approved'] = 0

for annotation in software_annotations:
    if annotation['annotators'][0]['externalCreatorName'] == 'CRAFTED color recognizer with object detection':
        total_annotations_object_algorithm += 1
        color = annotation['body']['label']['en'][0]   
        object_detection_algorithm_color_statistics[color]['total'] += 1
        if key_exists_in_dict(annotation, 'score'):
            
            score = annotation['score']
            
            approvals = 0
            if key_exists_in_dict(score, 'approvedBy'):
                approvals = len([x for x in annotation['score']['approvedBy'] if x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
            
            rejections = 0
            if key_exists_in_dict(score, 'rejectedBy'):
                rejections = len([x for x in annotation['score']['rejectedBy'] if  x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
           
            object_detection_algorithm_color_statistics[color]['upvotes'] += approvals
            object_detection_algorithm_color_statistics[color]['downvotes'] += rejections
            total_upvotes += approvals
            total_downvotes += rejections
            
            if approvals >= rejections:
                total_approved_annotations_object_algorithm += 1
    else:
        total_annotations_simple_algorithm += 1
        color = annotation['body']['label']['default'][0]   
        simple_algorithm_color_statistics[color]['total'] += 1
        if key_exists_in_dict(annotation, 'score'):

            score = annotation['score']

            approvals = 0
            if key_exists_in_dict(score, 'approvedBy'):
                approvals = len([x for x in annotation['score']['approvedBy'] if x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
            
            rejections = 0
            if key_exists_in_dict(score, 'rejectedBy'):
                rejections = len([x for x in annotation['score']['rejectedBy'] if  x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
            
            simple_algorithm_color_statistics[color]['upvotes'] += approvals
            simple_algorithm_color_statistics[color]['downvotes'] += rejections
            total_upvotes += approvals
            total_downvotes += rejections
            if not(approvals == 0 and rejections == 0):
                software_annotations_with_feedback += 1
            if approvals >= rejections:
                total_approved_annotations_simple_algorithm += 1

# iterate to the annotations of every record
for record in annotations_on_records:
    annotations = annotations_on_records[record]

    # here we keep for each algorithm the 'correctly' added annotations
    annotations_object = []
    annotations_simple = []

    # iterate to the annotations of the record
    for annotation in annotations:
        # if the annotation is not scored, we skip it
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
        
        algorithm = annotation['annotators'][0]['externalCreatorName'] if key_exists_in_dict(annotation['annotators'][0], 'externalCreatorName') else None
        color = annotation['body']['label']['default'][0].lower()
        
        # calculate true positives, false positives
        if algorithm is not None:
            if algorithm == 'CRAFTED color recognizer with object detection':
                if approvals >= rejections:
                    object_detection_algorithm_color_statistics[color]['true_positives'] += 1
                    # since color was correctly added by software generated annotation, add it to the list
                    annotations_object.append(color)
                else:
                    object_detection_algorithm_color_statistics[color]['false_positives'] += 1
            else:
                if approvals >= rejections:
                    simple_algorithm_color_statistics[color]['true_positives'] += 1
                    # since color was correctly added by software generated annotation, add it to the list
                    annotations_simple.append(color)
                else:
                    simple_algorithm_color_statistics[color]['false_positives'] += 1

    # iterate once again for the human annotations
    for annotation in annotations:
        if not key_exists_in_dict(annotation, 'score'):
            continue

        approvals = 0
        if key_exists_in_dict(annotation['score'], 'approvedBy'):
            approvals = len([x for x in annotation['score']['approvedBy'] if x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])
        
        rejections = 0
        if key_exists_in_dict(annotation['score'], 'rejectedBy'):
            rejections = len([x for x in annotation['score']['rejectedBy'] if  x['generator'] == 'CrowdHeritage ' + CAMPAIGN_NAME])

        if approvals == 0 and rejections == 0:
            continue

        algorithm = annotation['annotators'][0]['externalCreatorName'] if key_exists_in_dict(annotation['annotators'][0], 'externalCreatorName') else None
        color = annotation['body']['label']['en'][0].lower()

        if not algorithm:
            if approvals >= rejections:
                object_detection_algorithm_color_statistics[color]['false_negatives'] += 1
                simple_algorithm_color_statistics[color]['false_negatives'] += 1

    # now get the colors that were not added by the algo, and this was a correct decision
    colors_not_added_correctly_by_object_algorithm = [x for x in colors_list if x not in annotations_object]
    colors_not_added_correctly_by_simple_algorithm = [x for x in colors_list if x not in annotations_simple]

    for color in colors_not_added_correctly_by_object_algorithm:
        object_detection_algorithm_color_statistics[color]['true_negatives'] += 1

    for color in colors_not_added_correctly_by_simple_algorithm:
        simple_algorithm_color_statistics[color]['true_negatives'] += 1

for color in colors_list:
    simple_algorithm_color_statistics[color]['precision'] = round(simple_algorithm_color_statistics[color]['true_positives'] / (simple_algorithm_color_statistics[color]['true_positives'] + simple_algorithm_color_statistics[color]['false_positives']),3 )
    simple_algorithm_color_statistics[color]['recall'] = round(simple_algorithm_color_statistics[color]['true_positives'] / (simple_algorithm_color_statistics[color]['true_positives'] + simple_algorithm_color_statistics[color]['false_negatives']), 3)
    simple_algorithm_color_statistics[color]['accuracy'] = round((simple_algorithm_color_statistics[color]['true_positives'] + simple_algorithm_color_statistics[color]['true_negatives']) / (simple_algorithm_color_statistics[color]['true_positives'] + simple_algorithm_color_statistics[color]['true_negatives'] + simple_algorithm_color_statistics[color]['false_positives'] + simple_algorithm_color_statistics[color]['false_negatives']), 3)
    object_detection_algorithm_color_statistics[color]['precision'] = round(object_detection_algorithm_color_statistics[color]['true_positives'] / (object_detection_algorithm_color_statistics[color]['true_positives'] + object_detection_algorithm_color_statistics[color]['false_positives']),3 )
    object_detection_algorithm_color_statistics[color]['recall'] = round(object_detection_algorithm_color_statistics[color]['true_positives'] / (object_detection_algorithm_color_statistics[color]['true_positives'] + object_detection_algorithm_color_statistics[color]['false_negatives']), 3)
    object_detection_algorithm_color_statistics[color]['accuracy'] = round((object_detection_algorithm_color_statistics[color]['true_positives'] + object_detection_algorithm_color_statistics[color]['true_negatives']) / (object_detection_algorithm_color_statistics[color]['true_positives'] + object_detection_algorithm_color_statistics[color]['true_negatives'] + object_detection_algorithm_color_statistics[color]['false_positives'] + object_detection_algorithm_color_statistics[color]['false_negatives']), 3)

print(f'Software annotations with feedback: {software_annotations_with_feedback}')
print(f'Total upvotes: {total_upvotes}')
print(f'Total downvotes: {total_downvotes}')
print(f'Human annotations: {len(human_annotations)}')



print('\nTotal accuracy statistics for algorithms:')
total_true_positives_object = 0
total_false_positives_object = 0
total_true_negatives_object = 0
total_false_negatives_object = 0

total_true_positives_simple = 0
total_false_positives_simple = 0
total_true_negatives_simple = 0
total_false_negatives_simple = 0

for color in colors_list:
    total_true_positives_object += object_detection_algorithm_color_statistics[color]['true_positives']
    total_false_positives_object += object_detection_algorithm_color_statistics[color]['false_positives']
    total_true_negatives_object += object_detection_algorithm_color_statistics[color]['true_negatives']
    total_false_negatives_object += object_detection_algorithm_color_statistics[color]['false_negatives']

    total_true_positives_simple += simple_algorithm_color_statistics[color]['true_positives']
    total_false_positives_simple += simple_algorithm_color_statistics[color]['false_positives']
    total_true_negatives_simple += simple_algorithm_color_statistics[color]['true_negatives']
    total_false_negatives_simple += simple_algorithm_color_statistics[color]['false_negatives']

print('Object Detection Stats:')
print(f'Total annotations from object detection algorithm: {total_annotations_object_algorithm}')
print(f'Total  approved annotations from object detection algorithm: {total_approved_annotations_object_algorithm}')
print(f'Object algorithm precision: {round(total_true_positives_object / (total_true_positives_object + total_false_positives_object),3 )}')
print(f'Object algorithm recall: {round(total_true_positives_object / (total_true_positives_object + total_false_negatives_object), 3)}')
print(f'Object algorithm accuracy: {round((total_true_positives_object + total_true_negatives_object) / (total_true_positives_object + total_true_negatives_object + total_false_positives_object + total_false_negatives_object), 3)}')
print()
print('Statistics by color:')
pprint.pprint(object_detection_algorithm_color_statistics, sort_dicts=False)

print('\nSimple algorithm stats:')
print(f'Total annotations from simple algorithm: {total_annotations_simple_algorithm}')
print(f'Total  approved annotations from simple algorithm: {total_approved_annotations_simple_algorithm}')
print(f'Simple algorithm precision: {round(total_true_positives_simple / (total_true_positives_simple + total_false_positives_simple),3 )}')
print(f'Simple algorithm recall: {round(total_true_positives_simple / (total_true_positives_simple + total_false_negatives_simple), 3)}')
print(f'Simple algorithm accuracy: {round((total_true_positives_simple + total_true_negatives_simple) / (total_true_positives_simple + total_true_negatives_simple + total_false_positives_simple + total_false_negatives_simple), 3)}')
print()

print('Statistics by color:')
pprint.pprint(simple_algorithm_color_statistics, sort_dicts=False)

for annotation in human_annotations:
    color = annotation['body']['label']['en'][0].lower()
    human_annotation_statistics[color]['total'] += 1

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
        human_annotation_statistics[color]['approved'] += 1

print('Human annotation stats:')
pprint.pprint(human_annotation_statistics, sort_dicts=False)
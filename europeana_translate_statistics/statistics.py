import requests

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

def print_final_report(statistics):
    print('-------------------------------')
    print('GENERAL STATISTICS')
    print('-------------------------------')
    print('Total annotations: {}'.format(TOTAL_ANNOTATIONS))
    print('Annotations with ratings: {}'.format(annotations_with_score))
    print('Average rating: {}'.format(sum(all_annotations_avg_ratings_list) / annotations_with_score, 2) if annotations_with_score else 0)
    print('corellation whatever:\n')

    print('\n')

    for stat in statistics:
        print('-------------------------------')
        print('Property name: {}'.format(stat['property_name']))
        print('-------------------------------')
        print('Annotations: {}'.format(stat['annotations_count']))
        print('Annotations with feedback: {}'.format(stat['annotations_with_feedback_count']))
        print('Average rating of property: {}'.format(stat['avg_rating']))
        print('\n')

CAMPAIGN_NAME = 'translate-dutch'
CROWDHERITAGE_API_BASE_URL = 'api.crowdheritage.eu'
CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL = "https://{}/annotation/exportCampaignAnnotations?filterForPublish=false&europeanaModelExport=false&campaignName={}".format(CROWDHERITAGE_API_BASE_URL, CAMPAIGN_NAME)

export_annotations_crowdheritage_response = requests.get(CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL)
annotations_json = export_annotations_crowdheritage_response.json()
annotations_per_propetry = {}
property_statistics = {}

TOTAL_ANNOTATIONS = len(annotations_json)
all_annotations_avg_ratings_list = []
all_annotations_confidence_list = []
annotations_with_score = 0

for annotation in annotations_json:
    annotation_property = annotation['target']['selector']['property']

    # if property first encounter, initialize relevant fields
    if annotation_property not in annotations_per_propetry:
        annotations_per_propetry[annotation_property] = []
        property_statistics[annotation_property] = {}
        property_statistics[annotation_property]['property_name'] = annotation_property
        property_statistics[annotation_property]['annotations_count'] = 0
        property_statistics[annotation_property]['annotations_with_feedback_count'] = 0
        property_statistics[annotation_property]['average_propery_ratings_list'] = []
    
    annotations_per_propetry[annotation_property].append(annotation)
    property_statistics[annotation_property]['annotations_count'] += 1

    # annotation has score, so calculate statistics of score
    if key_exists_in_dict(annotation, 'score') and key_exists_in_dict(annotation['score'], 'ratedBy'):
        property_statistics[annotation_property]['annotations_with_feedback_count'] += 1
        ratings = annotation['score']['ratedBy']
        avg_rating = calculate_average_rating(ratings)
        property_statistics[annotation_property]['average_propery_ratings_list'].append(avg_rating)
        # print(avg_rating / 100)
        all_annotations_avg_ratings_list.append(round(avg_rating / 100,2))
        all_annotations_confidence_list.append(annotation['annotators'][0]['confidence'])
        annotations_with_score += 1

statistics = []
for key, value in property_statistics.items():
    statistics.append(value)

for stat in statistics:
    avg_stats_list = stat['average_propery_ratings_list']
    annotations_with_feedback = stat['annotations_with_feedback_count']
    stat['avg_rating'] = round(sum(avg_stats_list) / annotations_with_feedback if annotations_with_feedback else 0, 2)
    stat.pop('average_propery_ratings_list')

# print_final_report(statistics)
print(len(all_annotations_confidence_list))

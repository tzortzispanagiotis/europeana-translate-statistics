import requests
import numpy as np
from fpdf import FPDF
from datetime import date
import matplotlib.pyplot as plt
from statistics import stdev

plt.style.use('ggplot')

ERROR_TYPES = {
    "ERROR_1":
        {
            "shortDescription" : "Incorrect translations of named references",
            "longDescription" : "Incorrect/undesidered translations of named references (incl. historical names)",
            "severity" : "Severe"
        }, 
    "ERROR_2":
        {
                        "shortDescription" : "Mistranslation of idiomatic expression",
            "longDescription" : "Mistranslation of idiomatic expressions",
            "severity" : "Severe"
        }, 
    "ERROR_3":
        {
                        "shortDescription" : "Incomplete translations",
            "longDescription" : "Incomplete translations",
            "severity" : "Severe"
        }, 
    "ERROR_4":
        {
            "shortDescription" : "Undesired translations of quoted text",
            "longDescription" : "Undesired translations of quoted text",
            "severity" : "Severe"
        }, 
    "ERROR_5":
        {
                        "shortDescription" : "Biases - descriminations - prejudices",
            "longDescription" : "Biases that represent human discriminations and prejudices: gender bias, ableism, etc.",
            "severity" : "Severe"
        }, 
    "ERROR_6":
        {
                        "shortDescription" : "Bad word selection",
            "longDescription" : "Bad word selection when a term has multiple translations",
            "severity" : "High"
        }, 
    "ERROR_7":
        {
                        "shortDescription" : "Inconsistent translations",
            "longDescription" : "Inconsistent translations (a word is translated differently in different places, whereas the same translation should be used)",
            "severity" : "MediumHigh"
        }, 
    "ERROR_8":
        {
                        "shortDescription" : "Spelling mistakes - Correct source",
            "longDescription" : "Spelling mistakes in the translation while the source is correct",
            "severity" : "Medium"
        }, 
    "ERROR_9":
        {
                        "shortDescription" : "Grammatical mistakes",
            "longDescription" : "Grammatical mistakes: genre, number, etc",
            "severity" : "MediumLow"
        }, 
    "ERROR_10":
        {
            
            "shortDescription" : "Wrong encoding - escaping",
            "longDescription" : "Translations with wrong encoding or escaping of characters",
            "severity" : "MediumLow"
        }, 
    "ERROR_11":
        {
            
            "shortDescription" : "Removed punctuation of names, acronyms",
            "longDescription" : "Removing of punctuation when dealing with names and acronyms",
            "severity" : "MediumLow"
        }, 
    "ERROR_12":
        {
            
            "shortDescription" : "Variation of word order",
            "longDescription" : "Variation of word order, words omitted, inserted or replaced with synonymous expressions",
            "severity" : "MediumLow"
        },
    "ERROR_13": 
        {
            
            "shortDescription" : "Errors in original text",
            "longDescription" : "Errors in original text",
            "severity" : "Low"
        }
}
class PDF(FPDF):
    def __init__(self, name_of_report):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self.name_of_report = name_of_report
    
    def header(self):
        # Custom logo and positioning
        # Create an `assets` folder and put any wide and short image inside
        # Name the image `logo.png`
        self.image('assets/ic-logo2.png', 160, 8, 40)
        self.set_font('Arial', 'B', 15)
        self.cell(1, h=2,ln=1)

        self.cell(60, 1, '{} Report ({})'.format(self.name_of_report, date.today().strftime("%d/%m/%Y")), 0, 0)
        self.ln(20)

    def footer(self):
        # Page numbers in the footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

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

def calculate_correlation_coefficient(x, y):
    x_formatted = np.array(x)
    y_formatted = np.array(y)
    coefficient = np.corrcoef(x_formatted,y_formatted)
    # print(coefficient)
    # plt.matshow(coefficient)
    # plt.savefig('a.png')
    # plt.imsave('test.png', img)
    return coefficient

def print_final_report(statistics):
    print('-------------------------------')
    print('GENERAL STATISTICS')
    print('-------------------------------')
    print('Total annotations: {}'.format(TOTAL_ANNOTATIONS))
    print('Annotations with ratings: {}'.format(annotations_with_score))
    print('Average rating: {}'.format(sum(all_annotations_avg_ratings_list) / annotations_with_score, 2) if annotations_with_score else 0)
    print('corellation whatever:')
    print(np.corrcoef(all_annotations_avg_ratings_list, all_annotations_confidence_list))
    print('\n')

    for stat in statistics:
        print('-------------------------------')
        print('Property name: {}'.format(stat['property_name']))
        print('-------------------------------')
        print('Annotations: {}'.format(stat['annotations_count']))
        print('Annotations with feedback: {}'.format(stat['annotations_with_feedback_count']))
        print('Average rating of property: {}'.format(stat['avg_rating']))
        print('\n')

def print_pdf_report_for_annotations_extended_feedback():
    pdf = PDF('Validation Feedback')
    pdf.add_font('Arial', "", "assets/arial/arial.ttf", uni=True)
    pdf.add_page()
    

    for index, annotation in enumerate(annotations_with_extended_feedback, start=1):
        pdf.set_font('Arial', 'U', 14)
        pdf.cell(w=0, h=8,txt="Translation #{}".format(index),border=0, ln=1)
        pdf.set_font('Arial', size=10)
        pdf.cell(w=0, h=8,txt="Property: {}".format(annotation['target']['selector']['property']),border=0, ln=1)
        pdf.multi_cell(w=0, h=8,txt="Original Value: {}".format(annotation['target']['selector']['origValue']),border=0)
        pdf.cell(w=0, h=8,txt="Original Language: {}".format(annotation['target']['selector']['origLang']),border=0, ln=1)
        pdf.multi_cell(w=0, h=8,txt="Translation: {}".format(annotation['body']['label']['default'][0]),border=0)
        pdf.ln(5)
        ratings = annotation['score']['ratedBy']
        for rating in ratings:
            if key_exists_in_dict(rating, 'validationErrorType') or key_exists_in_dict(rating, 'validationComment') or key_exists_in_dict(rating, 'validationCorrection'):
                pdf.set_font('Arial', 'U', 10)
                pdf.cell(w=0, h=8,txt="Translation review",border=0, ln=1)
                pdf.set_font('Arial', size=10)
                pdf.cell(5)
                pdf.cell(w=0, h=8,txt="Translation rating: {}".format(rating['confidence']),border=0, ln=1)
                if key_exists_in_dict(rating, 'validationErrorType'):
                    pdf.set_font('Arial', size=10)
                    pdf.cell(5)
                    pdf.cell(w=0, h=8,txt="Translation Error Types:",border=0, ln=1)
                    
                    for index, error_type in enumerate(rating['validationErrorType'], start=1):
                        pdf.cell(7)
                        pdf.cell(w=0, h=8,txt="{}. {}".format(index, ERROR_TYPES[error_type]['shortDescription']),border=0, ln=1)
                if key_exists_in_dict(rating, 'validationComment'):
                    pdf.cell(5)

                    pdf.multi_cell(w=0, h=8,txt="Validation Comment: {}".format(rating['validationComment']),border=0)
                if key_exists_in_dict(rating, 'validationCorrection'):
                    pdf.cell(5)
                    pdf.multi_cell(w=0, h=8,txt="Validation Correction: {}".format(rating['validationCorrection']),border=0)
                pdf.ln(5)
        pdf.ln(5)
    pdf.output('{}-translations-extended-feedback-report-{}.pdf'.format(CAMPAIGN_NAME, date.today().strftime("%d-%m-%Y")), 'F')

def print_pdf_report_for_statistics():
    pdf = PDF('Ratings')
    pdf.add_page()
    pdf.set_font('Arial', 'BU', 16)
    pdf.cell(40,10, "General Statistics",0)
    pdf.ln(15)

    pdf.set_font('Arial', size=14)
    pdf.cell(w=0, h=8,txt="Campaign name: {}".format(CAMPAIGN_NAME),border=0, ln=1)
    pdf.cell(w=0, h=8,txt="Total annotations: {}".format(TOTAL_ANNOTATIONS),border=0, ln=1)
    avg_rat = sum([ item / 10 for item in all_annotations_avg_ratings_list]) / annotations_with_score if annotations_with_score else 0
    pdf.cell(w=0, h=8,txt="Annotations with ratings: {}".format(annotations_with_score),border=0, ln=1)
    pdf.cell(w=0, h=8,txt="Average rating: {}".format(round(avg_rat,3)),border=0, ln=1)
    pdf.cell(w=0, h=8,txt="Average confidence: {}".format(round(sum(all_annotations_confidence_list) / annotations_with_score if annotations_with_score else 0,3)),border=0, ln=1)
    corr_matrix = calculate_correlation_coefficient(all_annotations_avg_ratings_list, all_annotations_confidence_list)
    pdf.cell(w=0, h=8, txt="Pearson Correlation coefficient: {}".format(round(corr_matrix[0][1], 3)), border=0, ln=1)
    pdf.cell(w=0, h=8, txt="Standard deviation of human-generated rating scores: {}".format(round(stdev([ item / 10 for item in all_annotations_avg_ratings_list ]), 3)), border=0, ln=1)
    pdf.cell(w=0, h=8, txt="Standard deviation of software-generated confidence scores: {}".format(round(stdev(all_annotations_confidence_list), 3)), border=0, ln=1)

    pdf.ln(10)

    pdf.set_font('Arial', 'BU', 16)
    pdf.cell(40,10, "General Error Type Statistics",0)
    pdf.ln(15)
    for error_type in all_annotations_error_type:
        pdf.set_font('Arial', size=14)
        pdf.cell(w=0, h=8,txt="{}: {}".format(ERROR_TYPES[error_type]['shortDescription'], all_annotations_error_type[error_type]),border=0, ln=1)
       
    pdf.ln(10)

    pdf.set_font('Arial', 'BU', 16)
    pdf.cell(40,10, "Statistics per field",0)
    pdf.ln(20)
    pdf.set_font('Arial', size=14)

    for stat in statistics:
        pdf.set_font('Arial', 'BU', size=14)
        pdf.cell(w=0, h=8,txt="Property name: {}".format(stat['property_name']),border=0, ln=1)
        pdf.set_font('Arial', size=14)
        pdf.cell(w=0, h=8,txt="Annotations with ratings: {}".format(stat['annotations_with_feedback_count']),border=0, ln=1)
        pdf.cell(w=0, h=8,txt="Average rating: {}".format(round(stat['avg_rating'] / 10, 3)),border=0, ln=1)
        pdf.cell(w=0, h=8,txt="Average confidence: {}".format(round(sum(stat['confidence_values_list']) / stat['annotations_with_feedback_count'] if stat['annotations_with_feedback_count'] else 0, 3)),border=0, ln=1)
        corr_matrix = calculate_correlation_coefficient([ item / 10 for item in stat['average_propery_ratings_list']], [item / 10 for item in stat['confidence_values_list']])
        pdf.cell(w=0, h=8,txt="Pearson Correlation Coefficient: {}".format(round(corr_matrix[0][1], 3)),border=0, ln=1)
        if len(stat['average_propery_ratings_list']) > 1:
            pdf.cell(w=0, h=8, txt="Standard deviation of human-generated rating scores: {}".format(round(stdev([ item / 10 for item in stat['average_propery_ratings_list']]), 3)), border=0, ln=1)
        else:
            pdf.cell(w=0, h=8, txt="-", border=0, ln=1)
        if len(stat['confidence_values_list']) > 1:
            pdf.cell(w=0, h=8, txt="Standard deviation of software-generated confidence scores: {}".format(round(stdev(stat['confidence_values_list']), 3)), border=0, ln=1)
        else:
            pdf.cell(w=0, h=8, txt="-", border=0, ln=1)

        pdf.ln(5)

        pdf.set_font('Arial', 'U', size=14)
        pdf.cell(w=0, h=8,txt="Error Type Statistics:",border=0, ln=1)
        pdf.ln(5)
        pdf.set_font('Arial', size=14)
        
        for error_type in stat['error_types']:
            pdf.cell(5)
            pdf.cell(w=0, h=8,txt="{}: {}".format(ERROR_TYPES[error_type]['shortDescription'], stat['error_types'][error_type]),border=0, ln=1)
        

        pdf.ln(10)

    pdf.output('{}-annotations-report-{}.pdf'.format(CAMPAIGN_NAME, date.today().strftime("%d-%m-%Y")), 'F')

# CAMPAIGN_NAME = 'translate-dutch'
# CAMPAIGN_NAME = 'translate-italian'
CAMPAIGN_NAME = 'translate-french'
CROWDHERITAGE_API_BASE_URL = 'api.crowdheritage.eu'
CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL = "https://{}/annotation/exportCampaignAnnotations?filterForPublish=false&europeanaModelExport=false&campaignName={}".format(CROWDHERITAGE_API_BASE_URL, CAMPAIGN_NAME)

export_annotations_crowdheritage_response = requests.get(CROWDHERITAGE_EXPORT_CAMPAIGN_ANNOTATIONS_URL)
annotations_json = export_annotations_crowdheritage_response.json()
annotations_per_propetry = {}
property_statistics = {}

TOTAL_ANNOTATIONS = len(annotations_json)
all_annotations_avg_ratings_list = []
all_annotations_confidence_list = []
all_annotations_error_type = {}
for key in ERROR_TYPES:
    all_annotations_error_type[key] = 0

annotations_with_score = 0
annotations_with_extended_feedback = []

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
        property_statistics[annotation_property]['confidence_values_list'] = []
        property_statistics[annotation_property]['error_types'] = {}
        for key in ERROR_TYPES:
            property_statistics[annotation_property]['error_types'][key] = 0
    
    annotations_per_propetry[annotation_property].append(annotation)
    property_statistics[annotation_property]['annotations_count'] += 1

    # annotation has score, so calculate statistics of score
    if key_exists_in_dict(annotation, 'score') and key_exists_in_dict(annotation['score'], 'ratedBy'):
        property_statistics[annotation_property]['annotations_with_feedback_count'] += 1
        ratings = annotation['score']['ratedBy']
        annotation_error_types = []

        for rating in ratings:
            if key_exists_in_dict(rating, 'validationErrorType'):
                for error_type in rating['validationErrorType']:
                    if error_type not in annotation_error_types:
                        annotation_error_types.append(error_type)
        for err_type in annotation_error_types:
            all_annotations_error_type[err_type] += 1
            property_statistics[annotation_property]['error_types'][err_type] += 1

        for rating in ratings:
            if key_exists_in_dict(rating, 'validationErrorType') or key_exists_in_dict(rating, 'validationComment') or key_exists_in_dict(rating, 'validationCorrection'):
                annotations_with_extended_feedback.append(annotation)
                break
        avg_rating = calculate_average_rating(ratings)
        property_statistics[annotation_property]['average_propery_ratings_list'].append(avg_rating)
        property_statistics[annotation_property]['confidence_values_list'].append(annotation['annotators'][0]['confidence'])
        # print(avg_rating / 100)
        all_annotations_avg_ratings_list.append(avg_rating)
        all_annotations_confidence_list.append(annotation['annotators'][0]['confidence'])
        annotations_with_score += 1

statistics = []
for key, value in property_statistics.items():
    statistics.append(value)

for stat in statistics:
    avg_stats_list = stat['average_propery_ratings_list']
    annotations_with_feedback = stat['annotations_with_feedback_count']
    stat['avg_rating'] = sum(avg_stats_list) / annotations_with_feedback if annotations_with_feedback else 0

print_pdf_report_for_statistics()
print_pdf_report_for_annotations_extended_feedback()
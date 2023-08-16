#dataflow pipeline code to run 
import apache_beam as beam
import os
import argparse
import logging
import pandas as  pd
import datetime
import pytz
from oauth2client.client import GoogleCredentials
from datetime import datetime,date,timedelta
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import time
import json
import requests
from google.cloud import pubsub_v1
import google.cloud.dlp_v2
from json import loads
import smtplib
from email.utils import formataddr
#from google.cloud import dlp_v2
from google.protobuf import json_format

class readandwrite(beam.DoFn):
    def deidentify_content_with_dlp(self,content_json):
        import google.cloud.dlp_v2
        from google.cloud import pubsub_v1
        # Existing code for DLP de-identification
        publish_topic="dlp_data"
        publisher = pubsub_v1.PublisherClient()
        dlp_client = google.cloud.dlp_v2.DlpServiceClient()
        item = {"value": json.dumps(content_json)}
        credit_card_info_type = {"name": "CREDIT_CARD_NUMBER"}
        phone_number_info_type = {"name": "PHONE_NUMBER"}
        aadhar_card_info_type = {"name": "INDIA_AADHAAR_INDIVIDUAL"}
        email_info_type={"name":"EMAIL_ADDRESS"}

    # Update: Include info types in InspectConfig
        inspect_config = {
            "info_types": [
                credit_card_info_type,
                phone_number_info_type,
                aadhar_card_info_type,
                email_info_type
            ]
        }

        # Use a consistent number of masked characters for all info types
        # The transformation configuration to de-identify the content.
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        "info_types": [credit_card_info_type],
                        "primitive_transformation": {
                            "character_mask_config": {
                                "masking_character": "#",
                                "number_to_mask":14 ,
                                "characters_to_ignore": [
                                    {"characters_to_skip": "-"},
                                    #{"characters_to_skip": "."}
                                    
                                ],
                                "reverse_order":True,
                            }
                        },
                    },
                    {
                        "info_types": [phone_number_info_type],
                        "primitive_transformation": {
                            "character_mask_config": {
                                "masking_character": "#",
                                "number_to_mask": 8,
                                "characters_to_ignore": [
                                    {"characters_to_skip": "-"},
                                    #{"characters_to_skip": "."}
                                ],
                                "reverse_order":True,
                                
                            }
                        }
                    },
                    {
                        "info_types": [email_info_type],
                        "primitive_transformation": {
                            "character_mask_config": {
                                "masking_character": "#",
                                "number_to_mask": 15,
                                "characters_to_ignore": [
                                    {"characters_to_skip": "@"},
                                    {"characters_to_skip": "."}
                                ],
                                "reverse_order":True,
                            }
                        }
                    },

                    {
                        "info_types": [aadhar_card_info_type],
                        "primitive_transformation": {
                            "character_mask_config": {
                                "masking_character": "#",
                                "number_to_mask": 10,
                                "characters_to_ignore": [
                                    {"characters_to_skip": "-"},
                                    #{"characters_to_skip": "."}
                                ],
                                "reverse_order":True,
                            }
                        },
                    },
                ]
            }
        }


        # Convert the project ID into a full resource ID.
        project_id = "sandydev"
        parent = f"projects/{project_id}"

        # Call the API to inspect and de-identify the content.
        try:
            response = dlp_client.deidentify_content(
                request={
                    "parent": parent,
                    "inspect_config": inspect_config,  # Include the inspect config
                    "deidentify_config": deidentify_config,
                    "item": item,
                }
            )

            # Check if PII information was found by DLP
            logging.info("Applying DLP de-identification...")
            if response.item.value and response.overview.transformation_summaries:
                logging.info("Sensitive Data found")
                topic_path = publisher.topic_path(project_id, publish_topic)
                message_data = json.dumps(content_json).encode('utf-8')
                logging.info(message_data)
                publisher.publish(topic_path, message_data)
                #logging.info("data published", message_data)

            return json.loads(response.item.value) if response.item.value else content_json
        except Exception as e:
            print(f"Error: {e}")
            print("Error during de-identification. Inserting original content to BigQuery.")
            return content_json  # In case of an error, insert the original content to BigQuery
            logging.info("DLP de-identification completed...")

    def process(self, conetxt):
        import time
        import json
        import requests
        from google.cloud import pubsub_v1
        import google.cloud.dlp_v2
        from json import loads
        import smtplib
        from email.utils import formataddr
        from google.cloud import bigquery
        project_id = "sandydev"
        subscription_id = "audio_msg-sub"
        client_bigquery = bigquery.Client()
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project_id, subscription_id)
        masked_table_id = "sandydev.call_interaction.cleansed_dlp_raw_table"
        raw_table_id="sandydev.call_interaction.raw_audio_data"
        dlp_count_table_id="sandydev.call_interaction.dlp_count"
        max_messages = 1
        count=0
        rows_to_insert_raw = []  # Clear the list after inserting the rows
        rows_to_insert_masked = []
        rows_to_insert_dlp_count=[]
        logging.info("Starting data processing workflow...")
        while True:
            response = subscriber.pull(request={"subscription": subscription_path, "max_messages": max_messages})

            for received_message in response.received_messages:
                message = received_message.message
                content_json = json.loads(message.data.decode('utf-8'))
                masked_data = self.deidentify_content_with_dlp(content_json)
                logging.info(masked_data)
                audio_file_name=masked_data['audio_file_name']
                print("masked data is :" , masked_data)
                dlp_list= masked_data['text'].split(" ")
                for value in dlp_list:
                    if '#' in value:
                        count += 1
                print("masked data count:", count)
                insert_data = {
                    "audio_file_name": audio_file_name,
                    "PII_count": count
                }
                rows_to_insert_dlp_count.append(insert_data)
                load_PII_count = client_bigquery.insert_rows_json(dlp_count_table_id, rows_to_insert_dlp_count)
                count=0
                ##extract audio file name and the count value and insert to another bigquery table
                subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": [received_message.ack_id]})
                #inserts original data to a different bigquery table
                rows_to_insert_raw.append(content_json)
                load_raw = client_bigquery.insert_rows_json(raw_table_id, rows_to_insert_raw)

                # Insert the masked data into dlp_masked_data table
                rows_to_insert_masked.append(masked_data)
                load_masked = client_bigquery.insert_rows_json(masked_table_id, rows_to_insert_masked)

                rows_to_insert_raw = []  # Clear the list after inserting the rows
                rows_to_insert_masked = []  # Clear the list after inserting the rows
                rows_to_insert_dlp_count=[]
                logging.info("Data processing workflow completed.")

            time.sleep(2)
    
def run():    
    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--dfBucket',
            required=True,
            help= ('Bucket where JARS/JDK is present')
            )
        known_args, pipeline_args = parser.parse_known_args()
        global df_Bucket 
        df_Bucket = known_args.dfBucket
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        pipeline_options = PipelineOptions(pipeline_args)
        pipeline_options.view_as(StandardOptions).streaming = True
        pcoll = beam.Pipeline(options=pipeline_options)
        logging.info("Pipeline Starts")
        dummy= pcoll | 'Initializing..' >> beam.Create(['1'])
        dummy_env = dummy | 'Processing' >>  beam.ParDo(readandwrite())
        p=pcoll.run()
        logging.info('Job Run Successfully!')
        p.wait_until_finish()
    except Exception as e:
        logging.exception('Failed to launch datapipeline')
        logging.exception('Failed to launch datapipeline: %s', str(e))
        raise    
if __name__ == '__main__':
    run()
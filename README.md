# De-Identify-PII-data-in-real-time-using-cloud-DLP-and-Data-quality-checks-using-Soda-Core

Introducing the Audio PII Detection and De-Identification project—a comprehensive solution to identify and protect Personally Identifiable Information (PII) within audio interactions. This system utilizes advanced speech recognition and Cloud DLP to identify PII in audio files, ensuring data privacy. Detected PII is automatically de-identified using Cloud DLP, preserving anonymity. Alerts are sent to BigQuery owners, and ServiceNow tickets are generated for immediate action. Leveraging Soda's data quality tools, we ensure post-processing data integrity. Elevate your data security while maintaining quality with our integrated workflow.

## Toolbox 🧰
<img src="https://miro.medium.com/v2/resize:fit:335/0*ARUQelkPpC1LwNFN" width="200" height="120" alt="Pub Sub"/> &emsp; <img src="https://lh6.googleusercontent.com/1MICxjbrbRPtEnzE54g2shaMRD2RocCIcuSOrqwaqryObCR6IrsXNb3Sd5MjBBwmoLeVcgVu_SE3vw-IbRA24SFhH4IT1xppVuuNGodDtFEykgD0Cw1vB2jITTsOgBNHvWfw27icmMs30SYgWQ" width="200" alt="GCP DTAFLOW" height="70"/>
&emsp; <img src="https://miro.medium.com/max/600/1*HEzofakm1-c4c_Qn4zjmnQ.jpeg" width ="170" height="75" alt="Apache Beam"/>
&emsp;<img src ="https://i.ytimg.com/vi/s6ytxB0YSR0/mqdefault.jpg" width="170" height="70" alt="Secret Manager"/> &emsp;
<img src ="https://th.bing.com/th/id/OIP.k11NKB6vQbDyHstjaXOJygHaCk?pid=ImgDet&rs=1" width="200" height="100" alt="Google Cloud Storage"/> &emsp;
<img src ="https://cxl.com/wp-content/uploads/2019/10/google-bigquery-logo-1.png" width="170" height="100" alt="Google Big Query"/> &emsp;
<img src ="https://miro.medium.com/v2/resize:fit:584/1*q4EVSAndlvgFLyR6ncc4Bg.png" width="170" height="100" alt="Google cloud Functions"/> &emsp;
<img src ="https://miro.medium.com/v2/resize:fit:961/1*tQKERQdZsjUArxXjaHo9PA.png" width="170" height="100" alt="Secret Manager"/> &emsp;
<img src ="https://logos-world.net/wp-content/uploads/2022/02/ServiceNow-Symbol.png" width="100" height="100" alt="ServiceNow"/> &emsp;
<img src ="https://i.pinimg.com/originals/8d/39/f3/8d39f3958e82028615cdedacb496a114.jpg" width="170" height="100" alt="SMTP"/> &emsp;
<img src ="https://www.python.org/static/community_logos/python-logo-master-v3-TM-flattened.png" width="170" height="100" alt="Python"/> &emsp;
<img src ="https://github.com/sandy0298/De-Identify-PII-data-in-real-time-using-cloud-DLP-and-Data-quality-checks-using-Soda-Core/blob/main/screenshots/soda-2.jpg" width="150" height="100" alt="sodacore"/> &emsp;

## Architecture Diagram

<img src ="https://github.com/sandy0298/De-Identify-PII-data-in-real-time-using-cloud-DLP-and-Data-quality-checks-using-Soda-Core/blob/68b7b782e859755bd9d759056543563ca7c6d45e/screenshots/dlp_checkv1.png" width="800" height="500" alt="architecture"/> &emsp;

## Project Workflow

This GitHub project showcases a robust and efficient real-time data processing pipeline designed for audio content, incorporating various Google Cloud Platform (GCP) services and advanced functionalities. The pipeline seamlessly converts audio files into text using the Speech to Text API, evaluates data quality through Soda Core, ensures Personal Identifiable Information (PII) protection using the Data Loss Prevention (DLP) API, and culminates in creating insightful Looker dashboards.

## Key Features:

## Audio-to-Text Conversion:
Audio files are initially stored in Google Cloud Storage (GCS). Upon arrival, a cloud function is triggered, which leverages the Speech to Text API. This enables the transformation of audio content into text format. The resulting text is then published to a Pub/Sub topic.

## Real-time Data Flow and PII Management:
The data flow streaming pipeline begins as subscribers draw data from the Pub/Sub topic. This data is then channeled into the Cloud DLP API for PII detection. In the event PII is identified, the DLP API takes action: de-identification and masking of the sensitive information. Both the processed, sanitized data and the original raw data are loaded into separate BigQuery tables. While sanitized data can be accessed by authorized users, the raw data table, containing PII details, is exclusively available to the BigQuery owner.

## Event-Triggered Notifications:
The pipeline incorporates robust event-driven mechanisms. When PII data is detected, a separate Pub/Sub topic is engaged. This triggers a cloud function, initiating a two-fold process: first, an email notification is dispatched to the BigQuery administrator, alerting them of the incident; second, ServiceNow incidents are autonomously generated for DLP administrators, ensuring swift and informed response.

## Looker Dashboards for Insights:
Transforming data into actionable insights, this project also encompasses the creation of Looker dashboards. These dashboards visually present the sanitized data, providing users with intuitive access to valuable insights and trends derived from the processed information.

## Data Quality and Accuracy Assessment:
To maintain a high standard of data quality and accuracy, the pipeline integrates **Soda Core Data Quality**. This component continually assesses the quality of the data flowing through the pipeline, guaranteeing that the processed information is reliable and dependable.

This dynamic project highlights the potential of real-time data processing, PII management, and data quality assessment within the GCP ecosystem. By harnessing the power of GCP services, such as Speech to Text API, Cloud DLP API, Pub/Sub, BigQuery, and Looker, it offers a comprehensive solution for organizations aiming to process and manage audio data in a secure, efficient, and insightful manner and also leverages the power of Soda Core.









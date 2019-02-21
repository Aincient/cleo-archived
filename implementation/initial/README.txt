Contents of this folder needs to be download from a bucket in the google cloud.
Bucket is at:  gs://ai-data-cleo-aincient-org 

gcloud auth login
gcloud config set project gothic-depth-160720 

cd initial
gsutil cp gs://ai-data-cleo-aincient-org/initial .

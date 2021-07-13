pipeline {
    agent {
        dockerfile {
            filename 'Environment-A22-Processing/infrastructure/Dockerfile'
        }
    }

    environment {
        PROJECT_FOLDER="Environment-A22-Processing"
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION="eu-west-1"
        BUILD_BUNDLE="dataprocessing.zip"
	    AUTHENTICATION_SERVER='https://auth.opendatahub.testingmachine.eu/auth/'
        CLIENT_SECRET= credentials('test-keycloak-lambda-secret')
        ODH_SHARE_ENDPOINT='https://share.opendatahub.testingmachine.eu/'
        RAW_DATA_ENDPOINT='https://mobility.api.opendatahub.testingmachine.eu/v2'
        PROVENANCE_NAME="dataprocessing-a22-environment"
        PROVENANCE_VERSION="0.1.0"
        PROVENANCE_LINEAGE="NOI"
    }

    stages {
        stage('Build') {
            steps {
                sh 'cd ${PROJECT_FOLDER} && pip install --no-cache-dir -r requirements.txt -t ./src'
                sh "cd ${PROJECT_FOLDER}/src && zip -r ../${BUILD_BUNDLE} ."
            }
        }
        stage('Upload') {
            steps {
                sh """aws lambda update-function-configuration --function-name a22DataProcessing \
		        --environment Variables={AUTHENTICATION_SERVER=${AUTHENTICATION_SERVER},CLIENT_SECRET=${CLIENT_SECRET},ODH_SHARE_ENDPOINT=${ODH_SHARE_ENDPOINT},RAW_DATA_ENDPOINT=${RAW_DATA_ENDPOINT},PROVENANCE_NAME=${PROVENANCE_NAME},PROVENANCE_VERSION=${PROVENANCE_VERSION},PROVENANCE_LINEAGE=${PROVENANCE_LINEAGE}} """
                sh 'aws lambda update-function-code --function-name freeParkingLotsElaborations --zip-file fileb://${PROJECT_FOLDER}/${BUILD_BUNDLE}'
            }
        }
    }
}

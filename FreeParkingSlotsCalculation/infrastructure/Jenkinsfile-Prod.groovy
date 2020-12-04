pipeline {
    agent {
        dockerfile {
            filename 'FreeParkingSlotsCalculation/infrastructure/Dockerfile'
        }
    }

    environment {
        PROJECT_FOLDER="FreeParkingSlotsCalculation"
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION="eu-west-1"
        BUILD_BUNDLE="freeParkingSlotsCalculator.zip"
	    AUTHENTICATION_SERVER='https://auth.opendatahub.bz.it/auth/'
        CLIENT_SECRET= credentials('prod-keycloak-lambda-secret')
        ODH_SHARE_ENDPOINT='https://share.opendatahub.bz.it/'
        RAW_DATA_ENDPOINT='https://mobility.api.opendatahub.bz.it/v2'
        PROVENANCE_NAME="FreeParkingSlotsCalculation"
        PROVENANCE_VERSION="0.1.0"
        PROVENANCE_LINEAGE="NOI"
        FUNCTION_NAME="freeParkingLotsElaborations-prod"
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
                sh """aws lambda update-function-configuration --function-name ${FUNCTION_NAME} \
		        --environment Variables={AUTHENTICATION_SERVER=${AUTHENTICATION_SERVER},CLIENT_SECRET=${CLIENT_SECRET},ODH_SHARE_ENDPOINT=${ODH_SHARE_ENDPOINT},RAW_DATA_ENDPOINT=${RAW_DATA_ENDPOINT},PROVENANCE_NAME=${PROVENANCE_NAME},PROVENANCE_VERSION=${PROVENANCE_VERSION},PROVENANCE_LINEAGE=${PROVENANCE_LINEAGE}} """
                sh 'aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb://${PROJECT_FOLDER}/${BUILD_BUNDLE}'
            }
        }
    }
}

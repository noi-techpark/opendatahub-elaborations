pipeline {
    agent {
        dockerfile {
            filename 'FreeParkingSlotsCalculations/infrastructure/Dockerfile'
            additionalBuildArgs '--build-arg JENKINS_USER_ID=`id -u jenkins` --build-arg JENKINS_GROUP_ID=`id -g jenkins`'
        }
    }

    environment {
        PROJECT_FOLDER="FreeParkingSlotsCalculation"
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AUTHENTICATION_SERVER='https://auth.opendatahub.testingmachine.eu/auth/'
        CLIENT_SECRET= credentials('keycloak-datacollectors-secret')
        ODH_SHARE_ENDPOINT='https://share.opendatahub.testingmachine.eu/'
        RAW_DATA_ENDPOINT='https://mobility.api.opendatahub.testingmachine.eu/v2'
        PROVENANCE_NAME="FreeParkingSlotsCalculation"
        PROVENANCE_VERSION="0.1.0"
        PROVENANCE_LINEAGE="noi"
        BUILD_BUNDLE="freeParkingSlotsCalculator.zip"
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
                s3Upload(bucket: 'it.bz.opendatahub.lambda-functions', file: '${PROJECT_FOLDER}/${BUILD_BUNDLE}')
            }
        }
    }
}

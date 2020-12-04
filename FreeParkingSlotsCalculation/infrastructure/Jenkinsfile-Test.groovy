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
                sh 'aws lambda update-function-code --function-name freeParkingLotsElaborations --zip-file fileb://${PROJECT_FOLDER}/${BUILD_BUNDLE}'
            }
        }
    }
}

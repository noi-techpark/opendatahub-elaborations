pipeline {
    agent {
        dockerfile {
            filename 'ShapefileFeatureImporter/docker/Dockerfile'
            additionalBuildArgs '--build-arg JENKINS_USER_ID=`id -u jenkins` --build-arg JENKINS_GROUP_ID=`id -g jenkins`'
        }
    }
    environment{
        DB_HOST=
        DB_USER=
        DB_NAME=
    }
    stages {
        stage('Create geometry table') {
            steps {
                sh '''shp2pgsql ShapefileFeatureImporter/LinkStationsGeometries.shp elaboration.bluetoothlinks_tmp | psql -h "${DB_HOST}" -U"${DB_USER}" "${DB_NAME}"'''
            }
        }
        stage('update geometries') {
            steps {
		        sh '''psql -h "${DB_HOST}" -U"${DB_USER}" -d "${DB_NAME}"-c "set search_path=public,intimev2,elaboration;update edge as e set linegeometry = tmp.geom from ( select s.id,t.geom from elaboration.bluetoothlinks_tmp t join intimev2.station s on t.id=s.id) as tmp where tmp.id=e.edge_data_id;"'''
            }
        }
        stage('Clean'){
		        sh '''psql -h "${DB_HOST}" -U"${DB_USER}" -d "${DB_NAME}"-c "drop table elaboration.bluetoothlinks_tmp;"'''
        }
    }
}

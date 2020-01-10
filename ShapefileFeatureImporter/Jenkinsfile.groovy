pipeline {
    agent {
        dockerfile {
            filename 'ShapefileFeatureImporter/docker/Dockerfile'
            additionalBuildArgs '--build-arg JENKINS_USER_ID=`id -u jenkins` --build-arg JENKINS_GROUP_ID=`id -g jenkins`'
        }
    }
    environment{
        DB_HOST= 'prod-pg-bdp.co90ybcr8iim.eu-west-1.rds.amazonaws.com'
        DB_USER= 'bdp'
        PGPASSWORD= credentials('bdp-core-prod-database-write-password')
        DB_NAME= 'bdp';
    }
    stages {
        stage('Create geometry table') {
            steps {
                sh '''shp2pgsql ShapefileFeatureImporter/links/LinkStationsGeometries.shp elaboration.bluetoothlinks_tmp | psql -h "${DB_HOST}" -U"${DB_USER}" "${DB_NAME}"'''
            }
        }
        stage('update geometries') {
            steps {
		        sh '''psql -h "${DB_HOST}" -U"${DB_USER}" -d "${DB_NAME}" -c "set search_path=public,intimev2,elaboration;update edge as e set linegeometry = tmp.geom from ( select s.id,t.geom from elaboration.bluetoothlinks_tmp t join intimev2.station s on t.id=s.id) as tmp where tmp.id=e.edge_data_id;"'''
            }
        }
        stage('Clean'){
            steps {
		        sh '''psql -h "${DB_HOST}" -U"${DB_USER}" -d "${DB_NAME}"-c "drop table elaboration.bluetoothlinks_tmp;"'''
            }
        }
    }
}

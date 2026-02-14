pipeline {
    agent any
    environment {
        REGISTRY = 'registry.ka8zrt.com:5000'
        TAG = "${env.BUILD_ID}"
    }
    stages {
        stage('Build') {
            steps {
                sh 'docker compose -f docker-compose-prod.yml -p unemployment build'
            }
        }
        /*
        stage('Push') {
            steps {
                sh "docker push registry.home.ka8zrt.com:5000/unemployment-web"
                sh "docker push registry.home.ka8zrt.com:5000/unemployment-nginx"
            }
        }
        stage('Deploy') {
            steps {
                sshagent(credentials: ['jenkins-ssh']) {
                    sh '''
                        scp -p docker-compose-prod.yml root@r720:~/docker-compose/unemployment.yml
                        ssh root@r720 'docker compose -f ~/docker-compose/unemployment.yml up -d --pull always'
                    '''
                }
            }
        }
        */
    }
}

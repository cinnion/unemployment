pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'unemployment-prod-env',
                        variable: 'credvar')
                ]) {
                    sh 'rm -f config/.env.prod'
                    sh 'cp "\$credvar" config/.env.prod'
                    sh 'cat config/.env.prod'
                    sh 'docker compose -f docker-compose-prod.yml build'
                }
            }
        }
        stage('Push') {
            steps {
                sh "docker push registry.home.ka8zrt.com:5000/unemployment-web:latest"
                sh "docker push registry.home.ka8zrt.com:5000/unemployment-nginx:latest"
            }
        }
        stage('Deploy') {
            steps {
                sshagent(credentials: ['jenkins-ssh']) {
                    sh '''
                        ssh root@r720 'docker run -d registry.home.ka8zrt.com:5000/unemployment-web:latest'
                        ssh root@r720 'docker run -d registry.home.ka8zrt.com:5000/unemployment-nginx:latest'
                    '''
                }
            }
        }
    }
}

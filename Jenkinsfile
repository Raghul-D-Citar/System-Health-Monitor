pipeline {
    agent { label 'ubuntu-vm' }

    triggers {
        pollSCM('')  // only triggered by webhook, not polling
    }

    environment {
        APP_DIR = '/opt/system-health-monitor'
        SERVICE = 'system-health'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    cd "${APP_DIR}"
                    . venv/bin/activate
                    pip install --quiet --upgrade pip
                    pip install --quiet -r requirements.txt
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    rsync -av --delete --exclude 'venv' --exclude '.env' \
                        "${WORKSPACE}/" "${APP_DIR}/"
                    sudo systemctl daemon-reload
                '''
            }
        }
    }

    post {
        success {
            sh 'sudo systemctl restart system-health.service'
        }
        failure {
            echo 'Deployment failed – service not restarted.'
        }
    }
}

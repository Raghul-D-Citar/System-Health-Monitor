pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PIP_NO_CACHE_DIR = '1'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend setup') {
            steps {
                sh '''
                    set -eu
                    python3 -m venv .venv-backend
                    ./.venv-backend/bin/pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Backend tests') {
            steps {
                sh '''
                    set -eu
                    ./.venv-backend/bin/python -m pytest tests -v
                '''
            }
        }

        stage('Metrics Agent tests') {
            steps {
                dir('metrics-agent') {
                    sh '''
                        set -eu
                        python3 -m venv .venv-agent
                        ./.venv-agent/bin/pip install -r requirements-dev.txt
                        ./.venv-agent/bin/python -m pytest tests -v
                    '''
                }
            }
        }

        stage('Frontend install') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eu
                        npm ci
                    '''
                }
            }
        }

        stage('Frontend tests') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eu
                        npm test
                    '''
                }
            }
        }

        stage('Frontend production build') {
            steps {
                dir('frontend') {
                    sh '''
                        set -eu
                        npm run build
                    '''
                }
            }
        }
    }
}
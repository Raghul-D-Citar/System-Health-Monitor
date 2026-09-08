pipeline {
    agent any

    parameters {
        string(name: 'DEPLOY_HOST', defaultValue: '', description: 'Target Linux host for deployment (for example, 192.168.1.100).')
        string(name: 'DEPLOY_USER', defaultValue: 'deploy', description: 'SSH user on the target host.')
        string(name: 'DEPLOY_PORT', defaultValue: '22', description: 'SSH port on the target host.')
        string(name: 'DEPLOY_DIR', defaultValue: '/opt/system-health-monitor', description: 'Target deployment directory on the Linux host.')
        string(name: 'SSH_CREDENTIALS_ID', defaultValue: 'shm-deploy-ssh', description: 'Jenkins SSH credential ID for deployment.')
    }

    properties {
        pipelineTriggers([
            githubPush()
        ])
    }

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

        stage('Deploy to target Linux host') {
            when {
                allOf {
                    expression { return params.DEPLOY_HOST?.trim() }
                    expression { return params.DEPLOY_USER?.trim() }
                    expression { return params.DEPLOY_DIR?.trim() }
                    expression { return env.BRANCH_NAME == 'main' || env.GIT_BRANCH == 'origin/main' }
                }
            }
            steps {
                script {
                    sshagent(credentials: [params.SSH_CREDENTIALS_ID]) {
                        sh '''
                            set -eu

                            DEPLOY_HOST="${DEPLOY_HOST}"
                            DEPLOY_USER="${DEPLOY_USER}"
                            DEPLOY_PORT="${DEPLOY_PORT}"
                            DEPLOY_DIR="${DEPLOY_DIR}"

                            # Sync the validated repository to the target host.
                            # Exclude local build artifacts, virtual environments,
                            # dependency caches, and generated TLS material.
                            rsync -az --delete \
                                --exclude '.git/' \
                                --exclude '.venv/' \
                                --exclude '.venv-backend/' \
                                --exclude 'metrics-agent/.venv/' \
                                --exclude 'metrics-agent/.venv-agent/' \
                                --exclude 'frontend/node_modules/' \
                                --exclude '.pytest_cache/' \
                                --exclude '**/__pycache__/' \
                                --exclude 'nginx/certs/*' \
                                -e "ssh -p ${DEPLOY_PORT} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
                                ./ "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_DIR}/"

                            # Prepare the runtime venv if it does not exist, then
                            # install or refresh only the production dependencies.
                            ssh -p "${DEPLOY_PORT}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
                                "${DEPLOY_USER}@${DEPLOY_HOST}" \
                                "set -eu; cd '${DEPLOY_DIR}'; if [ ! -d .venv ]; then python3 -m venv .venv; fi; . .venv/bin/activate; pip install -r requirements.txt"

                            # Install the committed systemd unit and reload systemd so
                            # any service definition changes take effect immediately.
                            ssh -p "${DEPLOY_PORT}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
                                "${DEPLOY_USER}@${DEPLOY_HOST}" \
                                "set -eu; sudo -n install -Dm644 '${DEPLOY_DIR}/deploy/systemd/system-health-monitor.service' /etc/systemd/system/system-health-monitor.service; sudo -n systemctl daemon-reload; sudo -n systemctl enable system-health-monitor.service"

                            # Restart only the monitoring server service and verify its state.
                            ssh -p "${DEPLOY_PORT}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
                                "${DEPLOY_USER}@${DEPLOY_HOST}" \
                                "set -eu; sudo -n systemctl restart system-health-monitor.service; sudo -n systemctl status --no-pager --full system-health-monitor.service"

                            # Wait for the application to become healthy before completing the pipeline.
                            ssh -p "${DEPLOY_PORT}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
                                "${DEPLOY_USER}@${DEPLOY_HOST}" \
                                "set -eu; for attempt in 1 2 3 4 5 6 7 8 9 10; do if curl -fsS http://127.0.0.1:8000/api/health; then exit 0; fi; sleep 2; done; exit 1"
                        '''
                    }
                }
            }
        }
    }
}
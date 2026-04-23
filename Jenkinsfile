pipeline {
    agent any

    environment {
        DOCKERHUB_USER  = "fakhirhassan"
        BACKEND_IMAGE   = "fakhirhassan/devops-3tier-backend"
        FRONTEND_IMAGE  = "fakhirhassan/devops-3tier-frontend"
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        APP_HOST        = "13.49.138.217"
        APP_USER        = "ubuntu"
        DEPLOY_DIR      = "/home/ubuntu/app"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('Build Backend Image') {
            steps {
                echo 'Building backend Docker image...'
                sh 'docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest ./backend'
            }
        }

        stage('Build Frontend Image') {
            steps {
                echo 'Building frontend Docker image...'
                sh 'docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest ./frontend'
            }
        }

        stage('Test Backend') {
            steps {
                echo 'Smoke-testing backend image...'
                sh 'docker run --rm ${BACKEND_IMAGE}:${IMAGE_TAG} python -c "import flask; print(\'flask ok, version:\', flask.__version__)"'
            }
        }

        stage('Test Frontend') {
            steps {
                echo 'Smoke-testing frontend image...'
                sh 'docker run --rm ${FRONTEND_IMAGE}:${IMAGE_TAG} sh -c "test -f /usr/share/nginx/html/index.html && nginx -v"'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing images to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                        docker push ${BACKEND_IMAGE}:latest
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to App EC2') {
            steps {
                echo "Deploying to ${APP_HOST}..."
                sshagent(credentials: ['app-ec2-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${APP_USER}@${APP_HOST} "mkdir -p ${DEPLOY_DIR}"
                        scp -o StrictHostKeyChecking=no docker-compose.yml init.sql ${APP_USER}@${APP_HOST}:${DEPLOY_DIR}/
                        ssh -o StrictHostKeyChecking=no ${APP_USER}@${APP_HOST} "cd ${DEPLOY_DIR} && docker compose pull && docker compose up -d"
                        ssh -o StrictHostKeyChecking=no ${APP_USER}@${APP_HOST} "docker ps"
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Waiting for app to come up, then checking...'
                sh '''
                    sleep 10
                    curl -fsS http://${APP_HOST}/ > /dev/null && echo "Frontend responding on :80"
                    curl -fsS http://${APP_HOST}/api/health && echo ""
                '''
            }
        }
    }

    post {
        success {
            echo "Build #${env.BUILD_NUMBER} succeeded. App is live at http://${APP_HOST}/"
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed. Check the stage logs above."
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}

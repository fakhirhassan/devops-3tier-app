pipeline {
    agent any

    environment {
        BACKEND_IMAGE  = "devops-3tier-backend"
        FRONTEND_IMAGE = "devops-3tier-frontend"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
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
                echo 'Smoke-testing backend image (starts + imports app)...'
                sh '''
                    docker run --rm ${BACKEND_IMAGE}:${IMAGE_TAG} python -c "import flask; print('flask ok, version:', flask.__version__)"
                '''
            }
        }

        stage('Test Frontend') {
            steps {
                echo 'Smoke-testing frontend image (nginx config valid)...'
                sh 'docker run --rm ${FRONTEND_IMAGE}:${IMAGE_TAG} nginx -t'
            }
        }

        stage('List Built Images') {
            steps {
                sh 'docker images | grep -E "${BACKEND_IMAGE}|${FRONTEND_IMAGE}" || true'
            }
        }
    }

    post {
        success {
            echo "Build #${env.BUILD_NUMBER} succeeded."
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed. Check the stage logs above."
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}

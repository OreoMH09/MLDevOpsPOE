pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m venv .venv'
                        sh '.venv/bin/python -m pip install --upgrade pip'
                        sh '.venv/bin/python -m pip install -r requirements.txt'
                    } else {
                        bat 'py -3 -m venv .venv'
                        bat '.venv\\Scripts\\python -m pip install --upgrade pip'
                        bat '.venv\\Scripts\\python -m pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Pytest') {
            steps {
                script {
                    if (isUnix()) {
                        sh '.venv/bin/python -m pytest -v'
                    } else {
                        bat '.venv\\Scripts\\python -m pytest -v'
                    }
                }
            }
        }

        stage('Generate Evidently Report') {
            steps {
                script {
                    if (isUnix()) {
                        sh '.venv/bin/python monitoring/generate_report.py'
                    } else {
                        bat '.venv\\Scripts\\python monitoring\\generate_report.py'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.html,reports/*.json', allowEmptyArchive: true
        }
        success {
            echo 'Arithmetic API pipeline completed: dependencies, pytest and Evidently report.'
        }
        failure {
            echo 'Pipeline failed. Check the stage log and fix the reported error.'
        }
    }
}

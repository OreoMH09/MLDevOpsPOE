pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        PYTHON_HOME = 'C:\\Users\\Sanika Naik\\AppData\\Local\\Programs\\Python\\Python311'
        PATH = "${env.PYTHON_HOME};${env.PYTHON_HOME}\\Scripts;${env.PATH}"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m venv venv'
                        sh 'venv/bin/python -m pip install --upgrade pip'
                        sh 'venv/bin/python -m pip install -r requirements.txt'
                    } else {
                        bat '''
                            python -m venv venv
                            venv\\Scripts\\python -m pip install --upgrade pip
                            venv\\Scripts\\python -m pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Run Pytest') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'export PYTHONPATH=$PWD && venv/bin/python -m pytest tests/ -v'
                    } else {
                        bat '''
                            set PYTHONPATH=%CD%
                            venv\\Scripts\\python -m pytest tests/ -v
                        '''
                    }
                }
            }
        }

        stage('Generate Evidently Report') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'export PYTHONPATH=$PWD && venv/bin/python monitoring/generate_report.py'
                    } else {
                        bat '''
                            set PYTHONPATH=%CD%
                            venv\\Scripts\\python monitoring\\generate_report.py
                        '''
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

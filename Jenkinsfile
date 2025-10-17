pipeline {
  agent any

  environment {      
    ENV = "prod"  // Change this as needed: prod/dev/staging
    TF_BUCKET = "terraform-state-bucket-eks-cluster"  
    TF_KEY = "${ENV}/terraform.tfstate"  
    SECRET_NAME = 'aws-cred'
    AWS_REGION = 'us-east-1'
  }

  stages {
    stage('Checkout') {
      steps {
        script {
            // Full clone with tags
            checkout([$class: 'GitSCM',
                branches: [[name: "*/${BRANCH_NAME}"]],
                doGenerateSubmoduleConfigurations: false,
                extensions: [[$class: 'CloneOption', depth: 0, noTags: false, reference: '', shallow: false]],
                userRemoteConfigs: [[url: 'https://github.com/grevyrincon/python-app.git']]]
            )
            env.IMAGE_TAG = sh(script: "git describe --tags --always", returnStdout: true).trim()
            echo "Using IMAGE_TAG: ${env.IMAGE_TAG}"
        }
      }
    }
    stage('Load Environment from Terraform State') {
      steps {
        withAWS(region: "${AWS_REGION}", credentials: "${SECRET_NAME}") {
          script {
              // Download the tfstate file
              sh "aws s3 cp s3://${TF_BUCKET}/${TF_KEY} ./terraform.tfstate"

              // Read the state file JSON
              def tfStateText = readFile('terraform.tfstate')
              def tfState = readJSON text: tfStateText
              def outputs = tfState.outputs

              env.ECR_REGISTRY = outputs.ecr_repository_url.value
              env.AWS_REGION = outputs.aws_region.value

          }
        }
      }
    }
    stage('Login to ECR') {
      steps {
        withAWS(region: "${AWS_REGION}", credentials: 'aws-cred') {
          sh '''
            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
          '''
        }
      }
    }
    stage('Build Docker image') {
      steps {
        sh "docker build -t ${ECR_REGISTRY}:${IMAGE_TAG} ./app"
      }
    }

    stage('Push to ECR') {
      steps {
        sh "docker push ${ECR_REGISTRY}:${IMAGE_TAG}"
      }
    }
  }

  post {
    success {
      echo "Deploy successful"
    }
    failure {
      echo "Pipeline failed"
    }
  }
}

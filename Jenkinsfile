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
    stage('Load Environment from Terraform State') {
      steps {
        withAWS(region: "${AWS_REGION}", credentials: "${SECRET_NAME}") {
          script {
              // Download the tfstate file
              sh "aws s3 cp s3://${TF_BUCKET}/${TF_KEY} ./terraform.tfstate"

              // Read the state file JSON
              def tfStateText = readFile('terraform.tfstate')
              def tfState = readJSON text: tfStateText

              // Extract outputs
              def outputs = tfState.outputs

              env.ECR_REGISTRY = outputs.ecr_repository_url.value
              env.AWS_REGION = outputs.aws_region.value

              def tag = sh(script: "git fetch --tags && git describe --tags --abbrev=0", returnStdout: true).trim()
              env.IMAGE_TAG = tag
              echo "Docker image will be tagged with: ${env.IMAGE_TAG}" 
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

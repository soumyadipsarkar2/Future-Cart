#!/bin/bash

# AWS Deployment Script for Customer Purchase Prediction
# This script provides multiple AWS deployment options

set -e

echo "🚀 AWS Deployment Script for Customer Purchase Prediction"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: $0 [OPTION]${NC}"
    echo ""
    echo "Options:"
    echo "  elastic-beanstalk  - Deploy to AWS Elastic Beanstalk (Recommended)"
    echo "  ecs               - Deploy to AWS ECS/Fargate"
    echo "  ec2               - Deploy to AWS EC2"
    echo "  setup             - Setup AWS credentials and configuration"
    echo "  status            - Check deployment status"
    echo "  cleanup           - Clean up AWS resources"
    echo ""
    echo "Examples:"
    echo "  $0 setup              # Setup AWS configuration"
    echo "  $0 elastic-beanstalk  # Deploy to Elastic Beanstalk"
    echo "  $0 ecs               # Deploy to ECS"
}

# Function to check AWS credentials
check_aws_credentials() {
    echo -e "${YELLOW}Checking AWS credentials...${NC}"
    if ! aws sts get-caller-identity &>/dev/null; then
        echo -e "${RED}❌ AWS credentials not configured${NC}"
        echo "Please run: $0 setup"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS credentials configured${NC}"
    
    # Get AWS account ID and region
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    export AWS_REGION=$(aws configure get region || echo "us-east-1")
    echo "Account ID: $AWS_ACCOUNT_ID"
    echo "Region: $AWS_REGION"
}

# Function to setup AWS
setup_aws() {
    echo -e "${BLUE}🔧 Setting up AWS configuration...${NC}"
    
    echo "Please enter your AWS credentials:"
    echo "1. Access Key ID"
    echo "2. Secret Access Key"
    echo "3. Default region (e.g., us-east-1, us-west-2, eu-west-1)"
    echo ""
    
    aws configure
    
    echo -e "${GREEN}✅ AWS configuration complete!${NC}"
    echo "You can now deploy your application."
}

# Function to deploy to Elastic Beanstalk
deploy_elastic_beanstalk() {
    echo -e "${BLUE}🌱 Deploying to AWS Elastic Beanstalk...${NC}"
    
    check_aws_credentials
    
    # Create application directory for Elastic Beanstalk
    mkdir -p .ebextensions
    mkdir -p .elasticbeanstalk
    
    # Create Elastic Beanstalk configuration
    cat > .ebextensions/01_environment.config << EOF
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current
  aws:elasticbeanstalk:container:python:
    WSGIPath: src.api.main:app
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: src/static
EOF

    # Create Procfile for Elastic Beanstalk
    cat > Procfile << EOF
web: uvicorn src.api.main:app --host 0.0.0.0 --port \$PORT
EOF

    # Create requirements.txt for Elastic Beanstalk (if not exists)
    if [ ! -f requirements.txt ]; then
        echo "Creating requirements.txt..."
        cat > requirements.txt << EOF
fastapi>=0.104.1
uvicorn>=0.24.0
streamlit>=1.28.1
pandas>=2.2.0
numpy>=1.26.0
scikit-learn>=1.4.0
xgboost>=2.0.3
plotly>=5.17.0
shap>=0.44.0
pydantic>=2.5.0
python-dotenv>=1.0.0
requests>=2.31.0
EOF
    fi

    # Initialize Elastic Beanstalk application
    echo "Initializing Elastic Beanstalk application..."
    eb init customer-purchase-prediction \
        --platform python-3.9 \
        --region $AWS_REGION \
        --source codecommit/customer-purchase-prediction || true

    # Create environment
    echo "Creating Elastic Beanstalk environment..."
    eb create customer-prediction-env \
        --instance-type t3.small \
        --min-instances 1 \
        --max-instances 3 \
        --elb-type application \
        --envvars PYTHONPATH=/var/app/current

    # Deploy
    echo "Deploying application..."
    eb deploy

    # Get the URL
    APP_URL=$(eb status | grep CNAME | awk '{print $2}')
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo -e "${GREEN}🌐 Your public URL: http://$APP_URL${NC}"
    echo -e "${GREEN}📚 API Documentation: http://$APP_URL/docs${NC}"
    echo -e "${GREEN}❤️ Health Check: http://$APP_URL/health${NC}"
}

# Function to deploy to ECS
deploy_ecs() {
    echo -e "${BLUE}🐳 Deploying to AWS ECS/Fargate...${NC}"
    
    check_aws_credentials
    
    # Create ECR repository
    echo "Creating ECR repository..."
    aws ecr create-repository --repository-name customer-purchase-prediction --region $AWS_REGION 2>/dev/null || true
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Tag and push image
    echo "Building and pushing Docker image..."
    docker build -t customer-purchase-prediction .
    docker tag customer-purchase-prediction:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/customer-purchase-prediction:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/customer-purchase-prediction:latest
    
    # Create ECS cluster
    echo "Creating ECS cluster..."
    aws ecs create-cluster --cluster-name customer-prediction-cluster --region $AWS_REGION 2>/dev/null || true
    
    # Create task definition
    cat > task-definition.json << EOF
{
    "family": "customer-purchase-prediction",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "customer-prediction-app",
            "image": "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/customer-purchase-prediction:latest",
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/customer-purchase-prediction",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF

    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION
    
    # Create Application Load Balancer
    echo "Creating Application Load Balancer..."
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION)
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0:2].SubnetId' --output text --region $AWS_REGION)
    
    # Create ALB
    ALB_ARN=$(aws elbv2 create-load-balancer \
        --name customer-prediction-alb \
        --subnets $SUBNET_IDS \
        --security-groups sg-0123456789abcdef0 \
        --region $AWS_REGION \
        --query 'LoadBalancers[0].LoadBalancerArn' \
        --output text 2>/dev/null || echo "ALB already exists")
    
    # Create ECS service
    echo "Creating ECS service..."
    aws ecs create-service \
        --cluster customer-prediction-cluster \
        --service-name customer-prediction-service \
        --task-definition customer-purchase-prediction \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[sg-0123456789abcdef0],assignPublicIp=ENABLED}" \
        --region $AWS_REGION 2>/dev/null || true
    
    echo -e "${GREEN}✅ ECS deployment initiated!${NC}"
    echo "Check AWS Console for the load balancer URL."
}

# Function to deploy to EC2
deploy_ec2() {
    echo -e "${BLUE}🖥️ Deploying to AWS EC2...${NC}"
    
    check_aws_credentials
    
    # Create EC2 instance
    echo "Creating EC2 instance..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id ami-0c02fb55956c7d316 \
        --count 1 \
        --instance-type t3.small \
        --key-name your-key-pair \
        --security-group-ids sg-0123456789abcdef0 \
        --user-data file://ec2-user-data.sh \
        --region $AWS_REGION \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo "Instance ID: $INSTANCE_ID"
    echo "Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $AWS_REGION
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --region $AWS_REGION \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    echo -e "${GREEN}✅ EC2 deployment complete!${NC}"
    echo -e "${GREEN}🌐 Your public URL: http://$PUBLIC_IP:8000${NC}"
    echo -e "${GREEN}📚 API Documentation: http://$PUBLIC_IP:8000/docs${NC}"
}

# Function to check deployment status
check_status() {
    echo -e "${BLUE}📊 Checking deployment status...${NC}"
    
    # Check Elastic Beanstalk
    if command -v eb &> /dev/null; then
        echo "Elastic Beanstalk Status:"
        eb status 2>/dev/null || echo "No EB environment found"
    fi
    
    # Check ECS
    echo "ECS Status:"
    aws ecs list-services --cluster customer-prediction-cluster --region $AWS_REGION 2>/dev/null || echo "No ECS cluster found"
    
    # Check EC2
    echo "EC2 Status:"
    aws ec2 describe-instances --filters "Name=tag:Name,Values=customer-prediction" --region $AWS_REGION --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name,IP:PublicIpAddress}' --output table 2>/dev/null || echo "No EC2 instances found"
}

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up AWS resources...${NC}"
    
    # Cleanup Elastic Beanstalk
    if command -v eb &> /dev/null; then
        eb terminate customer-prediction-env --force 2>/dev/null || true
    fi
    
    # Cleanup ECS
    aws ecs delete-service --cluster customer-prediction-cluster --service customer-prediction-service --force --region $AWS_REGION 2>/dev/null || true
    aws ecs delete-cluster --cluster customer-prediction-cluster --region $AWS_REGION 2>/dev/null || true
    
    # Cleanup ECR
    aws ecr delete-repository --repository-name customer-purchase-prediction --force --region $AWS_REGION 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

# Main script logic
case "${1:-}" in
    "setup")
        setup_aws
        ;;
    "elastic-beanstalk")
        deploy_elastic_beanstalk
        ;;
    "ecs")
        deploy_ecs
        ;;
    "ec2")
        deploy_ec2
        ;;
    "status")
        check_status
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

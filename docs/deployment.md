# Deployment

The application is deployed to AWS Elastic Container Service (ECS) using settings provided in the
[Task Definition template][ecs-task-definition].

[GitHub Actions][github-actions] performs the following steps on pushes to `main`:

1. Login to Elastic Container Registry (ECR) using AWS credentials stored in repository secrets
1. Build and push a new image using the repository's `Dockerfile`, saving the image tag as output
1. Using the Task Definition template, fill in the newly built image tag
1. Push the new Task Definition to ECS, triggering a re-deploy

## Configuration data

The production configuration data (a version of `localhost/data/client.json`) is stored in an AWS S3 bucket.

The [Task Definition template][ecs-task-definition] includes a container definition that uses the AWS CLI
Docker image to pull this config file from S3 during the bootup sequence, storing it in a volume that is mounted into the main
application container.

To replicate the production configuration locally, fill in the appropriate values for AWS configuration in the `.env` file and
then run:

```console
docker-compose run s3config
```

[ecs-task-definition]: https://github.com/cal-itp/benefits/blob/dev/.aws/ecs-task.json
[github-actions]: https://github.com/cal-itp/benefits/tree/dev/.github/workflows

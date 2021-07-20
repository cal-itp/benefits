# Configuration data

The configuration data (based on [`localhost/.env.sample`][.env.sample] and [`localhost/data/client.json`][client.json]) is
stored in AWS S3 buckets for each deploy environment.

## Runtime AWS configuration

The [Task Definition template][ecs-task-definition] includes a container definition that uses the [AWS CLI][aws-cli]
Docker image to pull configuration data from S3 during the bootup sequence.

The file is stored in a volume that is also mounted into the main application container.

The main application container definition uses [`dependsOn`][depends-on] to enforce that the AWS CLI container be in the
`SUCCESS` state in order for the application container to start.

Both containers use the [`environmentFiles`][env-files] setting to load an `.env` file from their deploy environment's S3
bucket.

## Local AWS configuration

To replicate the AWS configuration locally, fill in the appropriate values in your local `.env` file:

* for the AWS connection:

    ```console
    AWS_DEFAULT_REGION=us-west-2
    AWS_ACCESS_KEY_ID=access-key-id
    AWS_SECRET_ACCESS_KEY=secret-access-key
    AWS_BUCKET=bucket-name
    CONFIG_FILE=file.json
    ```

* and to ensure Django looks in the `configvolume` (defined in [docker-compose.yml][docker-compose.yml]):

    ```console
    DJANGO_INIT_PATH=config/file.json
    ```

and then pull the files down to your local computer:

```bash
docker-compose run s3pull
```

## Updating the AWS configuration

A Docker Compose service can also be used to push updates to the configuration data into S3 for the given deploy environment:

```bash
docker-compose run s3push
```


[.env.sample]: https://github.com/cal-itp/benefits/tree/dev/localhost/.env.sample
[aws-cli]: https://aws.amazon.com/cli/
[client.json]: https://github.com/cal-itp/benefits/tree/dev/localhost/data/client.json
[depends-on]: https://docs.aws.amazon.com/AmazonECS/latest/userguide/task_definition_parameters.html#container_definition_dependson
[docker-compose.yml]: https://github.com/cal-itp/benefits/tree/dev/localhost/docker-compose.yml
[ecs-task-definition]: https://github.com/cal-itp/benefits/blob/dev/.aws/ecs-task.json
[env-files]: https://docs.aws.amazon.com/AmazonECS/latest/userguide/taskdef-envfiles.html

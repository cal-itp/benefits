# Overview

The application is deployed to [AWS Elastic Container Service (ECS)][ecs-welcome] using a
[Task Definition][ecs-task-definition] generated from the template file at [`.aws/ecs-task.json`][ecs-task-definition-template].

The application is deployed into three separate AWS environments for `dev`, `test`, and `prod`.
[GitHub Environments][gh-environments] exist corresponding to each AWS deployment environment, with secrets and protection
rules specific to each GitHub Environment.

A [GitHub Action][gh-actions] per Environment is responsible for deploying that Environment's branch to the corresponding
AWS location.

## Configuration

Configuration data (based on [`.devcontainer/.env.sample`][.env.sample] and [`fixtures/`][fixtures]) is stored
in AWS S3 buckets for each deployment environment.

### ECS runtime

The ECS Task Definition includes a `containerDefinition`, using the [AWS CLI][aws-cli] Docker image, to pull the fixture data
from the corresponding S3 bucket during service (re)start. This configuration is copied into a volume that is also mounted
into the main application container.

The main application `containerDefinition` uses [`dependsOn`][depends-on] to ensure that the AWS CLI container task has
completed successfully, before starting itself.

Both containers use the [`environmentFiles`][env-files] setting to load an `.env` file from their deploy environment's S3
bucket.

### Local AWS

!!! warning

    The following command will decrypt and download the `benefits` configuration from S3 into the `.aws/config` directory on
    your local computer. Be sure this is what you want to do.

To copy the AWS configuration locally, fill in the appropriate values in your local `.env` file:

- for the AWS connection:

  ```console
  AWS_DEFAULT_REGION=us-west-2
  AWS_ACCESS_KEY_ID=access-key-id
  AWS_SECRET_ACCESS_KEY=secret-access-key
  AWS_BUCKET=bucket-name
  ```

- and to ensure Django uses the downloaded configuration:

  ```console
  DJANGO_INIT_PATH=config/<file>.json
  ```

and then pull the files down to your local computer:

```bash
docker compose run s3pull
```

### Update AWS

!!! warning

    The following command will send the **entire contents** of the `.aws/config` directory from your local computer into the
    `benefits` S3 bucket for the configured environment. Be sure this is what you want to do.

A Docker Compose service can also be used to push updates to the configuration data into S3 for the given deploy environment:

Ensure you have content (e.g. an `.env` or `config.json` file) inside `.aws/config` in your local repository and then run:

```bash
docker compose run s3push
```

[.env.sample]: https://github.com/cal-itp/benefits/tree/dev/.devcontainer/.env.sample
[aws-cli]: https://aws.amazon.com/cli/
[depends-on]: https://docs.aws.amazon.com/AmazonECS/latest/userguide/task_definition_parameters.html#container_definition_dependson
[ecs-task-definition]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html
[ecs-task-definition-template]: https://github.com/cal-itp/benefits/blob/dev/.aws/ecs-task.json
[ecs-welcome]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
[env-files]: https://docs.aws.amazon.com/AmazonECS/latest/userguide/taskdef-envfiles.html
[fixtures]: https://github.com/cal-itp/benefits/tree/dev/fixtures/
[gh-actions]: https://docs.github.com/en/actions
[gh-environments]: https://docs.github.com/en/actions/reference/environments

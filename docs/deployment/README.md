# Deployment

The application is deployed to AWS Elastic Container Service (ECS) using a [Task Definition template][ecs-task-definition].

The application is deployed into three separate AWS environments for dev, test, and production.
[GitHub Environments](https://docs.github.com/en/actions/reference/environments) exist corresponding to each AWS deployment
environment, with secrets and protection rules specific to each GitHub Environment.

A [GitHub Action][github-actions] per Environment is responsible for deploying that Environment's branch to the corresponding
AWS location.

Configuration data (based on [`localhost/.env.sample`][.env.sample] and [`localhost/data/client.json`][client.json]) is stored
in AWS S3 buckets for each deployment environment.


[.env.sample]: https://github.com/cal-itp/benefits/blob/dev/localhost/.env.sample
[client.json]: https://github.com/cal-itp/benefits/blob/dev/localhost/data/client.json
[ecs-task-definition]: https://github.com/cal-itp/benefits/blob/dev/.aws/ecs-task.json
[github-actions]: https://github.com/cal-itp/benefits/tree/dev/.github/workflows

# Workflows

There are three different GitHub Actions deployment workflows, one for each environment:

* [`.github/workflows/deploy-dev.yml`][deploy-dev]
* [`.github/workflows/deploy-test.yml`][deploy-test]
* [`.github/workflows/deploy-prod.yml`][deploy-prod]

!!! info

    The entire process from GitHub commit to full redeploy of the application can take from around 5 minutes to 10 minutes
    or more depending on the deploy environment. Have patience!

## Deployment steps

Each of the three workflows are [triggered][gh-actions-trigger] with a `push` to the corresponding branch. Each workflow also
responds to the `workflow_dispatch` event to allow manually triggering via the GitHub Actions UI.

When a deployment workflow runs, the following steps are taken:

### 1. Checkout code

From the tip of the corresponding branch (e.g. `dev`)

### 2. Authenticate to AWS

Using secrets defined in the corresponding GitHub environment (e.g. `dev`)

### 3. Build and push image to ECR

Build the root [`Dockerfile`][Dockerfile], tagging with the SHA from the checked-out commit.

Push this main application image/tag into an [ECR][ecr] corresponding to the deploy environment in AWS.

Using the same ECR information, the (static) path to the configuration image is also output for use later in the workflow.

### 4. Generate ECS Task Definition

The [`.aws/ecs-task.json`][ecs-task-template] file serves as a template from which the corresponding ECS Task Definition is
generated, with build and environment-specific information filled in.

Values wrapped in angle brackets, such as `<aws_account>` and `<aws_bucket>`, are replaced in the template by their
corresponding secret from the GitHub environment.

The image names/tags generated from the ECR push step are inserted into the container definitions.

### 5. Deploy Task Definition to ECS

The final step is deploying the newly created Task Definition to the Amazon ECS cluster.

Once deployed, ECS does the following:

1. Drains existing connections
2. Increments service version number
3. Restarts the service

The GitHub Actions workflows wait for the service to restart and to reach a steady state before marking successful completion.

## How do the workflows differ?

The only differences between the three workflow files are the **name**:

```diff
-name: Deploy to Amazon ECS (dev)
+name: Deploy to Amazon ECS (test)
```

the **branch** filter:

```diff
 on:
   push:
     branches:
-      - dev
+      - test
```

and the **environment** (and related *concurrency* setting) to load with each run:

```diff
 jobs:
   deploy:
     runs-on: ubuntu-latest
-    environment: dev
-    concurrency: dev
+    environment: test
+    concurrency: test
```

If in the future GitHub allows for templated workflows or branch-matrix support, these definitions may be collapsed into a
single file.


[deploy-dev]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy-dev.yml
[deploy-test]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy-test.yml
[deploy-prod]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy-prod.yml
[dockerfile]: https://github.com/cal-itp/benefits/blob/dev/Dockerfile
[ecr]: https://aws.amazon.com/ecr/
[ecs-task-template]: https://github.com/cal-itp/benefits/blob/dev/.aws/ecs-task.json
[gh-actions-trigger]: https://docs.github.com/en/actions/reference/events-that-trigger-workflows

const fs = require("fs");
const path = require("path");

module.exports = async ({
  github,
  context,
  core,
  parentNodeId,
  templateName,
  title,
}) => {
  const { long_name, short_name, transit_processor, website } =
    context.payload.inputs;

  // read and process body template
  const templatePath = path.join(
    process.env.GITHUB_WORKSPACE,
    `.github/workflows/agency-onboarding/${templateName}`
  );

  let body = fs.readFileSync(templatePath, "utf8");

  // replace all placeholders
  body = body
    .replace(/{{LONG_NAME}}/g, long_name)
    .replace(/{{SHORT_NAME}}/g, short_name)
    .replace(/{{TRANSIT_PROCESSOR}}/g, transit_processor)
    .replace(/{{WEBSITE}}/g, website || "N/A");

  // create the child issue
  const child = await github.rest.issues.create({
    owner: context.repo.owner,
    repo: context.repo.repo,
    title: title,
    labels: ["agency-onboarding"],
    body: body,
  });
  const childNodeId = child.data.node_id;

  // link sub-issue using GraphQL
  try {
    await github.graphql(
      `mutation AddSubIssue($issueId: ID!, $subIssueId: ID!) {
        addSubIssue(input: { issueId: $issueId, subIssueId: $subIssueId }) {
          issue {
            id
          }
        }
      }`,
      {
        issueId: parentNodeId,
        subIssueId: childNodeId,
      }
    );
  } catch (error) {
    core.warning(`Failed to link sub-issue via GraphQL: ${error.message}`);
  }

  return child.data.number;
};

const fs = await import("fs");
const path = await import("path");

export const createChild = async ({
  github,
  context,
  core,
  parentNodeId,
  templateName,
  title,
}) => {
  const { long_name, short_name, transit_processor, website, launch_date } =
    context.payload.inputs;

  // read and process body template
  const templatePath = path.join(
    process.env.GITHUB_WORKSPACE,
    `.github/workflows/agency-onboarding/${templateName}`
  );

  // replace all placeholders
  const body = fs
    .readFileSync(templatePath, "utf8")
    .replace(/{{LONG_NAME}}/g, long_name)
    .replace(/{{SHORT_NAME}}/g, short_name)
    .replace(/{{TRANSIT_PROCESSOR}}/g, transit_processor)
    .replace(/{{WEBSITE}}/g, website || "N/A")
    .replace(/{{LAUNCH_DATE}}/g, launch_date || "TBD");

  // create the child issue
  const child = await github.rest.issues.create({
    owner: context.repo.owner,
    repo: context.repo.repo,
    title: `${short_name}: ${title}`,
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

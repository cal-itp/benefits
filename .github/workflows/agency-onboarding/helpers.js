import { readFileSync } from "fs";

const createIssue = async ({
  context,
  github,
  labels,
  templateName,
  title,
}) => {
  const templatePath = `.github/workflows/agency-onboarding/${templateName}`;
  const { long_name, short_name, transit_processor, website, launch_date } =
    context.payload.inputs;

  // read body from template, fill in placeholders
  const body = readFileSync(templatePath, "utf8")
    .replace(/{{LONG_NAME}}/g, long_name)
    .replace(/{{SHORT_NAME}}/g, short_name)
    .replace(/{{TRANSIT_PROCESSOR}}/g, transit_processor)
    .replace(/{{WEBSITE}}/g, website || "N/A")
    .replace(/{{LAUNCH_DATE}}/g, launch_date || "TBD");

  return await github.rest.issues.create({
    owner: context.repo.owner,
    repo: context.repo.repo,
    title,
    labels,
    body,
  });
};

export const createEpicIssue = async ({ github, context, core }) => {
  const { long_name, initiative_issue } = context.payload.inputs;

  const epicIssue = await createIssue({
    context,
    github,
    labels: ["epic", "agency-onboarding"],
    templateName: "parent.md",
    title: `Agency onboarding: ${long_name}`,
  });

  if (initiative_issue) {
    const initiativeIssue = await github.rest.issues.get({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: initiative_issue,
    });
    await linkSubIssue({
      github,
      core,
      parentNodeId: initiativeIssue.data.node_id,
      childNodeId: epicIssue.data.node_id,
    });
  }

  return epicIssue;
};

export const createSubIssue = async ({
  github,
  context,
  core,
  parentNodeId,
  templateName,
  title,
}) => {
  const { short_name } = context.payload.inputs;

  // create the child issue
  const child = await createIssue({
    context,
    github,
    labels: ["agency-onboarding"],
    templateName,
    title: `${short_name}: ${title}`,
  });

  const childNodeId = child.data.node_id;
  await linkSubIssue({ github, core, parentNodeId, childNodeId });

  return child.data.number;
};

export const linkSubIssue = async ({
  github,
  core,
  parentNodeId,
  childNodeId,
}) => {
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
      },
    );
  } catch (error) {
    core.warning(`Failed to link sub-issue via GraphQL: ${error.message}`);
  }
};

// Helper functions to convert "Month Year" to "MM/YYYY", or return "Planned"

function monthFromString(month) {
  // March > '3'
  // march > '3'
  // mar > '3'
  return String(new Date(Date.parse(month + " 1, 2026")).getMonth() + 1);
}

function convertToMMYYYY(dateStr) {
  if (!dateStr || !dateStr.trim()) {
    return "Planned";
  }

  const parts = dateStr.trim().split(/\s+/);
  if (parts.length >= 2) {
    const month = monthFromString(parts[0]);
    const year = parts.slice(1).join("");
    if (month && year && /^\d{4}$/.test(year)) {
      return `${month}/${year} (target)`;
    }
  }

  // If not in expected format, return as-is (assume it's already MM/YYYY)
  return dateStr.trim();
}

export const updateAdoptionTable = async ({ github, context, parentIssue }) => {
  const { long_name, launch_date, short_name } = context.payload.inputs;

  const launchDateStr = convertToMMYYYY(launch_date);

  // Read the current docs/index.md file
  const filePath = "docs/index.md";
  let content = readFileSync(filePath, "utf8");

  // Create the new row with proper padding
  const namePadding = " ".repeat(Math.max(0, 47 - long_name.length));
  const datePadding = " ".repeat(Math.max(0, 17 - launchDateStr.length));
  const newRow = `| **${long_name}**${namePadding} | ${launchDateStr}${datePadding} | \\*           | \\*                   | \\*            | \\*          | \\*         |`;

  // Find the adoption table section
  const lines = content.split("\n");
  let adoptionIdx = -1;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes("Adoption by transit providers")) {
      adoptionIdx = i;
      break;
    }
  }

  // Find the end of the table
  let tableEndIdx = -1;
  if (adoptionIdx !== -1) {
    for (let i = adoptionIdx + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith("|")) {
        tableEndIdx = i;
      } else if (tableEndIdx !== -1 && !line.startsWith("|")) {
        // We've exited the table
        break;
      }
    }
  }

  // Insert the new row at the end of the table
  if (tableEndIdx !== -1) {
    lines.splice(tableEndIdx + 1, 0, newRow);
    content = lines.join("\n");
  }

  // Create a new branch name
  const branchName = `docs/update-adoption-table-${short_name.toLowerCase()}`;

  // Get the main branch reference
  const mainRef = await github.rest.git.getRef({
    owner: context.repo.owner,
    repo: context.repo.repo,
    ref: "heads/main",
  });

  const baseSha = mainRef.data.object.sha;

  // Create a new branch
  await github.rest.git.createRef({
    owner: context.repo.owner,
    repo: context.repo.repo,
    ref: `refs/heads/${branchName}`,
    sha: baseSha,
  });

  // Get the current file content
  const currentFile = await github.rest.repos.getContent({
    owner: context.repo.owner,
    repo: context.repo.repo,
    path: filePath,
    ref: branchName,
  });

  // Update the file with the new row
  await github.rest.repos.createOrUpdateFileContents({
    owner: context.repo.owner,
    repo: context.repo.repo,
    path: filePath,
    message: `docs(onboarding): add ${long_name} to adoption table`,
    content: Buffer.from(content).toString("base64"),
    sha: currentFile.data.sha,
    branch: branchName,
  });

  // Create a Draft PR
  const prResponse = await github.rest.pulls.create({
    owner: context.repo.owner,
    repo: context.repo.repo,
    title: `Docs: Add ${long_name} to adoption table`,
    head: branchName,
    base: "main",
    body: `Adds **${long_name}** to the adoption table in the docs.\n\nPart of onboarding epic #${parentIssue}.`,
    draft: true,
  });

  return prResponse.data;
};

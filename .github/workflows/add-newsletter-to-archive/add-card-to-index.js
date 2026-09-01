import { readFileSync, writeFileSync } from "fs";

export const addCardToIndex = ({ core }) => {
  const { NEWSLETTER_NICENAME, NEWSLETTER_SLUG } = process.env;

  // Read the current index file
  const filePath = "docs/reference/newsletter-archive/index.md";
  let content = readFileSync(filePath, "utf8");

  // Create the new card lines
  const newCard = `
    -   ### :material-email-newsletter: ${NEWSLETTER_NICENAME}

          *Subtitle TKTKTK*

          ---

          Summary TKTKTK

        [Read full newsletter →](${NEWSLETTER_SLUG}/)`;

  // Find the current year's section
  const lines = content.split("\n");
  let currentYearIdx = -1;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(".insertion-point")) {
      currentYearIdx = i;
      break;
    }
  }

  // Insert the new card at the top of the current year section
  if (currentYearIdx !== -1) {
    lines.splice(currentYearIdx + 1, 0, newCard);
    content = lines.join("\n");
  } else {
    core.error("Newsletter index insertion point not found.");
    core.setFailed();
  }

  // Update the file
  try {
    writeFileSync(filePath, content);
  } catch (err) {
    core.error("Error updating newsletter index:", err);
    core.setFailed();
  }
};

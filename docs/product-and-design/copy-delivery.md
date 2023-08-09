# Copy delivery process

The [`locale`](https://github.com/cal-itp/benefits/tree/dev/benefits/locale) folder in this repository contain the `django.po` message files for English and Spanish translation strings for the Benefits application.

Translation strings include all application copy, including:

- All application copy
- Image and illustration alt tags
- Page titles used in the browser tab
- In-line link URLs
- Error messages (like [no script](https://github.com/cal-itp/benefits/blob/dev/benefits/core/templates/core/includes/noscript.html), [no cookies](https://github.com/cal-itp/benefits/blob/dev/benefits/core/templates/core/includes/nocookies.html) warnings)

## Cal-ITP Benefits Application Copy (Configurable Strings)

The human-readable version of the English and Spanish translation strings for the application are delivered to Design and Engineering by Product, and live at this link: [Cal-ITP Benefits Application Copy (Configurable Strings)](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit#gid=0).

By tabs:

- `EN-USA` tab contains all copy for English, which each row representing a page. This copy uses a sample agency, called California State Transit (CST) with an Agency Card. This copy is used in Figma.
- `forTranslation` and `All Agencies` tab contains the English and Spanish translation side by side, with agency-specific copy.

## Copy delivery process responsibilities

### Product

- Engage with product stakeholders to get the information necessary for copy writing.
- Engage with copy writers to get the English language copy drafted, proofed and ready for design.
- Engage with client editorial/communications team to ensure English language and Spanish language copy are edited according to client style guides.
- Engage all necessary stakeholders to get English language copy approved and ready for design.
- Compile copy in [Cal-ITP Benefits Application Copy (Configurable Strings)](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit#gid=0), ready to be used by Design, so Design can sync the spreadsheet to Figma.
- Engage with the translation agency, [iBabbleOn](https://ibabbleon.com/), to get Spanish translations ready for Engineering.
- Ensure English and Spanish copy is ready for Engineering.

### Design

- Sync copy from [Cal-ITP Benefits Application Copy (Configurable Strings)](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit#gid=0) into Figma.
- Ensure the string is in the appropriate column (e.g. `Subtitle`, `ButtonLabel`)

### Engineering

- Use copy from the English and Spanish language tabs of the spreadsheet, and turning it into code in `django.po` message files. Developer-specific instructions in the [Django message files technical documentation](https://docs.calitp.org/benefits/development/i18n/).
- Ensure the messages accurately reflect the spreadsheet and Figma designs.

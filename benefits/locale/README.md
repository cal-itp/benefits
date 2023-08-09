# Copy process

The `LC_MESSAGES` folders in this directory contain the `django.po` message files for English and Spanish translation strings for the Benefits application.

Translation strings include all application copy, including:

- All application copy
- Image and illustration alt tags
- Page titles used in the browser tab
- In-line link URLs

## Cal-ITP Benefits Application Copy (Configurable Strings)

The human-readable version of the English and Spanish translation strings for the application are delivered to Design and Engineering by Product, and live at this link: [Cal-ITP Benefits Application Copy (Configurable Strings)](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit#gid=0).

## Copy process responsibilities

### Product

- Engaging with product stakeholders to get the information necessary for copy writing.
- Engaging with copy writers to get the English language copy drafted, proofed and ready for design.
- Engaging with client editorial/communications team to ensure English language and Spanish language copy are edited according to client style guides.
- Engaging all necessary stakeholders to get English language copy approved and ready for design.
- Compiling copy in [Cal-ITP Benefits Application Copy (Configurable Strings)](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit#gid=0), ready to be used by Design, so Design can sync the spreadsheet to Figma.
- Engaging with the translation agency, [iBabbleOn](https://ibabbleon.com/), to get Spanish translations ready for Engineering.
- Ensure English and Spanish copy is ready for Engineering.

### Design

- Syncing copy from [Cal-ITP Benefits Application Copy (Configurable Strings)](https://docs.google.com/spreadsheets/d/1_Gi_YbJr4ZuXCOsnOWaewvHqUO1nC1nKqiVDHvw0118/edit#gid=0) into Figma.
- Ensuring the string is in the appropriate column (e.g. `Subtitle`, `ButtonLabel`)

### Engineering

- Using copy from the English and Spanish language tabs of the spreadsheet, and turning it into code in `django.po` message files. Read more in the [Django message files technical documentation](https://docs.calitp.org/benefits/development/i18n/).
- Ensuring the messages accurately reflect the spreadsheet and Figma designs.

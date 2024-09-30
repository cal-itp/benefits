# Copy delivery process

The [`locale`](https://github.com/cal-itp/benefits/tree/main/benefits/locale) folder in this repository contain the `django.po` message files for English and Spanish translation strings for the Benefits application.

Translation strings include all application copy, including:

- All application copy
- Image and illustration alt tags
- Page titles used in the browser tab
- In-line link URLs
- Error messages (like [no script](https://github.com/cal-itp/benefits/blob/main/benefits/core/templates/core/includes/noscript.html), [no cookies](https://github.com/cal-itp/benefits/blob/main/benefits/core/templates/core/includes/nocookies.html) warnings)

Developers create and update `django.po` message files for each supported language from copy created and implemented by Design and Product. Design and Product use the tools Figma, Ditto, and Crowdin to craft product copy, manage all copy and variantions of copy (e.g. agency-specific copy or Spanish translation copy), and translate copy.

## Tools used in Cal-ITP Benefits Application Copy

### Figma

Figma is our primary design tool and is the source of truth for all design decisions, concepts, and directions for the Benefits app and all Cal-ITP sites. We have Figma Organization which includes developer mode, version history, and branching–a tool to explore new design directions.

The development team prefers not to have admin or editor capabilities so as not to accidentally interfere with any designs. Currently there is no formal process within Figma for handoff. Instead handoffs occur over the course of two meetings, a review of the designs and then what we call “issue-fest,” or a chance for developers to create Github issues while designers can weigh in and answer questions.

The dev team and design largely collaborate on designs through Slack and comments directly in Figma. Design aims to address Figma comments as soon as possible or within one day.

### Ditto

The human-readable version of the English and Spanish translation strings for the application are delivered to Product and Engineering by Design, and are managed in the Ditto application. [Cal-ITP Benefits](https://app.dittowords.com/projects/65e119db3f806ee92198378a/page/5766:22626).

Ditto is our copy management system for Benefits and the Cal-ITP sites. It syncs directly with Figma and uses many of the same conventions found in Figma, including components and variables (therefore, it is important to be specific when referring to a Ditto component or a Figma variable).

The Benefits project within Ditto is fully synced with Figma. Product and design may use either Figma or Ditto as their source of truth on copy, though it is recommended that Developers use Figma for all final copy. Compiler is considering using the GitHub integration that comes with Ditto, but has not formally integrated Ditto into their workflow as of yet.

In the Benefits project, all of the text has been componentized. Agencies are represented in the text as variants on components. Languages are also represented in the text as variants. Currently Benefits has two languages: English and Spanish. English is the assumed default in the copy in Ditto and Spanish is a variant. There are variants within Ditto that include both an agency and Spanish, such as MST-Spanish.

### Crowdin

Crowdin is our translation platform. We use iBabbleon to provide our translations. With very simple translations (or more complex if you are fluent or native in the language), Compiler team members can translate the strings of text directly in the Crowdin platform. For anything above our language skills, Design contacts Salim at iBabbleon and ask for the new files to be translated once the language files have been synced from Ditto to Crowdin.

## Copy delivery process responsibilities

### Product

- Engage with product stakeholders to get the information necessary for copy writing.
- Collaborate with Design on copy writing.
- Help verify English and Spanish copy is ready for Engineering.

### Design

- Collaborate with Product on copy writing.
- Draft, proof and ready the copy for review in Figma and Ditto.
- Engage with client editorial/communications team to ensure English language and Spanish language copy are edited according to client style guides.
- Ensure copy is synced between Figma, Ditto, and Crowdin.
- Engage with the translation agency, [iBabbleOn](https://ibabbleon.com/), to get Spanish translations ready for Engineering.

### Engineering

- Use copy from Figma, properly synced with Ditto, into code in `django.po` message files. Developer-specific instructions in the [Django message files technical documentation](../development/i18n.md).
- Ensure the messages accurately reflect Figma/Ditto.
